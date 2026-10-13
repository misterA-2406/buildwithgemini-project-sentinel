"""Unit tests for public holiday tools."""

from app.holiday_tools import check_upcoming_public_holidays


def test_check_upcoming_public_holidays():
    holidays = check_upcoming_public_holidays(country_code="US")
    assert isinstance(holidays, list)
    assert len(holidays) > 0
    first = holidays[0]
    assert "date" in first
    assert "name" in first
    assert first["country_code"] == "US"
