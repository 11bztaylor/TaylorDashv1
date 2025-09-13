#!/bin/bash
# TaylorDash Production Environment Startup Script

set -e

cd /TaylorProjects/TaylorDashv1

echo "🚀 Starting TaylorDash Production Environment..."
echo "================================================"

# Verify Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check for required files
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ docker-compose.yml not found in current directory"
    exit 1
fi

if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please create from .env.example"
    exit 1
fi

# Function to wait for service health
wait_for_service() {
    local service=$1
    local max_attempts=60
    local attempt=1

    echo "⏳ Waiting for $service to be healthy..."

    while [ $attempt -le $max_attempts ]; do
        local status=$(docker-compose ps $service 2>/dev/null | grep $service || echo "not found")
        if echo "$status" | grep -q "healthy\|Up"; then
            echo "✅ $service is ready"
            return 0
        fi
        echo "   Attempt $attempt/$max_attempts - $service status: $(echo "$status" | awk '{print $NF}')"
        sleep 5
        attempt=$((attempt + 1))
    done

    echo "❌ $service failed to start within timeout"
    echo "📋 Service logs:"
    docker-compose logs --tail=20 $service
    return 1
}

# Pull latest images
echo ""
echo "📥 Pulling Latest Images..."
echo "--------------------------"
docker-compose pull

# Start core infrastructure services first
echo ""
echo "🏗️  Starting Core Infrastructure..."
echo "-----------------------------------"

echo "📚 Starting PostgreSQL database..."
docker-compose up -d postgres
wait_for_service postgres

echo "📊 Starting VictoriaMetrics TSDB..."
docker-compose up -d victoriametrics
wait_for_service victoriametrics

echo "🗄️  Starting MinIO object storage..."
docker-compose up -d minio
wait_for_service minio

echo "📨 Starting Mosquitto MQTT broker..."
docker-compose up -d mosquitto
wait_for_service mosquitto

# Start monitoring services
echo ""
echo "📈 Starting Monitoring Services..."
echo "----------------------------------"

echo "🔍 Starting Prometheus..."
docker-compose up -d prometheus
wait_for_service prometheus

echo "📊 Starting Grafana..."
docker-compose up -d grafana
wait_for_service grafana

# Start application services
echo ""
echo "🚀 Starting Application Services..."
echo "-----------------------------------"

# Check if backend service is defined in docker-compose
if docker-compose config --services | grep -q "^backend$"; then
    echo "🔧 Starting Backend API..."
    docker-compose up -d backend
    wait_for_service backend
else
    echo "⚠️  Backend service not defined in docker-compose.yml"
    echo "   Please add backend service configuration"
fi

# Check if frontend service is defined in docker-compose
if docker-compose config --services | grep -q "^frontend$"; then
    echo "🌐 Starting Frontend..."
    docker-compose up -d frontend
    wait_for_service frontend
else
    echo "⚠️  Frontend service not defined in docker-compose.yml"
    echo "   Please add frontend service configuration"
fi

# Start reverse proxy last
echo ""
echo "🌐 Starting Reverse Proxy..."
echo "----------------------------"

echo "🚦 Starting Traefik..."
docker-compose up -d traefik
wait_for_service traefik

# Wait for Traefik to configure routes
echo "⏳ Waiting for Traefik route configuration..."
sleep 10

# Health checks
echo ""
echo "🏥 Production Health Checks"
echo "============================="

health_check_url() {
    local url=$1
    local name=$2
    local timeout=${3:-10}

    if timeout $timeout curl -sf "$url" >/dev/null 2>&1; then
        echo "✅ $name - OK"
        return 0
    else
        echo "❌ $name - FAIL"
        return 1
    fi
}

# Core service health checks
echo "Core Services:"
health_check_url "http://localhost:8080/ping" "Traefik Health"
health_check_url "http://localhost:8428/health" "VictoriaMetrics"
health_check_url "http://localhost:9000/minio/health/live" "MinIO Health"

# Database connectivity
echo ""
echo "Database:"
if docker-compose exec -T postgres pg_isready -U taylordash -d taylordash >/dev/null 2>&1; then
    echo "✅ PostgreSQL - Ready"
else
    echo "❌ PostgreSQL - Not ready"
fi

# MQTT connectivity
echo ""
echo "Message Broker:"
if docker-compose exec -T mosquitto mosquitto_pub -h localhost -t health/check -m "test" -u taylordash -P taylordash >/dev/null 2>&1; then
    echo "✅ Mosquitto MQTT - Ready"
else
    echo "❌ Mosquitto MQTT - Connection failed"
fi

# Application health checks (if services exist)
echo ""
echo "Application Services:"
if docker-compose ps backend >/dev/null 2>&1; then
    backend_url=$(docker-compose port backend 8000 2>/dev/null | sed 's/0.0.0.0/localhost/' || echo "")
    if [ -n "$backend_url" ]; then
        health_check_url "http://$backend_url/health" "Backend API" 15
    else
        # Try through Traefik
        health_check_url "http://taylordash.local/api/health" "Backend API (via Traefik)" 15
    fi
else
    echo "⚠️  Backend service not running"
fi

if docker-compose ps frontend >/dev/null 2>&1; then
    health_check_url "http://taylordash.local/" "Frontend (via Traefik)" 15
else
    echo "⚠️  Frontend service not running"
fi

# Show final status
echo ""
echo "📊 Production Environment Status"
echo "================================="

echo "🐳 Docker Services:"
docker-compose ps

echo ""
echo "🌐 Service Access URLs:"
echo "   Main Application:  https://taylordash.local"
echo "   Traefik Dashboard: http://localhost:8080"
echo "   MinIO Console:     http://localhost:9001"

echo ""
echo "📋 Internal Service Ports:"
echo "   PostgreSQL:        localhost:5432"
echo "   VictoriaMetrics:   localhost:8428"
echo "   MinIO API:         localhost:9000"
echo "   MQTT:              localhost:1883"

echo ""
echo "🔐 Security Notes:"
echo "   - All external traffic routes through Traefik (ports 80/443)"
echo "   - Internal services are not directly exposed"
echo "   - Database and MQTT require authentication"
echo "   - SSL certificates managed by Traefik"

echo ""
echo "📝 Management Commands:"
echo "   - View logs:       docker-compose logs -f [service]"
echo "   - Scale service:   docker-compose up -d --scale [service]=N"
echo "   - Update service:  docker-compose pull [service] && docker-compose up -d [service]"
echo "   - Stop all:        docker-compose down"

# Final validation
all_critical_healthy=true

# Check critical services
critical_services="postgres victoriametrics minio mosquitto prometheus grafana traefik"
for service in $critical_services; do
    if ! docker-compose ps $service | grep -q "Up\|healthy"; then
        echo "❌ Critical service $service is not healthy"
        all_critical_healthy=false
    fi
done

echo ""
if [ "$all_critical_healthy" = true ]; then
    echo "🎉 Production environment is ready and all critical services are healthy!"
    echo ""
    echo "📈 Next Steps:"
    echo "   1. Configure DNS: taylordash.local -> your-server-ip"
    echo "   2. Set up SSL certificates for production domain"
    echo "   3. Configure monitoring alerts"
    echo "   4. Set up backup procedures"
else
    echo "⚠️  Production environment started but some services may need attention."
    echo "   Run 'scripts/health-check.sh' for detailed diagnostics"
fi