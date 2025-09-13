#!/usr/bin/env python3
"""
Manual UI Inspection for TaylorDash Frontend
Captures current state and identifies actual UI elements
"""

import asyncio
from playwright.async_api import async_playwright
import time

async def inspect_ui():
    """Manually inspect the UI to understand structure"""

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            print("🔍 Inspecting TaylorDash UI Structure...")

            # Visit the home page
            response = await page.goto("http://localhost:3000")
            print(f"📄 Response status: {response.status}")

            await page.wait_for_load_state('networkidle')

            # Take initial screenshot
            await page.screenshot(path="/TaylorProjects/TaylorDashv1/inspection_home.png", full_page=True)
            print("📸 Home page screenshot saved")

            # Get page title and content
            title = await page.title()
            print(f"📋 Page title: {title}")

            # Check for various login elements
            login_forms = await page.query_selector_all('form')
            print(f"🔐 Login forms found: {len(login_forms)}")

            input_fields = await page.query_selector_all('input')
            print(f"📝 Input fields found: {len(input_fields)}")

            buttons = await page.query_selector_all('button')
            print(f"🔘 Buttons found: {len(buttons)}")

            # Get all text content to understand what's displayed
            body_text = await page.text_content('body')
            print(f"📄 Body text (first 500 chars): {body_text[:500] if body_text else 'None'}")

            # Check specific authentication elements
            login_selectors = [
                'input[type="text"]',
                'input[type="password"]',
                'input[name="username"]',
                'input[name="password"]',
                '[data-testid="username"]',
                '[data-testid="password"]',
                'button[type="submit"]',
                '.login-form',
                '#login',
                '.auth-form'
            ]

            print("\n🔍 Checking for authentication elements:")
            for selector in login_selectors:
                elements = await page.query_selector_all(selector)
                print(f"   {selector}: {len(elements)} found")

            # Check if we're already logged in or redirected
            current_url = page.url
            print(f"🌐 Current URL: {current_url}")

            # Try common navigation elements
            nav_elements = await page.query_selector_all('nav, .navbar, .navigation')
            print(f"🧭 Navigation elements found: {len(nav_elements)}")

            # Check for any error messages
            error_elements = await page.query_selector_all('.error, .alert, .warning')
            print(f"⚠️ Error/alert elements found: {len(error_elements)}")

            # Get the HTML structure
            html_content = await page.content()
            with open("/TaylorProjects/TaylorDashv1/page_source.html", "w") as f:
                f.write(html_content)
            print("💾 Page source saved to page_source.html")

            # Try different URLs to understand routing
            test_urls = [
                "http://localhost:3000/login",
                "http://localhost:3000/auth",
                "http://localhost:3000/dashboard",
                "http://localhost:3000/plugins"
            ]

            print("\n🌐 Testing different routes:")
            for url in test_urls:
                try:
                    response = await page.goto(url)
                    await page.wait_for_load_state('networkidle', timeout=5000)
                    title = await page.title()
                    print(f"   {url}: {response.status} - '{title}'")

                    # Take screenshot for each route
                    filename = url.split('/')[-1] or 'root'
                    await page.screenshot(path=f"/TaylorProjects/TaylorDashv1/route_{filename}.png", full_page=True)

                except Exception as e:
                    print(f"   {url}: Error - {str(e)}")

        except Exception as e:
            print(f"❌ Inspection error: {str(e)}")

        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect_ui())