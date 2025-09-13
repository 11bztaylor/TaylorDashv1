"""
MCP (Model Context Protocol) proxy router for TaylorDash backend.
Handles communication with MCP servers via stdio and provides HTTP API.
"""

import json
import subprocess
import asyncio
import logging
import signal
import weakref
import atexit
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from .auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mcp", tags=["MCP"])

# Global process cleanup registry
_process_registry = weakref.WeakSet()

# Process locks for thread safety
_process_locks: Dict[str, asyncio.Lock] = {}

class MCPProcess:
    """Managed MCP subprocess with proper resource cleanup."""
    
    def __init__(self, server_id: str, command: List[str]):
        self.server_id = server_id
        self.command = command
        self.process: Optional[subprocess.Popen] = None
        self._cleanup_registered = False
    
    async def start(self) -> subprocess.Popen:
        """Start the MCP process with proper cleanup registration."""
        if self.process and self.process.poll() is None:
            return self.process
        
        try:
            self.process = subprocess.Popen(
                self.command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                preexec_fn=None  # Don't set process group to avoid zombie processes
            )
            
            # Register for cleanup
            if not self._cleanup_registered:
                _process_registry.add(self.process)
                self._cleanup_registered = True
            
            logger.info(f"Started MCP process {self.server_id} with PID {self.process.pid}")
            return self.process
            
        except Exception as e:
            logger.error(f"Failed to start MCP process {self.server_id}: {e}")
            await self.cleanup()
            raise
    
    async def cleanup(self, timeout: float = 5.0):
        """Cleanup process with timeout and force kill if needed."""
        if not self.process:
            return
        
        try:
            if self.process.poll() is None:  # Still running
                logger.info(f"Terminating MCP process {self.server_id} (PID {self.process.pid})")
                self.process.terminate()
                
                try:
                    # Wait for graceful shutdown
                    self.process.wait(timeout=timeout)
                except subprocess.TimeoutExpired:
                    # Force kill if needed
                    logger.warning(f"Force killing MCP process {self.server_id} (PID {self.process.pid})")
                    self.process.kill()
                    self.process.wait()  # This should return immediately after kill
                    
            # Close file descriptors to prevent leaks
            if self.process.stdin:
                self.process.stdin.close()
            if self.process.stdout:
                self.process.stdout.close()
            if self.process.stderr:
                self.process.stderr.close()
                
        except Exception as e:
            logger.error(f"Error during MCP process cleanup {self.server_id}: {e}")
        finally:
            self.process = None
            self._cleanup_registered = False
    
    def is_alive(self) -> bool:
        """Check if process is still alive."""
        return self.process is not None and self.process.poll() is None

# Emergency cleanup function
def _emergency_cleanup():
    """Emergency cleanup for process registry on exit."""
    for process in list(_process_registry):
        try:
            if process and process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
        except:
            pass

# Register emergency cleanup
atexit.register(_emergency_cleanup)

# MCP Server configurations
MCP_SERVERS = {
    "homelab-mcp": {
        "name": "Home Lab MCP",
        "description": "MCP server for managing home lab infrastructure", 
        "command": ["node", "/home/zach/home-ops/mcp-homelab-server/src/server.js"],
        "status": "offline",
        "last_health_check": None,
        "metrics": {"requests": 0, "errors": 0, "start_time": None}
    },
    "unifi-network-mcp": {
        "name": "UniFi Network MCP",
        "description": "UniFi Controller integration for network management",
        "command": ["python", "/home/zach/home-ops/unifi-network-mcp/main.py"],
        "status": "offline", 
        "last_health_check": None,
        "metrics": {"requests": 0, "errors": 0, "start_time": None}
    }
}

# Active MCP server processes with proper resource management
active_processes: Dict[str, MCPProcess] = {}

# Initialize locks for each server
for server_id in MCP_SERVERS.keys():
    _process_locks[server_id] = asyncio.Lock()

class MCPConnectRequest(BaseModel):
    serverId: str
    endpoint: str

class MCPRequest(BaseModel):
    serverId: str
    request: Dict[str, Any]

