"""Pydantic models for agent communication"""
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime


class SurveyRequest(BaseModel):
    """Request model for survey analysis"""
    user_id: str = Field(..., description="Unique user identifier")
    recent_activity: str = Field(..., description="Description of recent user activity")
    last_purchase: Optional[str] = Field("", description="Last product purchased")
    last_survey_date: Optional[str] = Field(None, description="Date of last survey (ISO format)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "recent_activity": "Support chat with negative sentiment",
                "last_purchase": "Wireless Earbuds",
                "last_survey_date": "2025-09-20"
            }
        }


class SurveyResponse(BaseModel):
    """Response model for survey decision"""
    survey_trigger: bool
    survey_type: Optional[str] = None
    priority: Optional[str] = None
    reason: str
    questions: Optional[List[str]] = None
    timestamp: str


class AgentMessage(BaseModel):
    """Generic message model for agent communication"""
    message_id: str
    sender: str
    recipient: str
    type: str
    timestamp: str
    payload: Optional[dict] = None


class TaskAssignment(BaseModel):
    """Task assignment from supervisor to worker"""
    message_id: str
    sender: str
    recipient: str
    type: str = "task_assignment"
    task: dict
    timestamp: str


class CompletionReport(BaseModel):
    """Completion report from worker to supervisor"""
    message_id: str
    sender: str
    recipient: str
    type: str = "completion_report"
    related_message_id: str
    status: str  # SUCCESS or FAILURE
    results: dict
    timestamp: str


class AgentRegistration(BaseModel):
    """Model for agent registration with supervisor"""
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

