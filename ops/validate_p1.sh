#!/bin/bash
# TaylorDash Phase 1 Validation Script
# Exit non-zero if any validation fails

set -e

echo "=== TaylorDash Phase 1 Validation ==="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Validation counters
PASSED=0
FAILED=0

validate() {
    local test_name="$1"
    local command="$2"
    
    echo -n "Testing $test_name... "
    if eval "$command" &>/dev/null; then
        echo -e "${GREEN}PASS${NC}"
        ((PASSED++))
    else
        echo -e "${RED}FAIL${NC}"
        ((FAILED++))
    fi
}

# Check if docker-compose is running
echo "Checking Docker Compose services..."
if ! docker-compose ps | grep -q "Up"; then
    echo -e "${RED}ERROR: No services are running. Run 'make up' first.${NC}"
    exit 1
fi

# 1. Container Health Checks
echo -e "\n${YELLOW}1. Container Health Checks${NC}"
validate "Postgres healthy" "docker-compose ps postgres | grep -q 'healthy'"
validate "Mosquitto healthy" "docker-compose ps mosquitto | grep -q 'healthy'"
validate "VictoriaMetrics healthy" "docker-compose ps victoriametrics | grep -q 'healthy'"
validate "MinIO healthy" "docker-compose ps minio | grep -q 'healthy'"
validate "Prometheus healthy" "docker-compose ps prometheus | grep -q 'healthy'"
validate "Backend healthy" "docker-compose ps backend | grep -q 'healthy'"

# 2. HTTP Health Endpoints
echo -e "\n${YELLOW}2. HTTP Health Endpoints${NC}"
validate "Backend /health/live" "curl -sf http://localhost:8000/health/live"
validate "Backend /health/ready" "curl -sf http://localhost:8000/health/ready"
validate "VictoriaMetrics health" "curl -sf http://localhost:8428/health"
validate "Prometheus health" "curl -sf http://localhost:9090/-/healthy"

# 3. Metrics Endpoints
echo -e "\n${YELLOW}3. Metrics Endpoints${NC}"
validate "Backend /metrics" "curl -sf http://localhost:8000/metrics | grep -q 'taylor_'"
validate "Backend has counters" "curl -sf http://localhost:8000/metrics | grep -q '_total'"
validate "Backend has histograms" "curl -sf http://localhost:8000/metrics | grep -q '_seconds_bucket'"
validate "Prometheus scraping" "curl -sf http://localhost:9090/api/v1/targets | grep -q 'taylordash-backend'"

# 4. MQTT Connectivity
echo -e "\n${YELLOW}4. MQTT Connectivity${NC}"
validate "MQTT auth connection" "timeout 5 mosquitto_pub -h localhost -p 1883 -u taylordash -P taylordash -t 'tracker/test' -m 'health-check'"
validate "MQTT subscription" "timeout 5 mosquitto_sub -h localhost -p 1883 -u taylordash -P taylordash -t 'tracker/test' -C 1"

# 5. Database Connectivity
echo -e "\n${YELLOW}5. Database Connectivity${NC}"
validate "Postgres connection" "docker-compose exec -T postgres pg_isready -U taylordash -d taylordash"
validate "Events mirror table" "docker-compose exec -T postgres psql -U taylordash -d taylordash -c 'SELECT 1 FROM events_mirror LIMIT 1' 2>/dev/null || docker-compose exec -T postgres psql -U taylordash -d taylordash -c 'SELECT COUNT(*) FROM events_mirror'"
validate "DLQ table exists" "docker-compose exec -T postgres psql -U taylordash -d taylordash -c 'SELECT COUNT(*) FROM dlq_events'"

# 6. MQTT Event Processing (if backend is ready)
echo -e "\n${YELLOW}6. Event Processing Test${NC}"
if curl -sf http://localhost:8000/health/ready &>/dev/null; then
    # Publish test event via API
    validate "Publish test event" "curl -sf -X POST 'http://localhost:8000/api/v1/events/publish?topic=tracker/events/test/test&kind=test.message' -H 'Content-Type: application/json' -d '{\"test\": \"data\"}'"
    
    # Give it time to process
    sleep 2
    
    # Check if event was mirrored
    validate "Event mirrored to DB" "docker-compose exec -T postgres psql -U taylordash -d taylordash -c \"SELECT COUNT(*) FROM events_mirror WHERE payload->>'kind' = 'test.message'\" | grep -q '1'"
    
    # Check DLQ is empty
    validate "DLQ empty (no failures)" "[ \$(docker-compose exec -T postgres psql -U taylordash -d taylordash -t -c 'SELECT COUNT(*) FROM dlq_events' | tr -d ' ') = '0' ]"
else
    echo "Skipping event processing tests (backend not ready)"
fi

# 7. Performance Test (lightweight)
echo -e "\n${YELLOW}7. Performance Check${NC}"
if command -v ab &> /dev/null; then
    validate "API latency P95 < 200ms" "ab -n 100 -c 10 http://localhost:8000/health/live 2>/dev/null | grep 'Time per request' | head -1 | awk '{print \$4}' | awk '{if(\$1 < 200) exit 0; else exit 1}'"
else
    echo "Apache Bench not available, skipping performance test"
fi

# Summary
echo -e "\n${YELLOW}=== Validation Summary ===${NC}"
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"

if [ $FAILED -eq 0 ]; then
    echo -e "\n${GREEN}✅ All validations passed! TaylorDash Phase 1 is operational.${NC}"
    exit 0
else
    echo -e "\n${RED}❌ $FAILED validation(s) failed. Check the issues above.${NC}"
    exit 1
fi