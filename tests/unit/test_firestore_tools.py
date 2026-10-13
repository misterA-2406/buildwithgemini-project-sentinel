"""Unit tests for Firestore backend tools."""

from app.firestore_tools import (
    PROJECT_ID,
    get_risk_signal,
    list_risk_signals,
)


def test_project_id_hardcoded():
    assert PROJECT_ID == "qwiklabs-gcp-04-ae4fde46980b"


def test_list_and_get_risk_signals():
    signals = list_risk_signals()
    assert isinstance(signals, list)
    assert len(signals) >= 4

    signal = get_risk_signal("RS-101")
    assert signal.get("id") == "RS-101"
    assert "Creative Asset Approval Deadlock" in signal.get("title", "")
    assert signal.get("severity") == "CRITICAL"
