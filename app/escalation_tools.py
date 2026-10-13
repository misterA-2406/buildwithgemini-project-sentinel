"""Escalation drafting and dispatch tools for Project Sentinel.

Generates channel-specific, diplomacy-tuned escalation messages and
optionally dispatches to live Slack webhooks or logs to Firestore.
Hardcoded GCP project ID: qwiklabs-gcp-04-ae4fde46980b
"""

from datetime import datetime, timezone
import json
import os
from typing import Any
import urllib.request
from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-04-ae4fde46980b"
RISK_COLLECTION = "risk_signals"

_db_client: firestore.Client | None = None


def get_db() -> firestore.Client:
    """Return Firestore client instance with hardcoded project ID."""
    global _db_client
    if _db_client is None:
        _db_client = firestore.Client(project=PROJECT_ID)
    return _db_client


def draft_escalation_message(
    signal_id: str,
    target_channel: str = "slack",
    urgency_level: str = "HIGH",
    additional_context: str = "",
) -> dict[str, Any]:
    """Drafts a targeted, high-impact escalation message for a specific risk signal.

    Pulls root cause, blocked party, and target deadline from Firestore to craft
    a ready-to-send draft tailored for Slack, Email, or Jira.

    Args:
        signal_id: ID of the risk signal (e.g. 'RS-101').
        target_channel: Preferred format: 'slack', 'email', or 'jira'.
        urgency_level: Urgency tier: 'CRITICAL', 'HIGH', or 'NUDGE'.
        additional_context: Any optional manager notes to include.

    Returns:
        A dictionary containing the formatted draft, recipient, and subject/header.
    """
    db = get_db()
    doc_ref = db.collection(RISK_COLLECTION).document(signal_id.strip())
    doc = doc_ref.get()

    if not doc.exists:
        return {"error": f"Risk signal '{signal_id}' not found in Firestore."}

    data = doc.to_dict() or {}
    title = data.get("title", "Project Blocker")
    project = data.get("project", "Active Project")
    blocked_party = data.get("blocked_party", "Team")
    waiting_on = data.get("waiting_on", "Stakeholder")
    root_cause = data.get("root_cause", "Unspecified blocker")
    deadline = data.get("deadline", "Upcoming deadline")
    recommended_action = data.get("recommended_action", "Review and unblock")

    ch = target_channel.lower().strip()
    urgency = urgency_level.upper().strip()

    prefix = "🚨 [ACTION REQUIRED - CRITICAL]" if urgency == "CRITICAL" else "⚠️ [BLOCKED DEPENDENCY]"

    if ch == "email":
        subject = f"{prefix} {project}: {title} (Target: {deadline})"
        body = (
            f"Hi {waiting_on},\n\n"
            f"We are tracking a critical path delivery risk on '{project}'.\n\n"
            f"• Current Status: {blocked_party} is currently blocked and unable to proceed.\n"
            f"• Dependency: Waiting on approval / assets from {waiting_on}.\n"
            f"• Root Cause: {root_cause}\n"
            f"• Target Milestone: {deadline}\n"
            f"{'• Context: ' + additional_context + chr(10) if additional_context else ''}\n"
            f"Proposed Next Step:\n"
            f"{recommended_action}\n\n"
            f"Could you please review and provide an update today to keep the launch on schedule?\n\n"
            f"Best regards,\nProject Sentinel Operations"
        )
    elif ch == "jira":
        subject = f"[{urgency}] {title}"
        body = (
            f"h3. Blocker Escalation Notice\n"
            f"*Project:* {project}\n"
            f"*Blocked Party:* {blocked_party}\n"
            f"*Waiting On:* {waiting_on}\n"
            f"*Impact Date:* {deadline}\n\n"
            f"h4. Root Cause\n{root_cause}\n\n"
            f"h4. Action Needed\n{recommended_action}\n"
            f"{'h4. Additional Notes' + chr(10) + additional_context if additional_context else ''}"
        )
    else:  # Default to Slack
        subject = f"{prefix} *{title}* ({project})"
        body = (
            f"{prefix} *{title}*\n"
            f"> *Project:* `{project}` | *Target:* `{deadline}`\n"
            f"> *Blocked:* {blocked_party} ➔ *Waiting On:* @{waiting_on}\n"
            f"> *Bottleneck:* {root_cause}\n"
            f"{'> *Notes:* ' + additional_context + chr(10) if additional_context else ''}"
            f"👉 *Action Needed:* {recommended_action}\n"
            f"_Reply directly or react with ✅ once unblocked._"
        )

    return {
        "signal_id": signal_id,
        "channel": ch,
        "urgency": urgency,
        "recipient": waiting_on,
        "subject_or_header": subject,
        "draft_body": body,
        "status": "DRAFT_READY_FOR_APPROVAL",
    }


def dispatch_escalation(
    signal_id: str,
    channel: str,
    message_text: str,
    recipient: str,
) -> dict[str, Any]:
    """Dispatches an approved escalation notice to a live channel or records it.

    If the environment variable `SLACK_WEBHOOK_URL` is set and channel is 'slack',
    it immediately dispatches a live HTTP POST to the Slack channel.
    Otherwise, it logs the dispatch event to the Firestore risk signal record.

    Args:
        signal_id: ID of the risk signal (e.g. 'RS-101').
        channel: Delivery channel ('slack', 'email', 'jira').
        message_text: The approved message text to send.
        recipient: The target stakeholder name or email.

    Returns:
        A dictionary with dispatch confirmation, live delivery status, and timestamps.
    """
    db = get_db()
    now_iso = datetime.now(timezone.utc).isoformat()
    slack_webhook = os.environ.get("SLACK_WEBHOOK_URL", "").strip()

    live_delivered = False
    delivery_note = "Logged to Firestore escalation history."

    if channel.lower() == "slack" and slack_webhook:
        try:
            payload = json.dumps({"text": message_text}).encode("utf-8")
            req = urllib.request.Request(
                slack_webhook,
                data=payload,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    live_delivered = True
                    delivery_note = "Live message delivered to Slack webhook successfully."
        except Exception as e:
            delivery_note = f"Slack webhook attempt failed ({e}); saved to audit log."

    # Update risk signal record in Firestore
    doc_ref = db.collection(RISK_COLLECTION).document(signal_id.strip())
    doc = doc_ref.get()
    if doc.exists:
        doc_ref.update(
            {
                "status": "ESCALATED",
                "last_escalated_at": now_iso,
                "last_escalation_recipient": recipient,
                "updated_at": now_iso,
            }
        )

    return {
        "success": True,
        "signal_id": signal_id,
        "dispatched_at": now_iso,
        "recipient": recipient,
        "channel": channel,
        "live_api_delivered": live_delivered,
        "delivery_note": delivery_note,
    }
