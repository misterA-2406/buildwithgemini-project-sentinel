"""Firestore backend tools for Project Sentinel risk signals and dependency blockers.

Hardcoded GCP project ID: qwiklabs-gcp-04-ae4fde46980b
Do NOT read project ID from google.auth.default() or GOOGLE_CLOUD_PROJECT;
on Agent Platform those return the numeric project number, breaking Firestore.
"""

from datetime import datetime, timezone
from typing import Any
from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-04-ae4fde46980b"
COLLECTION_NAME = "risk_signals"

_db_client: firestore.Client | None = None


def get_db() -> firestore.Client:
    """Return a Firestore client instance with hardcoded project ID."""
    global _db_client
    if _db_client is None:
        _db_client = firestore.Client(project=PROJECT_ID)
    return _db_client


def list_risk_signals(severity: str = "", status: str = "") -> list[dict[str, Any]]:
    """Fetches risk signals and blocker records from Firestore.

    Use this tool to view all active blockers, dependency deadlocks, or risks
    across projects. Can be filtered by severity or status.

    Args:
        severity: Optional filter for severity level: 'CRITICAL', 'WARNING', or 'MONITOR'.
        status: Optional filter for status: 'OPEN', 'INVESTIGATING', or 'RESOLVED'.

    Returns:
        A list of risk signal dictionaries.
    """
    db = get_db()
    query = db.collection(COLLECTION_NAME)

    if severity:
        query = query.where("severity", "==", severity.upper().strip())
    if status:
        query = query.where("status", "==", status.upper().strip())

    docs = query.stream()
    results: list[dict[str, Any]] = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        results.append(data)

    return results


def get_risk_signal(signal_id: str) -> dict[str, Any]:
    """Retrieves full details of a specific risk signal by ID.

    Args:
        signal_id: The ID of the risk signal (e.g. 'RS-101').

    Returns:
        A dictionary containing the risk signal's fields, or an error message if not found.
    """
    db = get_db()
    doc_ref = db.collection(COLLECTION_NAME).document(signal_id.strip())
    doc = doc_ref.get()
    if not doc.exists:
        return {"error": f"Risk signal '{signal_id}' not found in Firestore."}

    data = doc.to_dict() or {}
    data["id"] = doc.id
    return data


def create_risk_signal(
    title: str,
    project: str,
    severity: str,
    owner: str,
    blocked_party: str,
    waiting_on: str,
    dependency_chain: str,
    root_cause: str,
    recommended_action: str,
    deadline: str = "",
) -> dict[str, Any]:
    """Creates a new risk signal or blocker record in Firestore.

    Args:
        title: Short title of the risk or blocker deadlock.
        project: Name of the project or sprint.
        severity: Severity level: 'CRITICAL', 'WARNING', or 'MONITOR'.
        owner: Person responsible for resolving or tracking this risk.
        blocked_party: The person or team whose progress is currently stalled.
        waiting_on: The person, team, or dependency holding up progress.
        dependency_chain: Explanation of who is waiting on whom.
        root_cause: Identified underlying root cause.
        recommended_action: Recommended remediation or escalation step.
        deadline: Targeted resolution or project deadline date (e.g. '2026-10-20').

    Returns:
        A dictionary containing the created risk signal and its assigned ID.
    """
    db = get_db()
    now_iso = datetime.now(timezone.utc).isoformat()

    # Generate an incremental-style ID if possible, or timestamp-based
    existing_docs = list(db.collection(COLLECTION_NAME).stream())
    signal_id = f"RS-{101 + len(existing_docs)}"

    new_record: dict[str, Any] = {
        "id": signal_id,
        "title": title,
        "project": project,
        "severity": severity.upper().strip(),
        "status": "OPEN",
        "owner": owner,
        "blocked_party": blocked_party,
        "waiting_on": waiting_on,
        "dependency_chain": dependency_chain,
        "root_cause": root_cause,
        "recommended_action": recommended_action,
        "deadline": deadline or "TBD",
        "created_at": now_iso,
        "updated_at": now_iso,
    }

    db.collection(COLLECTION_NAME).document(signal_id).set(new_record)
    return {
        "success": True,
        "message": f"Created risk signal {signal_id}",
        "risk_signal": new_record,
    }


def update_risk_signal(
    signal_id: str,
    status: str = "",
    recommended_action: str = "",
    resolution_notes: str = "",
) -> dict[str, Any]:
    """Updates an existing risk signal's status, action, or resolution notes.

    Args:
        signal_id: The ID of the risk signal to update (e.g. 'RS-101').
        status: Updated status ('OPEN', 'INVESTIGATING', or 'RESOLVED'). Optional.
        recommended_action: Updated recommended remediation action. Optional.
        resolution_notes: Notes explaining how the issue was triaged or resolved. Optional.

    Returns:
        A dictionary with the update confirmation and updated fields.
    """
    db = get_db()
    doc_ref = db.collection(COLLECTION_NAME).document(signal_id.strip())
    doc = doc_ref.get()

    if not doc.exists:
        return {"error": f"Risk signal '{signal_id}' not found in Firestore."}

    updates: dict[str, Any] = {
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    if status:
        updates["status"] = status.upper().strip()
    if recommended_action:
        updates["recommended_action"] = recommended_action
    if resolution_notes:
        updates["resolution_notes"] = resolution_notes

    doc_ref.update(updates)
    return {
        "success": True,
        "signal_id": signal_id,
        "updated_fields": updates,
    }
