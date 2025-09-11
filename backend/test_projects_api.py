#!/usr/bin/env python3
"""
Quick test script for the Projects API
Tests authentication, RBAC, and basic CRUD operations
"""
import asyncio
import json
import os
import sys
from typing import Dict, Any

import httpx

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
TEST_JWT_TOKEN = os.getenv("TEST_JWT_TOKEN", "")

# Test JWT payload (for development/testing)
# This is what a real JWT from Keycloak would contain
TEST_JWT_PAYLOAD = {
    "iss": "http://keycloak:8080/realms/taylordash",
    "sub": "test-user-123",
    "preferred_username": "testuser",
    "email": "test@example.com",
    "realm_access": {
        "roles": ["maintainer"]
    },
    "resource_access": {
        "taylordash-api": {
            "roles": ["maintainer"]
        }
    },
    "exp": 9999999999,  # Far future expiry
    "iat": 1000000000,
    "jti": "test-jti-123"
}

async def test_health_endpoints():
    """Test basic health endpoints (no auth required)"""
    print("Testing health endpoints...")
    
    async with httpx.AsyncClient() as client:
        # Test liveness
        response = await client.get(f"{API_BASE_URL}/health/live")
        assert response.status_code == 200
        print("✓ Health live endpoint working")
        
        # Test readiness
        response = await client.get(f"{API_BASE_URL}/health/ready")
        assert response.status_code in [200, 503]  # May be 503 if MQTT not running
        print("✓ Health ready endpoint working")

async def test_projects_without_auth():
    """Test that projects endpoints require authentication"""
    print("Testing projects endpoints without auth...")
    
    async with httpx.AsyncClient() as client:
        # Test GET projects without auth
        response = await client.get(f"{API_BASE_URL}/api/v1/projects")
        assert response.status_code == 401
        print("✓ GET projects correctly requires authentication")
        
        # Test POST projects without auth
        response = await client.post(
            f"{API_BASE_URL}/api/v1/projects",
            json={"name": "Test Project"}
        )
        assert response.status_code == 401
        print("✓ POST projects correctly requires authentication")

async def test_projects_with_auth():
    """Test projects endpoints with authentication"""
    if not TEST_JWT_TOKEN:
        print("⚠ Skipping auth tests - TEST_JWT_TOKEN not provided")
        return
    
    print("Testing projects endpoints with auth...")
    
    headers = {"Authorization": f"Bearer {TEST_JWT_TOKEN}"}
    
    async with httpx.AsyncClient() as client:
        # Test GET projects with auth
        response = await client.get(f"{API_BASE_URL}/api/v1/projects", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "projects" in data
        assert "total" in data
        print(f"✓ GET projects returned {data['total']} projects")
        
        # Test POST projects with auth
        project_data = {
            "name": f"Test Project {asyncio.get_event_loop().time()}",
            "description": "A test project created by the test script",
            "status": "new"
        }
        
        response = await client.post(
            f"{API_BASE_URL}/api/v1/projects",
            json=project_data,
            headers=headers
        )
        assert response.status_code == 201
        created_project = response.json()
        assert created_project["name"] == project_data["name"]
        assert created_project["status"] == "new"
        print(f"✓ POST projects created project: {created_project['id']}")
        
        return created_project

async def test_openapi_docs():
    """Test that OpenAPI documentation is available"""
    print("Testing OpenAPI documentation...")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/docs")
        assert response.status_code == 200
        print("✓ OpenAPI docs available at /docs")
        
        response = await client.get(f"{API_BASE_URL}/openapi.json")
        assert response.status_code == 200
        openapi_spec = response.json()
        
        # Check that our projects endpoints are documented
        paths = openapi_spec.get("paths", {})
        assert "/api/v1/projects/" in paths
        print("✓ Projects endpoints documented in OpenAPI spec")

async def main():
    """Run all tests"""
    print("🚀 Starting TaylorDash Projects API Tests")
    print(f"API Base URL: {API_BASE_URL}")
    print(f"Using JWT: {'Yes' if TEST_JWT_TOKEN else 'No'}")
    print()
    
    try:
        await test_health_endpoints()
        print()
        
        await test_projects_without_auth()
        print()
        
        await test_projects_with_auth()
        print()
        
        await test_openapi_docs()
        print()
        
        print("✅ All tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Generate a simple test JWT for development
    if not TEST_JWT_TOKEN and os.getenv("SKIP_JWT_VERIFICATION", "false").lower() == "true":
        import jwt
        TEST_JWT_TOKEN = jwt.encode(TEST_JWT_PAYLOAD, "test-secret", algorithm="HS256")
        print(f"Generated test JWT: {TEST_JWT_TOKEN[:50]}...")
        os.environ["TEST_JWT_TOKEN"] = TEST_JWT_TOKEN
    
    asyncio.run(main())