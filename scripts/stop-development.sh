#!/bin/bash

# TaylorDash Development Environment Cleanup
# Stops all development services cleanly

set -e

echo "🛑 Stopping TaylorDash Development Environment..."

# Kill by saved PIDs first (clean shutdown)
if [ -f /tmp/taylordash/dev-pids.txt ]; then
    echo "🔍 Reading saved process IDs..."
    source /tmp/taylordash/dev-pids.txt

    echo "🔄 Stopping services gracefully..."

    # Stop in reverse dependency order
    [ ! -z "$PROJECTS_PID" ] && kill -TERM $PROJECTS_PID 2>/dev/null && echo "  ✅ Projects Manager stopped (PID: $PROJECTS_PID)"
    [ ! -z "$MIDNIGHT_PID" ] && kill -TERM $MIDNIGHT_PID 2>/dev/null && echo "  ✅ Midnight HUD stopped (PID: $MIDNIGHT_PID)"
    [ ! -z "$MCP_PID" ] && kill -TERM $MCP_PID 2>/dev/null && echo "  ✅ MCP Manager stopped (PID: $MCP_PID)"
    [ ! -z "$FRONTEND_PID" ] && kill -TERM $FRONTEND_PID 2>/dev/null && echo "  ✅ Frontend stopped (PID: $FRONTEND_PID)"
    [ ! -z "$BACKEND_PID" ] && kill -TERM $BACKEND_PID 2>/dev/null && echo "  ✅ Backend API stopped (PID: $BACKEND_PID)"

    # Give processes time to shut down gracefully
    sleep 3

    # Force kill any remaining processes
    [ ! -z "$PROJECTS_PID" ] && kill -KILL $PROJECTS_PID 2>/dev/null || true
    [ ! -z "$MIDNIGHT_PID" ] && kill -KILL $MIDNIGHT_PID 2>/dev/null || true
    [ ! -z "$MCP_PID" ] && kill -KILL $MCP_PID 2>/dev/null || true
    [ ! -z "$FRONTEND_PID" ] && kill -KILL $FRONTEND_PID 2>/dev/null || true
    [ ! -z "$BACKEND_PID" ] && kill -KILL $BACKEND_PID 2>/dev/null || true

    # Clean up PID file
    rm -f /tmp/taylordash/dev-pids.txt
    echo "  🗑️  Cleaned up PID file"
else
    echo "⚠️  No PID file found, using process name cleanup..."
fi

# Aggressive cleanup for any remaining processes
echo "🧹 Performing system-wide cleanup..."

# Kill any remaining TaylorDash development processes
pkill -f "npm run dev" 2>/dev/null && echo "  🔄 Killed remaining npm dev processes" || true
pkill -f "vite.*TaylorDash" 2>/dev/null && echo "  🔄 Killed remaining vite processes" || true
pkill -f "uvicorn.*app.main:app" 2>/dev/null && echo "  🔄 Killed remaining uvicorn processes" || true

# Kill processes by port (fallback)
lsof -ti :3000 2>/dev/null | xargs -r kill -9 && echo "  🔄 Freed port 3000" || true
lsof -ti :5173 2>/dev/null | xargs -r kill -9 && echo "  🔄 Freed port 5173" || true
lsof -ti :5174 2>/dev/null | xargs -r kill -9 && echo "  🔄 Freed port 5174" || true
lsof -ti :5175 2>/dev/null | xargs -r kill -9 && echo "  🔄 Freed port 5175" || true
lsof -ti :5176 2>/dev/null | xargs -r kill -9 && echo "  🔄 Freed port 5176" || true

echo ""
echo "🔍 Verifying cleanup..."

# Check if any TaylorDash processes are still running
if pgrep -f "TaylorDash\|uvicorn.*app.main\|vite.*5173\|vite.*5174\|vite.*5175\|vite.*5176" >/dev/null; then
    echo "⚠️  Some processes may still be running:"
    pgrep -f "TaylorDash\|uvicorn.*app.main\|vite.*5173\|vite.*5174\|vite.*5175\|vite.*5176" || true
else
    echo "✅ All TaylorDash development processes stopped"
fi

# Check if ports are freed
echo "🔍 Port status:"
for port in 3000 5173 5174 5175 5176; do
    if netstat -tuln 2>/dev/null | grep -q ":$port "; then
        echo "  ⚠️  Port $port still in use"
    else
        echo "  ✅ Port $port is free"
    fi
done

echo ""
echo "🎉 TaylorDash Development Environment cleanup complete!"
echo "💡 To restart cleanly, run: ./scripts/start-clean-development.sh"