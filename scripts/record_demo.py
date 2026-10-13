"""Automated demo video recording script using Playwright and Chromium."""

import os
import glob
import subprocess
import time
from playwright.sync_api import sync_playwright

VIDEO_DIR = "/config/Desktop/BuildWithGemini/project-sentinel/recordings"
OUTPUT_MP4 = "/config/Desktop/BuildWithGemini/project-sentinel/demo_video.mp4"
ARTIFACT_DIR = "/config/.gemini/antigravity/brain/aad946fa-1aaa-4d2e-926c-856860d2d6a3"

os.makedirs(VIDEO_DIR, exist_ok=True)

def type_smoothly(page, selector, text, delay_ms=22):
    """Types text character by character to look natural."""
    page.click(selector)
    for char in text:
        page.keyboard.type(char, delay=delay_ms)

def record():
    print("[1/5] Launching browser and starting recording...")
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

        print("[2/5] Navigating to Project Sentinel Dashboard...")
        page.goto("http://localhost:8080", wait_until="networkidle")
        page.wait_for_timeout(2500)

        # 1. Overview Tab Tour
        print("  - Showcasing Overview KPIs & Risk Cards...")
        page.evaluate("window.scrollTo({top: 320, behavior: 'smooth'})")
        page.wait_for_timeout(2500)
        page.evaluate("window.scrollTo({top: 0, behavior: 'smooth'})")
        page.wait_for_timeout(1200)

        # 2. Dependency Map Tab Tour
        print("  - Showcasing Dependency Topology Map...")
        page.click("#nav-map")
        page.wait_for_timeout(2000)
        # Select N3 (Legal Bottleneck node)
        page.evaluate("if (window.selectNode) window.selectNode('N3');")
        page.wait_for_timeout(2500)

        # 3. Schedule Calculator Tour
        print("  - Showcasing Schedule Slip Calculator...")
        page.click("#nav-calculator")
        page.wait_for_timeout(2000)
        # Adjust slider to simulate dynamic calculation
        page.fill("#calc-stalled", "4")
        page.evaluate("if (window.updateRangeLabel) window.updateRangeLabel('stalled'); if (window.runCalculation) window.runCalculation();")
        page.wait_for_timeout(2500)

        # 4. AI Operations Assistant - Prompt 1 (What app does best)
        print("  - Navigating to AI Assistant...")
        page.click("#nav-assistant")
        page.wait_for_timeout(1500)

        prompt1 = "What are our critical risk signals and what is blocking Friday's release?"
        print(f"  - Typing Prompt 1: '{prompt1}'...")
        type_smoothly(page, "#chat-input", prompt1, delay_ms=18)
        page.wait_for_timeout(800)
        page.click("#chat-send-btn")
        
        print("  - Waiting for agent response to Prompt 1...")
        # Wait until chat log has at least 3 children (greeting + user msg + agent reply)
        page.wait_for_function("""
            () => {
                const log = document.getElementById('chat-log');
                return log && log.querySelectorAll(':scope > div:not([id^="typing-"])').length >= 3;
            }
        """, timeout=50000)
        page.wait_for_timeout(2500)
        
        # Scroll down chat log smoothly to read response
        page.evaluate("""
            const c = document.getElementById('chat-log');
            if (c) c.scrollTo({top: c.scrollHeight, behavior: 'smooth'});
        """)
        page.wait_for_timeout(3000)

        # 5. AI Operations Assistant - Prompt 2 (Richer tool call + schedule calc + escalation)
        prompt2 = "Please calculate the exact schedule slip for RS-101 if stalled 3 days past the 2026-10-17 deadline with 0 buffer days, and draft an urgent Slack escalation message for Marcus Vance."
        print(f"  - Typing Prompt 2: '{prompt2}'...")
        type_smoothly(page, "#chat-input", prompt2, delay_ms=16)
        page.wait_for_timeout(800)
        page.click("#chat-send-btn")

        print("  - Waiting for agent response to Prompt 2 (tool calls)...")
        # Wait until chat log has at least 5 children (greeting + user1 + agent1 + user2 + agent2)
        page.wait_for_function("""
            () => {
                const log = document.getElementById('chat-log');
                return log && log.querySelectorAll(':scope > div:not([id^="typing-"])').length >= 5;
            }
        """, timeout=60000)
        page.wait_for_timeout(2500)

        # Scroll to show complete tool response
        page.evaluate("""
            const c = document.getElementById('chat-log');
            if (c) c.scrollTo({top: c.scrollHeight, behavior: 'smooth'});
        """)
        page.wait_for_timeout(5000)

        print("[3/5] Closing context and finalizing video...")
        context.close()
        browser.close()

    # Find the latest webm recorded
    webms = sorted(glob.glob(os.path.join(VIDEO_DIR, "*.webm")), key=os.path.getmtime, reverse=True)
    if not webms:
        raise RuntimeError("No recorded webm found in " + VIDEO_DIR)
    
    latest_webm = webms[0]
    print(f"[4/5] Transcoding {latest_webm} to MP4 ({OUTPUT_MP4})...")
    
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-i", latest_webm,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "22",
        "-pix_fmt", "yuv420p",
        "-r", "30",
        OUTPUT_MP4
    ]
    subprocess.run(ffmpeg_cmd, check=True)
    
    # Also copy to artifact directory
    artifact_mp4 = os.path.join(ARTIFACT_DIR, "demo_video.mp4")
    subprocess.run(["cp", OUTPUT_MP4, artifact_mp4], check=True)
    print(f"[5/5] Successfully saved demo video to {OUTPUT_MP4} and {artifact_mp4}!")

if __name__ == "__main__":
    record()
