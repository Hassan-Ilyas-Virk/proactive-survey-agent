#!/usr/bin/env python3
"""
Demonstration script for Proactive Survey Agent
Shows all capabilities including AbstractWorkerAgent implementation
"""
import json
import asyncio
import httpx
from agent import ProactiveSurveyAgent


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


async def demo_http_api():
    """Demonstrate HTTP API calls"""
    print_section("HTTP API Demonstration")
    
    base_url = "http://localhost:8001"
    
    async with httpx.AsyncClient() as client:
        try:
            # Health check
            print("1. Health Check")
            response = await client.get(f"{base_url}/health")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {json.dumps(response.json(), indent=2)}\n")
            
            # Status endpoint
            print("2. Detailed Status")
            response = await client.get(f"{base_url}/status")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {json.dumps(response.json(), indent=2)}\n")
            
            # Analyze endpoint - Example from requirements
            print("3. Analyze User (Contract Example)")
            request_data = {
                "user_id": "user123",
                "recent_activity": "Support chat with negative sentiment",
                "last_purchase": "Wireless Earbuds",
                "last_survey_date": "2025-09-20"
            }
            print(f"   Request: {json.dumps(request_data, indent=2)}")
            
            response = await client.post(f"{base_url}/analyze", json=request_data)
            result = response.json()
            print(f"\n   Response: {json.dumps(result, indent=2)}")
            
            print("\n   ✓ Verification:")
            print(f"     - survey_trigger: {result['survey_trigger']} (Expected: True)")
            print(f"     - survey_type: {result['survey_type']} (Expected: Product Experience)")
            print(f"     - priority: {result['priority']} (Expected: high)")
            print(f"     - questions: {len(result['questions'])} questions generated")
            
        except Exception as e:
            print(f"\n   ⚠️  Error: {e}")
            print(f"   Make sure the agent is running: ./run_agent.sh")


def demo_abstract_worker():
    """Demonstrate AbstractWorkerAgent implementation"""
    print_section("AbstractWorkerAgent Implementation")
    
    # Initialize agent
    agent = ProactiveSurveyAgent(
        agent_id="DemoAgent",
        supervisor_id="SupervisorRegistry"
    )
    
    print("1. Agent Initialization")
    print(f"   Agent ID: {agent._id}")
    print(f"   Supervisor ID: {agent._supervisor_id}")
    print(f"   Current Task: {agent._current_task_id}\n")
    
    # Test LTM operations
    print("2. Long-Term Memory (LTM)")
    agent.write_to_ltm("user_pref_001", {"survey_type": "product", "frequency": "monthly"})
    agent.write_to_ltm("user_pref_002", {"survey_type": "support", "frequency": "weekly"})
    
    pref_001 = agent.read_from_ltm("user_pref_001")
    print(f"   Stored: user_pref_001 = {pref_001}")
    print(f"   Total LTM entries: {len(agent.ltm_storage)}\n")
    
    # Test process_task
    print("3. Process Task (Business Logic)")
    task_data = {
        "user_id": "user456",
        "recent_activity": "Happy with recent purchase",
        "last_purchase": "Smart Watch",
        "last_survey_date": None
    }
    
    result = agent.process_task(task_data)
    print(f"   Input: {json.dumps(task_data, indent=2)}")
    print(f"\n   Output: {json.dumps(result, indent=2)}\n")
    
    # Test message handling
    print("4. Message Handling Protocol")
    task_message = {
        "message_id": "msg_demo_123",
        "sender": "SupervisorRegistry",
        "recipient": agent._id,
        "type": "task_assignment",
        "task": {
            "name": "analyze_survey",
            "parameters": {
                "user_id": "user789",
                "recent_activity": "Browsing products",
                "last_purchase": "",
                "last_survey_date": None
            }
        }
    }
    
    print(f"   Incoming Message: {task_message['type']}")
    agent.handle_incoming_message(json.dumps(task_message))
    
    queued = agent.get_queued_messages()
    print(f"   Queued Messages: {len(queued)}")
    if queued:
        last_msg = queued[-1]
        print(f"   Last Message Type: {last_msg['message']['type']}")
        print(f"   Recipient: {last_msg['recipient']}\n")
    
    # Final status
    print("5. Agent Status")
    status = agent.get_status()
    print(f"   {json.dumps(status, indent=2)}\n")


def demo_survey_scenarios():
    """Demonstrate different survey trigger scenarios"""
    print_section("Survey Trigger Scenarios")
    
    agent = ProactiveSurveyAgent()
    
    scenarios = [
        {
            "name": "Negative Support Experience",
            "data": {
                "user_id": "user001",
                "recent_activity": "Support chat - issue not resolved, frustrated",
                "last_purchase": "",
                "last_survey_date": None
            }
        },
        {
            "name": "Positive Recent Purchase",
            "data": {
                "user_id": "user002",
                "recent_activity": "Very satisfied with new product",
                "last_purchase": "Laptop Stand",
                "last_survey_date": "2025-08-01"
            }
        },
        {
            "name": "Neutral Engagement",
            "data": {
                "user_id": "user003",
                "recent_activity": "Logged in and viewed dashboard",
                "last_purchase": "",
                "last_survey_date": None
            }
        },
        {
            "name": "Survey Cooldown Active",
            "data": {
                "user_id": "user004",
                "recent_activity": "Browsing products",
                "last_purchase": "Phone Case",
                "last_survey_date": "2025-11-19"  # Yesterday
            }
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"{i}. {scenario['name']}")
        result = agent.analyze_request(scenario['data'])
        print(f"   Trigger: {result['survey_trigger']}")
        if result['survey_trigger']:
            print(f"   Type: {result['survey_type']}")
            print(f"   Priority: {result['priority']}")
        print(f"   Reason: {result['reason']}\n")


def main():
    """Run all demonstrations"""
    print("\n" + "█"*70)
    print("█" + " "*68 + "█")
    print("█" + "  PROACTIVE SURVEY AGENT - COMPLETE DEMONSTRATION".center(68) + "█")
    print("█" + " "*68 + "█")
    print("█"*70)
    
    # Demo 1: AbstractWorkerAgent
    demo_abstract_worker()
    
    # Demo 2: Survey Scenarios
    demo_survey_scenarios()
    
    # Demo 3: HTTP API (async)
    print_section("Attempting HTTP API Demo")
    print("NOTE: This requires the agent to be running on port 8001")
    print("      Run './run_agent.sh' in another terminal first\n")
    
    try:
        asyncio.run(demo_http_api())
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    
    # Summary
    print("\n" + "█"*70)
    print("█" + " "*68 + "█")
    print("█" + "  DEMONSTRATION COMPLETE".center(68) + "█")
    print("█" + " "*68 + "█")
    print("█"*70)
    
    print("\n✓ All Features Demonstrated:")
    print("  • AbstractWorkerAgent implementation (LTM, messaging, task processing)")
    print("  • Survey analysis with intelligent decision-making")
    print("  • Sentiment detection and pattern recognition")
    print("  • HTTP API with health checks and status endpoints")
    print("  • JSON contract compliance")
    print("\n✓ Ready for Deployment!")
    print("\nNext Steps:")
    print("  1. Start the agent: ./run_agent.sh")
    print("  2. Test the API: curl http://localhost:8001/health")
    print("  3. Run integration tests: pytest test_integration.py -v")
    print("  4. (Optional) Start supervisor: ./run_supervisor.sh")
    print("\nAPI Documentation: http://localhost:8001/docs\n")


if __name__ == "__main__":
    main()

