"""Communication protocol constants and enums"""
from enum import Enum


class MessageType(Enum):
    """Enum for message types between agents"""
    TASK_ASSIGNMENT = "task_assignment"
    COMPLETION_REPORT = "completion_report"
    AGENT_REGISTRATION = "agent_registration"
    HEARTBEAT = "heartbeat"
    STATUS_REQUEST = "status_request"
    STATUS_RESPONSE = "status_response"
    ERROR = "error"


class TaskStatus(Enum):
    """Enum for task execution status"""
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    IN_PROGRESS = "IN_PROGRESS"
    PENDING = "PENDING"


class AgentStatus(Enum):
    """Enum for agent health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    OFFLINE = "offline"


class SurveyType(Enum):
    """Enum for survey types"""
    PRODUCT_EXPERIENCE = "Product Experience"
    SUPPORT_QUALITY = "Support Quality"
    GENERAL_FEEDBACK = "General Feedback"
    ENGAGEMENT = "Engagement Check"


class Priority(Enum):
    """Enum for priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


# Protocol Constants
PROTOCOL_VERSION = "1.0"
DEFAULT_TIMEOUT = 30  # seconds
MAX_RETRIES = 3

