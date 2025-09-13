#!/bin/bash
# TaylorDash Infrastructure Health Check Script

set -e

cd /TaylorProjects/TaylorDashv1

echo "🏥 TaylorDash Infrastructure Health Check"
echo "=========================================="
echo "Timestamp: $(date)"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check service health
check_endpoint() {
    local url=$1
    local name=$2
    local timeout=${3:-5}

    if timeout $timeout curl -sf "$url" >/dev/null 2>&1; then
        echo -e "   ${GREEN}✅ $name${NC} - OK"
        return 0
    else
        echo -e "   ${RED}❌ $name${NC} - FAIL"
        return 1
    fi
}

# Function to check port status
check_port() {
    local port=$1
    local service=$2

    local result=$(netstat -tlnp 2>/dev/null | grep ":$port " || true)
    if [ -n "$result" ]; then
        echo -e "   ${GREEN}✅ Port $port ($service)${NC} - ACTIVE"
        echo "      $(echo "$result" | awk '{print $1, $4, $7}')"
    else
        echo -e "   ${RED}❌ Port $port ($service)${NC} - INACTIVE"
    fi
}

# Check Docker status
echo "🐳 Docker Services Status"
echo "-------------------------"

if docker info >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Docker daemon${NC} - Running"

    # Check Docker Compose services
    if docker-compose ps >/dev/null 2>&1; then
        echo ""
        echo "Docker Compose Services:"
        docker-compose ps --format "table {{.Name}}\t{{.State}}\t{{.Health}}\t{{.Ports}}"
    else
        echo -e "${YELLOW}⚠️  Docker Compose${NC} - No services running"
    fi
else
    echo -e "${RED}❌ Docker daemon${NC} - Not running"
fi

# Check port usage
echo ""
echo "🔌 Port Status"
echo "--------------"
check_port "80" "HTTP"
check_port "443" "HTTPS"
check_port "3000" "Backend Dev"
check_port "5173" "Frontend Dev"
check_port "5432" "PostgreSQL"
check_port "8080" "Traefik Dashboard"
check_port "8428" "VictoriaMetrics"
check_port "1883" "MQTT"
check_port "9000" "MinIO API"
check_port "9001" "MinIO Console"

# Check service endpoints
echo ""
echo "🌐 Service Endpoints"
echo "-------------------"
check_endpoint "http://localhost:8080/ping" "Traefik Health"
check_endpoint "http://localhost:3000/health" "Backend API"
check_endpoint "http://localhost:5173" "Frontend Dev"
check_endpoint "http://localhost:8428/health" "VictoriaMetrics"
check_endpoint "http://localhost:9000/minio/health/live" "MinIO Health"

# Check processes
echo ""
echo "🔄 Running Processes"
echo "-------------------"

# Backend processes
backend_procs=$(ps aux | grep -E "python.*uvicorn.*app.main:app" | grep -v grep || true)
if [ -n "$backend_procs" ]; then
    echo -e "${GREEN}Backend Processes:${NC}"
    echo "$backend_procs" | while read line; do
        echo "   $line"
    done
else
    echo -e "${YELLOW}No backend processes running${NC}"
fi

echo ""
# Frontend processes
frontend_procs=$(ps aux | grep -E "node.*vite" | grep -v grep || true)
if [ -n "$frontend_procs" ]; then
    echo -e "${GREEN}Frontend Processes:${NC}"
    echo "$frontend_procs" | while read line; do
        port=$(echo "$line" | grep -o "517[0-9]" || echo "default")
        echo "   Port $port: $line"
    done
else
    echo -e "${YELLOW}No frontend processes running${NC}"
fi

# Check database connectivity
echo ""
echo "🗄️  Database Connectivity"
echo "-------------------------"

if docker-compose exec -T postgres pg_isready -U taylordash -d taylordash >/dev/null 2>&1; then
    echo -e "${GREEN}✅ PostgreSQL${NC} - Ready"

    # Check database stats
    db_stats=$(docker-compose exec -T postgres psql -U taylordash -d taylordash -c "
        SELECT
            schemaname,
            tablename,
            n_tup_ins as inserts,
            n_tup_upd as updates,
            n_tup_del as deletes
        FROM pg_stat_user_tables
        ORDER BY schemaname, tablename;
    " 2>/dev/null || echo "Error getting stats")

    if [ "$db_stats" != "Error getting stats" ] && [ -n "$db_stats" ]; then
        echo "   Database activity:"
        echo "$db_stats" | head -10 | sed 's/^/   /'
    fi
else
    echo -e "${RED}❌ PostgreSQL${NC} - Not ready"
fi

# Check MQTT connectivity
echo ""
echo "📨 MQTT Broker Status"
echo "--------------------"

if docker-compose exec -T mosquitto mosquitto_pub -h localhost -t health/check -m "test" -u taylordash -P taylordash >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Mosquitto MQTT${NC} - Ready"
else
    echo -e "${RED}❌ Mosquitto MQTT${NC} - Connection failed"
fi

# Check disk space
echo ""
echo "💾 Storage Status"
echo "----------------"

df -h / | tail -1 | while read line; do
    usage=$(echo $line | awk '{print $5}' | sed 's/%//')
    if [ $usage -gt 90 ]; then
        echo -e "${RED}⚠️  Root filesystem: $line${NC}"
    elif [ $usage -gt 80 ]; then
        echo -e "${YELLOW}⚠️  Root filesystem: $line${NC}"
    else
        echo -e "${GREEN}✅ Root filesystem: $line${NC}"
    fi
done

# Docker volume usage
echo ""
docker_volumes=$(docker volume ls -q | grep taylordash || true)
if [ -n "$docker_volumes" ]; then
    echo "Docker volumes:"
    for vol in $docker_volumes; do
        size=$(docker run --rm -v $vol:/data alpine du -sh /data 2>/dev/null | awk '{print $1}' || echo "unknown")
        echo "   $vol: $size"
    done
fi

# System resource usage
echo ""
echo "⚡ System Resources"
echo "------------------"

# Memory usage
mem_usage=$(free | awk 'NR==2{printf "%.1f%%", $3*100/$2}')
echo -e "Memory usage: ${mem_usage}"

# CPU load
load_avg=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1,$2,$3}')
echo -e "Load average: ${load_avg}"

# Generate summary
echo ""
echo "📋 Health Summary"
echo "=================="

# Count services
total_services=0
healthy_services=0

# Docker services
docker_running=$(docker-compose ps -q 2>/dev/null | wc -l)
docker_healthy=$(docker-compose ps --filter "status=running" -q 2>/dev/null | wc -l || echo "0")

# Development services
dev_backend=$(pgrep -f "uvicorn.*app.main:app" | wc -l || echo "0")
dev_frontend=$(pgrep -f "node.*vite" | wc -l || echo "0")

echo "Docker Services: $docker_healthy/$docker_running healthy"
echo "Development Services: $((dev_backend + dev_frontend)) running"

# Overall status
if [ $docker_healthy -gt 0 ] || [ $dev_backend -gt 0 ] || [ $dev_frontend -gt 0 ]; then
    echo -e "${GREEN}🎉 System Status: OPERATIONAL${NC}"
else
    echo -e "${RED}💥 System Status: DOWN${NC}"
fi

echo ""
echo "💡 Useful Commands:"
echo "   - Restart dev: scripts/start-development.sh"
echo "   - Stop services: scripts/stop-development.sh"
echo "   - Full cleanup: scripts/cleanup-infrastructure.sh"
echo "   - View logs: docker-compose logs <service>"