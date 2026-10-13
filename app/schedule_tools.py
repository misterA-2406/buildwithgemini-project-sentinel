"""Schedule and critical path delay impact calculation tool.

Performs deterministic business-day and weekend-rollover math to quantify
exact milestone slip without LLM arithmetic hallucinations.
"""

from datetime import date, datetime, timedelta
from typing import Any


def _add_business_days(start_date: date, num_days: int) -> tuple[date, int]:
    """Adds business days (Monday-Friday) to a date, tracking weekend days skipped."""
    current = start_date
    added = 0
    weekend_days = 0
    while added < num_days:
        current += timedelta(days=1)
        if current.weekday() >= 5:  # 5=Saturday, 6=Sunday
            weekend_days += 1
        else:
            added += 1
    return current, weekend_days


def calculate_schedule_slip(
    target_deadline: str,
    days_stalled: int,
    remaining_buffer_days: int = 0,
    blocked_task_duration_days: int = 1,
) -> dict[str, Any]:
    """Calculates the exact critical path delay and projected completion date.

    Uses deterministic calendar arithmetic to compute how a blocker impacts
    the final deadline, taking into account business days, remaining project
    buffer, and weekend rollover penalties.

    Args:
        target_deadline: The current target deadline in 'YYYY-MM-DD' format.
        days_stalled: Number of days the task or approval has been stalled/waiting.
        remaining_buffer_days: Available contingency buffer days for the project (default 0).
        blocked_task_duration_days: Days required to finish the blocked task once unblocked (default 1).

    Returns:
        A dictionary with exact dates, delay breakdown, and severity assessment.
    """
    try:
        deadline_dt = datetime.strptime(target_deadline.strip(), "%Y-%m-%d").date()
    except ValueError:
        return {
            "error": f"Invalid date format: '{target_deadline}'. Expected 'YYYY-MM-DD'."
        }

    # Calculate net slip past existing buffer
    net_stalled_days = max(0, days_stalled - remaining_buffer_days)
    total_working_days_needed = net_stalled_days + blocked_task_duration_days

    today = date.today()
    projected_finish_date, weekend_days = _add_business_days(
        today, total_working_days_needed
    )

    calendar_days_total = (projected_finish_date - today).days
    calendar_slip_days = (projected_finish_date - deadline_dt).days
    is_breached = projected_finish_date > deadline_dt

    if is_breached:
        if calendar_slip_days >= 3:
            severity = "CRITICAL"
        else:
            severity = "HIGH"
    elif calendar_slip_days == 0:
        severity = "WARNING (ZERO_BUFFER)"
    else:
        severity = "ON_TRACK (BUFFER_INTACT)"

    return {
        "target_deadline": deadline_dt.isoformat(),
        "today": today.isoformat(),
        "days_stalled": days_stalled,
        "remaining_buffer_days": remaining_buffer_days,
        "net_delay_work_days": net_stalled_days,
        "weekend_days_incurred": weekend_days,
        "total_calendar_days_needed": calendar_days_total,
        "projected_finish_date": projected_finish_date.isoformat(),
        "projected_finish_day_of_week": projected_finish_date.strftime("%A"),
        "calendar_days_slipped": max(0, calendar_slip_days),
        "is_deadline_breached": is_breached,
        "severity": severity,
        "summary": (
            f"With {days_stalled} days stalled and {remaining_buffer_days} buffer days, "
            f"the projected delivery date is {projected_finish_date.strftime('%A, %b %d, %Y')}. "
            f"{'DEADLINE BREACHED by ' + str(calendar_slip_days) + ' calendar days.' if is_breached else 'Within buffer.'}"
        ),
    }