class MCPToolCall(BaseModel):
    serverId: str
    toolName: str
    args: Dict[str, Any]

@router.get("/servers")
async def list_mcp_servers(current_user: Optional[dict] = Depends(get_current_user)):
    """List all configured MCP servers and their status."""
    
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    servers = []
    for server_id, config in MCP_SERVERS.items():
        # Check if process is still running with thread safety
        async with _process_locks[server_id]:
            if server_id in active_processes:
                mcp_process = active_processes[server_id]
                if mcp_process.is_alive():
                    config["status"] = "online"
                else:
                    config["status"] = "offline"
                    await mcp_process.cleanup()
                    del active_processes[server_id]
        
        servers.append({
            "id": server_id,
            "name": config["name"],
            "description": config["description"],
            "status": config["status"],
            "lastHealthCheck": config["last_health_check"],
            "metrics": config["metrics"]
        })
    
    return {"servers": servers}

@router.post("/connect")
async def connect_mcp_server(request: MCPConnectRequest, current_user: Optional[dict] = Depends(get_current_user)):
    """Connect to an MCP server and start the process if needed."""
    
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    server_id = request.serverId
    
    if server_id not in MCP_SERVERS:
        raise HTTPException(status_code=404, detail=f"MCP server {server_id} not found")
    
    # Input validation to prevent injection
    if not server_id.replace('-', '').replace('_', '').isalnum():
        raise HTTPException(status_code=400, detail="Invalid server ID format")
    
    config = MCP_SERVERS[server_id]
    
    # Use lock to prevent race conditions
    async with _process_locks[server_id]:
        try:
            # Check if already running
            if server_id in active_processes:
                mcp_process = active_processes[server_id]
                if mcp_process.is_alive():
                    logger.info(f"MCP server {server_id} already running")
                    return {
                        "status": "connected",
                        "serverId": server_id,
                        "version": "1.0.0"
                    }
                else:
                    # Clean up dead process
                    await mcp_process.cleanup()
                    del active_processes[server_id]
            
            # Start the MCP server process with proper resource management
            logger.info(f"Starting MCP server: {server_id}")
            
            mcp_process = MCPProcess(server_id, config["command"])
            await mcp_process.start()
            
            active_processes[server_id] = mcp_process
            config["status"] = "online"
            config["metrics"]["start_time"] = datetime.now()
            config["last_health_check"] = datetime.now()
            
            logger.info(f"MCP server {server_id} started successfully")
            
            return {
                "status": "connected",
                "serverId": server_id,
                "version": "1.0.0"
            }
            
        except Exception as e:
            logger.error(f"Failed to connect to MCP server {server_id}: {str(e)}")
            config["status"] = "error"
            config["metrics"]["errors"] += 1
            
            # Ensure cleanup on failure
            if server_id in active_processes:
                try:
                    await active_processes[server_id].cleanup()
                    del active_processes[server_id]
                except:
                    pass
            
            raise HTTPException(status_code=500, detail=f"Failed to connect to server: {str(e)}")

async def _safe_read_with_timeout(process: subprocess.Popen, timeout: float) -> str:
    """Safely read from process stdout with timeout and deadlock prevention."""
    try:
        # Use asyncio.create_subprocess_exec would be better, but since we already have Popen,
        # we need to work with what we have. This approach is safer than run_in_executor.
        import select
        import sys
        
        if sys.platform == 'win32':
            # Windows doesn't support select on pipes, fall back to threading approach
            # but with much shorter timeout to reduce deadlock risk
            response_line = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(None, process.stdout.readline),
                timeout=timeout
            )
        else:
            # Unix systems: use select to avoid blocking
            deadline = asyncio.get_event_loop().time() + timeout
            
            while asyncio.get_event_loop().time() < deadline:
                ready, _, _ = select.select([process.stdout], [], [], 0.1)
                if ready:
                    response_line = process.stdout.readline()
                    break
                await asyncio.sleep(0.01)  # Small yield to event loop
            else:
                raise asyncio.TimeoutError()
        
        return response_line
        
    except Exception as e:
        logger.error(f"Error in safe read: {e}")
        raise

