"""Seed script to populate Cloud Firestore with initial risk signals and team activity data.

Hardcoded GCP project ID: qwiklabs-gcp-04-ae4fde46980b
"""

import datetime
from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-04-ae4fde46980b"
RISK_COLLECTION = "risk_signals"
ACTIVITY_COLLECTION = "team_activity"

SEED_SIGNALS = [
    {
        "id": "RS-101",
        "title": "Creative Asset Approval Deadlock",
        "project": "Q4 Growth Campaign",
        "severity": "CRITICAL",
        "status": "OPEN",
        "owner": "Sarah Jenkins (PM)",
        "blocked_party": "Alex Rivera (Design Lead)",
        "waiting_on": "Marcus Vance (VP Marketing)",
        "dependency_chain": "Design team is waiting on approved headline copy; Copywriter is waiting on brand legal signoff; Legal reviewer has not replied for 3 days.",
        "root_cause": "Legal review bottleneck with no designated secondary approver before Friday launch deadline.",
        "recommended_action": "Escalate directly to VP Marketing for provisional approval to prevent 4-day launch slip.",
        "deadline": "2026-10-17",
        "created_at": "2026-10-13T04:00:00Z",
        "updated_at": "2026-10-13T05:30:00Z",
    },
    {
        "id": "RS-102",
        "title": "Payment Gateway Sandbox API Credentials Missing",
        "project": "Fintech Checkout Redesign",
        "severity": "CRITICAL",
        "status": "OPEN",
        "owner": "Liam Chen (Tech Lead)",
        "blocked_party": "Backend Engineering Team",
        "waiting_on": "Stripe Partner Operations / Procurement",
        "dependency_chain": "Backend engineers ready to integrate payment webhooks; Security team waiting on vendor SOC2 questionnaire; Vendor account rep unresponsive.",
        "root_cause": "Vendor onboarding ticket stalled in security review with no escalation trigger.",
        "recommended_action": "Issue executive escalation ticket to Stripe partner manager; use sandbox mock server as interim stub.",
        "deadline": "2026-10-20",
        "created_at": "2026-10-12T14:30:00Z",
        "updated_at": "2026-10-13T02:15:00Z",
    },
    {
        "id": "RS-103",
        "title": "Unassigned Migration Script QA Verification",
        "project": "Postgres Database Upgrade",
        "severity": "WARNING",
        "status": "INVESTIGATING",
        "owner": "Elena Rostova (DevOps Lead)",
        "blocked_party": "DevOps Team",
        "waiting_on": "Data Analytics Team",
        "dependency_chain": "Migration scripts written; dry-run executed; analytics schema validation has no assigned tester.",
        "root_cause": "Task ownership gap during sprint handoff.",
        "recommended_action": "Assign senior analytics engineer before maintenance window on Saturday 02:00 UTC.",
        "deadline": "2026-10-18",
        "created_at": "2026-10-13T01:15:00Z",
        "updated_at": "2026-10-13T01:15:00Z",
    },
    {
        "id": "RS-104",
        "title": "Mobile Push Notification APNs Cert Renewal",
        "project": "Mobile App v2.4 Release",
        "severity": "MONITOR",
        "status": "RESOLVED",
        "owner": "David Kim (Release Manager)",
        "blocked_party": "Mobile App Release Team",
        "waiting_on": "Apple Developer Account Admin",
        "dependency_chain": "APNs certificate expires in 14 days; admin credentials required for signing.",
        "root_cause": "Annual certificate expiration.",
        "recommended_action": "Certificate renewed and uploaded to Cloud KMS.",
        "deadline": "2026-10-25",
        "created_at": "2026-10-10T09:00:00Z",
        "updated_at": "2026-10-12T11:00:00Z",
    },
]

SEED_ACTIVITY = [
    {
        "id": "msg-001",
        "channel": "#proj-q4-launch",
        "project": "Q4 Growth Campaign",
        "sender": "Alex Rivera (Design Lead)",
        "text": "@marcus @sarah pinging again on the approved hero copy for Friday's launch campaign. We are completely blocked on asset exports without final copy signoff.",
        "mentions": ["marcus", "sarah"],
        "hours_unanswered": 52,
        "timestamp": "2026-10-11T02:00:00Z",
    },
    {
        "id": "msg-002",
        "channel": "#proj-q4-launch",
        "project": "Q4 Growth Campaign",
        "sender": "Chloe Bennett (Copywriter)",
        "text": "Submitted copy variations to Legal 3 days ago. No ticket update or feedback received yet.",
        "mentions": ["legal-ops"],
        "hours_unanswered": 48,
        "timestamp": "2026-10-11T06:00:00Z",
    },
    {
        "id": "msg-003",
        "channel": "#team-fintech-checkout",
        "project": "Fintech Checkout Redesign",
        "sender": "Liam Chen (Tech Lead)",
        "text": "Our webhook integration PR is ready for testing, but we still haven't received sandbox API credentials from Stripe partner operations.",
        "mentions": ["procurement", "security"],
        "hours_unanswered": 36,
        "timestamp": "2026-10-11T18:00:00Z",
    },
    {
        "id": "msg-004",
        "channel": "#devops-infra",
        "project": "Postgres Database Upgrade",
        "sender": "Elena Rostova (DevOps Lead)",
        "text": "Reminder: Postgres maintenance window is scheduled for Saturday 02:00 UTC. Still waiting on analytics team to assign someone for QA schema verification.",
        "mentions": ["analytics-lead"],
        "hours_unanswered": 28,
        "timestamp": "2026-10-12T02:00:00Z",
    },
    {
        "id": "msg-005",
        "channel": "#mobile-releases",
        "project": "Mobile App v2.4 Release",
        "sender": "David Kim (Release Manager)",
        "text": "APNs certificate has been renewed and pushed to Cloud KMS. Build pipelines green.",
        "mentions": ["mobile-team"],
        "hours_unanswered": 0,
        "timestamp": "2026-10-12T11:00:00Z",
    },
]


def seed_database():
    """Connect to Firestore and populate risk signals and team activity collections."""
    print(f"Connecting to Firestore using project ID: {PROJECT_ID}...")
    db = firestore.Client(project=PROJECT_ID)

    # Seed risk signals
    risk_col = db.collection(RISK_COLLECTION)
    for item in SEED_SIGNALS:
        doc_id = item["id"]
        risk_col.document(doc_id).set(item)
        print(f"Seeded risk signal [{doc_id}]: {item['title']} ({item['severity']})")

    # Seed team activity
    act_col = db.collection(ACTIVITY_COLLECTION)
    for msg in SEED_ACTIVITY:
        msg_id = msg["id"]
        act_col.document(msg_id).set(msg)
        print(f"Seeded team activity [{msg_id}]: {msg['channel']} from {msg['sender']}")

    print("Successfully seeded all Firestore collections.")


if __name__ == "__main__":
    seed_database()
