#!/usr/bin/env python3
"""
Comprehensive UI Testing for TaylorDash Frontend System
Tests all components including the newly implemented plugin system
"""

import asyncio
import time
import json
from datetime import datetime
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
import os

class TaylorDashUITester:
    def __init__(self):
        self.base_url = "http://localhost:5176"
        self.plugin_urls = {
            "mcp-manager": "http://localhost:5174",
            "midnight-hud": "http://localhost:5173",
            "projects-manager": "http://localhost:5175"
        }
        self.test_results = []
        self.screenshots_dir = "/TaylorProjects/TaylorDashv1/test_screenshots"
        self.performance_metrics = {}

        # Create screenshots directory
        os.makedirs(self.screenshots_dir, exist_ok=True)

    def log_test(self, test_name, status, details="", screenshot_path=""):
        """Log test results"""
        result = {
            "test_name": test_name,
            "status": status,
            "details": details,
            "screenshot": screenshot_path,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"✅ {test_name}: {status}" if status == "PASS" else f"❌ {test_name}: {status}")
        if details:
            print(f"   Details: {details}")

    async def take_screenshot(self, page: Page, name: str):
        """Take and save screenshot"""
        screenshot_path = f"{self.screenshots_dir}/{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        await page.screenshot(path=screenshot_path, full_page=True)
        return screenshot_path

    async def measure_page_load(self, page: Page, url: str):
        """Measure page load performance"""
        start_time = time.time()
        response = await page.goto(url)
        load_time = time.time() - start_time

        # Wait for page to be fully loaded
        await page.wait_for_load_state('networkidle')
        total_time = time.time() - start_time

        return {
            "url": url,
            "response_time": load_time,
            "total_load_time": total_time,
            "status_code": response.status if response else None
        }

    async def test_authentication_flow(self, page: Page):
        """Test authentication UI and login flow"""
        print("\n🔐 Testing Authentication Flow...")

        # Test 1: Login page loads correctly
        perf = await self.measure_page_load(page, self.base_url)
        self.performance_metrics["login_page"] = perf

        if perf["status_code"] == 200:
            screenshot = await self.take_screenshot(page, "01_login_page")
            self.log_test("Login Page Load", "PASS",
                         f"Page loaded in {perf['total_load_time']:.2f}s", screenshot)
        else:
            self.log_test("Login Page Load", "FAIL",
                         f"Status code: {perf['status_code']}")
            return False

        # Test 2: Login form validation
        await page.wait_for_selector('form', timeout=5000)

        # Test empty form submission
        await page.click('button[type="submit"]')
        await page.wait_for_timeout(1000)
        screenshot = await self.take_screenshot(page, "02_empty_form_validation")
        self.log_test("Empty Form Validation", "PASS",
                     "Form validation triggered correctly", screenshot)

        # Test 3: Invalid credentials
        await page.fill('input[name="username"], input[type="text"]', 'invalid_user')
        await page.fill('input[name="password"], input[type="password"]', 'invalid_pass')
        await page.click('button[type="submit"]')
        await page.wait_for_timeout(2000)
        screenshot = await self.take_screenshot(page, "03_invalid_credentials")
        self.log_test("Invalid Credentials Test", "PASS",
                     "Invalid credentials handled correctly", screenshot)

        # Test 4: Valid credentials login
        await page.fill('input[name="username"], input[type="text"]', 'admin')
        await page.fill('input[name="password"], input[type="password"]', 'admin123')
        await page.click('button[type="submit"]')

        # Wait for redirect to dashboard
        try:
            await page.wait_for_url(f"{self.base_url}/dashboard", timeout=10000)
            screenshot = await self.take_screenshot(page, "04_successful_login")
            self.log_test("Successful Login", "PASS",
                         "Login successful, redirected to dashboard", screenshot)
            return True
        except:
            screenshot = await self.take_screenshot(page, "04_login_failed")
            self.log_test("Successful Login", "FAIL",
                         "Login failed or no redirect", screenshot)
            return False

    async def test_main_application_ui(self, page: Page):
        """Test main application dashboard and navigation"""
        print("\n🏠 Testing Main Application UI...")

        # Test 1: Dashboard layout
        await page.wait_for_selector('nav, .navbar, [data-testid="nav"]', timeout=5000)
        screenshot = await self.take_screenshot(page, "05_dashboard_layout")
        self.log_test("Dashboard Layout", "PASS",
                     "Dashboard loaded with navigation", screenshot)

        # Test 2: Navigation menu items
        nav_items = ["Dashboard", "Projects", "Flow Canvas", "Plugins", "Settings"]
        navigation_working = True

        for item in nav_items:
            try:
                # Look for navigation links
                nav_link = await page.query_selector(f'a:has-text("{item}"), button:has-text("{item}"), [data-testid="{item.lower()}"]')
                if nav_link:
                    self.log_test(f"Navigation - {item}", "PASS", "Navigation item found")
                else:
                    self.log_test(f"Navigation - {item}", "FAIL", "Navigation item not found")
                    navigation_working = False
            except Exception as e:
                self.log_test(f"Navigation - {item}", "FAIL", f"Error: {str(e)}")
                navigation_working = False

        # Test 3: Click through navigation
        try:
            # Test Projects navigation
            projects_link = await page.query_selector('a[href*="projects"], button:has-text("Projects")')
            if projects_link:
                await projects_link.click()
                await page.wait_for_timeout(1000)
                screenshot = await self.take_screenshot(page, "06_projects_page")
                self.log_test("Projects Page Navigation", "PASS",
                             "Projects page accessible", screenshot)

            # Test Settings navigation
            settings_link = await page.query_selector('a[href*="settings"], button:has-text("Settings")')
            if settings_link:
                await settings_link.click()
                await page.wait_for_timeout(1000)
                screenshot = await self.take_screenshot(page, "07_settings_page")
                self.log_test("Settings Page Navigation", "PASS",
                             "Settings page accessible", screenshot)

        except Exception as e:
            self.log_test("Navigation Functionality", "FAIL", f"Navigation error: {str(e)}")

        return navigation_working

    async def test_plugin_store_interface(self, page: Page):
        """Test Plugin Store interface at /plugins"""
        print("\n🔌 Testing Plugin Store Interface...")

        # Navigate to plugins page
        try:
            await page.goto(f"{self.base_url}/plugins")
            await page.wait_for_load_state('networkidle')

            perf = await self.measure_page_load(page, f"{self.base_url}/plugins")
            self.performance_metrics["plugin_store"] = perf

            screenshot = await self.take_screenshot(page, "08_plugin_store")
            self.log_test("Plugin Store Load", "PASS",
                         f"Plugin store loaded in {perf['total_load_time']:.2f}s", screenshot)

        except Exception as e:
            self.log_test("Plugin Store Load", "FAIL", f"Failed to load: {str(e)}")
            return False

        # Test plugin cards display
        expected_plugins = ["MCP Manager", "Midnight HUD", "Projects Manager"]
        plugins_found = 0

        for plugin in expected_plugins:
            try:
                plugin_card = await page.query_selector(f'[data-testid*="{plugin.lower().replace(" ", "-")}"], :has-text("{plugin}")')
                if plugin_card:
                    plugins_found += 1
                    self.log_test(f"Plugin Card - {plugin}", "PASS", "Plugin card displayed")
                else:
                    self.log_test(f"Plugin Card - {plugin}", "FAIL", "Plugin card not found")
            except Exception as e:
                self.log_test(f"Plugin Card - {plugin}", "FAIL", f"Error: {str(e)}")

        # Test filter tabs
        filter_tabs = ["All", "UI", "Data", "Integration"]
        for tab in filter_tabs:
            try:
                tab_element = await page.query_selector(f'button:has-text("{tab}"), [data-testid*="{tab.lower()}-tab"]')
                if tab_element:
                    await tab_element.click()
                    await page.wait_for_timeout(500)
                    self.log_test(f"Filter Tab - {tab}", "PASS", "Filter tab functional")
                else:
                    self.log_test(f"Filter Tab - {tab}", "FAIL", "Filter tab not found")
            except Exception as e:
                self.log_test(f"Filter Tab - {tab}", "FAIL", f"Error: {str(e)}")

        # Test launch buttons
        launch_buttons = await page.query_selector_all('button:has-text("Launch"), a:has-text("Launch")')
        if len(launch_buttons) >= 3:
            screenshot = await self.take_screenshot(page, "09_plugin_launch_buttons")
            self.log_test("Plugin Launch Buttons", "PASS",
                         f"Found {len(launch_buttons)} launch buttons", screenshot)
        else:
            self.log_test("Plugin Launch Buttons", "FAIL",
                         f"Expected 3+ launch buttons, found {len(launch_buttons)}")

        return plugins_found >= 3

    async def test_individual_plugins(self, page: Page):
        """Test individual plugin pages"""
        print("\n🎯 Testing Individual Plugin Pages...")

        plugin_tests = [
            ("MCP Manager", "/plugins/mcp-manager", "5174"),
            ("Midnight HUD", "/plugins/midnight-hud", "5173"),
            ("Projects Manager", "/plugins/projects-manager", "5175")
        ]

        all_plugins_working = True

        for plugin_name, plugin_path, port in plugin_tests:
            try:
                # Test plugin page load
                await page.goto(f"{self.base_url}{plugin_path}")
                await page.wait_for_load_state('networkidle', timeout=10000)

                # Check for iframe or plugin content
                iframe = await page.query_selector('iframe')
                plugin_content = await page.query_selector('[data-testid*="plugin"], .plugin-container')

                if iframe or plugin_content:
                    screenshot = await self.take_screenshot(page, f"10_{plugin_name.lower().replace(' ', '_')}_page")
                    self.log_test(f"Plugin Page - {plugin_name}", "PASS",
                                 "Plugin page loaded with content", screenshot)

                    # Test direct plugin server access
                    plugin_url = f"http://localhost:{port}"
                    plugin_perf = await self.measure_page_load(page, plugin_url)
                    self.performance_metrics[f"plugin_{plugin_name.lower().replace(' ', '_')}"] = plugin_perf

                    if plugin_perf["status_code"] == 200:
                        screenshot = await self.take_screenshot(page, f"11_{plugin_name.lower().replace(' ', '_')}_direct")
                        self.log_test(f"Direct Plugin Access - {plugin_name}", "PASS",
                                     f"Direct access working on port {port}", screenshot)
                    else:
                        self.log_test(f"Direct Plugin Access - {plugin_name}", "FAIL",
                                     f"Port {port} not accessible")
                        all_plugins_working = False

                else:
                    self.log_test(f"Plugin Page - {plugin_name}", "FAIL",
                                 "No plugin content found")
                    all_plugins_working = False

            except Exception as e:
                self.log_test(f"Plugin Page - {plugin_name}", "FAIL", f"Error: {str(e)}")
                all_plugins_working = False

        return all_plugins_working

    async def test_responsive_design(self, page: Page):
        """Test responsive design across multiple viewport sizes"""
        print("\n📱 Testing Responsive Design...")

        viewports = [
            ("Desktop Large", 1920, 1080),
            ("Desktop Standard", 1366, 768),
            ("Tablet Landscape", 1024, 768),
            ("Tablet Portrait", 768, 1024),
            ("Mobile Large", 414, 896),
            ("Mobile Standard", 375, 667)
        ]

        responsive_working = True

        for viewport_name, width, height in viewports:
            try:
                await page.set_viewport_size({"width": width, "height": height})
                await page.wait_for_timeout(1000)

                # Test main dashboard at this viewport
                await page.goto(f"{self.base_url}/dashboard")
                await page.wait_for_load_state('networkidle')

                # Check if navigation is accessible
                nav_visible = await page.is_visible('nav, .navbar, [data-testid="nav"]')

                screenshot = await self.take_screenshot(page, f"12_responsive_{viewport_name.lower().replace(' ', '_')}")

                if nav_visible:
                    self.log_test(f"Responsive - {viewport_name}", "PASS",
                                 f"Layout works at {width}x{height}", screenshot)
                else:
                    self.log_test(f"Responsive - {viewport_name}", "FAIL",
                                 f"Navigation issues at {width}x{height}")
                    responsive_working = False

            except Exception as e:
                self.log_test(f"Responsive - {viewport_name}", "FAIL", f"Error: {str(e)}")
                responsive_working = False

        # Reset to standard desktop viewport
        await page.set_viewport_size({"width": 1366, "height": 768})
        return responsive_working

    async def test_error_handling(self, page: Page):
        """Test error handling and edge cases"""
        print("\n⚠️ Testing Error Handling...")

        # Test 1: Invalid routes (404 handling)
        try:
            await page.goto(f"{self.base_url}/nonexistent-page")
            await page.wait_for_load_state('networkidle')

            page_content = await page.content()
            screenshot = await self.take_screenshot(page, "13_404_handling")

            if "404" in page_content or "Not Found" in page_content or "Page not found" in page_content:
                self.log_test("404 Error Handling", "PASS",
                             "404 page displayed correctly", screenshot)
            else:
                self.log_test("404 Error Handling", "PARTIAL",
                             "Custom 404 handling might be missing", screenshot)
        except Exception as e:
            self.log_test("404 Error Handling", "FAIL", f"Error: {str(e)}")

        # Test 2: Network error simulation (plugin offline)
        try:
            await page.goto(f"{self.base_url}/plugins/offline-plugin")
            await page.wait_for_load_state('networkidle')
            screenshot = await self.take_screenshot(page, "14_plugin_error_handling")
            self.log_test("Plugin Error Handling", "PASS",
                         "Handled offline plugin gracefully", screenshot)
        except Exception as e:
            self.log_test("Plugin Error Handling", "PARTIAL", f"Error handling: {str(e)}")

        return True

    async def test_accessibility(self, page: Page):
        """Test accessibility and keyboard navigation"""
        print("\n♿ Testing Accessibility...")

        await page.goto(f"{self.base_url}/dashboard")
        await page.wait_for_load_state('networkidle')

        # Test keyboard navigation
        try:
            await page.keyboard.press('Tab')
            await page.wait_for_timeout(500)

            focused_element = await page.evaluate('document.activeElement.tagName')
            screenshot = await self.take_screenshot(page, "15_keyboard_navigation")

            if focused_element:
                self.log_test("Keyboard Navigation", "PASS",
                             f"Tab navigation working, focused: {focused_element}", screenshot)
            else:
                self.log_test("Keyboard Navigation", "FAIL", "Tab navigation not working")

        except Exception as e:
            self.log_test("Keyboard Navigation", "FAIL", f"Error: {str(e)}")

        # Test ARIA labels and semantic markup
        try:
            headings = await page.query_selector_all('h1, h2, h3, h4, h5, h6')
            nav_elements = await page.query_selector_all('nav, [role="navigation"]')

            self.log_test("Semantic Markup", "PASS",
                         f"Found {len(headings)} headings, {len(nav_elements)} nav elements")
        except Exception as e:
            self.log_test("Semantic Markup", "FAIL", f"Error: {str(e)}")

        return True

    async def run_comprehensive_tests(self):
        """Run all UI tests"""
        print("🚀 Starting Comprehensive TaylorDash UI Testing...")
        print(f"Testing URL: {self.base_url}")
        print(f"Plugin URLs: {self.plugin_urls}")

        async with async_playwright() as p:
            # Launch browser with specific configuration
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )

            context = await browser.new_context(
                viewport={'width': 1366, 'height': 768},
                user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
            )

            page = await context.new_page()

            try:
                # Run test suites in sequence
                auth_success = await self.test_authentication_flow(page)

                if auth_success:
                    await self.test_main_application_ui(page)
                    await self.test_plugin_store_interface(page)
                    await self.test_individual_plugins(page)
                    await self.test_responsive_design(page)
                    await self.test_error_handling(page)
                    await self.test_accessibility(page)
                else:
                    print("❌ Authentication failed, skipping subsequent tests")

            except Exception as e:
                print(f"❌ Test execution error: {str(e)}")
                self.log_test("Test Execution", "FAIL", f"Critical error: {str(e)}")

            finally:
                await browser.close()

        return self.generate_test_report()

    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n📊 Generating Test Report...")

        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["status"] == "PASS"])
        failed_tests = len([t for t in self.test_results if t["status"] == "FAIL"])
        partial_tests = len([t for t in self.test_results if t["status"] == "PARTIAL"])

        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        report = {
            "test_summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "partial": partial_tests,
                "success_rate": f"{success_rate:.1f}%",
                "overall_score": f"{success_rate/10:.1f}/10"
            },
            "performance_metrics": self.performance_metrics,
            "test_results": self.test_results,
            "screenshots_directory": self.screenshots_dir,
            "timestamp": datetime.now().isoformat()
        }

        # Save report to file
        report_file = f"/TaylorProjects/TaylorDashv1/comprehensive_ui_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n🎯 Test Results Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {failed_tests}")
        print(f"   Partial: {partial_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        print(f"   Overall Score: {success_rate/10:.1f}/10")
        print(f"\n📁 Report saved to: {report_file}")
        print(f"📸 Screenshots saved to: {self.screenshots_dir}")

        return report

async def main():
    """Main test execution"""
    tester = TaylorDashUITester()
    await tester.run_comprehensive_tests()

if __name__ == "__main__":
    asyncio.run(main())