@router.post("/request")
async def send_mcp_request(request: MCPRequest, current_user: Optional[dict] = Depends(get_current_user)):
    """Send a request to an MCP server and return the response."""
    
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    server_id = request.serverId
    
    if server_id not in MCP_SERVERS:
        raise HTTPException(status_code=404, detail=f"MCP server {server_id} not found")
    
    # Input validation to prevent injection
    if not server_id.replace('-', '').replace('_', '').isalnum():
        raise HTTPException(status_code=400, detail="Invalid server ID format")
    
    # Validate JSON request structure to prevent injection
    try:
        # Ensure request.request is valid JSON-serializable
        json.dumps(request.request)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid request format")
    
    # Use lock to prevent race conditions in communication
    async with _process_locks[server_id]:
        if server_id not in active_processes:
            raise HTTPException(status_code=400, detail=f"MCP server {server_id} not connected")
        
        mcp_process = active_processes[server_id]
        
        if not mcp_process.is_alive():
            # Process died, clean up
            await mcp_process.cleanup()
            del active_processes[server_id]
            MCP_SERVERS[server_id]["status"] = "offline"
            raise HTTPException(status_code=400, detail=f"MCP server {server_id} process died")
        
        process = mcp_process.process
        
        try:
            # Send request to MCP server
            request_json = json.dumps(request.request) + "\n"
            logger.debug(f"Sending MCP request to {server_id}: {request_json.strip()}")
            
            # Validate request size to prevent DoS
            if len(request_json) > 1024 * 1024:  # 1MB limit
                raise HTTPException(status_code=413, detail="Request too large")
            
            process.stdin.write(request_json)
            process.stdin.flush()
            
            # Read response with safer timeout mechanism
            try:
                response_line = await _safe_read_with_timeout(process, 30.0)
                
                if not response_line or not response_line.strip():
                    raise HTTPException(status_code=500, detail="MCP server closed connection")
                
                response = json.loads(response_line.strip())
                logger.debug(f"Received MCP response from {server_id}: {response}")
                
                # Update metrics
                MCP_SERVERS[server_id]["metrics"]["requests"] += 1
                MCP_SERVERS[server_id]["last_health_check"] = datetime.now()
                
                return response
                
            except asyncio.TimeoutError:
                logger.error(f"MCP server {server_id} request timed out")
                MCP_SERVERS[server_id]["metrics"]["errors"] += 1
                
                # Mark process as potentially dead after timeout
                try:
                    await mcp_process.cleanup()
                    del active_processes[server_id] 
                    MCP_SERVERS[server_id]["status"] = "offline"
                except:
                    pass
                
                raise HTTPException(status_code=504, detail="MCP server request timed out")
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from MCP server {server_id}: {str(e)}")
            MCP_SERVERS[server_id]["metrics"]["errors"] += 1
            raise HTTPException(status_code=500, detail="Invalid response from MCP server")
        
        except BrokenPipeError:
            logger.error(f"Broken pipe communicating with MCP server {server_id}")
            MCP_SERVERS[server_id]["metrics"]["errors"] += 1
            
            # Clean up broken process
            try:
                await mcp_process.cleanup()
                del active_processes[server_id]
                MCP_SERVERS[server_id]["status"] = "offline"
            except:
                pass
                
            raise HTTPException(status_code=500, detail="MCP server connection broken")
        
        except Exception as e:
            logger.error(f"Error communicating with MCP server {server_id}: {str(e)}")
            MCP_SERVERS[server_id]["metrics"]["errors"] += 1
            raise HTTPException(status_code=500, detail=f"MCP communication error: {str(e)}")

