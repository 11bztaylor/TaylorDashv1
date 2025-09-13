#!/usr/bin/env python3
"""
TaylorDash UI Testing - Manual Testing Guide and Basic Connectivity Tests
Comprehensive testing approach without requiring Selenium
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


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
    execution_time: float = 0.0
    details: Optional[Dict[str, Any]] = None


class TaylorDashBasicTester:
    def __init__(self, frontend_url: str = "http://localhost:5174", backend_url: str = "http://localhost:3000"):
        self.frontend_url = frontend_url
        self.backend_url = backend_url
        self.results: List[TestResult] = []
        self.start_time = datetime.now()

    def test_frontend_connectivity(self):
        """Test frontend server connectivity and basic response"""
        start_time = time.time()
        try:
            response = requests.get(self.frontend_url, timeout=10)

            if response.status_code == 200:
                content = response.text.lower()

                # Check for key indicators
                indicators = {
                    "TaylorDash branding": "taylordash" in content,
                    "React app": "react" in content or "div id=\"root\"" in content,
                    "Vite dev server": "vite" in content,
                    "CSS/styling": "css" in content or "style" in content,
                    "JavaScript modules": "script" in content or "module" in content
                }

                found_indicators = [name for name, found in indicators.items() if found]

                self.results.append(TestResult(
                    test_name="frontend_connectivity",
                    status="pass",
                    message=f"Frontend accessible. Found: {', '.join(found_indicators)}",
                    execution_time=time.time() - start_time,
                    details={
                        "status_code": response.status_code,
                        "content_length": len(response.text),
                        "indicators": indicators,
                        "response_headers": dict(response.headers)
                    }
                ))
            else:
                self.results.append(TestResult(
                    test_name="frontend_connectivity",
                    status="fail",
                    message=f"Frontend returned status code: {response.status_code}",
                    severity=TestSeverity.CRITICAL,
                    execution_time=time.time() - start_time
                ))

        except requests.RequestException as e:
            self.results.append(TestResult(
                test_name="frontend_connectivity",
                status="fail",
                message=f"Frontend connection failed: {str(e)}",
                severity=TestSeverity.CRITICAL,
                execution_time=time.time() - start_time
            ))

    def test_backend_connectivity(self):
        """Test backend API connectivity"""
        start_time = time.time()
        try:
            # Test health endpoint
            health_response = requests.get(f"{self.backend_url}/api/v1/health", timeout=10)

            if health_response.status_code == 200:
                health_data = health_response.json()

                self.results.append(TestResult(
                    test_name="backend_health",
                    status="pass",
                    message="Backend health check successful",
                    execution_time=time.time() - start_time,
                    details={"health_data": health_data}
                ))
            else:
                self.results.append(TestResult(
                    test_name="backend_health",
                    status="fail",
                    message=f"Backend health check failed: {health_response.status_code}",
                    severity=TestSeverity.MAJOR,
                    execution_time=time.time() - start_time
                ))

        except requests.RequestException as e:
            self.results.append(TestResult(
                test_name="backend_connectivity",
                status="fail",
                message=f"Backend connection failed: {str(e)}",
                severity=TestSeverity.CRITICAL,
                execution_time=time.time() - start_time
            ))

    def test_api_endpoints(self):
        """Test key API endpoints"""
        start_time = time.time()

        endpoints_to_test = [
            {"path": "/api/v1/health", "method": "GET", "requires_auth": False},
            {"path": "/api/v1/health/stack", "method": "GET", "requires_auth": True},
            {"path": "/docs", "method": "GET", "requires_auth": False},
            {"path": "/api/v1/auth/login", "method": "POST", "requires_auth": False},
            {"path": "/api/v1/projects", "method": "GET", "requires_auth": True}
        ]

        results = []

        for endpoint in endpoints_to_test:
            try:
                url = f"{self.backend_url}{endpoint['path']}"
                headers = {"X-API-Key": "taylordash-dev-key"}

                if endpoint["method"] == "GET":
                    response = requests.get(url, headers=headers, timeout=5)
                elif endpoint["method"] == "POST":
                    if "login" in endpoint["path"]:
                        response = requests.post(url,
                                               json={"username": "admin", "password": "admin123"},
                                               headers=headers, timeout=5)
                    else:
                        response = requests.post(url, headers=headers, timeout=5)

                results.append({
                    "endpoint": endpoint["path"],
                    "status_code": response.status_code,
                    "accessible": response.status_code < 500,
                    "response_time": response.elapsed.total_seconds()
                })

            except Exception as e:
                results.append({
                    "endpoint": endpoint["path"],
                    "error": str(e),
                    "accessible": False
                })

        accessible_endpoints = [r for r in results if r.get("accessible", False)]

        self.results.append(TestResult(
            test_name="api_endpoints",
            status="pass" if len(accessible_endpoints) > 0 else "fail",
            message=f"API endpoint test: {len(accessible_endpoints)}/{len(endpoints_to_test)} accessible",
            severity=TestSeverity.MAJOR if len(accessible_endpoints) == 0 else TestSeverity.MINOR,
            execution_time=time.time() - start_time,
            details={"endpoint_results": results}
        ))

    def test_authentication_api(self):
        """Test authentication API specifically"""
        start_time = time.time()

        try:
            # Test login with correct credentials
            login_data = {
                "username": "admin",
                "password": "admin123"
            }

            headers = {"X-API-Key": "taylordash-dev-key", "Content-Type": "application/json"}

            response = requests.post(
                f"{self.backend_url}/api/v1/auth/login",
                json=login_data,
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                auth_data = response.json()
                token = auth_data.get("access_token")

                if token:
                    # Test authenticated endpoint
                    auth_headers = {
                        "X-API-Key": "taylordash-dev-key",
                        "Authorization": f"Bearer {token}"
                    }

                    protected_response = requests.get(
                        f"{self.backend_url}/api/v1/auth/me",
                        headers=auth_headers,
                        timeout=5
                    )

                    if protected_response.status_code == 200:
                        user_data = protected_response.json()

                        self.results.append(TestResult(
                            test_name="authentication_api",
                            status="pass",
                            message="Authentication API working correctly",
                            execution_time=time.time() - start_time,
                            details={
                                "login_successful": True,
                                "token_received": True,
                                "protected_endpoint_accessible": True,
                                "user_data": user_data
                            }
                        ))
                    else:
                        self.results.append(TestResult(
                            test_name="authentication_api",
                            status="fail",
                            message=f"Protected endpoint failed: {protected_response.status_code}",
                            severity=TestSeverity.MAJOR,
                            execution_time=time.time() - start_time
                        ))
                else:
                    self.results.append(TestResult(
                        test_name="authentication_api",
                        status="fail",
                        message="Login successful but no token received",
                        severity=TestSeverity.MAJOR,
                        execution_time=time.time() - start_time
                    ))
            else:
                self.results.append(TestResult(
                    test_name="authentication_api",
                    status="fail",
                    message=f"Login failed: {response.status_code}",
                    severity=TestSeverity.CRITICAL,
                    execution_time=time.time() - start_time
                ))

        except Exception as e:
            self.results.append(TestResult(
                test_name="authentication_api",
                status="fail",
                message=f"Authentication test failed: {str(e)}",
                severity=TestSeverity.CRITICAL,
                execution_time=time.time() - start_time
            ))

    def run_basic_tests(self):
        """Run all basic connectivity and API tests"""
        print(f"Starting TaylorDash Basic Testing at {self.start_time}")
        print(f"Frontend URL: {self.frontend_url}")
        print(f"Backend URL: {self.backend_url}")
        print("=" * 60)

        tests = [
            self.test_frontend_connectivity,
            self.test_backend_connectivity,
            self.test_api_endpoints,
            self.test_authentication_api
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

        return self.generate_report()

    def generate_report(self) -> Dict[str, Any]:
        """Generate test report"""
        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds()

        passed = [r for r in self.results if r.status == "pass"]
        failed = [r for r in self.results if r.status == "fail"]

        critical_issues = [r for r in failed if r.severity == TestSeverity.CRITICAL]
        major_issues = [r for r in failed if r.severity == TestSeverity.MAJOR]
        minor_issues = [r for r in failed if r.severity == TestSeverity.MINOR]

        report = {
            "test_summary": {
                "total_tests": len(self.results),
                "passed": len(passed),
                "failed": len(failed),
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

        for result in self.results:
            report["test_results"].append({
                "test_name": result.test_name,
                "status": result.status,
                "message": result.message,
                "severity": result.severity.value,
                "execution_time": result.execution_time,
                "details": result.details
            })

        return report

    def generate_manual_test_guide(self):
        """Generate comprehensive manual testing guide"""
        guide = """
