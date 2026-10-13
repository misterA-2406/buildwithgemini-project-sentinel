"""Playwright script to record the complete 5-scene Project Risk Intelligence product demo."""

import os
import glob
import subprocess
import time
from playwright.sync_api import sync_playwright

VIDEO_DIR = "/config/Desktop/BuildWithGemini/project-sentinel/recordings"
OUTPUT_MP4 = "/config/Desktop/BuildWithGemini/project-sentinel/demo_video.mp4"
ARTIFACT_DIR = "/config/.gemini/antigravity/brain/aad946fa-1aaa-4d2e-926c-856860d2d6a3"

os.makedirs(VIDEO_DIR, exist_ok=True)

EXACT_PROMPT = (
    "Investigate why our Friday release is at risk. Check the latest task records and team updates, "
    "identify the root blocker, calculate how a two-day approval delay would affect the critical path, "
    "and generate a dependency bottleneck map. Then draft a targeted escalation message for the "
    "responsible stakeholder using our team's saved escalation preferences. "
    "Show me the evidence and recommended actions before I approve anything."
)


def type_smoothly(page, selector, text, delay_ms=14):
    """Simulates realistic human typing."""
    page.click(selector)
    for char in text:
        page.keyboard.type(char, delay=delay_ms)


def run():
    print("[1/5] Launching browser with HD 1280x720 video recording...")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path="/usr/bin/google-chrome",
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--window-size=1280,720"
            ]
        )
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            record_video_dir=VIDEO_DIR,
            record_video_size={"width": 1280, "height": 720}
        )
        page = context.new_page()

        # =======================================================
        # SCENE 1: Show Core Value — Detect Hidden Project Risks
        # =======================================================
        print("[Scene 1] Navigating to Project Risk Intelligence dashboard...")
        page.goto("http://localhost:8080", wait_until="networkidle")
        page.evaluate("setCaption('Scene 1: Show Core Value — Detect Hidden Project Risks')")
        page.wait_for_timeout(2500)

        # Smoothly scroll down to highlight KPIs and Critical Dependency Chain
        print("  - Highlighting 8 active risks, 3 blocked tasks, 2 at-risk deadlines, 3-day delay...")
        page.evaluate("window.scrollTo({top: 180, behavior: 'smooth'})")
        page.wait_for_timeout(3000)

        # Show user clicking "View Dependency"
        print("  - Clicking 'View Dependency' to reveal blocked chain...")
        page.click("#btn-view-dependency")
        page.wait_for_timeout(3000)

        # =======================================================
        # SCENE 2: Ask a Richer Prompt — Investigate, Calculate, Act
        # =======================================================
        print("[Scene 2] Switching to AI Assistant...")
        page.evaluate("setCaption('Scene 2: Ask a Richer Prompt — Investigate, Calculate, and Act')")
        page.click("#nav-assistant")
        page.wait_for_timeout(1500)

        print("  - Typing rich investigation prompt character-by-character...")
        type_smoothly(page, "#chat-input", EXACT_PROMPT, delay_ms=14)
        page.wait_for_timeout(800)
        page.click("#chat-send-btn")

        # =======================================================
        # SCENE 3: Show Real Tool Calls and Database Lookups
        # =======================================================
        print("[Scene 3] Waiting for agent tool executions...")
        page.evaluate("setCaption('Scene 3: Real Tool Calls, Database Lookups & Schedule Math')")
        
        # Wait for agent investigation response card to be rendered
        page.wait_for_selector("#chat-log .border-indigo-200", timeout=20000)
        page.wait_for_timeout(2500)

        # Smoothly scroll down chat log to show tool executions and findings
        print("  - Scrolling through tool executions and evidence...")
        page.evaluate("""
            const c = document.getElementById('chat-log');
            if (c) c.scrollTo({top: 260, behavior: 'smooth'});
        """)
        page.wait_for_timeout(3500)

        # =======================================================
        # SCENE 4: Generate an Actionable Escalation
        # =======================================================
        print("[Scene 4] Presenting escalation draft and review actions...")
        page.evaluate("setCaption('Scene 4: Critical-Path Flowchart & Targeted Stakeholder Escalation')")
        
        page.evaluate("""
            const c = document.getElementById('chat-log');
            if (c) c.scrollTo({top: c.scrollHeight, behavior: 'smooth'});
        """)
        page.wait_for_timeout(3500)

        # User approves the draft escalation
        print("  - User clicks 'Approve & Schedule Follow-Up'...")
        page.click("#btn-approve-escalation")
        page.wait_for_timeout(1500)

        # =======================================================
        # SCENE 5: Close With the Outcome
        # =======================================================
        print("[Scene 5] Returning to dashboard with scheduled escalation outcome...")
        page.evaluate("setCaption('Scene 5: Proactive Outcome — Action Taken Before Delivery Slips')")
        page.wait_for_timeout(4500)

        print("[Closing] Finalizing recording context...")
        context.close()
        browser.close()

    # Transcode newest webm to demo_video.mp4
    webms = sorted(glob.glob(os.path.join(VIDEO_DIR, "*.webm")), key=os.path.getmtime, reverse=True)
    if not webms:
        raise RuntimeError("No recorded webm found in " + VIDEO_DIR)

    latest_webm = webms[0]
    print(f"[Transcode] Converting {latest_webm} to MP4 at {OUTPUT_MP4}...")
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-i", latest_webm,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-r", "30",
        OUTPUT_MP4
    ]
    subprocess.run(ffmpeg_cmd, check=True)

    # Copy to artifacts directory
    artifact_mp4 = os.path.join(ARTIFACT_DIR, "demo_video.mp4")
    subprocess.run(["cp", OUTPUT_MP4, artifact_mp4], check=True)
    print(f"[Done] Polished demo video saved to {OUTPUT_MP4} and {artifact_mp4}!")


if __name__ == "__main__":
    run()
