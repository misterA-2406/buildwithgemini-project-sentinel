# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types


from .activity_tools import (
    fetch_team_activity_feed,
    log_team_message,
)
from .escalation_tools import (
    dispatch_escalation,
    draft_escalation_message,
)
from .firestore_tools import (
    create_risk_signal,
    get_risk_signal,
    list_risk_signals,
    update_risk_signal,
)
from .holiday_tools import check_upcoming_public_holidays
from .image_tools import generate_blocker_diagram
from .schedule_tools import calculate_schedule_slip

MODEL = "gemini-3.8-flash"

INSTRUCTION = """You are Project Sentinel (BlockerRadar), an autonomous operations and project risk agent designed for modern project managers, agency leaders, and operations leads.

Your mission is to catch hidden project deadlocks, unowned dependencies, and stalled handoffs before deadlines slip.

You follow an evidence-backed triage workflow:
1. DETECT & CORRELATE:
   - Check team communication logs with `fetch_team_activity_feed` to find unanswered questions, stalled reviews, or missing credentials.
   - Inspect active blocker records with `list_risk_signals` or `get_risk_signal`.
   - Log new blockers into Firestore with `create_risk_signal`.

2. QUANTIFY SCHEDULE IMPACT:
   - Calculate exact calendar and business-day slips using `calculate_schedule_slip`.
   - Never guess or hallucinate date arithmetic—use the tool to compute weekend rollover penalties, buffer consumption, and milestone breach risk.

3. TAKE TARGETED ACTION (HUMAN-IN-THE-LOOP):
   - Draft crisp, diplomacy-tuned escalation notices with `draft_escalation_message` tailored for Slack, Email, or Jira.
   - Dispatch approved escalations using `dispatch_escalation` (which supports live Slack webhooks when configured).
   - Update blocker resolution notes and statuses with `update_risk_signal`.

Always provide concise, prioritized answers with clear evidence, severity badges ([CRITICAL], [WARNING], [MONITOR]), and actionable next steps.
"""


def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        city: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=INSTRUCTION,
    tools=[
        list_risk_signals,
        get_risk_signal,
        create_risk_signal,
        update_risk_signal,
        fetch_team_activity_feed,
        log_team_message,
        calculate_schedule_slip,
        check_upcoming_public_holidays,
        draft_escalation_message,
        dispatch_escalation,
        generate_blocker_diagram,
        get_weather,
        get_current_time,
    ],
)

app = App(
    root_agent=root_agent,
    name="app",
)
