#!/bin/bash

# TaylorDash Clean Development Environment Startup
# Standardized service management with proper port assignments

set -e

echo "🧹 Starting TaylorDash Clean Development Environment..."

# Configuration - CANONICAL PORT ASSIGNMENTS
BACKEND_PORT=3000
FRONTEND_PORT=5173
MCP_MANAGER_PORT=5174
MIDNIGHT_HUD_PORT=5175
PROJECTS_MANAGER_PORT=5176

# Environment variables for backend
export DATABASE_URL="postgresql://taylordash_app:password@localhost:5432/taylordash"
export MQTT_HOST="localhost"
export MQTT_PORT="1883"
export MQTT_USERNAME="taylordash"
export MQTT_PASSWORD="taylordash"
export API_KEY="taylordash-dev-key"

# Function to check if port is available
check_port() {
    local port=$1
    if netstat -tuln 2>/dev/null | grep -q ":$port "; then
        echo "❌ Port $port is already in use"
        return 1
    fi
    echo "✅ Port $port is available"
    return 0
}

# Function to wait for service
wait_for_service() {
    local url=$1
    local name=$2
    echo "⏳ Waiting for $name to be ready..."
    for i in {1..30}; do
        if curl -s "$url" >/dev/null 2>&1; then
            echo "✅ $name is ready!"
            return 0
        fi
        sleep 2
    done
    echo "❌ $name failed to start"
    return 1
}

echo ""
echo "🔍 Checking port availability..."

# Check all required ports
check_port $BACKEND_PORT || exit 1
check_port $FRONTEND_PORT || exit 1
check_port $MCP_MANAGER_PORT || exit 1
check_port $MIDNIGHT_HUD_PORT || exit 1
check_port $PROJECTS_MANAGER_PORT || exit 1

echo ""
echo "🚀 Starting services in dependency order..."

# 1. Start Backend API (core dependency)
echo ""
echo "📡 Starting Backend API on port $BACKEND_PORT..."
cd /TaylorProjects/TaylorDashv1/backend
source venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port $BACKEND_PORT &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait for backend to be ready
wait_for_service "http://localhost:$BACKEND_PORT/health/live" "Backend API"

# 2. Start Frontend (depends on backend)
echo ""
echo "🌐 Starting Frontend on port $FRONTEND_PORT..."
cd /TaylorProjects/TaylorDashv1/frontend
npm run dev -- --host 0.0.0.0 --port $FRONTEND_PORT &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

# 3. Start Plugins (independent of each other)
echo ""
echo "🔌 Starting Plugins..."

# MCP Manager Plugin
echo "  • MCP Manager on port $MCP_MANAGER_PORT..."
cd /TaylorProjects/TaylorDashv1/examples/mcp-manager
npm run dev -- --host 0.0.0.0 --port $MCP_MANAGER_PORT &
MCP_PID=$!
echo "    MCP Manager PID: $MCP_PID"

# Midnight HUD Plugin
echo "  • Midnight HUD on port $MIDNIGHT_HUD_PORT..."
cd /TaylorProjects/TaylorDashv1/examples/midnight-hud
npm run dev -- --host 0.0.0.0 --port $MIDNIGHT_HUD_PORT &
MIDNIGHT_PID=$!
echo "    Midnight HUD PID: $MIDNIGHT_PID"

# Projects Manager Plugin
echo "  • Projects Manager on port $PROJECTS_MANAGER_PORT..."
cd /TaylorProjects/TaylorDashv1/examples/projects-manager
npm run dev -- --host 0.0.0.0 --port $PROJECTS_MANAGER_PORT &
PROJECTS_PID=$!
echo "    Projects Manager PID: $PROJECTS_PID"

echo ""
echo "⏳ Waiting for all services to initialize..."
sleep 5

# Wait for frontend to be ready
wait_for_service "http://localhost:$FRONTEND_PORT" "Frontend"

echo ""
echo "🎉 TaylorDash Development Environment Ready!"
echo ""
echo "📋 Service Endpoints:"
echo "  🌐 Frontend:         http://localhost:$FRONTEND_PORT"
echo "  📡 Backend API:      http://localhost:$BACKEND_PORT"
echo "  📊 API Docs:         http://localhost:$BACKEND_PORT/docs"
echo ""
echo "🔌 Plugin Endpoints:"
echo "  🔧 MCP Manager:      http://localhost:$MCP_MANAGER_PORT"
echo "  🌙 Midnight HUD:     http://localhost:$MIDNIGHT_HUD_PORT"
echo "  📁 Projects Manager: http://localhost:$PROJECTS_MANAGER_PORT"
echo ""
echo "🌍 Remote Access (replace with your IP):"
echo "  🌐 Frontend:         http://192.168.20.17:$FRONTEND_PORT"
echo "  📡 Backend API:      http://192.168.20.17:$BACKEND_PORT"
echo ""
echo "💡 To stop all services, run: ./scripts/stop-development.sh"

# Save PIDs for cleanup script
mkdir -p /tmp/taylordash
cat > /tmp/taylordash/dev-pids.txt << EOF
BACKEND_PID=$BACKEND_PID
FRONTEND_PID=$FRONTEND_PID
MCP_PID=$MCP_PID
MIDNIGHT_PID=$MIDNIGHT_PID
PROJECTS_PID=$PROJECTS_PID
EOF

echo ""
echo "✅ Service management ready!"
echo "   PIDs saved to /tmp/taylordash/dev-pids.txt"

# Keep script running to maintain processes
wait