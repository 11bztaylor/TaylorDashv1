#!/bin/bash
# TaylorDash Development Environment Startup Script

set -e

cd /TaylorProjects/TaylorDashv1

echo "🚀 Starting TaylorDash Development Environment..."
echo "================================================="

# Verify Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Function to wait for service health
wait_for_service() {
    local service=$1
    local max_attempts=30
    local attempt=1

    echo "⏳ Waiting for $service to be healthy..."

    while [ $attempt -le $max_attempts ]; do
        if docker-compose ps $service 2>/dev/null | grep -q "healthy\|Up"; then
            echo "✅ $service is ready"
            return 0
        fi
        echo "   Attempt $attempt/$max_attempts - $service not ready yet..."
        sleep 2
        attempt=$((attempt + 1))
    done

    echo "❌ $service failed to start properly"
    return 1
}

# Start infrastructure services
echo ""
echo "🏗️  Starting Infrastructure Services..."
echo "---------------------------------------"

echo "📚 Starting PostgreSQL database..."
docker-compose up -d postgres
wait_for_service postgres

echo "📨 Starting Mosquitto MQTT broker..."
docker-compose up -d mosquitto
wait_for_service mosquitto

echo "📊 Starting VictoriaMetrics TSDB..."
docker-compose up -d victoriametrics
wait_for_service victoriametrics

echo "🗄️  Starting MinIO object storage..."
docker-compose up -d minio
wait_for_service minio

echo "📈 Starting monitoring services..."
docker-compose up -d prometheus grafana
wait_for_service prometheus
wait_for_service grafana

# Start Traefik last
echo "🌐 Starting Traefik reverse proxy..."
docker-compose up -d traefik
wait_for_service traefik

# Check if backend is already running
echo ""
echo "🔧 Development Services Setup"
echo "-----------------------------"

backend_running=$(pgrep -f "uvicorn.*app.main:app.*port.*3000" || true)
if [ -n "$backend_running" ]; then
    echo "✅ Backend already running on port 3000"
else
    echo "🚀 Starting backend development server..."
    if [ ! -d "backend/venv" ]; then
        echo "❌ Backend virtual environment not found. Please run 'cd backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt'"
        exit 1
    fi

    # Start backend in background
    (
        cd backend
        source venv/bin/activate
        export DATABASE_URL="postgresql://taylordash:taylordash_secure_password@localhost:5432/taylordash"
        export MQTT_HOST="localhost"
        export MQTT_PORT="1883"
        export MQTT_USERNAME="taylordash"
        export MQTT_PASSWORD="taylordash"
        export API_KEY="taylordash-dev-key"

        echo "🔄 Backend starting on port 3000..."
        uvicorn app.main:app --reload --host 0.0.0.0 --port 3000 > /tmp/backend-dev.log 2>&1 &
        echo $! > /tmp/backend-dev.pid
    )

    # Wait a moment for backend to start
    sleep 3
    if curl -s http://localhost:3000/health >/dev/null 2>&1; then
        echo "✅ Backend started successfully on port 3000"
    else
        echo "⚠️  Backend may still be starting... check logs with: tail -f /tmp/backend-dev.log"
    fi
fi

# Check if frontend is already running
frontend_running=$(pgrep -f "vite.*5173" | grep -v "5174\|5175\|5176\|5177\|5178" || true)
if [ -n "$frontend_running" ]; then
    echo "✅ Frontend already running on port 5173"
else
    echo "🌐 Starting frontend development server..."
    if [ ! -d "frontend/node_modules" ]; then
        echo "❌ Frontend dependencies not found. Please run 'cd frontend && npm install'"
        exit 1
    fi

    # Start frontend in background
    (
        cd frontend
        echo "🔄 Frontend starting on port 5173..."
        npm run dev > /tmp/frontend-dev.log 2>&1 &
        echo $! > /tmp/frontend-dev.pid
    )

    # Wait a moment for frontend to start
    sleep 5
    if curl -s http://localhost:5173 >/dev/null 2>&1; then
        echo "✅ Frontend started successfully on port 5173"
    else
        echo "⚠️  Frontend may still be starting... check logs with: tail -f /tmp/frontend-dev.log"
    fi
fi

# Show service status
echo ""
echo "📊 Development Environment Status"
echo "================================="

echo "🐳 Docker Services:"
docker-compose ps

echo ""
echo "🔄 Development Processes:"
ps aux | grep -E "(node.*vite.*5173|python.*uvicorn.*3000)" | grep -v grep || echo "   No development processes found"

echo ""
echo "🌐 Service URLs:"
echo "   Frontend:         http://localhost:5173"
echo "   Backend API:      http://localhost:3000"
echo "   API Docs:         http://localhost:3000/docs"
echo "   Traefik Dashboard: http://localhost:8080"
echo "   Grafana:          http://taylordash.local:3000 (via Traefik)"

echo ""
echo "📋 Example Services (if running):"
echo "   MCP Manager:      http://localhost:5174"
echo "   Projects Manager: http://localhost:5175"
echo "   Midnight HUD:     http://localhost:5177"

echo ""
echo "📝 Development Notes:"
echo "   - Backend logs:   tail -f /tmp/backend-dev.log"
echo "   - Frontend logs:  tail -f /tmp/frontend-dev.log"
echo "   - Stop services:  scripts/stop-development.sh"
echo "   - Health check:   scripts/health-check.sh"

echo ""
echo "🎉 Development environment is ready!"