# TaylorDash UI Manual Testing Guide

## Authentication Testing
### Login Page Testing (http://localhost:5174/login)

1. **Visual Elements Check:**
   - [ ] TaylorDash logo and branding visible
   - [ ] Username field with user icon
   - [ ] Password field with lock icon and toggle visibility
   - [ ] "Remember me" checkbox
   - [ ] "Tablet/Kiosk Mode Options" collapsible section
   - [ ] Sign In button
   - [ ] Demo credentials displayed: admin / admin123

2. **Login Functionality:**
   - [ ] Test with correct credentials (admin/admin123)
   - [ ] Test with incorrect credentials
   - [ ] Test password visibility toggle
   - [ ] Test remember me functionality
   - [ ] Test tablet/kiosk mode options
   - [ ] Verify redirect to dashboard after successful login

3. **Responsive Design:**
   - [ ] Test on desktop (1920x1080)
   - [ ] Test on laptop (1366x768)
   - [ ] Test on tablet (768x1024)
   - [ ] Test on mobile (375x667)

## Main Application Testing
### Navigation Testing

1. **Header Navigation:**
   - [ ] TaylorDash title visible
   - [ ] Current time display working
   - [ ] Connection status indicator
   - [ ] User dropdown menu with logout

2. **Main Navigation Menu:**
   - [ ] Dashboard link
   - [ ] Projects link
   - [ ] Flow Canvas link
   - [ ] MCP Manager link
   - [ ] Settings link

