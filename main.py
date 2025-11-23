"""
Main entry point for Proactive Survey Agent

This agent can run standalone or be integrated into a multi-agent system.
"""
import uvicorn
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from api import app
from shared.utils import load_json_config

# Load configuration
config = load_json_config("config/agent_config.json")
port = config.get("network", {}).get("port", 8001)
host = config.get("network", {}).get("host", "0.0.0.0")

if __name__ == "__main__":
    print(f"""
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║              PROACTIVE SURVEY AGENT - Starting Up                     ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝

Agent Name: {config.get('agent_name', 'ProactiveSurveyAgent')}
Version: {config.get('version', '1.0.0')}
Type: {config.get('agent_type', 'survey_agent')}

Network:
  - API: http://{host}:{port}
  - Docs: http://{host}:{port}/docs
  - Health: http://{host}:{port}/health

Capabilities:
""")
    for capability in config.get('capabilities', []):
        print(f"  ✓ {capability}")
    
    print(f"\nPress CTRL+C to stop the agent\n")
    print("="*75 + "\n")
    
    uvicorn.run(
        "api:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )

