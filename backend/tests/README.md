# 🧪 TaylorDash Backend Tests

Comprehensive test suite for the TaylorDash backend using pytest, covering API endpoints, database operations, and security features.

## 📁 Current Tests

- **`test_plugin_security.py`** - Plugin security and validation tests
- **Integration tests** - End-to-end API testing
- **Unit tests** - Individual component testing
- **Security tests** - Authentication and authorization testing

## 💻 Code Examples

### Common Patterns

#### Basic Test Setup
```python
# conftest.py - Test configuration and fixtures
import pytest
import asyncio
from httpx import AsyncClient
from app.main import app
from app.database import get_db_pool

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def client():
    """Create test client for API testing"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def api_headers():
    """Standard API headers for testing"""
    return {"X-API-Key": "taylordash-dev-key"}
```

#### API Endpoint Testing
```python
# test_api_endpoints.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_plugins(client: AsyncClient, api_headers):
    """Test getting all plugins"""
    response = await client.get("/api/v1/plugins/", headers=api_headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

@pytest.mark.asyncio
async def test_create_plugin(client: AsyncClient, api_headers):
    """Test creating a new plugin"""
    plugin_data = {
        "id": "test-plugin",
        "name": "Test Plugin",
        "repository_url": "https://github.com/user/test-plugin"
    }

    response = await client.post(
        "/api/v1/plugins/install",
        json=plugin_data,
        headers=api_headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["plugin_id"] == "test-plugin"
    assert "installation_id" in data

@pytest.mark.asyncio
async def test_plugin_not_found(client: AsyncClient, api_headers):
    """Test 404 for non-existent plugin"""
    response = await client.get(
        "/api/v1/plugins/non-existent",
        headers=api_headers
    )

    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()

@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient):
    """Test API without authentication"""
    response = await client.get("/api/v1/plugins/")

    assert response.status_code == 401
    data = response.json()
    assert "Missing API key" in data["detail"]
```

#### Security Testing
```python
# test_security.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_api_key_validation(client: AsyncClient):
    """Test various API key scenarios"""
    # Missing API key
    response = await client.get("/api/v1/plugins/")
    assert response.status_code == 401

    # Invalid API key
    response = await client.get(
        "/api/v1/plugins/",
        headers={"X-API-Key": "invalid-key"}
    )
    assert response.status_code == 401

    # Valid API key
    response = await client.get(
        "/api/v1/plugins/",
        headers={"X-API-Key": "taylordash-dev-key"}
    )
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_plugin_security_validation(client: AsyncClient, api_headers):
    """Test plugin security validation"""
    malicious_plugin = {
        "id": "../../../etc/passwd",
        "name": "Malicious Plugin",
        "repository_url": "javascript:alert('xss')"
    }

    response = await client.post(
        "/api/v1/plugins/install",
        json=malicious_plugin,
        headers=api_headers
    )

    # Should reject malicious plugin
    assert response.status_code == 400
    data = response.json()
    assert "invalid" in data["detail"].lower()

@pytest.mark.asyncio
async def test_input_sanitization(client: AsyncClient, api_headers):
    """Test input sanitization and validation"""
    test_cases = [
        {"id": "", "name": "Empty ID"},
        {"id": "x" * 300, "name": "Too Long ID"},
        {"id": "test", "name": "<script>alert('xss')</script>"},
        {"id": "test", "repository_url": "not-a-url"}
    ]

    for test_case in test_cases:
        response = await client.post(
            "/api/v1/plugins/install",
            json=test_case,
            headers=api_headers
        )

        # Should reject invalid input
        assert response.status_code in [400, 422]
```

### How to Extend

#### 1. Add New Test File
```python
# test_my_feature.py
import pytest
from httpx import AsyncClient

class TestMyFeature:
    """Test suite for my new feature"""

    @pytest.mark.asyncio
    async def test_feature_creation(self, client: AsyncClient, api_headers):
        """Test creating new feature"""
        feature_data = {
            "name": "Test Feature",
            "description": "A test feature"
        }

        response = await client.post(
            "/api/v1/my-feature/",
            json=feature_data,
            headers=api_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Feature"

    @pytest.mark.asyncio
    async def test_feature_validation(self, client: AsyncClient, api_headers):
        """Test feature input validation"""
        invalid_data = {"name": ""}  # Empty name should fail

        response = await client.post(
            "/api/v1/my-feature/",
            json=invalid_data,
            headers=api_headers
        )

        assert response.status_code == 422
```

#### 2. Database Testing
```python
# test_database_operations.py
import pytest
from app.database import get_db_connection

@pytest.fixture
async def db_transaction():
    """Provide database transaction that rolls back after test"""
    async with get_db_connection() as conn:
        async with conn.transaction():
            yield conn
            # Transaction automatically rolls back

@pytest.mark.asyncio
async def test_plugin_crud(db_transaction):
    """Test plugin CRUD operations"""
    # Create
    plugin_id = "test-plugin-db"
    await db_transaction.execute("""
        INSERT INTO plugins (id, name, version, author, type, kind,
                           repository_url, install_path, manifest, status)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
    """, plugin_id, "Test Plugin", "1.0.0", "Test Author", "ui", "ui",
         "https://github.com/test/plugin", "/plugins/test", '{}', 'active')

    # Read
    result = await db_transaction.fetchrow("""
        SELECT * FROM plugins WHERE id = $1
    """, plugin_id)

    assert result is not None
    assert result['name'] == "Test Plugin"
    assert result['status'] == "active"

    # Update
    await db_transaction.execute("""
        UPDATE plugins SET status = 'disabled' WHERE id = $1
    """, plugin_id)

    updated = await db_transaction.fetchrow("""
        SELECT status FROM plugins WHERE id = $1
    """, plugin_id)

    assert updated['status'] == "disabled"

    # Delete would happen here, but transaction rollback handles cleanup
```

