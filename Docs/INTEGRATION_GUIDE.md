# Proactive Survey Agent - Integration Guide

This guide is for integrators who need to combine this worker agent with other agents in a multi-agent system.

## 📦 Worker Agent Overview

**Agent Name:** ProactiveSurveyAgent  
**Type:** `survey_agent`  
**Version:** 1.0.0  
**Language:** Python 3.8+

### Capabilities
- `survey_analysis` - Analyzes user behavior for survey triggers
- `sentiment_detection` - Detects positive/negative/neutral sentiment
- `pattern_recognition` - Identifies purchase and engagement patterns
- `feedback_generation` - Generates personalized survey questions
- `user_profiling` - Tracks user survey history

## 🏗️ Architecture

### Inheritance Structure
```
AbstractWorkerAgent (agents/worker_base.py)
    ↓
ProactiveSurveyAgent (agents/workers/proactive_survey_agent.py)
```

### Key Components

1. **AbstractWorkerAgent** (`agents/worker_base.py`)
   - Base class that ALL workers must inherit from
   - Provides: LTM, messaging, task execution protocol
   - Abstract methods: `process_task()`, `send_message()`, `write_to_ltm()`, `read_from_ltm()`

2. **ProactiveSurveyAgent** (`agents/workers/proactive_survey_agent.py`)
   - Implements survey analysis business logic
   - Uses file-based LTM storage
   - Communicates via HTTP and message queue

3. **Communication Models** (`communication/models.py`)
   - Pydantic models for type-safe messaging
   - Standard message formats for inter-agent communication

4. **Configuration** (`config/`)
   - `agent_config.json` - Agent-specific settings
   - `settings.yaml` - Shared system settings

## 🔌 Integration Methods

### Method 1: HTTP API Integration (Recommended for Multi-Agent Systems)

The agent exposes a REST API that can be called by other agents or a supervisor.

```python
import httpx

# Call the agent
async def call_survey_agent(user_data):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8001/analyze",
            json={
                "user_id": "user123",
                "recent_activity": "Support chat with negative sentiment",
                "last_purchase": "Wireless Earbuds",
                "last_survey_date": "2025-09-20"
            }
        )
        return response.json()
```

**Endpoints:**
- `POST /analyze` - Main analysis endpoint
- `GET /health` - Health check
- `GET /status` - Detailed status
- `GET /docs` - Interactive API documentation

### Method 2: Direct Python Import

For same-process integration:

```python
from agents.workers.proactive_survey_agent import ProactiveSurveyAgent

# Initialize agent
agent = ProactiveSurveyAgent(
    agent_id="proactive_survey_001",
    supervisor_id="MainSupervisor"
)

# Use the agent
task_data = {
    "user_id": "user123",
    "recent_activity": "Support chat",
    "last_purchase": "Earbuds",
    "last_survey_date": None
}

result = agent.process_task(task_data)
```

### Method 3: Message-Based Communication

Using the AbstractWorkerAgent protocol:

```python
import json

# Send task via message
message = {
    "message_id": "task_123",
    "sender": "Supervisor",
    "recipient": "ProactiveSurveyAgent",
    "type": "task_assignment",
    "task": {
        "name": "analyze_user",
        "parameters": {
            "user_id": "user123",
            "recent_activity": "...",
            "last_purchase": "...",
            "last_survey_date": None
        }
    }
}

agent.handle_incoming_message(json.dumps(message))

# Agent will automatically:
# 1. Execute the task
# 2. Send completion report back to sender
```

## 📋 Contract Specification

### Input Contract

```json
{
  "user_id": "string (required)",
  "recent_activity": "string (required)",
  "last_purchase": "string (optional)",
  "last_survey_date": "string (optional, ISO format: YYYY-MM-DD)"
}
```

### Output Contract

```json
{
  "survey_trigger": "boolean",
  "survey_type": "string (if triggered)",
  "priority": "string (low|medium|high|urgent)",
  "reason": "string",
  "questions": ["array", "of", "strings"],
  "timestamp": "string (ISO format)"
}
```

### Example

**Request:**
```json
{
  "user_id": "user123",
  "recent_activity": "Support chat with negative sentiment",
  "last_purchase": "Wireless Earbuds",
  "last_survey_date": "2025-09-20"
}
```

**Response:**
```json
{
  "survey_trigger": true,
  "survey_type": "Product Experience",
  "priority": "high",
  "reason": "Negative sentiment after purchase",
  "questions": [
    "How satisfied are you with your product?",
    "Was your issue resolved effectively?"
  ],
  "timestamp": "2025-11-20T10:30:00.123456"
}
```

## 🔧 Configuration

### Port Configuration
Edit `config/agent_config.json`:
```json
{
  "network": {
    "host": "localhost",
    "port": 8001
  }
}
```

### Supervisor Configuration
```json
{
  "supervisor": {
    "id": "SupervisorRegistry",
    "host": "localhost",
    "port": 8000,
    "auto_register": true,
    "heartbeat_interval": 60
  }
}
```

### LTM Storage Configuration
```json
{
  "ltm_config": {
    "storage_type": "file",
    "base_directory": "shared/LTM/ProactiveSurveyAgent",
    "max_entries": 10000
  }
}
```

## 📁 File Structure for Integration

When integrating, you need these files:

