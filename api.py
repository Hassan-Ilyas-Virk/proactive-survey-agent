"""HTTP API for Proactive Survey Agent"""
import logging
import sys
import os
from typing import Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException
import httpx
from contextlib import asynccontextmanager

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.workers.proactive_survey_agent import ProactiveSurveyAgent
from communication.models import SurveyRequest, SurveyResponse, AgentRegistration
from shared.utils import load_json_config, get_timestamp

# Load configuration
config = load_json_config("config/agent_config.json")

# Setup logging
log_config = config.get("logging", {})
logging.basicConfig(
    level=getattr(logging, log_config.get("level", "INFO")),
    format=log_config.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger = logging.getLogger(__name__)


# Agent instance
agent = ProactiveSurveyAgent()


async def register_with_supervisor():
    """Register this agent with the supervisor"""
    supervisor_config = config.get("supervisor", {})
    if not supervisor_config.get("auto_register", True):
        return
    
    supervisor_url = f"http://{supervisor_config.get('host', 'localhost')}:{supervisor_config.get('port', 8000)}"
    
    try:
        async with httpx.AsyncClient() as client:
            network_config = config.get("network", {})
            registration_data = {
                "agent_name": config.get("agent_name", "ProactiveSurveyAgent"),
                "agent_type": config.get("agent_type", "survey_agent"),
                "host": network_config.get("host", "localhost"),
                "port": network_config.get("port", 8001),
                "version": config.get("version", "1.0.0"),
                "capabilities": config.get("capabilities", [])
            }
            
            response = await client.post(
                f"{supervisor_url}/register",
                json=registration_data,
                timeout=5.0
            )
            
            if response.status_code == 200:
                logger.info("Successfully registered with Supervisor")
            else:
                logger.warning(f"Failed to register with Supervisor: {response.status_code}")
    except Exception as e:
        logger.warning(f"Could not connect to Supervisor: {e}")


async def send_heartbeat():
    """Send heartbeat to supervisor"""
    supervisor_config = config.get("supervisor", {})
    supervisor_url = f"http://{supervisor_config.get('host', 'localhost')}:{supervisor_config.get('port', 8000)}"
    
    try:
        async with httpx.AsyncClient() as client:
            heartbeat_data = {
                "agent_name": config.get("agent_name", "ProactiveSurveyAgent"),
                "status": "healthy",
                "timestamp": get_timestamp()
            }
            
            await client.post(
                f"{supervisor_url}/heartbeat",
                json=heartbeat_data,
                timeout=5.0
            )
    except Exception as e:
        logger.debug(f"Heartbeat failed: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management - startup and shutdown"""
    # Startup
    agent_name = config.get("agent_name", "ProactiveSurveyAgent")
    logger.info(f"Starting {agent_name}")
    await register_with_supervisor()
    yield
    # Shutdown
    logger.info(f"Shutting down {agent_name}")


# Create FastAPI app
app = FastAPI(
    title=config.get("agent_name", "Proactive Survey Agent"),
    description=config.get("description", "AI Agent that analyzes user interactions and triggers personalized surveys"),
    version=config.get("version", "1.0.0"),
    lifespan=lifespan
)


@app.post("/analyze", response_model=SurveyResponse)
async def analyze_user(request: SurveyRequest):
    """
    Analyze user data and determine if a survey should be triggered.
    
    This endpoint processes user activity, sentiment, and history to make
    intelligent decisions about survey timing and content.
    """
    try:
        logger.info(f"Received analyze request for user: {request.user_id}")
        
        # Convert request to dict for processing
        request_data = request.model_dump()
        
        # Process through agent
        result = agent.analyze_request(request_data)
        
        # Send heartbeat to supervisor after successful operation
        await send_heartbeat()
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    Returns agent status and system information.
    """
    status = agent.get_status()
    status["api_version"] = config.get("version", "1.0.0")
    return status


@app.get("/status")
async def get_status():
    """
    Detailed status endpoint with system metrics.
    """
    business_logic = config.get("business_logic", {})
    return {
        "agent_name": config.get("agent_name", "ProactiveSurveyAgent"),
        "version": config.get("version", "1.0.0"),
        "status": "operational",
        "timestamp": get_timestamp(),
        "configuration": {
            "min_days_between_surveys": business_logic.get("survey_cooldown_days", 30),
            "supported_survey_types": business_logic.get("survey_types", []),
            "priority_levels": business_logic.get("priority_levels", [])
        }
    }


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": config.get("agent_name", "Proactive Survey Agent"),
        "version": config.get("version", "1.0.0"),
        "type": config.get("agent_type", "survey_agent"),
        "status": "running",
        "capabilities": config.get("capabilities", []),
        "endpoints": {
            "analyze": "/analyze (POST) - Analyze user and trigger surveys",
            "health": "/health (GET) - Health check",
            "status": "/status (GET) - Detailed status",
            "docs": "/docs (GET) - Interactive API documentation"
        }
    }

