"""Supervisor/Registry System for Agent Communication"""
import logging
from typing import Dict, List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import config

# Setup logging
logging.basicConfig(level=config.LOG_LEVEL, format=config.LOG_FORMAT)
logger = logging.getLogger(__name__)


class AgentRegistration(BaseModel):
    """Model for agent registration"""
    agent_name: str
    agent_type: str
    host: str
    port: int
    version: str
    capabilities: List[str] = []


class AgentHeartbeat(BaseModel):
    """Model for agent heartbeat"""
    agent_name: str
    status: str
    timestamp: str


class SupervisorRegistry:
    """
    Registry that manages agent registrations and communication.
    Tracks available agents and their health status.
    """
    
    def __init__(self):
        self.agents: Dict[str, Dict] = {}
        logger.info("Supervisor Registry initialized")
    
    def register_agent(self, registration: AgentRegistration) -> Dict:
        """Register a new agent with the supervisor"""
        agent_id = f"{registration.agent_name}_{registration.port}"
        
        self.agents[agent_id] = {
            "agent_name": registration.agent_name,
            "agent_type": registration.agent_type,
            "host": registration.host,
            "port": registration.port,
            "version": registration.version,
            "capabilities": registration.capabilities,
            "status": "active",
            "registered_at": datetime.now().isoformat(),
            "last_heartbeat": datetime.now().isoformat()
        }
        
        logger.info(f"Agent registered: {agent_id}")
        return {
            "success": True,
            "agent_id": agent_id,
            "message": "Agent registered successfully"
        }
    
    def update_heartbeat(self, heartbeat: AgentHeartbeat) -> Dict:
        """Update agent heartbeat status"""
        agent_id = None
        for aid, agent in self.agents.items():
            if agent["agent_name"] == heartbeat.agent_name:
                agent_id = aid
                break
        
        if not agent_id:
            logger.warning(f"Heartbeat from unregistered agent: {heartbeat.agent_name}")
            raise HTTPException(status_code=404, detail="Agent not registered")
        
        self.agents[agent_id]["status"] = heartbeat.status
        self.agents[agent_id]["last_heartbeat"] = heartbeat.timestamp
        
        logger.debug(f"Heartbeat updated for: {agent_id}")
        return {"success": True, "message": "Heartbeat updated"}
    
    def get_agent(self, agent_name: str) -> Optional[Dict]:
        """Get agent information by name"""
        for agent in self.agents.values():
            if agent["agent_name"] == agent_name:
                return agent
        return None
    
    def list_agents(self) -> List[Dict]:
        """List all registered agents"""
        return list(self.agents.values())
    
    def deregister_agent(self, agent_name: str) -> Dict:
        """Deregister an agent"""
        agent_id = None
        for aid, agent in self.agents.items():
            if agent["agent_name"] == agent_name:
                agent_id = aid
                break
        
        if agent_id:
            del self.agents[agent_id]
            logger.info(f"Agent deregistered: {agent_id}")
            return {"success": True, "message": "Agent deregistered"}
        
        raise HTTPException(status_code=404, detail="Agent not found")


# Create FastAPI app for Supervisor
supervisor_app = FastAPI(title="Supervisor Registry", version="1.0.0")
registry = SupervisorRegistry()


@supervisor_app.post("/register")
async def register_agent(registration: AgentRegistration):
    """Register a new agent"""
    return registry.register_agent(registration)


@supervisor_app.post("/heartbeat")
async def agent_heartbeat(heartbeat: AgentHeartbeat):
    """Receive agent heartbeat"""
    return registry.update_heartbeat(heartbeat)


@supervisor_app.get("/agents")
async def list_agents():
    """List all registered agents"""
    return {"agents": registry.list_agents()}


@supervisor_app.get("/agents/{agent_name}")
async def get_agent(agent_name: str):
    """Get specific agent information"""
    agent = registry.get_agent(agent_name)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@supervisor_app.delete("/agents/{agent_name}")
async def deregister_agent(agent_name: str):
    """Deregister an agent"""
    return registry.deregister_agent(agent_name)


@supervisor_app.post("/messages")
async def receive_message(message: dict):
    """Receive messages from agents"""
    logger.info(f"Received message from {message.get('sender')}: {message.get('type')}")
    return {
        "success": True,
        "message": "Message received",
        "timestamp": datetime.now().isoformat()
    }


@supervisor_app.get("/health")
async def health_check():
    """Supervisor health check"""
    return {
        "status": "healthy",
        "service": "Supervisor Registry",
        "timestamp": datetime.now().isoformat(),
        "registered_agents": len(registry.agents)
    }

