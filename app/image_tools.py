"""Image generation tool for Project Sentinel.

Generates bottleneck dependency flowcharts and blocker visual diagrams
using gemini-3.1-flash-lite-image in the global region.
Saves the artifact in the session (ToolContext.save_artifact) and uploads
the raw bytes directly to Cloud Storage for public web rendering.
"""

import logging
import time
from typing import Any
from google import genai
from google.adk.tools import ToolContext
from google.cloud import storage
from google.genai import types

logger = logging.getLogger(__name__)

PROJECT_ID = "qwiklabs-gcp-04-ae4fde46980b"
BUCKET_NAME = "project-sentinel-assets-ae4fde46980b"
IMAGE_MODEL = "gemini-3.1-flash-lite-image"


async def generate_blocker_diagram(
    blocker_description: str,
    tool_context: ToolContext,
) -> str:
    """Generates an infographic or dependency bottleneck diagram for a project blocker.

    Uses the gemini-3.1-flash-lite-image model in the global region to create a
    visual representation of the stalled workflow or delivery chain. Saves the
    image to the session artifact store and uploads it to public Cloud Storage.

    Args:
        blocker_description: Description of the project blocker, dependency chain, or topic.

    Returns:
        The public HTTPS URL of the uploaded diagram image.
    """
    prompt = (
        f"A clean, modern, high-contrast infographic diagram illustrating a project "
        f"management workflow bottleneck: {blocker_description}. "
        f"Professional corporate tech style, minimal vector flowchart with nodes and connecting arrows, "
        f"a red blocked caution icon on the bottleneck step, and clear visual hierarchy."
    )

    client = genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location="global",
    )

    response = client.models.generate_content(
        model=IMAGE_MODEL,
        contents=prompt,
    )

    image_bytes: bytes | None = None
    mime_type = "image/png"

    for candidate in response.candidates:
        if candidate.content and candidate.content.parts:
            for part in candidate.content.parts:
                if part.inline_data and part.inline_data.data:
                    image_bytes = part.inline_data.data
                    mime_type = part.inline_data.mime_type or "image/png"
                    break
        if image_bytes:
            break

    if not image_bytes:
        raise RuntimeError("No image bytes returned by gemini-3.1-flash-lite-image.")

    ext = "jpg" if "jpeg" in mime_type else "png"
    filename = f"blocker_diagram_{int(time.time())}.{ext}"

    # (1) Save with tool_context.save_artifact so it shows up in Artifacts panel
    if tool_context is not None:
        try:
            artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
            await tool_context.save_artifact(
                filename=filename,
                artifact=artifact_part,
            )
        except Exception as e:
            logger.warning(f"Could not save session artifact: {e}")

    # (2) Upload same image bytes to public Cloud Storage bucket
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_string(image_bytes, content_type=mime_type)

    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"
    return public_url
