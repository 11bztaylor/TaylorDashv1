#!/usr/bin/env python3
"""
TaylorDash QA System Validation Suite
Comprehensive testing of all system components after security implementation
"""

import asyncio
import json
import time
import subprocess
import sys
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
import httpx
import uuid
import os

# Test configuration
API_KEY = "taylordash-dev-key"
BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:5173"
MQTT_HOST = "localhost"
MQTT_PORT = 1883
TIMEOUT = 30

class QATestSuite:
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
        self.client = httpx.AsyncClient(timeout=TIMEOUT)
        
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
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

    async def test_service_health_checks(self):
        """Test all service health endpoints"""
        print("\n🏥 Testing Service Health Checks...")
        
        # Backend health checks
        try:
            response = await self.client.get(f"{BASE_URL}/health/live")
            if response.status_code == 200:
                self.log_result("backend_liveness", "PASS", "Backend liveness check successful")
            else:
                self.log_result("backend_liveness", "FAIL", f"Backend liveness failed: {response.status_code}")
        except Exception as e:
            self.log_result("backend_liveness", "FAIL", f"Backend liveness error: {e}")
        
        try:
            response = await self.client.get(f"{BASE_URL}/health/ready")
            if response.status_code == 200:
                self.log_result("backend_readiness", "PASS", "Backend readiness check successful")
            else:
                self.log_result("backend_readiness", "FAIL", f"Backend readiness failed: {response.status_code}")
        except Exception as e:
            self.log_result("backend_readiness", "FAIL", f"Backend readiness error: {e}")
        
        # Stack health with authentication
        try:
            response = await self.client.get(
                f"{BASE_URL}/api/v1/health/stack",
                headers={"X-API-Key": API_KEY}
            )
            if response.status_code == 200:
                data = response.json()
                self.log_result("stack_health", "PASS", "Stack health check successful", data)
                
                # Check individual service health from stack response
                services = data.get("services", {})
                for service_name, service_info in services.items():
                    if service_info.get("status") != "healthy":
                        self.add_issue(f"Service {service_name} is unhealthy: {service_info.get('message')}")
            else:
                self.log_result("stack_health", "FAIL", f"Stack health failed: {response.status_code}")
        except Exception as e:
            self.log_result("stack_health", "FAIL", f"Stack health error: {e}")

    async def test_security_authentication(self):
        """Test API security and authentication"""
        print("\n🔐 Testing Security & Authentication...")
        
        # Test unauthenticated access (should fail)
        try:
            response = await self.client.get(f"{BASE_URL}/api/v1/projects")
            if response.status_code == 401:
                self.log_result("auth_protection", "PASS", "Unauthenticated access properly blocked")
            else:
                self.log_result("auth_protection", "FAIL", f"Unauthenticated access not blocked: {response.status_code}")
                self.add_issue("API endpoints not properly protected")
        except Exception as e:
            self.log_result("auth_protection", "FAIL", f"Auth protection test error: {e}")
        
        # Test with wrong API key (should fail)
        try:
            response = await self.client.get(
                f"{BASE_URL}/api/v1/projects",
                headers={"X-API-Key": "wrong-key"}
            )
            if response.status_code == 401:
                self.log_result("invalid_key_protection", "PASS", "Invalid API key properly rejected")
            else:
                self.log_result("invalid_key_protection", "FAIL", f"Invalid API key not rejected: {response.status_code}")
                self.add_issue("Invalid API keys not properly rejected")
        except Exception as e:
            self.log_result("invalid_key_protection", "FAIL", f"Invalid key test error: {e}")
        
        # Test with correct API key (should succeed)
        try:
            response = await self.client.get(
                f"{BASE_URL}/api/v1/projects",
                headers={"X-API-Key": API_KEY}
            )
            if response.status_code == 200:
                self.log_result("valid_key_access", "PASS", "Valid API key accepted")
            else:
                self.log_result("valid_key_access", "FAIL", f"Valid API key rejected: {response.status_code}")
                self.add_issue("Valid API key improperly rejected")
        except Exception as e:
            self.log_result("valid_key_access", "FAIL", f"Valid key test error: {e}")

    async def test_database_operations(self):
        """Test database connectivity and operations"""
        print("\n💾 Testing Database Operations...")
        
        headers = {"X-API-Key": API_KEY}
        
        # Test database read operations
        try:
            response = await self.client.get(f"{BASE_URL}/api/v1/projects", headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.log_result("db_read_projects", "PASS", f"Database read successful, found {data.get('count', 0)} projects")
            else:
                self.log_result("db_read_projects", "FAIL", f"Database read failed: {response.status_code}")
        except Exception as e:
            self.log_result("db_read_projects", "FAIL", f"Database read error: {e}")
        
        # Test database write operations (Create project)
        test_project = {
            "name": f"QA Test Project {uuid.uuid4().hex[:8]}",
            "description": "Test project created during QA validation",
            "status": "testing",
            "metadata": {"qa_test": True, "created_at": datetime.now(timezone.utc).isoformat()}
        }
        
        created_project_id = None
        try:
            response = await self.client.post(
                f"{BASE_URL}/api/v1/projects",
                headers=headers,
                json=test_project
            )
            if response.status_code == 201:
                data = response.json()
                created_project_id = data.get("id")
                self.log_result("db_write_create", "PASS", f"Database create successful, project ID: {created_project_id}")
            else:
                self.log_result("db_write_create", "FAIL", f"Database create failed: {response.status_code}")
                print(f"Response body: {response.text}")
        except Exception as e:
            self.log_result("db_write_create", "FAIL", f"Database create error: {e}")
        
        # Test database update operations
        if created_project_id:
            update_data = {"description": "Updated during QA validation", "status": "validated"}
            try:
                response = await self.client.put(
                    f"{BASE_URL}/api/v1/projects/{created_project_id}",
                    headers=headers,
                    json=update_data
                )
                if response.status_code == 200:
                    self.log_result("db_update", "PASS", "Database update successful")
                else:
                    self.log_result("db_update", "FAIL", f"Database update failed: {response.status_code}")
            except Exception as e:
                self.log_result("db_update", "FAIL", f"Database update error: {e}")
            
            # Test database delete operations
            try:
                response = await self.client.delete(
                    f"{BASE_URL}/api/v1/projects/{created_project_id}",
                    headers=headers
                )
                if response.status_code == 204:
                    self.log_result("db_delete", "PASS", "Database delete successful")
                else:
                    self.log_result("db_delete", "FAIL", f"Database delete failed: {response.status_code}")
            except Exception as e:
                self.log_result("db_delete", "FAIL", f"Database delete error: {e}")

    async def test_mqtt_integration(self):
        """Test MQTT event publishing and consumption"""
        print("\n📡 Testing MQTT Integration...")
        
        headers = {"X-API-Key": API_KEY}
        
        # Test MQTT event publishing via API
        try:
            response = await self.client.post(f"{BASE_URL}/api/v1/events/test", headers=headers)
            if response.status_code == 200:
                data = response.json()
                trace_id = data.get("trace_id")
                self.log_result("mqtt_publish_api", "PASS", f"MQTT event published via API, trace: {trace_id}")
                
                # Give some time for event to be processed
                await asyncio.sleep(2)
                
                # Check if event was stored in database
                try:
                    response = await self.client.get(
                        f"{BASE_URL}/api/v1/events?kind=test_event&limit=1",
                        headers=headers
                    )
                    if response.status_code == 200:
                        events_data = response.json()
                        if events_data.get("count", 0) > 0:
                            self.log_result("mqtt_event_storage", "PASS", "MQTT event successfully stored in database")
                        else:
                            self.log_result("mqtt_event_storage", "FAIL", "MQTT event not found in database")
                            self.add_issue("MQTT events not being stored in database")
                    else:
                        self.log_result("mqtt_event_storage", "FAIL", f"Failed to query events: {response.status_code}")
                except Exception as e:
                    self.log_result("mqtt_event_storage", "FAIL", f"Event storage check error: {e}")
                    
            else:
                self.log_result("mqtt_publish_api", "FAIL", f"MQTT publish failed: {response.status_code}")
                self.add_issue("MQTT event publishing not working")
        except Exception as e:
            self.log_result("mqtt_publish_api", "FAIL", f"MQTT publish error: {e}")

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

    async def test_api_performance(self):
        """Test API performance and response times"""
        print("\n⚡ Testing API Performance...")
        
        headers = {"X-API-Key": API_KEY}
        
        # Test multiple concurrent requests
        async def make_request(endpoint: str) -> Tuple[float, int]:
            start_time = time.time()
            try:
                response = await self.client.get(f"{BASE_URL}{endpoint}", headers=headers)
                end_time = time.time()
                return end_time - start_time, response.status_code
            except Exception as e:
                end_time = time.time()
                return end_time - start_time, 500
        
        endpoints_to_test = [
            "/health/ready",
            "/api/v1/projects",
            "/api/v1/events?limit=10",
            "/api/v1/health/stack"
        ]
        
        performance_results = {}
        
        for endpoint in endpoints_to_test:
            # Test single request performance
            duration, status = await make_request(endpoint)
            performance_results[endpoint] = {
                "single_request_time": duration,
                "status_code": status
            }
            
            if duration < 1.0 and status == 200:
                self.log_result(f"performance_{endpoint.replace('/', '_').replace('?', '_')}", "PASS", 
                              f"Response time: {duration:.3f}s")
            else:
                self.log_result(f"performance_{endpoint.replace('/', '_').replace('?', '_')}", "FAIL", 
                              f"Slow response: {duration:.3f}s or error: {status}")
                if duration > 2.0:
                    self.add_issue(f"Slow API response for {endpoint}: {duration:.3f}s")
        
        # Test concurrent load
        print("Testing concurrent load (10 requests)...")
        tasks = [make_request("/api/v1/projects") for _ in range(10)]
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time
        
        successful_requests = sum(1 for duration, status in results if isinstance((duration, status), tuple) and status == 200)
        avg_time = sum(duration for duration, status in results if isinstance((duration, status), tuple)) / len(results)
        
        performance_results["concurrent_load"] = {
            "total_requests": 10,
            "successful_requests": successful_requests,
            "total_time": total_time,
            "average_response_time": avg_time,
            "requests_per_second": 10 / total_time
        }
        
        if successful_requests >= 9 and avg_time < 2.0:
            self.log_result("concurrent_load", "PASS", 
                          f"Handled {successful_requests}/10 requests in {total_time:.2f}s, avg: {avg_time:.3f}s")
        else:
            self.log_result("concurrent_load", "FAIL", 
                          f"Poor concurrent performance: {successful_requests}/10 successful, avg: {avg_time:.3f}s")
            self.add_issue("Poor performance under concurrent load")
        
        self.results["performance_metrics"] = performance_results

    async def test_error_handling(self):
        """Test error handling and edge cases"""
        print("\n🛠️ Testing Error Handling...")
        
        headers = {"X-API-Key": API_KEY}
        
        # Test invalid endpoints
        try:
            response = await self.client.get(f"{BASE_URL}/api/v1/nonexistent", headers=headers)
            if response.status_code == 404:
                self.log_result("error_404", "PASS", "404 errors properly handled")
            else:
                self.log_result("error_404", "FAIL", f"Unexpected status for 404: {response.status_code}")
        except Exception as e:
            self.log_result("error_404", "FAIL", f"404 test error: {e}")
        
        # Test invalid project ID format
        try:
            response = await self.client.get(f"{BASE_URL}/api/v1/projects/invalid-id", headers=headers)
            if response.status_code in [400, 404]:
                self.log_result("error_invalid_id", "PASS", "Invalid ID format properly handled")
            else:
                self.log_result("error_invalid_id", "FAIL", f"Invalid ID not handled: {response.status_code}")
        except Exception as e:
            self.log_result("error_invalid_id", "FAIL", f"Invalid ID test error: {e}")
        
        # Test malformed JSON
        try:
            response = await self.client.post(
                f"{BASE_URL}/api/v1/projects",
                headers={**headers, "Content-Type": "application/json"},
                content="invalid json"
            )
            if response.status_code == 422:
                self.log_result("error_malformed_json", "PASS", "Malformed JSON properly rejected")
            else:
                self.log_result("error_malformed_json", "FAIL", f"Malformed JSON not handled: {response.status_code}")
        except Exception as e:
            self.log_result("error_malformed_json", "FAIL", f"Malformed JSON test error: {e}")

    def test_frontend_availability(self):
        """Test frontend service availability"""
        print("\n🌐 Testing Frontend Availability...")
        
        try:
            # Simple check if frontend is responding
            result = subprocess.run(
                ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", FRONTEND_URL],
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
        
        # Add performance recommendations
        perf_metrics = self.results.get("performance_metrics", {})
        if perf_metrics.get("concurrent_load", {}).get("requests_per_second", 0) < 50:
            self.add_recommendation("Consider performance optimization - current throughput is low")

    async def run_all_tests(self):
        """Run all QA tests"""
        print("🚀 Starting TaylorDash QA System Validation")
        print(f"Timestamp: {self.results['timestamp']}")
        print("=" * 80)
        
        # Run all test suites
        await self.test_service_health_checks()
        await self.test_security_authentication()
        await self.test_database_operations()
        await self.test_mqtt_integration()
        self.test_docker_services_status()
        await self.test_api_performance()
        await self.test_error_handling()
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

async def main():
    """Main execution function"""
    try:
        async with QATestSuite() as qa_suite:
            results = await qa_suite.run_all_tests()
            
            # Save detailed results to file
            results_file = "/TaylorProjects/TaylorDashv1/qa_results.json"
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
    asyncio.run(main())