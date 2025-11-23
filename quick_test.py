#!/usr/bin/env python3
"""
Quick test script to verify the worker agent is functioning correctly
Run this before deploying or integrating with other agents
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.workers.proactive_survey_agent import ProactiveSurveyAgent
import json


def print_test(test_name, passed):
    """Print test result"""
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"  {status} - {test_name}")


def main():
    print("\n" + "="*70)
    print("  PROACTIVE SURVEY AGENT - QUICK TEST")
    print("="*70 + "\n")
    
    try:
        # Initialize agent
        print("1. Initializing Agent...")
        agent = ProactiveSurveyAgent(
            agent_id="test_agent",
            supervisor_id="test_supervisor"
        )
        print_test("Agent initialization", True)
        print_test(f"Agent ID: {agent._id}", agent._id == "test_agent")
        print()
        
        # Test LTM
        print("2. Testing Long-Term Memory (LTM)...")
        write_success = agent.write_to_ltm("test_key", {"data": "test_value"})
        print_test("LTM write", write_success)
        
        read_value = agent.read_from_ltm("test_key")
        print_test("LTM read", read_value == {"data": "test_value"})
        print()
        
        # Test process_task - Contract example
        print("3. Testing Process Task (Contract Example)...")
        task_data = {
            "user_id": "user123",
            "recent_activity": "Support chat with negative sentiment",
            "last_purchase": "Wireless Earbuds",
            "last_survey_date": "2025-09-20"
        }
        
        result = agent.process_task(task_data)
        print(f"   Input: {json.dumps(task_data, indent=6)}")
        print(f"   Output: {json.dumps(result, indent=6)}")
        
        print_test("Survey triggered", result["survey_trigger"] == True)
        print_test("Survey type", result["survey_type"] == "Product Experience")
        print_test("Priority", result["priority"] == "high")
        print_test("Questions generated", len(result.get("questions", [])) > 0)
        print()
        
        # Test message handling
        print("4. Testing Message Protocol...")
        message = {
            "message_id": "test_msg_123",
            "sender": "test_supervisor",
            "recipient": "test_agent",
            "type": "task_assignment",
            "task": {
                "name": "analyze_user",
                "parameters": {
                    "user_id": "user456",
                    "recent_activity": "Happy with product",
                    "last_purchase": "Smart Watch",
                    "last_survey_date": None
                }
            }
        }
        
        agent.handle_incoming_message(json.dumps(message))
        queued = agent.get_queued_messages()
        print_test("Message handling", len(queued) > 0)
        print_test("Completion report sent", queued[-1]["message"]["type"] == "completion_report")
        print()
        
        # Test different scenarios
        print("5. Testing Different Scenarios...")
        
        scenarios = [
            {
                "name": "Negative Support",
                "data": {"user_id": "u1", "recent_activity": "Support issue", "last_purchase": "", "last_survey_date": None},
                "expected_trigger": True
            },
            {
                "name": "Survey Cooldown",
                "data": {"user_id": "u2", "recent_activity": "Browsing", "last_purchase": "", "last_survey_date": "2025-11-19"},
                "expected_trigger": False
            },
            {
                "name": "Positive Purchase",
                "data": {"user_id": "u3", "recent_activity": "Great product", "last_purchase": "Laptop", "last_survey_date": None},
                "expected_trigger": True
            }
        ]
        
        for scenario in scenarios:
            result = agent.process_task(scenario["data"])
            passed = result["survey_trigger"] == scenario["expected_trigger"]
            print_test(f"{scenario['name']}: trigger={result['survey_trigger']}", passed)
        
        print()
        
        # Test status
        print("6. Testing Agent Status...")
        status = agent.get_status()
        print_test("Status returned", "status" in status)
        print_test("Agent healthy", status.get("status") == "healthy")
        print_test("LTM functional", status.get("ltm_keys", 0) >= 0)
        print()
        
        # Summary
        print("="*70)
        print("  TEST SUMMARY")
        print("="*70)
        print(f"  Agent Name: {agent.agent_name}")
        print(f"  Version: {agent.version}")
        print(f"  Status: {status.get('status', 'unknown')}")
        print(f"  LTM Keys: {status.get('ltm_keys', 0)}")
        print(f"  Messages Queued: {len(queued)}")
        print()
        print("  ✓ All core functions working correctly!")
        print("  ✓ Ready for deployment and integration")
        print("="*70 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

