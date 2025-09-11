#!/usr/bin/env python3
"""
TaylorDash QA Docker Network Testing
Testing within the Docker network environment
"""

import asyncio
import json
import time
import subprocess
import sys
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
import uuid

class QADockerTestSuite:
    def __init__(self):
        self.results: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "overall_status": "unknown",
            "tests_passed": 0,
            "tests_failed": 0,
            "test_results": {},
            "performance_metrics": {},
            "security_validations": {},
            "issues_found": [],
            "recommendations": []
        }
        self.api_key = "taylordash-dev-key"
        self.backend_url = "http://backend:8000"
        
    def log_result(self, test_name: str, status: str, message: str, details: Optional[Dict] = None):
        """Log test result"""
        result = {
            "status": status,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": details or {}
        }
        self.results["test_results"][test_name] = result
        
        if status == "PASS":
            self.results["tests_passed"] += 1
            print(f"✅ {test_name}: {message}")
        else:
            self.results["tests_failed"] += 1
            print(f"❌ {test_name}: {message}")
            if details:
                print(f"   Details: {json.dumps(details, indent=2)}")
    
    def add_issue(self, issue: str):
        """Add issue to findings"""
        self.results["issues_found"].append(issue)
        print(f"⚠️  Issue: {issue}")
    
    def add_recommendation(self, recommendation: str):
        """Add recommendation"""
        self.results["recommendations"].append(recommendation)
        print(f"💡 Recommendation: {recommendation}")

    def run_curl_test(self, test_name: str, url: str, method: str = "GET", headers: Dict[str, str] = None, data: str = None) -> Tuple[int, str, str]:
        """Run curl test and return status code, stdout, stderr"""
        try:
            cmd = ["docker", "exec", "taylordashv1_backend_1", "curl", "-s", "-w", "%{http_code}", "-o", "/tmp/curl_response"]
            
            if method != "GET":
                cmd.extend(["-X", method])
            
            if headers:
                for key, value in headers.items():
                    cmd.extend(["-H", f"{key}: {value}"])
            
            if data:
                cmd.extend(["-d", data, "-H", "Content-Type: application/json"])
            
            cmd.append(url)
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                status_code = int(result.stdout.strip())
                
                # Get response body
                body_result = subprocess.run(
                    ["docker", "exec", "taylordashv1_backend_1", "cat", "/tmp/curl_response"],
                    capture_output=True, text=True, timeout=5
                )
                response_body = body_result.stdout if body_result.returncode == 0 else ""
                
                return status_code, response_body, result.stderr
            else:
                return 0, "", result.stderr
                
        except Exception as e:
            return 0, "", str(e)

    def test_service_health_checks(self):
        """Test all service health endpoints"""
        print("\n🏥 Testing Service Health Checks...")
        
        # Backend liveness
        status_code, response, error = self.run_curl_test("backend_liveness", f"{self.backend_url}/health/live")
        if status_code == 200:
            self.log_result("backend_liveness", "PASS", "Backend liveness check successful")
        else:
            self.log_result("backend_liveness", "FAIL", f"Backend liveness failed: {status_code}, error: {error}")
        
        # Backend readiness
        status_code, response, error = self.run_curl_test("backend_readiness", f"{self.backend_url}/health/ready")
        if status_code == 200:
            self.log_result("backend_readiness", "PASS", "Backend readiness check successful")
        else:
            self.log_result("backend_readiness", "FAIL", f"Backend readiness failed: {status_code}, error: {error}")
        
        # Stack health with authentication
        headers = {"X-API-Key": self.api_key}
        status_code, response, error = self.run_curl_test("stack_health", f"{self.backend_url}/api/v1/health/stack", headers=headers)
        if status_code == 200:
            try:
                data = json.loads(response)
                self.log_result("stack_health", "PASS", "Stack health check successful", data)
                
                # Check individual service health from stack response
                services = data.get("services", {})
                for service_name, service_info in services.items():
                    if service_info.get("status") != "healthy":
                        self.add_issue(f"Service {service_name} is unhealthy: {service_info.get('message')}")
            except json.JSONDecodeError:
                self.log_result("stack_health", "FAIL", f"Invalid JSON response: {response}")
        else:
            self.log_result("stack_health", "FAIL", f"Stack health failed: {status_code}, error: {error}")

    def test_security_authentication(self):
        """Test API security and authentication"""
        print("\n🔐 Testing Security & Authentication...")
        
        # Test unauthenticated access (should fail)
        status_code, response, error = self.run_curl_test("auth_protection", f"{self.backend_url}/api/v1/projects")
        if status_code == 401:
            self.log_result("auth_protection", "PASS", "Unauthenticated access properly blocked")
        else:
            self.log_result("auth_protection", "FAIL", f"Unauthenticated access not blocked: {status_code}")
            self.add_issue("API endpoints not properly protected")
        
        # Test with wrong API key (should fail)
        headers = {"X-API-Key": "wrong-key"}
        status_code, response, error = self.run_curl_test("invalid_key_protection", f"{self.backend_url}/api/v1/projects", headers=headers)
        if status_code == 401:
            self.log_result("invalid_key_protection", "PASS", "Invalid API key properly rejected")
        else:
            self.log_result("invalid_key_protection", "FAIL", f"Invalid API key not rejected: {status_code}")
            self.add_issue("Invalid API keys not properly rejected")
        
        # Test with correct API key (should succeed)
        headers = {"X-API-Key": self.api_key}
        status_code, response, error = self.run_curl_test("valid_key_access", f"{self.backend_url}/api/v1/projects", headers=headers)
        if status_code == 200:
            self.log_result("valid_key_access", "PASS", "Valid API key accepted")
        else:
            self.log_result("valid_key_access", "FAIL", f"Valid API key rejected: {status_code}")
            self.add_issue("Valid API key improperly rejected")

    def test_database_operations(self):
        """Test database connectivity and operations"""
        print("\n💾 Testing Database Operations...")
        
        headers = {"X-API-Key": self.api_key}
        
        # Test database read operations
        status_code, response, error = self.run_curl_test("db_read_projects", f"{self.backend_url}/api/v1/projects", headers=headers)
        if status_code == 200:
            try:
                data = json.loads(response)
                count = data.get('count', 0)
                self.log_result("db_read_projects", "PASS", f"Database read successful, found {count} projects")
            except json.JSONDecodeError:
                self.log_result("db_read_projects", "FAIL", f"Invalid JSON response: {response}")
        else:
            self.log_result("db_read_projects", "FAIL", f"Database read failed: {status_code}")
        
        # Test database write operations (Create project)
        test_project = {
            "name": f"QA Test Project {uuid.uuid4().hex[:8]}",
            "description": "Test project created during QA validation",
            "status": "testing",
            "metadata": {"qa_test": True, "created_at": datetime.now(timezone.utc).isoformat()}
        }
        
        status_code, response, error = self.run_curl_test(
            "db_write_create", 
            f"{self.backend_url}/api/v1/projects", 
            method="POST", 
            headers=headers, 
            data=json.dumps(test_project)
        )
        
        created_project_id = None
        if status_code == 201:
            try:
                data = json.loads(response)
                created_project_id = data.get("id")
                self.log_result("db_write_create", "PASS", f"Database create successful, project ID: {created_project_id}")
            except json.JSONDecodeError:
                self.log_result("db_write_create", "FAIL", f"Invalid JSON response: {response}")
        else:
            self.log_result("db_write_create", "FAIL", f"Database create failed: {status_code}, response: {response}")
        
        # Test database update operations
        if created_project_id:
            update_data = {"description": "Updated during QA validation", "status": "validated"}
            status_code, response, error = self.run_curl_test(
                "db_update", 
                f"{self.backend_url}/api/v1/projects/{created_project_id}", 
                method="PUT", 
                headers=headers, 
                data=json.dumps(update_data)
            )
            
            if status_code == 200:
                self.log_result("db_update", "PASS", "Database update successful")
            else:
                self.log_result("db_update", "FAIL", f"Database update failed: {status_code}")
            
            # Test database delete operations
            status_code, response, error = self.run_curl_test(
                "db_delete", 
                f"{self.backend_url}/api/v1/projects/{created_project_id}", 
                method="DELETE", 
                headers=headers
            )
            
            if status_code == 204:
                self.log_result("db_delete", "PASS", "Database delete successful")
            else:
                self.log_result("db_delete", "FAIL", f"Database delete failed: {status_code}")

    def test_mqtt_integration(self):
        """Test MQTT event publishing and consumption"""
        print("\n📡 Testing MQTT Integration...")
        
        headers = {"X-API-Key": self.api_key}
        
        # Test MQTT event publishing via API
        status_code, response, error = self.run_curl_test(
            "mqtt_publish_api", 
            f"{self.backend_url}/api/v1/events/test", 
            method="POST", 
            headers=headers
        )
        
        if status_code == 200:
            try:
                data = json.loads(response)
                trace_id = data.get("trace_id")
                self.log_result("mqtt_publish_api", "PASS", f"MQTT event published via API, trace: {trace_id}")
                
                # Give some time for event to be processed
                time.sleep(3)
                
                # Check if event was stored in database
                status_code, response, error = self.run_curl_test(
                    "mqtt_event_storage", 
                    f"{self.backend_url}/api/v1/events?kind=test_event&limit=1", 
                    headers=headers
                )
                
                if status_code == 200:
                    try:
                        events_data = json.loads(response)
                        if events_data.get("count", 0) > 0:
                            self.log_result("mqtt_event_storage", "PASS", "MQTT event successfully stored in database")
                        else:
                            self.log_result("mqtt_event_storage", "FAIL", "MQTT event not found in database")
                            self.add_issue("MQTT events not being stored in database")
                    except json.JSONDecodeError:
                        self.log_result("mqtt_event_storage", "FAIL", f"Invalid JSON response: {response}")
                else:
                    self.log_result("mqtt_event_storage", "FAIL", f"Failed to query events: {status_code}")
                    
            except json.JSONDecodeError:
                self.log_result("mqtt_publish_api", "FAIL", f"Invalid JSON response: {response}")
        else:
            self.log_result("mqtt_publish_api", "FAIL", f"MQTT publish failed: {status_code}")
            self.add_issue("MQTT event publishing not working")

    def test_docker_services_status(self):
        """Test Docker services health and status"""
        print("\n🐳 Testing Docker Services Status...")
        
        try:
            result = subprocess.run(
                ["docker-compose", "ps", "--format", "json"],
                capture_output=True,
                text=True,
                cwd="/TaylorProjects/TaylorDashv1"
            )
            
            if result.returncode == 0:
                services_output = result.stdout.strip()
                if services_output:
                    services = []
                    for line in services_output.split('\n'):
                        if line.strip():
                            try:
                                service = json.loads(line)
                                services.append(service)
                            except json.JSONDecodeError:
                                pass
                    
                    healthy_services = []
                    unhealthy_services = []
                    
                    for service in services:
                        name = service.get("Name", "unknown")
                        state = service.get("State", "unknown")
                        
                        if "healthy" in state.lower() or state.lower() == "up":
                            healthy_services.append(name)
                        else:
                            unhealthy_services.append(f"{name}: {state}")
                    
                    self.log_result("docker_services", "PASS", 
                                  f"Docker services check completed. Healthy: {len(healthy_services)}, Issues: {len(unhealthy_services)}",
                                  {"healthy": healthy_services, "unhealthy": unhealthy_services})
                    
                    if unhealthy_services:
                        for service in unhealthy_services:
                            self.add_issue(f"Docker service not healthy: {service}")
                else:
                    self.log_result("docker_services", "FAIL", "No Docker services found")
            else:
                self.log_result("docker_services", "FAIL", f"Docker compose ps failed: {result.stderr}")
                
        except Exception as e:
            self.log_result("docker_services", "FAIL", f"Docker services check error: {e}")

    def test_api_performance(self):
        """Test API performance and response times"""
        print("\n⚡ Testing API Performance...")
        
        headers = {"X-API-Key": self.api_key}
        endpoints_to_test = [
            "/health/ready",
            "/api/v1/projects",
            "/api/v1/events?limit=10",
            "/api/v1/health/stack"
        ]
        
        performance_results = {}
        
        for endpoint in endpoints_to_test:
            # Test single request performance
            start_time = time.time()
            status_code, response, error = self.run_curl_test(f"performance_{endpoint.replace('/', '_').replace('?', '_')}", f"{self.backend_url}{endpoint}", headers=headers if endpoint.startswith('/api') else None)
            duration = time.time() - start_time
            
            performance_results[endpoint] = {
                "single_request_time": duration,
                "status_code": status_code
            }
            
            if duration < 1.0 and status_code == 200:
                self.log_result(f"performance_{endpoint.replace('/', '_').replace('?', '_')}", "PASS", 
                              f"Response time: {duration:.3f}s")
            else:
                self.log_result(f"performance_{endpoint.replace('/', '_').replace('?', '_')}", "FAIL", 
                              f"Slow response: {duration:.3f}s or error: {status_code}")
                if duration > 2.0:
                    self.add_issue(f"Slow API response for {endpoint}: {duration:.3f}s")
        
        self.results["performance_metrics"] = performance_results

    def test_error_handling(self):
        """Test error handling and edge cases"""
        print("\n🛠️ Testing Error Handling...")
        
        headers = {"X-API-Key": self.api_key}
        
        # Test invalid endpoints
        status_code, response, error = self.run_curl_test("error_404", f"{self.backend_url}/api/v1/nonexistent", headers=headers)
        if status_code == 404:
            self.log_result("error_404", "PASS", "404 errors properly handled")
        else:
            self.log_result("error_404", "FAIL", f"Unexpected status for 404: {status_code}")
        
        # Test invalid project ID format
        status_code, response, error = self.run_curl_test("error_invalid_id", f"{self.backend_url}/api/v1/projects/invalid-id", headers=headers)
        if status_code in [400, 404]:
            self.log_result("error_invalid_id", "PASS", "Invalid ID format properly handled")
        else:
            self.log_result("error_invalid_id", "FAIL", f"Invalid ID not handled: {status_code}")
        
        # Test malformed JSON
        status_code, response, error = self.run_curl_test("error_malformed_json", f"{self.backend_url}/api/v1/projects", method="POST", headers=headers, data="invalid json")
        if status_code == 422:
            self.log_result("error_malformed_json", "PASS", "Malformed JSON properly rejected")
        else:
            self.log_result("error_malformed_json", "FAIL", f"Malformed JSON not handled: {status_code}")

    def test_frontend_availability(self):
        """Test frontend service availability"""
        print("\n🌐 Testing Frontend Availability...")
        
        try:
            # Simple check if frontend is responding
            result = subprocess.run(
                ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "http://localhost:5173"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                status_code = result.stdout.strip()
                if status_code == "200":
                    self.log_result("frontend_availability", "PASS", "Frontend service is available")
                else:
                    self.log_result("frontend_availability", "FAIL", f"Frontend returned status: {status_code}")
                    if status_code == "000":
                        self.add_issue("Frontend service not responding - may not be running")
            else:
                self.log_result("frontend_availability", "FAIL", "Frontend check failed")
                self.add_issue("Unable to reach frontend service")
                
        except Exception as e:
            self.log_result("frontend_availability", "FAIL", f"Frontend test error: {e}")

    def generate_report(self):
        """Generate final QA report"""
        print("\n📊 Generating QA Report...")
        
        total_tests = self.results["tests_passed"] + self.results["tests_failed"]
        success_rate = (self.results["tests_passed"] / total_tests * 100) if total_tests > 0 else 0
        
        if success_rate >= 95:
            self.results["overall_status"] = "EXCELLENT"
        elif success_rate >= 85:
            self.results["overall_status"] = "GOOD"
        elif success_rate >= 70:
            self.results["overall_status"] = "ACCEPTABLE"
        else:
            self.results["overall_status"] = "NEEDS_ATTENTION"
        
        # Add final recommendations based on findings
        if not self.results["issues_found"]:
            self.add_recommendation("System appears to be in good health - continue monitoring")
        else:
            self.add_recommendation("Address the issues found before production deployment")
            
        if success_rate < 90:
            self.add_recommendation("Implement automated testing pipeline to catch issues earlier")

    def run_all_tests(self):
        """Run all QA tests"""
        print("🚀 Starting TaylorDash QA Docker Network Validation")
        print(f"Timestamp: {self.results['timestamp']}")
        print("=" * 80)
        
        # Run all test suites
        self.test_service_health_checks()
        self.test_security_authentication()
        self.test_database_operations()
        self.test_mqtt_integration()
        self.test_docker_services_status()
        self.test_api_performance()
        self.test_error_handling()
        self.test_frontend_availability()
        
        # Generate final report
        self.generate_report()
        
        # Print summary
        print("\n" + "=" * 80)
        print("🏁 QA VALIDATION SUMMARY")
        print("=" * 80)
        print(f"Overall Status: {self.results['overall_status']}")
        print(f"Tests Passed: {self.results['tests_passed']}")
        print(f"Tests Failed: {self.results['tests_failed']}")
        print(f"Success Rate: {(self.results['tests_passed'] / (self.results['tests_passed'] + self.results['tests_failed']) * 100):.1f}%")
        
        if self.results["issues_found"]:
            print(f"\n⚠️  Issues Found ({len(self.results['issues_found'])}):")
            for i, issue in enumerate(self.results["issues_found"], 1):
                print(f"   {i}. {issue}")
        
        if self.results["recommendations"]:
            print(f"\n💡 Recommendations ({len(self.results['recommendations'])}):")
            for i, rec in enumerate(self.results["recommendations"], 1):
                print(f"   {i}. {rec}")
        
        print("\n" + "=" * 80)
        
        return self.results

def main():
    """Main execution function"""
    try:
        qa_suite = QADockerTestSuite()
        results = qa_suite.run_all_tests()
        
        # Save detailed results to file
        results_file = "/TaylorProjects/TaylorDashv1/qa_docker_results.json"
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n📋 Detailed results saved to: {results_file}")
        
        # Exit with error code if tests failed
        if results["tests_failed"] > 0:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n⏹️  QA validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 QA validation failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()