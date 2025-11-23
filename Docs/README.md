# Proactive Survey Agent

A fully functional AI worker agent that analyzes user interactions and automatically decides when to send feedback surveys. The agent detects patterns like negative sentiment, recent purchases, or reduced engagement to trigger personalized survey questions.

**This is a single worker agent designed to be integrated into a multi-agent system. See [`INTEGRATION_GUIDE.md`](INTEGRATION_GUIDE.md) for integration instructions.**

## 🎯 Features

- ✅ **AI-Powered Agent** - Uses Google Gemini for intelligent analysis
- ✅ **Advanced Sentiment Analysis** - AI-driven emotion detection with confidence scores
- ✅ **Personalized Question Generation** - AI creates context-specific survey questions
- ✅ **HTTP API Deployment** - FastAPI with REST endpoints
- ✅ **Supervisor/Registry Communication** - Agent registration and heartbeat system
- ✅ **Logging & Health Checks** - Comprehensive status monitoring
- ✅ **Integration Tests** - External API call validation
- ✅ **AbstractWorkerAgent Base Class** - Implements LTM and message handling
- ✅ **Fallback Mode** - Works without API key using rule-based logic
- ✅ **Smart Survey Triggers** - Intelligent decision-making for survey timing

## 📋 System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Supervisor Registry                     │
│              (Port 8000 - Optional)                      │
│  - Agent Registration                                    │
│  - Health Monitoring                                     │
│  - Message Routing                                       │
└───────────────────┬─────────────────────────────────────┘
                    │
                    │ Registration/Heartbeat
                    │
┌───────────────────▼─────────────────────────────────────┐
│            Proactive Survey Agent                        │
│                 (Port 8001)                              │
│  ┌─────────────────────────────────────────────┐        │
│  │  AbstractWorkerAgent                         │        │
│  │  - process_task()                            │        │
│  │  - send_message()                            │        │
│  │  - write_to_ltm() / read_from_ltm()         │        │
│  │  - handle_incoming_message()                │        │
│  └─────────────────────────────────────────────┘        │
│  ┌─────────────────────────────────────────────┐        │
│  │  Survey Analysis Logic                       │        │
│  │  - Sentiment Detection                       │        │
│  │  - Purchase Pattern Analysis                │        │
│  │  - Engagement Monitoring                     │        │
│  │  - Survey Question Generation                │        │
│  └─────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────┘
                    │
                    │ HTTP API Calls
                    │
┌───────────────────▼─────────────────────────────────────┐
│              External Systems/Clients                    │
│  - Web Applications                                      │
│  - Mobile Apps                                           │
│  - Integration Tests                                     │
└─────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)
- **Gemini API Key** (for AI features)

### Setup

1. **Create `.env` file** with your Gemini API key:
```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your API key
GEMINI_API_KEY=your_actual_api_key_here
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Run quick test**:
```bash
python3 quick_test.py
```

### Installation & Running

#### Option 1: Using Main Entry Point (Recommended)

```bash
# Install dependencies
pip install -r requirements.txt

# Run the agent
python main.py
```

#### Option 2: Using the Startup Script

```bash
# Make the script executable
chmod +x run_agent.sh

# Run the agent
./run_agent.sh
```

This script will:
- Create a virtual environment if needed
- Install all dependencies
- Start the agent on `http://localhost:8001`

#### Option 3: Direct Uvicorn

```bash
# Install dependencies first
pip install -r requirements.txt

# Run with uvicorn
uvicorn api:app --host 0.0.0.0 --port 8001 --reload
```

### Running with Supervisor (Optional)

The agent can optionally register with a supervisor for better orchestration:

```bash
# Terminal 1: Start Supervisor
chmod +x run_supervisor.sh
./run_supervisor.sh

# Terminal 2: Start Agent (will auto-register with supervisor)
./run_agent.sh
```

## 📖 API Usage

### Health Check

```bash
curl http://localhost:8001/health
```

**Response:**
```json
{
  "agent_id": "ProactiveSurveyAgent",
  "agent_name": "ProactiveSurveyAgent",
  "version": "1.0.0",
  "status": "healthy",
  "supervisor_id": "SupervisorRegistry",
  "current_task_id": null,
  "ltm_keys": 0,
  "queued_messages": 0,
  "timestamp": "2025-11-20T10:30:00.000000"
}
```

### Analyze User for Survey

