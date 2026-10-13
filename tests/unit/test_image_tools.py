"""Unit test for image generation and GCS upload tool."""

import pytest
from app.image_tools import BUCKET_NAME, PROJECT_ID, generate_blocker_diagram


def test_hardcoded_configs():
    assert PROJECT_ID == "qwiklabs-gcp-04-ae4fde46980b"
    assert BUCKET_NAME == "project-sentinel-assets-ae4fde46980b"


@pytest.mark.asyncio
async def test_generate_blocker_diagram():
    # Call with tool_context=None for standalone testing
    url = await generate_blocker_diagram(
        blocker_description="Designer blocked on copy approval ahead of launch",
        tool_context=None,
    )
    assert url.startswith(f"https://storage.googleapis.com/{BUCKET_NAME}/")
    assert url.endswith((".png", ".jpg", ".jpeg"))
