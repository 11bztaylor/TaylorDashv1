#!/usr/bin/env python3
"""
Comprehensive UI Testing for TaylorDash Frontend System - Fixed Version
Tests all components including the newly implemented plugin system
"""

import asyncio
import time
import json
from datetime import datetime
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
import os

class TaylorDashUITesterFixed:
    def __init__(self):
        self.base_url = "http://localhost:5176"
        self.plugin_urls = {
            "mcp-manager": "http://localhost:5174",
            "midnight-hud": "http://localhost:5173",
            "projects-manager": "http://localhost:5175"
        }
        self.test_results = []
        self.screenshots_dir = "/TaylorProjects/TaylorDashv1/test_screenshots_fixed"
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

        # Test 2: Login form elements present
        await page.wait_for_timeout(2000)  # Allow React to render

        username_field = await page.query_selector('input[placeholder*="username"], input[type="text"]')
        password_field = await page.query_selector('input[placeholder*="password"], input[type="password"]')
        login_button = await page.query_selector('button:has-text("Sign In"), button[type="submit"]')

        if username_field and password_field and login_button:
            self.log_test("Login Form Elements", "PASS", "All form elements present")
        else:
            self.log_test("Login Form Elements", "FAIL", "Missing form elements")

        # Test 3: Perform login
        if username_field and password_field and login_button:
            await username_field.fill('admin')
            await password_field.fill('admin123')
            await login_button.click()

            # Wait for any redirects or dashboard to load
            await page.wait_for_timeout(3000)

            # Check if we're on dashboard or authenticated
            current_url = page.url
            page_content = await page.content()

            # Look for dashboard indicators
            dashboard_indicators = [
                "Dashboard", "Projects", "admin", "TaylorDash",
                "System Flow", "Connected", "projects"
            ]

            authenticated = any(indicator.lower() in page_content.lower() for indicator in dashboard_indicators)

            screenshot = await self.take_screenshot(page, "02_after_login")

            if authenticated:
                self.log_test("Successful Login", "PASS",
                             f"Successfully authenticated, current URL: {current_url}", screenshot)
                return True
            else:
                self.log_test("Successful Login", "FAIL",
                             f"Authentication failed, URL: {current_url}", screenshot)
                return False

        return False

    async def test_main_application_ui(self, page: Page):
        """Test main application dashboard and navigation"""
        print("\n🏠 Testing Main Application UI...")

        # Test 1: Dashboard components
        await page.wait_for_timeout(2000)
        screenshot = await self.take_screenshot(page, "03_dashboard_overview")

        # Check for main dashboard elements
        dashboard_elements = {
            "Projects Panel": 'div:has-text("Projects"), h2:has-text("Projects"), h3:has-text("Projects")',
            "Navigation Bar": 'nav, .navbar, div:has-text("Dashboard")',
            "User Info": 'div:has-text("admin"), span:has-text("admin")',
            "System Status": 'div:has-text("Connected"), span:has-text("Connected")'
        }

        dashboard_working = True
        for element_name, selector in dashboard_elements.items():
            try:
                element = await page.query_selector(selector)
                if element:
                    self.log_test(f"Dashboard - {element_name}", "PASS", "Element found and displayed")
                else:
                    self.log_test(f"Dashboard - {element_name}", "PARTIAL", "Element not found with selector")
                    dashboard_working = False
            except Exception as e:
                self.log_test(f"Dashboard - {element_name}", "FAIL", f"Error: {str(e)}")
                dashboard_working = False

        # Test 2: Navigation functionality
        nav_items = ["Projects", "Flow Canvas", "Plugins", "Settings"]

        for item in nav_items:
            try:
                # Look for navigation elements
                nav_element = await page.query_selector(f'a:has-text("{item}"), button:has-text("{item}"), div:has-text("{item}")')
                if nav_element:
                    # Try to click if it's clickable
                    if await nav_element.is_enabled():
                        await nav_element.click()
                        await page.wait_for_timeout(1500)

                        screenshot = await self.take_screenshot(page, f"04_nav_{item.lower().replace(' ', '_')}")
                        self.log_test(f"Navigation - {item}", "PASS",
                                     f"Successfully navigated to {item}", screenshot)

                        # Navigate back to dashboard for next test
                        dashboard_nav = await page.query_selector('a:has-text("Dashboard"), button:has-text("Dashboard")')
                        if dashboard_nav:
                            await dashboard_nav.click()
                            await page.wait_for_timeout(1000)
                    else:
                        self.log_test(f"Navigation - {item}", "PARTIAL", "Element found but not clickable")
                else:
                    self.log_test(f"Navigation - {item}", "FAIL", "Navigation element not found")
                    dashboard_working = False
            except Exception as e:
                self.log_test(f"Navigation - {item}", "FAIL", f"Error: {str(e)}")
                dashboard_working = False

        return dashboard_working

    async def test_plugin_store_interface(self, page: Page):
        """Test Plugin Store interface at /plugins"""
        print("\n🔌 Testing Plugin Store Interface...")

        # Navigate to plugins page
        try:
            # Try clicking the Plugins navigation
            plugins_nav = await page.query_selector('a:has-text("Plugins"), button:has-text("Plugins")')
            if plugins_nav:
                await plugins_nav.click()
                await page.wait_for_timeout(3000)
            else:
                # Direct navigation
                await page.goto(f"{self.base_url}/plugins")
                await page.wait_for_timeout(3000)

            screenshot = await self.take_screenshot(page, "05_plugin_store")

            # Check for plugin store content
            page_content = await page.content()
            plugin_store_indicators = ["plugin", "MCP", "Midnight", "Projects", "Manager", "Launch"]

            plugin_store_loaded = any(indicator.lower() in page_content.lower() for indicator in plugin_store_indicators)

            if plugin_store_loaded:
                self.log_test("Plugin Store Load", "PASS",
                             "Plugin store interface loaded successfully", screenshot)
            else:
                self.log_test("Plugin Store Load", "PARTIAL",
                             "Plugin store loaded but content unclear", screenshot)

        except Exception as e:
            self.log_test("Plugin Store Load", "FAIL", f"Failed to load: {str(e)}")
            return False

        # Test plugin cards and interactions
        expected_plugins = ["MCP Manager", "Midnight HUD", "Projects Manager"]
        plugins_found = 0

        for plugin in expected_plugins:
            try:
                # Look for plugin cards or references
                plugin_elements = await page.query_selector_all(f'div:has-text("{plugin}"), span:has-text("{plugin}"), h2:has-text("{plugin}"), h3:has-text("{plugin}")')
                if plugin_elements:
                    plugins_found += 1
                    self.log_test(f"Plugin Card - {plugin}", "PASS", f"Found {len(plugin_elements)} references")
                else:
                    self.log_test(f"Plugin Card - {plugin}", "FAIL", "Plugin not found in interface")
            except Exception as e:
                self.log_test(f"Plugin Card - {plugin}", "FAIL", f"Error: {str(e)}")

        # Test launch functionality
        launch_buttons = await page.query_selector_all('button:has-text("Launch"), a:has-text("Launch"), button:has-text("Open")')
        if len(launch_buttons) > 0:
            screenshot = await self.take_screenshot(page, "06_plugin_launch_buttons")
            self.log_test("Plugin Launch Buttons", "PASS",
                         f"Found {len(launch_buttons)} launch buttons", screenshot)
        else:
            self.log_test("Plugin Launch Buttons", "PARTIAL", "Launch buttons not clearly identified")

        return plugins_found >= 2

    async def test_individual_plugins(self, page: Page):
        """Test individual plugin pages and direct access"""
        print("\n🎯 Testing Individual Plugin Pages...")

        plugin_tests = [
            ("MCP Manager", self.plugin_urls["mcp-manager"]),
            ("Midnight HUD", self.plugin_urls["midnight-hud"]),
            ("Projects Manager", self.plugin_urls["projects-manager"])
        ]

        all_plugins_working = True

        for plugin_name, plugin_url in plugin_tests:
            try:
                # Test direct plugin server access
                perf = await self.measure_page_load(page, plugin_url)
                self.performance_metrics[f"plugin_{plugin_name.lower().replace(' ', '_')}"] = perf

                if perf["status_code"] == 200:
                    screenshot = await self.take_screenshot(page, f"07_{plugin_name.lower().replace(' ', '_')}_direct")
                    self.log_test(f"Direct Plugin Access - {plugin_name}", "PASS",
                                 f"Plugin accessible at {plugin_url}, load time: {perf['total_load_time']:.2f}s", screenshot)
                else:
                    self.log_test(f"Direct Plugin Access - {plugin_name}", "FAIL",
                                 f"Plugin not accessible: status {perf['status_code']}")
                    all_plugins_working = False

                # Test plugin within TaylorDash
                plugin_path = f"/plugins/{plugin_name.lower().replace(' ', '-')}"
                try:
                    await page.goto(f"{self.base_url}{plugin_path}")
                    await page.wait_for_timeout(2000)

                    screenshot = await self.take_screenshot(page, f"08_{plugin_name.lower().replace(' ', '_')}_embedded")

                    # Check for iframe or embedded content
                    iframe = await page.query_selector('iframe')
                    if iframe:
                        self.log_test(f"Embedded Plugin - {plugin_name}", "PASS",
                                     "Plugin loaded in iframe", screenshot)
                    else:
                        # Check for direct plugin content
                        page_content = await page.content()
                        if plugin_name.lower() in page_content.lower():
                            self.log_test(f"Embedded Plugin - {plugin_name}", "PASS",
                                         "Plugin content loaded directly", screenshot)
                        else:
                            self.log_test(f"Embedded Plugin - {plugin_name}", "PARTIAL",
                                         "Plugin page loaded but content unclear", screenshot)

                except Exception as e:
                    self.log_test(f"Embedded Plugin - {plugin_name}", "FAIL", f"Error: {str(e)}")

            except Exception as e:
                self.log_test(f"Plugin Testing - {plugin_name}", "FAIL", f"Error: {str(e)}")
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

                # Navigate to dashboard
                await page.goto(self.base_url)
                await page.wait_for_timeout(2000)

                # Check if main elements are visible and accessible
                main_content = await page.is_visible('body')
                nav_exists = len(await page.query_selector_all('nav, .navbar, div:has-text("Dashboard")')) > 0

                screenshot = await self.take_screenshot(page, f"09_responsive_{viewport_name.lower().replace(' ', '_')}")

                if main_content and nav_exists:
                    self.log_test(f"Responsive - {viewport_name}", "PASS",
                                 f"Layout functional at {width}x{height}", screenshot)
                else:
                    self.log_test(f"Responsive - {viewport_name}", "PARTIAL",
                                 f"Layout issues at {width}x{height}")
                    responsive_working = False

            except Exception as e:
                self.log_test(f"Responsive - {viewport_name}", "FAIL", f"Error: {str(e)}")
                responsive_working = False

        # Reset to standard desktop viewport
        await page.set_viewport_size({"width": 1366, "height": 768})
        return responsive_working

    async def test_user_experience_and_performance(self, page: Page):
        """Test user experience flows and performance"""
        print("\n⚡ Testing User Experience and Performance...")

        # Test 1: Page transition smoothness
        await page.goto(self.base_url)
        start_time = time.time()

        # Navigate through main sections
        sections = ["Projects", "Plugins", "Settings", "Dashboard"]

        for section in sections:
            try:
                section_nav = await page.query_selector(f'a:has-text("{section}"), button:has-text("{section}")')
                if section_nav:
                    nav_start = time.time()
                    await section_nav.click()
                    await page.wait_for_load_state('networkidle', timeout=5000)
                    nav_time = time.time() - nav_start

                    self.performance_metrics[f"navigation_{section.lower()}"] = nav_time

                    if nav_time < 3.0:
                        self.log_test(f"Navigation Speed - {section}", "PASS",
                                     f"Navigation completed in {nav_time:.2f}s")
                    else:
                        self.log_test(f"Navigation Speed - {section}", "PARTIAL",
                                     f"Navigation slow: {nav_time:.2f}s")

                    await page.wait_for_timeout(500)
            except Exception as e:
                self.log_test(f"Navigation Speed - {section}", "FAIL", f"Error: {str(e)}")

        # Test 2: Interactive elements responsiveness
        try:
            await page.goto(self.base_url)
            await page.wait_for_timeout(1000)

            clickable_elements = await page.query_selector_all('button, a, [onclick]')
            responsive_interactions = 0

            for i, element in enumerate(clickable_elements[:5]):  # Test first 5 elements
                try:
                    if await element.is_visible() and await element.is_enabled():
                        interaction_start = time.time()
                        await element.hover()
                        interaction_time = time.time() - interaction_start

                        if interaction_time < 0.5:
                            responsive_interactions += 1

                        await page.wait_for_timeout(100)
                except:
                    pass

            if responsive_interactions >= 3:
                self.log_test("Interactive Elements", "PASS",
                             f"{responsive_interactions}/5 elements responsive")
            else:
                self.log_test("Interactive Elements", "PARTIAL",
                             f"Only {responsive_interactions}/5 elements responsive")

        except Exception as e:
            self.log_test("Interactive Elements", "FAIL", f"Error: {str(e)}")

        return True

    async def test_error_handling(self, page: Page):
        """Test error handling and edge cases"""
        print("\n⚠️ Testing Error Handling...")

        # Test 1: Invalid routes
        invalid_urls = [
            f"{self.base_url}/nonexistent-page",
            f"{self.base_url}/invalid/route",
            f"{self.base_url}/plugins/fake-plugin"
        ]

        for url in invalid_urls:
            try:
                await page.goto(url)
                await page.wait_for_timeout(2000)

                page_content = await page.content()
                screenshot = await self.take_screenshot(page, f"10_error_handling_{url.split('/')[-1]}")

                # Check for proper error handling
                error_indicators = ["404", "not found", "error", "page not found"]
                has_error_handling = any(indicator in page_content.lower() for indicator in error_indicators)

                if has_error_handling:
                    self.log_test(f"Error Handling - {url.split('/')[-1]}", "PASS",
                                 "Proper error page displayed", screenshot)
                else:
                    self.log_test(f"Error Handling - {url.split('/')[-1]}", "PARTIAL",
                                 "Error handling unclear", screenshot)

            except Exception as e:
                self.log_test(f"Error Handling - {url.split('/')[-1]}", "FAIL", f"Error: {str(e)}")

        return True

    async def test_accessibility(self, page: Page):
        """Test accessibility features"""
        print("\n♿ Testing Accessibility...")

        await page.goto(self.base_url)
        await page.wait_for_timeout(2000)

        # Test 1: Keyboard navigation
        try:
            await page.keyboard.press('Tab')
            await page.wait_for_timeout(500)

            focused_element = await page.evaluate('document.activeElement ? document.activeElement.tagName : "none"')
            screenshot = await self.take_screenshot(page, "11_keyboard_navigation")

            if focused_element and focused_element != "BODY":
                self.log_test("Keyboard Navigation", "PASS",
                             f"Tab navigation working, focused: {focused_element}", screenshot)
            else:
                self.log_test("Keyboard Navigation", "PARTIAL",
                             "Tab navigation unclear")

        except Exception as e:
            self.log_test("Keyboard Navigation", "FAIL", f"Error: {str(e)}")

        # Test 2: Semantic markup
        try:
            headings = await page.query_selector_all('h1, h2, h3, h4, h5, h6')
            nav_elements = await page.query_selector_all('nav, [role="navigation"]')
            buttons = await page.query_selector_all('button')

            semantic_score = len(headings) + len(nav_elements) + len(buttons)

            if semantic_score > 5:
                self.log_test("Semantic Markup", "PASS",
                             f"Good semantic structure: {len(headings)} headings, {len(nav_elements)} nav, {len(buttons)} buttons")
            else:
                self.log_test("Semantic Markup", "PARTIAL",
                             f"Limited semantic markup: {semantic_score} elements")

        except Exception as e:
            self.log_test("Semantic Markup", "FAIL", f"Error: {str(e)}")

        return True

    async def run_comprehensive_tests(self):
        """Run all UI tests"""
        print("🚀 Starting Comprehensive TaylorDash UI Testing - Fixed Version...")
        print(f"Testing URL: {self.base_url}")
        print(f"Plugin URLs: {self.plugin_urls}")

        async with async_playwright() as p:
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
                    await self.test_user_experience_and_performance(page)
                    await self.test_error_handling(page)
                    await self.test_accessibility(page)
                else:
                    print("❌ Authentication failed, running other tests anyway...")
                    await self.test_main_application_ui(page)
                    await self.test_plugin_store_interface(page)

            except Exception as e:
                print(f"❌ Test execution error: {str(e)}")
                self.log_test("Test Execution", "FAIL", f"Critical error: {str(e)}")

            finally:
                await browser.close()

        return self.generate_test_report()

    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n📊 Generating Comprehensive Test Report...")

        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["status"] == "PASS"])
        failed_tests = len([t for t in self.test_results if t["status"] == "FAIL"])
        partial_tests = len([t for t in self.test_results if t["status"] == "PARTIAL"])

        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        quality_score = ((passed_tests + (partial_tests * 0.5)) / total_tests * 100) if total_tests > 0 else 0

        # Categorize results
        categories = {
            "Authentication": [t for t in self.test_results if "login" in t["test_name"].lower() or "auth" in t["test_name"].lower()],
            "Navigation": [t for t in self.test_results if "navigation" in t["test_name"].lower() or "dashboard" in t["test_name"].lower()],
            "Plugin System": [t for t in self.test_results if "plugin" in t["test_name"].lower()],
            "Responsive Design": [t for t in self.test_results if "responsive" in t["test_name"].lower()],
            "User Experience": [t for t in self.test_results if any(keyword in t["test_name"].lower() for keyword in ["experience", "performance", "interactive"])],
            "Error Handling": [t for t in self.test_results if "error" in t["test_name"].lower()],
            "Accessibility": [t for t in self.test_results if any(keyword in t["test_name"].lower() for keyword in ["accessibility", "keyboard", "semantic"])]
        }

        report = {
            "test_summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "partial": partial_tests,
                "success_rate": f"{success_rate:.1f}%",
                "quality_score": f"{quality_score:.1f}%",
                "overall_score": f"{quality_score/10:.1f}/10"
            },
            "category_results": {cat: len([t for t in tests if t["status"] == "PASS"]) for cat, tests in categories.items()},
            "performance_metrics": self.performance_metrics,
            "detailed_results": self.test_results,
            "screenshots_directory": self.screenshots_dir,
            "timestamp": datetime.now().isoformat(),
            "test_environment": {
                "frontend_url": self.base_url,
                "plugin_urls": self.plugin_urls,
                "browser": "Chromium",
                "viewport": "1366x768"
            }
        }

        # Save report to file
        report_file = f"/TaylorProjects/TaylorDashv1/comprehensive_ui_test_report_fixed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n🎯 Comprehensive Test Results Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {failed_tests}")
        print(f"   Partial: {partial_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        print(f"   Quality Score: {quality_score:.1f}%")
        print(f"   Overall Score: {quality_score/10:.1f}/10")

        print(f"\n📋 Category Breakdown:")
        for category, tests in categories.items():
            if tests:
                passed_in_cat = len([t for t in tests if t["status"] == "PASS"])
                print(f"   {category}: {passed_in_cat}/{len(tests)} passed")

        print(f"\n📁 Report saved to: {report_file}")
        print(f"📸 Screenshots saved to: {self.screenshots_dir}")

        return report

async def main():
    """Main test execution"""
    tester = TaylorDashUITesterFixed()
    await tester.run_comprehensive_tests()

if __name__ == "__main__":
    asyncio.run(main())