@router.get("/health/{server_id}")
async def check_mcp_health(server_id: str, current_user: Optional[dict] = Depends(get_current_user)):
    """Check the health status of an MCP server."""
    
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if server_id not in MCP_SERVERS:
        raise HTTPException(status_code=404, detail=f"MCP server {server_id} not found")
    
    # Input validation to prevent injection
    if not server_id.replace('-', '').replace('_', '').isalnum():
        raise HTTPException(status_code=400, detail="Invalid server ID format")
    
    config = MCP_SERVERS[server_id]
    
    # Check process status with thread safety
    async with _process_locks[server_id]:
        if server_id in active_processes:
            mcp_process = active_processes[server_id]
            if mcp_process.is_alive():
                config["status"] = "online"
                config["last_health_check"] = datetime.now()
                return {"status": "online"}
            else:
                # Process died - clean up
                await mcp_process.cleanup()
                del active_processes[server_id]
                config["status"] = "offline"
    
    return {"status": config["status"]}

@router.get("/metrics/{server_id}")
async def get_mcp_metrics(server_id: str, current_user: Optional[dict] = Depends(get_current_user)):
    """Get metrics for an MCP server."""
    
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if server_id not in MCP_SERVERS:
        raise HTTPException(status_code=404, detail=f"MCP server {server_id} not found")
    
    # Input validation to prevent injection
    if not server_id.replace('-', '').replace('_', '').isalnum():
        raise HTTPException(status_code=400, detail="Invalid server ID format")
    
    config = MCP_SERVERS[server_id]
    metrics = config["metrics"].copy()
    
    # Calculate uptime
    if metrics["start_time"]:
        uptime_delta = datetime.now() - metrics["start_time"]
        days = uptime_delta.days
        hours, remainder = divmod(uptime_delta.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        if days > 0:
            metrics["uptime"] = f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            metrics["uptime"] = f"{hours}h {minutes}m"
        else:
            metrics["uptime"] = f"{minutes}m"
    else:
        metrics["uptime"] = "0m"
    
    # Remove internal fields
    metrics.pop("start_time", None)
    
    return metrics

@router.post("/disconnect/{server_id}")
async def disconnect_mcp_server(server_id: str, current_user: Optional[dict] = Depends(get_current_user)):
    """Disconnect from an MCP server and stop the process."""
    
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if server_id not in MCP_SERVERS:
        raise HTTPException(status_code=404, detail=f"MCP server {server_id} not found")
    
    # Input validation to prevent injection
    if not server_id.replace('-', '').replace('_', '').isalnum():
        raise HTTPException(status_code=400, detail="Invalid server ID format")
    
    # Use lock to prevent race conditions during shutdown
    async with _process_locks[server_id]:
        if server_id in active_processes:
            try:
                mcp_process = active_processes[server_id]
                await mcp_process.cleanup()
                
                del active_processes[server_id]
                MCP_SERVERS[server_id]["status"] = "offline"
                
                logger.info(f"MCP server {server_id} disconnected")
                
            except Exception as e:
                logger.error(f"Error disconnecting MCP server {server_id}: {str(e)}")
                
                # Force cleanup even on error
                try:
                    del active_processes[server_id]
                    MCP_SERVERS[server_id]["status"] = "offline"
                except:
                    pass
                    
                raise HTTPException(status_code=500, detail=f"Failed to disconnect: {str(e)}")
    
    return {"status": "disconnected"}

# Cleanup function to be called on app shutdown
async def cleanup_mcp_processes():
    """Clean up all active MCP server processes."""
    
    logger.info("Cleaning up MCP server processes...")
    
    cleanup_tasks = []
    for server_id, mcp_process in active_processes.items():
        try:
            logger.info(f"Terminating MCP server: {server_id}")
            cleanup_tasks.append(mcp_process.cleanup())
        except Exception as e:
            logger.error(f"Error initiating cleanup for MCP server {server_id}: {str(e)}")
    
    # Wait for all cleanups to complete with timeout
    if cleanup_tasks:
        try:
            await asyncio.wait_for(asyncio.gather(*cleanup_tasks, return_exceptions=True), timeout=10.0)
        except asyncio.TimeoutError:
            logger.warning("Some MCP process cleanups timed out")
    
    active_processes.clear()
    
    # Reset all server statuses
    for config in MCP_SERVERS.values():
        config["status"] = "offline"