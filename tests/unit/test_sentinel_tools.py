"""Unit tests for Project Sentinel schedule, activity, and escalation tools."""

from app.activity_tools import fetch_team_activity_feed
from app.escalation_tools import draft_escalation_message
from app.schedule_tools import calculate_schedule_slip


def test_calculate_schedule_slip():
    # Test deadline in past or soon
    result = calculate_schedule_slip(
        target_deadline="2026-10-17",
        days_stalled=3,
        remaining_buffer_days=0,
        blocked_task_duration_days=2,
    )
    assert "projected_finish_date" in result
    assert "weekend_days_incurred" in result
    assert "severity" in result
    assert "summary" in result


def test_fetch_team_activity():
    feed = fetch_team_activity_feed(limit=5)
    assert isinstance(feed, list)
    assert len(feed) > 0
    # Check fields
    first = feed[0]
    assert "channel" in first
    assert "sender" in first
    assert "text" in first


def test_draft_escalation_message():
    draft = draft_escalation_message(signal_id="RS-101", target_channel="slack")
    assert draft.get("signal_id") == "RS-101"
    assert "draft_body" in draft
    assert "recipient" in draft
    assert "Marcus Vance (VP Marketing)" in draft.get("recipient", "")

    # Test email format
    email_draft = draft_escalation_message(signal_id="RS-101", target_channel="email")
    assert "subject_or_header" in email_draft
    assert "Hi Marcus Vance (VP Marketing)" in email_draft["draft_body"]
