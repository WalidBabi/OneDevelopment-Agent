"""
Take screenshots of Luna AI application
"""
import asyncio
from playwright.async_api import async_playwright
import os

SCREENSHOTS_DIR = "/home/ec2-user/OneDevelopment-Agent/screenshots"
URL = "http://13.62.188.127:3000/"

async def take_screenshots():
    # Create screenshots directory
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    
    async with async_playwright() as p:
        # Launch browser with extra args for headless
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
        )
        
        # Desktop viewport
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            device_scale_factor=1.5
        )
        page = await context.new_page()
        
        print(f"📸 Opening {URL}...")
        
        try:
            # Navigate to the page with shorter timeout
            await page.goto(URL, wait_until='domcontentloaded', timeout=15000)
            print("✅ Page loaded!")
            await asyncio.sleep(3)  # Wait for React to render
            
            # Screenshot 1: Welcome screen (full page)
            print("📸 Taking screenshot 1: Welcome screen...")
            await page.screenshot(
                path=f"{SCREENSHOTS_DIR}/01_luna_welcome.png",
                full_page=False
            )
            print("✅ Screenshot 1 saved!")
            
            # Screenshot 2: Full page view
            print("📸 Taking screenshot 2: Full page...")
            await page.screenshot(
                path=f"{SCREENSHOTS_DIR}/02_luna_fullpage.png",
                full_page=True
            )
            print("✅ Screenshot 2 saved!")
            
            # Try to find and click a suggested question
            print("📸 Looking for suggested questions...")
            try:
                # Wait for suggested questions to appear
                await page.wait_for_selector('.suggested-question', timeout=5000)
                suggested = await page.query_selector('.suggested-question')
                if suggested:
                    question_text = await suggested.inner_text()
                    print(f"📸 Found question: {question_text[:50]}...")
                    await suggested.click()
                    print("📸 Clicked! Waiting for response...")
                    
                    # Wait for response (look for assistant message)
                    await asyncio.sleep(8)
                    
                    # Screenshot 3: Chat with response
                    print("📸 Taking screenshot 3: Chat conversation...")
                    await page.screenshot(
                        path=f"{SCREENSHOTS_DIR}/03_luna_conversation.png",
                        full_page=False
                    )
                    print("✅ Screenshot 3 saved!")
            except Exception as e:
                print(f"⚠️ Could not interact with suggestions: {e}")
            
            # Screenshot 4: Mobile view
            print("📸 Taking screenshot 4: Mobile view...")
            await page.set_viewport_size({'width': 390, 'height': 844})
            await asyncio.sleep(1)
            await page.screenshot(
                path=f"{SCREENSHOTS_DIR}/04_luna_mobile.png",
                full_page=False
            )
            print("✅ Screenshot 4 saved!")
            
            # Screenshot 5: Tablet view
            print("📸 Taking screenshot 5: Tablet view...")
            await page.set_viewport_size({'width': 768, 'height': 1024})
            await asyncio.sleep(1)
            await page.screenshot(
                path=f"{SCREENSHOTS_DIR}/05_luna_tablet.png",
                full_page=False
            )
            print("✅ Screenshot 5 saved!")
            
            print(f"\n✅ All screenshots saved to: {SCREENSHOTS_DIR}/")
            
            # List files
            for f in os.listdir(SCREENSHOTS_DIR):
                size = os.path.getsize(f"{SCREENSHOTS_DIR}/{f}") / 1024
                print(f"   📄 {f} ({size:.1f} KB)")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            # Take screenshot anyway to see what loaded
            try:
                await page.screenshot(path=f"{SCREENSHOTS_DIR}/error_state.png")
                print("📸 Saved error state screenshot")
            except:
                pass
        
        finally:
            await browser.close()

# Run
if __name__ == "__main__":
    asyncio.run(take_screenshots())
