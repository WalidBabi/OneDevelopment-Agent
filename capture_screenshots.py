#!/usr/bin/env python3
"""
Capture screenshots from Nova AI website and add to presentation
"""

import asyncio
from playwright.async_api import async_playwright
import os

SCREENSHOT_DIR = "/home/ec2-user/OneDevelopment-Agent/screenshots"
WEBSITE_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000/')

async def capture_screenshots():
    """Capture screenshots from the Nova AI website"""
    
    # Create screenshot directory
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            device_scale_factor=2  # High resolution
        )
        page = await context.new_page()
        
        print(f"🌐 Navigating to {WEBSITE_URL}")
        
        try:
            # Navigate to the main page
            await page.goto(WEBSITE_URL, wait_until='networkidle', timeout=30000)
            await asyncio.sleep(2)  # Wait for animations
            
            # Screenshot 1: Main landing page
            screenshot1 = f"{SCREENSHOT_DIR}/nova_landing.png"
            await page.screenshot(path=screenshot1, full_page=False)
            print(f"📸 Captured: {screenshot1}")
            
            # Screenshot 2: Chat interface - try clicking or scrolling
            await page.screenshot(path=f"{SCREENSHOT_DIR}/nova_main.png", full_page=True)
            print(f"📸 Captured: {SCREENSHOT_DIR}/nova_main.png")
            
            # Try to interact with chat if there's an input
            try:
                # Look for chat input
                chat_input = await page.query_selector('input[type="text"], textarea')
                if chat_input:
                    await chat_input.click()
                    await chat_input.fill("Tell me about One Development properties")
                    await page.screenshot(path=f"{SCREENSHOT_DIR}/nova_chat_typing.png")
                    print(f"📸 Captured: {SCREENSHOT_DIR}/nova_chat_typing.png")
                    
                    # Try to send message
                    send_btn = await page.query_selector('button[type="submit"], button:has-text("Send")')
                    if send_btn:
                        await send_btn.click()
                        await asyncio.sleep(3)  # Wait for response
                        await page.screenshot(path=f"{SCREENSHOT_DIR}/nova_chat_response.png")
                        print(f"📸 Captured: {SCREENSHOT_DIR}/nova_chat_response.png")
            except Exception as e:
                print(f"⚠️ Could not interact with chat: {e}")
            
            # Screenshot 3: Mobile view
            await page.set_viewport_size({'width': 390, 'height': 844})
            await asyncio.sleep(1)
            await page.screenshot(path=f"{SCREENSHOT_DIR}/nova_mobile.png")
            print(f"📸 Captured: {SCREENSHOT_DIR}/nova_mobile.png")
            
        except Exception as e:
            print(f"❌ Error capturing screenshots: {e}")
        
        await browser.close()
    
    print(f"\n✅ Screenshots saved to: {SCREENSHOT_DIR}")
    return SCREENSHOT_DIR

if __name__ == "__main__":
    asyncio.run(capture_screenshots())