**Endpoint:** `POST /analyze`

**Request:**
```bash
curl -X POST http://localhost:8001/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "recent_activity": "Support chat with negative sentiment",
    "last_purchase": "Wireless Earbuds",
    "last_survey_date": "2025-09-20"
  }'
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
  "timestamp": "2025-11-20T10:30:00.000000"
}
```

## 📝 JSON Contract

### Input Schema

```json
{
  "user_id": "string (required)",
  "recent_activity": "string (required)",
  "last_purchase": "string (optional)",
  "last_survey_date": "string (optional, ISO format)"
}
```

### Output Schema

```json
{
  "survey_trigger": "boolean",
  "survey_type": "string (if triggered)",
  "priority": "string (if triggered) - low|medium|high|urgent",
  "reason": "string",
  "questions": "array of strings (if triggered)",
  "timestamp": "string (ISO format)"
}
```

## 🧪 Testing

### Run Integration Tests

```bash
# Make sure the agent is running first
./run_agent.sh

# In another terminal, run tests
pytest test_integration.py -v
```

### Run AbstractWorkerAgent Tests

```bash
python test_abstract_worker.py
```

### Manual Testing

```bash
# Test with the exact contract example
python test_integration.py
```

## 🏗️ AbstractWorkerAgent Implementation

The agent implements the `AbstractWorkerAgent` base class with the following methods:

### Abstract Methods (Implemented)

1. **`process_task(task_data: dict) -> dict`**
   - Core business logic for survey analysis
   - Returns survey decision and details

2. **`send_message(recipient: str, message_obj: dict)`**
   - Sends messages to supervisor/other agents
   - Queues messages for async processing

3. **`write_to_ltm(key: str, value: Any) -> bool`**
   - Writes to Long-Term Memory
   - Stores analysis history and user preferences

4. **`read_from_ltm(key: str) -> Optional[Any]`**
   - Reads from Long-Term Memory
   - Retrieves past analyses and decisions

### Concrete Methods (Inherited)

- **`handle_incoming_message(json_message: str)`**
  - Processes incoming task assignments from supervisor
  - Automatically calls `process_task()` and reports completion

- **`_execute_task(task_data: dict, related_msg_id: str)`**
  - Executes task and handles error reporting

- **`_report_completion(related_msg_id: str, status: str, results: dict)`**
  - Sends completion reports to supervisor

## 🎯 Survey Trigger Logic

The agent uses intelligent decision-making based on:

### High Priority Triggers
- **Negative sentiment after purchase** → Product Experience Survey
- **Negative support interaction** → Support Quality Survey

### Medium Priority Triggers
- **Recent purchase (positive/neutral)** → Product Follow-up Survey
- **Positive engagement** → General Feedback Survey

### Low Priority Triggers
- **Neutral engagement** → Engagement Check Survey

### Cooldown Period
- Minimum 30 days between surveys (configurable in `config.py`)

## 📁 Project Structure

```
Project/
├── agents/                           # All agent code
│   ├── worker_base.py               # AbstractWorkerAgent base class
│   └── workers/                     # Worker implementations
│       ├── __init__.py
│       └── proactive_survey_agent.py # Main worker agent
├── communication/                    # Message protocols
│   ├── models.py                    # Pydantic models
│   └── protocol.py                  # Protocol constants
├── config/                          # Configuration files
│   ├── agent_config.json           # Agent-specific config
│   └── settings.yaml               # System settings
├── shared/                          # Shared utilities
│   ├── utils.py                    # Helper functions
│   └── LTM/                        # Long-Term Memory storage
│       └── ProactiveSurveyAgent/
├── api.py                          # FastAPI HTTP server
├── main.py                         # Main entry point
├── supervisor.py                   # Optional supervisor (for testing)
├── quick_test.py                   # Quick verification test
├── test_integration.py             # Integration tests
├── test_abstract_worker.py         # AbstractWorkerAgent tests
├── demo.py                         # Full demonstration
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── INTEGRATION_GUIDE.md            # Integration instructions
├── run_agent.sh                    # Agent startup script
└── run_supervisor.sh               # Supervisor startup script (optional)
```

## ⚙️ Configuration

### Agent Configuration

Edit `config/agent_config.json` to customize:

