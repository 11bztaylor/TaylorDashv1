# MQTT Broker (Mosquitto)

## 🎯 Purpose
Eclipse Mosquitto MQTT broker for real-time messaging between backend services, plugins, and frontend clients.

## 📁 Contents
- **Configuration Files:**
  - Mosquitto broker configuration
  - Authentication and authorization setup
  - TLS/SSL certificate configuration
  - Client connection settings

## 🔧 Common Tasks
- **Start broker**: `docker-compose up mosquitto -d`
- **Test connection**: Use MQTT client tools
- **Monitor connections**: Check broker logs and statistics
- **Manage topics**: Configure topic permissions and routing
- **Update credentials**: Modify authentication configuration

## 🔗 Dependencies
- Depends on: Docker, network configuration, certificates
- Used by: Backend MQTT client, real-time frontend updates
- Integrates with: WebSocket bridge, plugin messaging

## 💡 Quick Start for AI Agents
When working in this directory:
1. Configure proper authentication for MQTT clients
2. Set up topic-based permissions for security
3. Use TLS encryption for production deployment
4. Monitor connection counts and message throughput
5. Implement proper QoS levels for message delivery

## ⚠️ Important Notes
- All MQTT connections require authentication
- Use topic-based access control for security
- Monitor broker performance and memory usage
- Configure retention policies for persistent messages