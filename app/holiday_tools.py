"""Public holiday lookup tool for Project Sentinel.

Uses the free Nager.Date Public Holidays API (from the public-apis directory)
to check upcoming national and bank holidays that could delay project sprints
or stakeholder approvals across distributed teams.
"""

import json
import os
from typing import Any
import urllib.request


def check_upcoming_public_holidays(
    country_code: str = "US",
) -> list[dict[str, Any]]:
    """Checks upcoming official public holidays for a given country code.

    Use this tool to identify upcoming non-working days, bank holidays, or
    office closures that could delay project milestones, approvals, or handoffs.

    Args:
        country_code: 2-letter ISO country code (e.g. 'US', 'GB', 'CA', 'DE', 'IN'). Defaults to 'US'.

    Returns:
        A list of upcoming public holiday dictionaries with date, name, and localName.
    """
    code = (country_code or "US").strip().upper()
    api_key = os.environ.get("HOLIDAY_API_KEY", "")

    url = f"https://date.nager.at/api/v3/NextPublicHolidays/{code}"
    headers = {"User-Agent": "ProjectSentinel/1.0"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                results = []
                for item in data[:8]:
                    results.append(
                        {
                            "date": item.get("date"),
                            "name": item.get("name"),
                            "local_name": item.get("localName"),
                            "country_code": item.get("countryCode"),
                            "is_global": item.get("global", True),
                        }
                    )
                return results
    except Exception as e:
        return [{"error": f"Failed to fetch public holidays for '{code}': {e}"}]

    return []