```json
{
  "agent_name": "ProactiveSurveyAgent",
  "network": {
    "port": 8001
  },
  "supervisor": {
    "host": "localhost",
    "port": 8000
  },
  "business_logic": {
    "survey_cooldown_days": 30
  }
}
```

### System Settings

Edit `config/settings.yaml` for global settings.

## 📊 Endpoints Reference

### Agent Endpoints (Port 8001)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/analyze` | POST | Analyze user and trigger surveys |
| `/health` | GET | Health check with full status |
| `/status` | GET | Detailed system status |
| `/docs` | GET | Interactive API documentation |

### Supervisor Endpoints (Port 8000 - Optional)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/register` | POST | Register new agent |
| `/heartbeat` | POST | Agent heartbeat |
| `/agents` | GET | List all agents |
| `/agents/{name}` | GET | Get specific agent info |
| `/messages` | POST | Receive agent messages |
| `/health` | GET | Supervisor health check |

## 🔍 Example Use Cases

### 1. Post-Purchase Negative Sentiment
```json
Input: {
  "user_id": "user123",
  "recent_activity": "Support chat - product defective",
  "last_purchase": "Wireless Earbuds",
  "last_survey_date": "2025-08-01"
}

Output: {
  "survey_trigger": true,
  "survey_type": "Product Experience",
  "priority": "high",
  "reason": "Negative sentiment after purchase"
}
```

### 2. Positive Engagement
```json
Input: {
  "user_id": "user456",
  "recent_activity": "Great experience with new features",
  "last_purchase": "",
  "last_survey_date": null
}

Output: {
  "survey_trigger": true,
  "survey_type": "General Feedback",
  "priority": "medium",
  "reason": "Positive engagement - capture feedback"
}
```

### 3. Survey Cooldown
```json
Input: {
  "user_id": "user789",
  "recent_activity": "Browsing products",
  "last_purchase": "Phone Case",
  "last_survey_date": "2025-11-19"  // Yesterday
}

Output: {
  "survey_trigger": false,
  "reason": "Survey sent too recently"
}
```

## 🛠️ Development

### Adding New Survey Types

1. Edit `config.py` to add new survey type:
```python
SURVEY_TYPES = {
    "product_experience": "Product Experience",
    "your_new_type": "Your New Type"
}
```

2. Add decision logic in `agent.py` `_make_decision()` method

### Adding New Triggers

Modify the `_make_decision()` method in `agent.py` to add custom trigger logic.

## 📦 Dependencies

- **FastAPI** - Modern web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation
- **httpx** - Async HTTP client
- **python-dateutil** - Date parsing
- **pytest** - Testing framework
- **pyyaml** - YAML configuration parsing

Install all with: `pip install -r requirements.txt`

## 🐛 Troubleshooting

### Agent won't start
```bash
# Check if port is already in use
lsof -i :8001

# Use different port
uvicorn api:app --port 8002
```

### Import errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Tests failing
```bash
# Make sure agent is running
curl http://localhost:8001/health

# Run with verbose output
pytest test_integration.py -v -s
```

## 📄 License

This project is created for educational purposes as part of SPM coursework.

## 👥 Author

Created for Software Project Management - Semester 7

---

## 🔗 Integration with Other Agents

This is a **single worker agent** designed to be integrated into a larger multi-agent system. 

**For integrators:** See [`INTEGRATION_GUIDE.md`](INTEGRATION_GUIDE.md) for detailed instructions on:
- How to integrate this worker with other agents
- Message protocol specifications
- Configuration options
- Deployment strategies
- API contracts

The agent follows the project structure guidelines and inherits from `AbstractWorkerAgent` for standardized communication.

## 🎓 Assignment Requirements Checklist

- ✅ **Working AI Agent** - Fully functional and responds per JSON contract
- ✅ **Deployment** - HTTP API with FastAPI on port 8001
- ✅ **Communication** - Agent communicates with Supervisor/Registry structure
- ✅ **Logging & Health Check** - Returns status response when requested
- ✅ **Integration Test** - Can be called externally with correct outputs
- ✅ **AbstractWorkerAgent** - Implements base class with LTM and messaging
- ✅ **Single Worker Agent** - Proactive Survey Agent implementation
- ✅ **Project Structure** - Follows recommended multi-agent folder structure
- ✅ **Configuration** - JSON/YAML based configuration files
- ✅ **Integration Ready** - Complete guide for multi-agent integration

**Status:** ✅ All requirements met and tested