```
/your-multi-agent-system
├── /agents
│   ├── worker_base.py              # Required - Base class
│   └── /workers
│       ├── __init__.py
│       └── proactive_survey_agent.py  # The worker
├── /communication
│   ├── models.py                   # Message models
│   └── protocol.py                 # Protocol constants
├── /config
│   ├── agent_config.json           # Agent config
│   └── settings.yaml               # System settings
├── /shared
│   ├── utils.py                    # Utility functions
│   └── /LTM
│       └── /ProactiveSurveyAgent   # LTM storage
├── api.py                          # FastAPI server (if using HTTP)
├── main.py                         # Entry point
└── requirements.txt                # Dependencies
```

## 🚀 Deployment Options

### Option 1: Standalone Service
```bash
# Run as independent microservice
python main.py
# or
uvicorn api:app --host 0.0.0.0 --port 8001
```

### Option 2: Integrated with Supervisor
```python
# In your supervisor code
from agents.workers.proactive_survey_agent import ProactiveSurveyAgent

# Register worker
survey_agent = ProactiveSurveyAgent(
    agent_id="survey_001",
    supervisor_id="MainSupervisor"
)

# Supervisor assigns tasks
task_result = survey_agent.process_task(task_data)
```

### Option 3: Docker Container
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8001
CMD ["python", "main.py"]
```

## 🔄 Message Protocol

### Task Assignment (Supervisor → Worker)
```json
{
  "message_id": "uuid",
  "sender": "SupervisorID",
  "recipient": "ProactiveSurveyAgent",
  "type": "task_assignment",
  "task": {
    "name": "analyze_user",
    "parameters": { /* task data */ }
  },
  "timestamp": "ISO-8601"
}
```

### Completion Report (Worker → Supervisor)
```json
{
  "message_id": "uuid",
  "sender": "ProactiveSurveyAgent",
  "recipient": "SupervisorID",
  "type": "completion_report",
  "related_message_id": "original_task_id",
  "status": "SUCCESS",
  "results": { /* task results */ },
  "timestamp": "ISO-8601"
}
```

### Heartbeat (Worker → Supervisor)
```json
{
  "agent_name": "ProactiveSurveyAgent",
  "status": "healthy",
  "timestamp": "ISO-8601"
}
```

## 🧪 Testing the Agent

```python
# Test script
from agents.workers.proactive_survey_agent import ProactiveSurveyAgent

agent = ProactiveSurveyAgent()

# Test case 1: Negative sentiment
result = agent.process_task({
    "user_id": "test_001",
    "recent_activity": "Support chat - issue not resolved",
    "last_purchase": "Headphones",
    "last_survey_date": None
})

print(result)
# Expected: survey_trigger=True, priority=high

# Test case 2: Survey cooldown
result = agent.process_task({
    "user_id": "test_002",
    "recent_activity": "Browsing",
    "last_purchase": "",
    "last_survey_date": "2025-11-19"  # Yesterday
})

print(result)
# Expected: survey_trigger=False (cooldown active)
```

## 📊 Monitoring & Health Checks

### Health Check
```bash
curl http://localhost:8001/health
```

### Status
```bash
curl http://localhost:8001/status
```

### Check LTM Storage
```python
agent = ProactiveSurveyAgent()
print(f"LTM Keys: {len(agent.ltm.list_keys())}")
```

### Check Message Queue
```python
queued = agent.get_queued_messages()
print(f"Queued messages: {len(queued)}")
```

## ⚠️ Important Notes for Integration

1. **Port Conflicts**: Ensure port 8001 is available or configure a different port
2. **LTM Storage**: The agent creates `shared/LTM/ProactiveSurveyAgent/` directory for storage
3. **Dependencies**: Install all requirements from `requirements.txt`
4. **Python Version**: Requires Python 3.8 or higher
5. **Supervisor Optional**: The agent works standalone without a supervisor

## 🔐 Dependencies

```
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
httpx==0.25.1
python-dateutil==2.8.2
pytest==7.4.3
pytest-asyncio==0.21.1
pyyaml==6.0.1
```

## 📞 Agent Communication Examples

### Calling from Another Worker

```python
# In another worker agent
import httpx

async def request_survey_analysis(user_data):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8001/analyze",
            json=user_data,
            timeout=10.0
        )
        return response.json()
```

### Calling from Supervisor

```python
# In supervisor
from agents.workers.proactive_survey_agent import ProactiveSurveyAgent

class Supervisor:
    def __init__(self):
        self.survey_agent = ProactiveSurveyAgent(
            agent_id="survey_001",
            supervisor_id=self.id
        )
    
    def assign_survey_task(self, user_data):
        result = self.survey_agent.process_task(user_data)
        return result
```

## 🎯 Integration Checklist

- [ ] Copy `agents/` directory to your multi-agent system
- [ ] Copy `communication/` directory for message models
- [ ] Copy `config/` directory and customize settings
- [ ] Copy `shared/utils.py` for utility functions
- [ ] Install dependencies from `requirements.txt`
- [ ] Configure port in `config/agent_config.json`
- [ ] Configure supervisor connection (if using one)
- [ ] Test the agent with sample data
- [ ] Verify LTM storage is working
- [ ] Check health endpoint is responding
- [ ] Integrate with your supervisor/orchestrator

## 🤝 Support & Contact

For questions about integrating this worker:
1. Check the main `README.md` for usage examples
2. Run `python demo.py` to see all features
3. Check API docs at `http://localhost:8001/docs`
4. Review test files for usage patterns

## 📄 License

Educational project for SPM coursework.

