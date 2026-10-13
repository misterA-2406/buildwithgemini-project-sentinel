"""Team activity feed ingestion tools for Project Sentinel.

Ingests conversation threads and updates from team channels to detect
early blocker patterns, unanswered mentions, and stalled handoffs.
Hardcoded GCP project ID: qwiklabs-gcp-04-ae4fde46980b
"""

from datetime import datetime, timezone
import os
from typing import Any
from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-04-ae4fde46980b"
ACTIVITY_COLLECTION = "team_activity"

_db_client: firestore.Client | None = None


def get_db() -> firestore.Client:
    """Return Firestore client instance with hardcoded project ID."""
    global _db_client
    if _db_client is None:
        _db_client = firestore.Client(project=PROJECT_ID)
    return _db_client


def fetch_team_activity_feed(
    channel_or_project: str = "",
    min_unanswered_hours: int = 0,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Fetches recent team communication threads, chat messages, and updates.

    Use this tool to inspect raw team chatter, look for unanswered questions,
    unresponsive stakeholders, and stalled handoffs across channels.

    Args:
        channel_or_project: Optional filter for channel (e.g. '#proj-q4-launch') or project name.
        min_unanswered_hours: Filter for messages that have gone unanswered for at least this many hours.
        limit: Maximum number of messages to return (default 20).

    Returns:
        A list of team message records with sender, channel, text, and thread status.
    """
    db = get_db()
    query = db.collection(ACTIVITY_COLLECTION)

    docs = query.stream()
    messages: list[dict[str, Any]] = []

    channel_filter = channel_or_project.lower().strip() if channel_or_project else ""

    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id

        if channel_filter:
            doc_channel = str(data.get("channel", "")).lower()
            doc_project = str(data.get("project", "")).lower()
            if channel_filter not in doc_channel and channel_filter not in doc_project:
                continue

        unanswered = int(data.get("hours_unanswered", 0))
        if unanswered < min_unanswered_hours:
            continue

        messages.append(data)

    # Sort by hours_unanswered descending, then timestamp
    messages.sort(
        key=lambda x: (int(x.get("hours_unanswered", 0)), str(x.get("timestamp", ""))),
        reverse=True,
    )
    return messages[:limit]


def log_team_message(
    channel: str,
    project: str,
    sender: str,
    text: str,
    mentions: str = "",
    hours_unanswered: int = 0,
) -> dict[str, Any]:
    """Logs a new team message or communication update into the activity feed.

    Args:
        channel: Channel name (e.g. '#proj-q4-launch' or 'email').
        project: Project name (e.g. 'Q4 Growth Campaign').
        sender: Name and role of the sender.
        text: Body of the message.
        mentions: Comma-separated list of mentioned users or handles.
        hours_unanswered: Number of hours this message has been awaiting a reply.

    Returns:
        A dictionary confirming the logged message and its assigned ID.
    """
    db = get_db()
    now_iso = datetime.now(timezone.utc).isoformat()
    msg_id = f"msg-{int(datetime.now(timezone.utc).timestamp())}"

    record = {
        "id": msg_id,
        "channel": channel,
        "project": project,
        "sender": sender,
        "text": text,
        "mentions": [m.strip() for m in mentions.split(",") if m.strip()],
        "hours_unanswered": hours_unanswered,
        "timestamp": now_iso,
    }

    db.collection(ACTIVITY_COLLECTION).document(msg_id).set(record)
    return {
        "success": True,
        "message_id": msg_id,
        "record": record,
    }
