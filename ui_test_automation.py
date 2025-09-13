#!/usr/bin/env python3
"""
TaylorDash UI Testing Automation Script
Comprehensive testing of the frontend application using Selenium WebDriver
"""

import time
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

# Try to import selenium with fallback
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("Selenium not available. Using requests-based testing.")
    import requests


class TestSeverity(Enum):
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    COSMETIC = "cosmetic"


@dataclass
class TestResult:
    test_name: str
    status: str  # "pass", "fail", "skip"
    message: str
    severity: TestSeverity = TestSeverity.MINOR
    screenshot_path: Optional[str] = None
    execution_time: float = 0.0
    details: Optional[Dict[str, Any]] = None


class TaylorDashUITester:
    def __init__(self, base_url: str = "http://localhost:5174"):
        self.base_url = base_url
        self.driver = None
        self.results: List[TestResult] = []
        self.start_time = datetime.now()

    def setup_driver(self, browser="chrome", headless=True):
        """Setup WebDriver for browser automation"""
        if not SELENIUM_AVAILABLE:
            print("Selenium not available, using requests for basic connectivity tests")
            return False

        try:
            if browser.lower() == "chrome":
                options = ChromeOptions()
                if headless:
                    options.add_argument("--headless")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-gpu")
                options.add_argument("--window-size=1920,1080")
                self.driver = webdriver.Chrome(options=options)
            elif browser.lower() == "firefox":
                options = FirefoxOptions()
                if headless:
                    options.add_argument("--headless")
                self.driver = webdriver.Firefox(options=options)

            self.driver.implicitly_wait(10)
            return True
        except Exception as e:
            print(f"Failed to setup {browser} driver: {e}")
            return False

    def teardown(self):
        """Clean up WebDriver"""
        if self.driver:
            self.driver.quit()

    def take_screenshot(self, test_name: str) -> Optional[str]:
        """Take screenshot for test documentation"""
        if not self.driver:
            return None

        try:
            screenshot_dir = "/tmp/taylordash_screenshots"
            os.makedirs(screenshot_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{test_name}_{timestamp}.png"
            filepath = os.path.join(screenshot_dir, filename)
            self.driver.save_screenshot(filepath)
            return filepath
        except Exception as e:
            print(f"Failed to take screenshot: {e}")
            return None

    def wait_for_element(self, by: By, value: str, timeout: int = 10):
        """Wait for element to be present and return it"""
        if not self.driver:
            return None
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )

    def wait_for_clickable(self, by: By, value: str, timeout: int = 10):
        """Wait for element to be clickable and return it"""
        if not self.driver:
            return None
        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )

    def test_basic_connectivity(self):
        """Test basic connectivity to the application"""
        start_time = time.time()
        try:
            if SELENIUM_AVAILABLE and self.driver:
                self.driver.get(self.base_url)
                title = self.driver.title
                page_source = self.driver.page_source

                if "TaylorDash" in title or "TaylorDash" in page_source:
                    self.results.append(TestResult(
                        test_name="basic_connectivity",
                        status="pass",
                        message="Successfully connected to TaylorDash application",
                        execution_time=time.time() - start_time,
                        screenshot_path=self.take_screenshot("connectivity")
                    ))
                else:
                    self.results.append(TestResult(
                        test_name="basic_connectivity",
                        status="fail",
                        message=f"TaylorDash not detected in page title: {title}",
                        severity=TestSeverity.CRITICAL,
                        execution_time=time.time() - start_time
                    ))
            else:
                # Fallback to requests
                response = requests.get(self.base_url, timeout=10)
                if response.status_code == 200:
                    self.results.append(TestResult(
                        test_name="basic_connectivity",
                        status="pass",
                        message=f"HTTP connection successful (status: {response.status_code})",
                        execution_time=time.time() - start_time
                    ))
                else:
                    self.results.append(TestResult(
                        test_name="basic_connectivity",
                        status="fail",
                        message=f"HTTP connection failed (status: {response.status_code})",
                        severity=TestSeverity.CRITICAL,
                        execution_time=time.time() - start_time
                    ))
        except Exception as e:
            self.results.append(TestResult(
                test_name="basic_connectivity",
                status="fail",
                message=f"Connection failed: {str(e)}",
                severity=TestSeverity.CRITICAL,
                execution_time=time.time() - start_time
            ))

    def test_login_page_elements(self):
        """Test login page UI elements and functionality"""
        start_time = time.time()
        if not self.driver:
            self.results.append(TestResult(
                test_name="login_page_elements",
                status="skip",
                message="WebDriver not available",
                execution_time=time.time() - start_time
            ))
            return

        try:
            self.driver.get(f"{self.base_url}/login")

            # Check for essential login elements
            username_field = self.wait_for_element(By.CSS_SELECTOR, 'input[type="text"]')
            password_field = self.wait_for_element(By.CSS_SELECTOR, 'input[type="password"]')
            login_button = self.wait_for_element(By.CSS_SELECTOR, 'button[type="submit"]')

            elements_found = []
            if username_field:
                elements_found.append("Username field")
            if password_field:
                elements_found.append("Password field")
            if login_button:
                elements_found.append("Login button")

            # Check for TaylorDash branding
            title_element = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'TaylorDash')]")
            if title_element:
                elements_found.append("TaylorDash branding")

            # Check for tablet/kiosk mode options
            tablet_options = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Tablet') or contains(text(), 'Kiosk')]")
            if tablet_options:
                elements_found.append("Tablet/Kiosk mode options")

            self.results.append(TestResult(
                test_name="login_page_elements",
                status="pass",
                message=f"Login page elements found: {', '.join(elements_found)}",
                execution_time=time.time() - start_time,
                screenshot_path=self.take_screenshot("login_page"),
                details={"elements_found": elements_found}
            ))

        except TimeoutException:
            self.results.append(TestResult(
                test_name="login_page_elements",
                status="fail",
                message="Login page elements not found within timeout",
                severity=TestSeverity.MAJOR,
                execution_time=time.time() - start_time,
                screenshot_path=self.take_screenshot("login_page_timeout")
            ))
        except Exception as e:
            self.results.append(TestResult(
                test_name="login_page_elements",
                status="fail",
                message=f"Login page test failed: {str(e)}",
                severity=TestSeverity.MAJOR,
                execution_time=time.time() - start_time
            ))

    def test_authentication_flow(self):
        """Test the complete authentication flow"""
        start_time = time.time()
        if not self.driver:
            self.results.append(TestResult(
                test_name="authentication_flow",
                status="skip",
                message="WebDriver not available",
                execution_time=time.time() - start_time
            ))
            return

        try:
            self.driver.get(f"{self.base_url}/login")

            # Find and fill credentials
            username_field = self.wait_for_element(By.CSS_SELECTOR, 'input[type="text"]')
            password_field = self.wait_for_element(By.CSS_SELECTOR, 'input[type="password"]')
            login_button = self.wait_for_clickable(By.CSS_SELECTOR, 'button[type="submit"]')

            # Enter demo credentials
            username_field.clear()
            username_field.send_keys("admin")

            password_field.clear()
            password_field.send_keys("admin123")

            # Take screenshot before login
            screenshot_before = self.take_screenshot("login_before_submit")

            # Click login button
            login_button.click()

            # Wait for redirect or dashboard
            time.sleep(3)

            # Check if we're redirected to dashboard
            current_url = self.driver.current_url
            page_source = self.driver.page_source

            if "/login" not in current_url and ("Dashboard" in page_source or "TaylorDash" in page_source):
                self.results.append(TestResult(
                    test_name="authentication_flow",
                    status="pass",
                    message=f"Authentication successful, redirected to: {current_url}",
                    execution_time=time.time() - start_time,
                    screenshot_path=self.take_screenshot("login_success")
                ))
            else:
                self.results.append(TestResult(
                    test_name="authentication_flow",
                    status="fail",
                    message=f"Authentication failed, still at: {current_url}",
                    severity=TestSeverity.CRITICAL,
                    execution_time=time.time() - start_time,
                    screenshot_path=self.take_screenshot("login_failed")
                ))

        except Exception as e:
            self.results.append(TestResult(
                test_name="authentication_flow",
                status="fail",
                message=f"Authentication test failed: {str(e)}",
                severity=TestSeverity.CRITICAL,
                execution_time=time.time() - start_time,
                screenshot_path=self.take_screenshot("auth_error")
            ))

    def test_navigation_menu(self):
        """Test main navigation menu functionality"""
        start_time = time.time()
        if not self.driver:
            self.results.append(TestResult(
                test_name="navigation_menu",
                status="skip",
                message="WebDriver not available",
                execution_time=time.time() - start_time
            ))
            return

        try:
            # First login if not already logged in
            current_url = self.driver.current_url
            if "/login" in current_url:
                self.test_authentication_flow()
                time.sleep(2)

            # Look for navigation items
            nav_items = []

            # Check for main navigation items
            nav_links = self.driver.find_elements(By.CSS_SELECTOR, 'nav a, .nav a, [role="navigation"] a')

            for link in nav_links:
                try:
                    link_text = link.text.strip()
                    link_href = link.get_attribute('href')
                    if link_text and link_href:
                        nav_items.append({"text": link_text, "href": link_href})
                except:
                    continue

            # Test clicking on each navigation item
            successful_navigations = []
            failed_navigations = []

            for item in nav_items[:5]:  # Test first 5 items to avoid infinite loops
                try:
                    # Find the link again (in case page changed)
                    link = self.driver.find_element(By.XPATH, f"//a[contains(text(), '{item['text']}')]")
                    link.click()
                    time.sleep(2)

                    current_url = self.driver.current_url
                    successful_navigations.append({"item": item['text'], "url": current_url})

                except Exception as e:
                    failed_navigations.append({"item": item['text'], "error": str(e)})

            if nav_items:
                self.results.append(TestResult(
                    test_name="navigation_menu",
                    status="pass" if not failed_navigations else "fail",
                    message=f"Found {len(nav_items)} navigation items. Successful: {len(successful_navigations)}, Failed: {len(failed_navigations)}",
                    severity=TestSeverity.MAJOR if failed_navigations else TestSeverity.MINOR,
                    execution_time=time.time() - start_time,
                    screenshot_path=self.take_screenshot("navigation_test"),
                    details={
                        "nav_items": nav_items,
                        "successful_navigations": successful_navigations,
                        "failed_navigations": failed_navigations
                    }
                ))
            else:
                self.results.append(TestResult(
                    test_name="navigation_menu",
                    status="fail",
                    message="No navigation items found",
                    severity=TestSeverity.MAJOR,
                    execution_time=time.time() - start_time,
                    screenshot_path=self.take_screenshot("navigation_missing")
                ))

        except Exception as e:
            self.results.append(TestResult(
                test_name="navigation_menu",
                status="fail",
                message=f"Navigation test failed: {str(e)}",
                severity=TestSeverity.MAJOR,
                execution_time=time.time() - start_time
            ))

    def test_responsive_design(self):
        """Test responsive design across different screen sizes"""
        start_time = time.time()
        if not self.driver:
            self.results.append(TestResult(
                test_name="responsive_design",
                status="skip",
                message="WebDriver not available",
                execution_time=time.time() - start_time
            ))
            return

        try:
            # Test different screen sizes
            screen_sizes = [
                {"name": "Desktop", "width": 1920, "height": 1080},
                {"name": "Laptop", "width": 1366, "height": 768},
                {"name": "Tablet", "width": 768, "height": 1024},
                {"name": "Mobile", "width": 375, "height": 667}
            ]

            responsive_results = []

            for size in screen_sizes:
                try:
                    self.driver.set_window_size(size["width"], size["height"])
                    time.sleep(1)

                    # Check if page elements are still visible
                    body = self.driver.find_element(By.TAG_NAME, "body")
                    viewport_width = self.driver.execute_script("return window.innerWidth")
                    viewport_height = self.driver.execute_script("return window.innerHeight")

                    # Take screenshot for this size
                    screenshot_path = self.take_screenshot(f"responsive_{size['name'].lower()}")

                    responsive_results.append({
                        "size": size,
                        "viewport": {"width": viewport_width, "height": viewport_height},
                        "screenshot": screenshot_path
                    })

                except Exception as e:
                    responsive_results.append({
                        "size": size,
                        "error": str(e)
                    })

            # Reset to default size
            self.driver.set_window_size(1920, 1080)

            self.results.append(TestResult(
                test_name="responsive_design",
                status="pass",
                message=f"Tested responsive design across {len(screen_sizes)} screen sizes",
                execution_time=time.time() - start_time,
                details={"responsive_tests": responsive_results}
            ))

        except Exception as e:
            self.results.append(TestResult(
                test_name="responsive_design",
                status="fail",
                message=f"Responsive design test failed: {str(e)}",
                severity=TestSeverity.MINOR,
                execution_time=time.time() - start_time
            ))

    def test_error_handling(self):
        """Test error handling and validation"""
        start_time = time.time()
        if not self.driver:
            self.results.append(TestResult(
                test_name="error_handling",
                status="skip",
                message="WebDriver not available",
                execution_time=time.time() - start_time
            ))
            return

        try:
            # Test login with invalid credentials
            self.driver.get(f"{self.base_url}/login")

            username_field = self.wait_for_element(By.CSS_SELECTOR, 'input[type="text"]')
            password_field = self.wait_for_element(By.CSS_SELECTOR, 'input[type="password"]')
            login_button = self.wait_for_clickable(By.CSS_SELECTOR, 'button[type="submit"]')

            # Enter invalid credentials
            username_field.clear()
            username_field.send_keys("invalid_user")

            password_field.clear()
            password_field.send_keys("invalid_password")

            login_button.click()

            # Look for error messages
            time.sleep(2)
            error_messages = self.driver.find_elements(By.CSS_SELECTOR, '.error, .alert, .notification, [class*="error"], [class*="alert"]')

            error_handling_results = []

            if error_messages:
                for error in error_messages:
                    error_text = error.text.strip()
                    if error_text:
                        error_handling_results.append(error_text)

            # Test navigation to non-existent page
            self.driver.get(f"{self.base_url}/nonexistent-page")
            time.sleep(2)

            page_source = self.driver.page_source.lower()
            if "404" in page_source or "not found" in page_source or "error" in page_source:
                error_handling_results.append("404 page handling detected")

            self.results.append(TestResult(
                test_name="error_handling",
                status="pass" if error_handling_results else "minor_issue",
                message=f"Error handling test completed. Found: {', '.join(error_handling_results) if error_handling_results else 'No error messages detected'}",
                severity=TestSeverity.MINOR if not error_handling_results else TestSeverity.COSMETIC,
                execution_time=time.time() - start_time,
                screenshot_path=self.take_screenshot("error_handling"),
                details={"error_messages": error_handling_results}
            ))

        except Exception as e:
            self.results.append(TestResult(
                test_name="error_handling",
                status="fail",
                message=f"Error handling test failed: {str(e)}",
                severity=TestSeverity.MINOR,
                execution_time=time.time() - start_time
            ))

    def run_comprehensive_tests(self):
        """Run all UI tests"""
        print(f"Starting TaylorDash UI Testing at {self.start_time}")
        print(f"Testing URL: {self.base_url}")
        print("=" * 60)

        # Setup browser
        if not self.setup_driver("chrome", headless=False):  # Set to False to see browser
            print("Chrome not available, trying Firefox...")
            if not self.setup_driver("firefox", headless=False):
                print("No browser available, running limited tests...")

        # Run test suite
        tests = [
            self.test_basic_connectivity,
            self.test_login_page_elements,
            self.test_authentication_flow,
            self.test_navigation_menu,
            self.test_responsive_design,
            self.test_error_handling
        ]

        for test in tests:
            print(f"Running {test.__name__}...")
            try:
                test()
                print(f"✓ {test.__name__} completed")
            except Exception as e:
                print(f"✗ {test.__name__} failed: {e}")
                self.results.append(TestResult(
                    test_name=test.__name__,
                    status="fail",
                    message=f"Test execution failed: {str(e)}",
                    severity=TestSeverity.CRITICAL
                ))

        # Clean up
        self.teardown()

        # Generate report
        return self.generate_report()

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds()

        # Categorize results
        passed = [r for r in self.results if r.status == "pass"]
        failed = [r for r in self.results if r.status == "fail"]
        skipped = [r for r in self.results if r.status == "skip"]

        # Group by severity
        critical_issues = [r for r in failed if r.severity == TestSeverity.CRITICAL]
        major_issues = [r for r in failed if r.severity == TestSeverity.MAJOR]
        minor_issues = [r for r in failed if r.severity == TestSeverity.MINOR]

        report = {
            "test_summary": {
                "total_tests": len(self.results),
                "passed": len(passed),
                "failed": len(failed),
                "skipped": len(skipped),
                "success_rate": f"{(len(passed) / len(self.results) * 100):.1f}%" if self.results else "0%",
                "total_duration": f"{total_duration:.2f}s",
                "start_time": self.start_time.isoformat(),
                "end_time": end_time.isoformat()
            },
            "issue_severity": {
                "critical": len(critical_issues),
                "major": len(major_issues),
                "minor": len(minor_issues)
            },
            "test_results": []
        }

        # Add detailed results
        for result in self.results:
            report["test_results"].append({
                "test_name": result.test_name,
                "status": result.status,
                "message": result.message,
                "severity": result.severity.value,
                "execution_time": result.execution_time,
                "screenshot_path": result.screenshot_path,
                "details": result.details
            })

        return report


def main():
    """Main function to run UI tests"""
    tester = TaylorDashUITester()
    report = tester.run_comprehensive_tests()

    # Print summary
    print("\n" + "=" * 60)
    print("UI TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {report['test_summary']['total_tests']}")
    print(f"Passed: {report['test_summary']['passed']}")
    print(f"Failed: {report['test_summary']['failed']}")
    print(f"Skipped: {report['test_summary']['skipped']}")
    print(f"Success Rate: {report['test_summary']['success_rate']}")
    print(f"Duration: {report['test_summary']['total_duration']}")

    if report['issue_severity']['critical'] > 0:
        print(f"\n⚠️  CRITICAL ISSUES: {report['issue_severity']['critical']}")
    if report['issue_severity']['major'] > 0:
        print(f"⚠️  MAJOR ISSUES: {report['issue_severity']['major']}")
    if report['issue_severity']['minor'] > 0:
        print(f"ℹ️  MINOR ISSUES: {report['issue_severity']['minor']}")

    # Save detailed report
    report_file = f"/tmp/taylordash_ui_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\nDetailed report saved to: {report_file}")

    return report


if __name__ == "__main__":
    main()