3. **Page Navigation:**
   - [ ] Dashboard loads correctly
   - [ ] Projects page accessible
   - [ ] Flow Canvas page accessible
   - [ ] Settings page accessible
   - [ ] Plugin pages accessible

### Dashboard Testing

1. **Layout and Components:**
   - [ ] Projects section displays
   - [ ] Flow Canvas section visible
   - [ ] Status bar at bottom shows connection info

2. **Projects Section:**
   - [ ] Project list loads
   - [ ] "No projects" message if empty
   - [ ] Project cards display correctly
   - [ ] Project status badges work

3. **Flow Canvas Section:**
   - [ ] "Visual flow canvas coming soon..." placeholder visible

### Projects Page Testing

1. **Project Management:**
   - [ ] "New Project" button visible and clickable
   - [ ] Project creation modal opens
   - [ ] Form validation works
   - [ ] Projects list refreshes after creation

2. **Project Creation Modal:**
   - [ ] Project name field (required)
   - [ ] Description field
   - [ ] Status dropdown
   - [ ] Cancel and Create buttons
   - [ ] Error handling for validation

### Settings Page Testing

1. **Tab Navigation:**
   - [ ] System Settings tab
   - [ ] User Management tab (admin only)
   - [ ] System Logs tab

2. **System Settings:**
   - [ ] API Endpoint field (read-only)
   - [ ] Theme selection
   - [ ] Auto-refresh interval

3. **User Management (Admin Only):**
   - [ ] User list displays
   - [ ] User creation form
   - [ ] User editing functionality
   - [ ] Role management

4. **System Logs:**
   - [ ] Log entries display
   - [ ] Filter controls work
   - [ ] Auto-refresh toggle
   - [ ] Log detail modal

### Plugin Testing

1. **MCP Manager Plugin:**
   - [ ] Plugin page loads in iframe
   - [ ] Plugin functionality accessible
   - [ ] No security errors in console

2. **Midnight HUD Plugin:**
   - [ ] Plugin accessible
   - [ ] Interface loads correctly

3. **Projects Manager Plugin:**
   - [ ] Plugin loads
   - [ ] Integration with main projects

### Error Handling Testing

