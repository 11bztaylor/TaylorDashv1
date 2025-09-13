#!/bin/bash
# TaylorDash Infrastructure Cleanup Script
# This script stops all duplicate services and cleans up the infrastructure

set -e

echo "🧹 TaylorDash Infrastructure Cleanup Starting..."
echo "=============================================="

# Function to safely kill processes
safe_kill() {
    local pattern="$1"
    local description="$2"

    echo "🔍 Looking for $description processes..."
    local pids=$(pgrep -f "$pattern" || true)

    if [ -n "$pids" ]; then
        echo "⚠️  Found $description processes: $pids"
        echo "🛑 Stopping $description processes..."
        pkill -f "$pattern" || true
        sleep 2

        # Force kill if still running
        local remaining=$(pgrep -f "$pattern" || true)
        if [ -n "$remaining" ]; then
            echo "💀 Force killing remaining $description processes..."
            pkill -9 -f "$pattern" || true
        fi
        echo "✅ $description processes stopped"
    else
        echo "✅ No $description processes found"
    fi
}

# Stop duplicate backend processes
echo ""
echo "📡 Cleaning up Backend Services"
echo "--------------------------------"
safe_kill "uvicorn.*port.*3000" "Backend (port 3000)"
safe_kill "uvicorn.*port.*8000" "Backend (port 8000)"

# Stop duplicate frontend processes
echo ""
echo "🌐 Cleaning up Frontend Services"
echo "---------------------------------"
safe_kill "vite.*5173" "Frontend (port 5173)"
safe_kill "vite.*5176" "Frontend (port 5176)"
safe_kill "vite.*5178" "Frontend (port 5178)"

# Keep development example services (they have specific purposes)
echo ""
echo "🔧 Development Services Status"
echo "------------------------------"
echo "Keeping these development services (if running):"
echo "  - MCP Manager (port 5174)"
echo "  - Projects Manager (port 5175)"
echo "  - Midnight HUD (port 5177)"

# Clean up Docker state
echo ""
echo "🐳 Docker Cleanup"
echo "-----------------"
echo "🛑 Stopping Docker Compose services..."
cd /TaylorProjects/TaylorDashv1
docker-compose down || true

echo "🧽 Removing orphaned containers..."
docker container prune -f || true

echo "🗑️  Removing unused networks..."
docker network prune -f || true

# Verify port cleanup
echo ""
echo "🔍 Port Status Check"
echo "--------------------"
echo "Checking for remaining conflicts on key ports..."

check_port() {
    local port=$1
    local service=$2
    local result=$(netstat -tlnp 2>/dev/null | grep ":$port " || true)

    if [ -n "$result" ]; then
        echo "⚠️  Port $port ($service) still in use:"
        echo "   $result"
    else
        echo "✅ Port $port ($service) is free"
    fi
}

check_port "80" "HTTP"
check_port "443" "HTTPS"
check_port "3000" "Backend Dev"
check_port "5173" "Frontend Dev"
check_port "8000" "Backend Alt"
check_port "8080" "Traefik Dashboard"

# Final status report
echo ""
echo "📊 Cleanup Summary"
echo "==================="

echo "🐳 Docker Services:"
docker-compose ps || echo "   No services running"

echo ""
echo "🔄 Running Development Processes:"
ps aux | grep -E "(node.*vite|python.*uvicorn)" | grep -v grep || echo "   No development processes found"

echo ""
echo "🎉 Infrastructure cleanup complete!"
echo ""
echo "💡 Next Steps:"
echo "   1. Run 'scripts/start-development.sh' for development"
echo "   2. Run 'scripts/start-production.sh' for production"
echo "   3. Run 'scripts/health-check.sh' to verify status"