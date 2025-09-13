# CURRENT_SYSTEM_STATE.md

## Service Chaos Analysis - Immediate Cleanup Required

**Analysis Date**: 2025-09-13
**System**: TaylorDash v1
**Issue**: Multiple redundant services, port conflicts, unmanaged processes

## Critical Findings

### 🔥 ACTIVE PORT CONFLICTS
- **Port 5173**: 2 services running simultaneously
- **Port 5177**: 2 services (IPv4 + IPv6 conflicts)
- **Backend APIs**: 2 instances (ports 3000 + 8000)
- **Frontend instances**: 5+ Vite dev servers active

### 📊 Current Port Inventory

#### Docker Infrastructure (Managed - ✅ CLEAN)
```
80/443    - Traefik (reverse proxy)
1883/8883 - Mosquitto MQTT
5432      - PostgreSQL
8080      - Traefik dashboard
8428      - VictoriaMetrics
9001      - MinIO console
```

#### Node.js Development Servers (❌ CHAOS)
```
PORT   PID      SERVICE                    STATUS
5173   531222   midnight-hud              ❌ DUPLICATE
5173   -        midnight-hud (intended)   ❌ CONFIG MISMATCH
5174   3450495  mcp-manager               ❌ REDUNDANT
5175   3451491  midnight-hud              ❌ WRONG PORT
5176   542638   frontend                  ❌ UNPLANNED
5177   3451555  projects-manager          ❌ DUPLICATE (IPv4)
5177   543930   mcp-manager               ❌ DUPLICATE (IPv6)
5178   3460401  frontend                  ❌ REDUNDANT
5179   3461579  frontend                  ❌ REDUNDANT
```

#### Backend Services (❌ CHAOS)
```
PORT   PID      SERVICE                   STATUS
3000   3499880  FastAPI (uvicorn)        ❌ MANUAL LAUNCH
8000   3615086  FastAPI (uvicorn)        ❌ DUPLICATE
8000   -        Docker backend           ✅ INTENDED
```

## Intended vs Actual Architecture

### 🎯 INTENDED SERVICE LAYOUT
```
Service               Port    Status
frontend             5173    ✅ Should be single instance
midnight-hud         5173    ❌ Port conflict with frontend
mcp-manager          5174    ✅ Correct
projects-manager     5175    ❌ Currently wrong assignment
backend              8000    ✅ Docker container only
```

### 🔥 ACTUAL RUNNING SERVICES
```
Service               Port    PID       Issue
frontend             5176    542638    Wrong port
frontend             5178    3460401   Duplicate #1
frontend             5179    3461579   Duplicate #2
midnight-hud         5173    531222    Conflicts with frontend
midnight-hud         5175    3451491   Wrong port
mcp-manager          5174    3450495   Multiple instances
mcp-manager          5177    543930    IPv6 binding issue
projects-manager     5177    3451555   Port conflict
backend              3000    3499880   Manual dev server
backend              8000    3615086   Duplicate of Docker
```

## Cleanup Priority Matrix

### 🚨 IMMEDIATE ACTIONS REQUIRED

#### Kill Redundant Processes
```bash
# Frontend duplicates
kill 3460401 3461579  # ports 5178, 5179

# Backend manual instance
kill 3499880         # port 3000

# Service conflicts
kill 531222 3451491  # midnight-hud wrong ports
kill 3450495         # mcp-manager duplicate
```

#### Port Reassignments Needed
```
Current → Target
5176 → 5173  (frontend)
5175 → 5173  (midnight-hud, when frontend moves)
5177 → 5175  (projects-manager)
```

### ⚙️ ROOT CAUSE ANALYSIS

#### Configuration Mismatches
- `frontend/vite.config.ts`: Specifies port 5173, running on 5176+
- `midnight-hud/vite.config.ts`: Port 5173, conflicts with frontend
- Multiple manual `vite --port` overrides active

#### Process Management Issues
- No central process manager
- Manual terminal launches not tracked
- Background processes accumulating
- No automatic cleanup on restart

#### Development Workflow Problems
- `npm run dev` conflicts with Docker services
- Port auto-increment causing drift
- Multiple developers/sessions creating conflicts

## Recommended Service Architecture

### 🎯 CLEAN TARGET STATE
```
Service              Port    Access
frontend            5173    Primary UI
midnight-hud        5174    HUD interface
mcp-manager         5175    MCP tools
projects-manager    5176    Project tools
backend (docker)    8000    API (Docker only)
backend (dev)       3000    API (dev override only)
```

### 📝 Implementation Plan

#### Phase 1: Emergency Cleanup
1. Kill all redundant Node processes
2. Stop conflicting manual services
3. Verify Docker services remain healthy

#### Phase 2: Port Standardization
1. Update all vite.config.ts files
2. Create port allocation docs
3. Add port conflict detection

#### Phase 3: Process Management
1. Implement PM2 or similar
2. Create start/stop scripts
3. Add health monitoring

## Immediate Commands

### Emergency Cleanup
```bash
# Kill chaos processes
pkill -f "vite.*host.*0.0.0.0"
pkill -f "uvicorn.*port.*3000"

# Verify Docker stack health
docker-compose ps --services --filter "status=running"
```

### Service Restart (Clean)
```bash
# Start services in correct order
cd frontend && npm run dev &          # port 5173
cd examples/midnight-hud && npm run dev -- --port 5174 &
cd examples/mcp-manager && npm run dev -- --port 5175 &
cd examples/projects-manager && npm run dev -- --port 5176 &
```

## Security Implications

### 🔒 CURRENT RISKS
- Untracked processes with network access
- Multiple API endpoints (authentication bypass risk)
- Port exhaustion potential
- Resource consumption from duplicates

### ✅ POST-CLEANUP BENEFITS
- Single source of truth per service
- Predictable port allocation
- Resource optimization
- Clear service boundaries

---

**Next Steps**: Execute emergency cleanup, then implement systematic port management and process controls.