### Testing This Component

#### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest backend/tests/test_plugin_security.py

# Run tests with coverage
pytest --cov=app --cov-report=html

# Run tests in parallel
pytest -n auto

# Run only security tests
pytest -m security

# Verbose output
pytest -v

# Run tests matching pattern
pytest -k "test_plugin"
```

#### Test Configuration
```python
# pytest.ini or pyproject.toml
[tool.pytest.ini_options]
testpaths = ["backend/tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--disable-warnings",
    "--tb=short"
]
markers = [
    "security: marks tests as security tests",
    "integration: marks tests as integration tests",
    "slow: marks tests as slow running"
]
```

#### Fixtures and Mocking
```python
# Advanced fixtures
@pytest.fixture
async def mock_mqtt_client(monkeypatch):
    """Mock MQTT client for testing"""
    class MockMQTTClient:
        def __init__(self):
            self.published_messages = []

        async def publish(self, topic: str, payload: str):
            self.published_messages.append({"topic": topic, "payload": payload})

    mock_client = MockMQTTClient()
    monkeypatch.setattr("app.mqtt_client.get_mqtt_client", lambda: mock_client)
    return mock_client

@pytest.fixture
def mock_file_system(tmp_path, monkeypatch):
    """Mock file system operations"""
    monkeypatch.setattr("app.plugins.PLUGINS_DIR", str(tmp_path))
    return tmp_path
```

### Debugging Tips

#### Test Debugging
```python
# Add debugging to tests
import logging
logging.basicConfig(level=logging.DEBUG)

def test_with_debugging():
    """Example test with debugging"""
    import pdb; pdb.set_trace()  # Debugger breakpoint

    # Your test code here
    assert True

# Print debugging
@pytest.mark.asyncio
async def test_with_prints(client: AsyncClient, api_headers, caplog):
    """Test with print debugging and log capture"""
    with caplog.at_level(logging.INFO):
        response = await client.get("/api/v1/plugins/", headers=api_headers)

        print(f"Response: {response.json()}")
        print(f"Logs: {caplog.text}")

        assert response.status_code == 200
```

#### Performance Testing
```python
# test_performance.py
import time
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_api_response_time(client: AsyncClient, api_headers):
    """Test API response time"""
    start_time = time.time()

    response = await client.get("/api/v1/plugins/", headers=api_headers)

    end_time = time.time()
    response_time = (end_time - start_time) * 1000  # Convert to milliseconds

    assert response.status_code == 200
    assert response_time < 500  # Should respond within 500ms

@pytest.mark.asyncio
async def test_concurrent_requests(client: AsyncClient, api_headers):
    """Test handling concurrent requests"""
    import asyncio

    async def make_request():
        return await client.get("/api/v1/plugins/", headers=api_headers)

    # Make 10 concurrent requests
    tasks = [make_request() for _ in range(10)]
    responses = await asyncio.gather(*tasks)

    # All should succeed
    for response in responses:
        assert response.status_code == 200
```

### API Usage

#### Test Data Management
```python
# test_data.py
TEST_PLUGIN_DATA = {
    "valid_plugin": {
        "id": "test-plugin",
        "name": "Test Plugin",
        "version": "1.0.0",
        "author": "Test Author",
        "repository_url": "https://github.com/test/plugin"
    },
    "invalid_plugin": {
        "id": "",  # Invalid empty ID
        "name": "Invalid Plugin"
    }
}

@pytest.fixture
def plugin_data():
    """Provide test plugin data"""
    return TEST_PLUGIN_DATA

# Usage in tests
@pytest.mark.asyncio
async def test_plugin_creation(client: AsyncClient, api_headers, plugin_data):
    """Test plugin creation with test data"""
    response = await client.post(
        "/api/v1/plugins/install",
        json=plugin_data["valid_plugin"],
        headers=api_headers
    )

    assert response.status_code == 201
```

#### Environment-Specific Testing
```bash
# Set test environment variables
export TESTING=true
export DATABASE_URL="postgresql://test_user:test_pass@localhost/test_db"
export API_KEY="test-api-key"

# Run tests
pytest
```

## 🔧 Test Best Practices

- Use descriptive test names that explain what is being tested
- Arrange-Act-Assert pattern for clear test structure
- Use fixtures to avoid code duplication
- Mock external dependencies (MQTT, file system, external APIs)
- Test both happy path and error conditions
- Use parametrized tests for multiple input scenarios
- Keep tests independent and isolated

## 🚀 Continuous Integration

```yaml
# .github/workflows/tests.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: test_password
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-asyncio pytest-cov

    - name: Run tests
      run: pytest --cov=app --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v1
```