1. **Authentication Errors:**
   - [ ] Invalid login shows error message
   - [ ] Session expiry handling
   - [ ] Unauthorized access redirects

2. **Network Errors:**
   - [ ] Backend connection loss handling
   - [ ] API error responses
   - [ ] Timeout handling

3. **Validation Errors:**
   - [ ] Form validation messages
   - [ ] Required field indicators
   - [ ] Input format validation

### Accessibility Testing

1. **Keyboard Navigation:**
   - [ ] Tab order logical
   - [ ] All interactive elements accessible
   - [ ] Enter key submits forms

2. **Screen Reader Support:**
   - [ ] Form labels associated
   - [ ] ARIA attributes present
   - [ ] Semantic HTML structure

3. **Visual Accessibility:**
   - [ ] Color contrast adequate
   - [ ] Text readable at different sizes
   - [ ] Focus indicators visible

### Performance Testing

1. **Loading Times:**
   - [ ] Initial page load < 3 seconds
   - [ ] Navigation between pages smooth
   - [ ] API responses quick

2. **Resource Usage:**
   - [ ] No console errors
   - [ ] Memory usage reasonable
   - [ ] Network requests optimized

### Cross-Browser Testing

1. **Chrome:**
   - [ ] All features work
   - [ ] No console errors
   - [ ] Responsive design correct

2. **Firefox:**
   - [ ] Feature parity with Chrome
   - [ ] CSS rendering correct

3. **Safari (if available):**
   - [ ] Basic functionality works

### User Flow Testing

1. **Complete User Journey:**
   - [ ] Login → Dashboard → Projects → Create Project → Logout
   - [ ] Login → Settings → User Management → Create User
   - [ ] Login → Plugin Usage → Return to Dashboard

2. **Tablet/Kiosk Mode:**
   - [ ] Single view mode login
   - [ ] Navigation hidden in single view
   - [ ] Plugin-focused interface

## Issue Reporting Template

**Issue Title:** [Brief description]
**Severity:** Critical/Major/Minor/Cosmetic
**Browser:** Chrome/Firefox/Safari/Other
**Screen Size:** Desktop/Tablet/Mobile
**Steps to Reproduce:**
1. Step one
2. Step two
3. Step three

**Expected Result:** What should happen
**Actual Result:** What actually happens
**Screenshot:** [If applicable]
**Additional Notes:** Any other relevant information

## Testing Checklist Summary

- [ ] Authentication system fully functional
- [ ] All navigation links work
- [ ] Responsive design across screen sizes
- [ ] User management (admin features)
- [ ] Project management functionality
- [ ] Plugin system operational
- [ ] Error handling appropriate
- [ ] Performance acceptable
- [ ] Accessibility standards met
- [ ] Cross-browser compatibility
- [ ] User flows complete successfully

"""
        return guide


def main():
    """Main function to run basic tests and generate manual testing guide"""
    # Run basic connectivity tests
    tester = TaylorDashBasicTester()
    report = tester.run_basic_tests()

    # Print summary
    print("\n" + "=" * 60)
    print("BASIC CONNECTIVITY TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {report['test_summary']['total_tests']}")
    print(f"Passed: {report['test_summary']['passed']}")
    print(f"Failed: {report['test_summary']['failed']}")
    print(f"Success Rate: {report['test_summary']['success_rate']}")

    if report['issue_severity']['critical'] > 0:
        print(f"\n⚠️  CRITICAL ISSUES: {report['issue_severity']['critical']}")
    if report['issue_severity']['major'] > 0:
        print(f"⚠️  MAJOR ISSUES: {report['issue_severity']['major']}")

    # Save reports
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Save basic test report
    report_file = f"/tmp/taylordash_basic_test_report_{timestamp}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)

    # Save manual testing guide
    guide = tester.generate_manual_test_guide()
    guide_file = f"/tmp/taylordash_manual_test_guide_{timestamp}.md"
    with open(guide_file, 'w') as f:
        f.write(guide)

    print(f"\nBasic test report saved to: {report_file}")
    print(f"Manual testing guide saved to: {guide_file}")

    return report, guide


if __name__ == "__main__":
    main()