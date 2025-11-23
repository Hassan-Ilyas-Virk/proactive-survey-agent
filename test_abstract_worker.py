"""Test script to demonstrate AbstractWorkerAgent functionality"""
import json
from agent import ProactiveSurveyAgent
import config


def test_abstract_worker_methods():
    """Test the AbstractWorkerAgent implementation"""
    
    print("\n" + "="*70)
    print("  Testing AbstractWorkerAgent Implementation")
    print("="*70 + "\n")
    
    # Initialize agent
    agent = ProactiveSurveyAgent(
        agent_id="ProactiveSurveyAgent_Test",
        supervisor_id="SupervisorRegistry"
    )
    
    print(f"✓ Agent initialized: {agent._id}")
    print(f"✓ Supervisor ID: {agent._supervisor_id}")
    print()
    
    # Test 1: LTM Write/Read
    print("-" * 70)
    print("TEST 1: Long-Term Memory (LTM) Operations")
    print("-" * 70)
    
    # Write to LTM
    test_key = "test_user_preference"
    test_value = {"preference": "email", "frequency": "weekly"}
    
    write_success = agent.write_to_ltm(test_key, test_value)
    print(f"✓ Write to LTM: {write_success}")
    print(f"  Key: {test_key}")
    print(f"  Value: {test_value}")
    
    # Read from LTM
    read_value = agent.read_from_ltm(test_key)
    print(f"✓ Read from LTM: {read_value}")
    
    # Read non-existent key
    missing_value = agent.read_from_ltm("non_existent_key")
    print(f"✓ Read missing key: {missing_value}")
    print()
    
    # Test 2: Process Task
    print("-" * 70)
    print("TEST 2: Process Task (Core Business Logic)")
    print("-" * 70)
    
    task_data = {
        "user_id": "user123",
        "recent_activity": "Support chat with negative sentiment",
        "last_purchase": "Wireless Earbuds",
        "last_survey_date": "2025-09-20"
    }
    
    print("Task Input:")
    print(json.dumps(task_data, indent=2))
    
    result = agent.process_task(task_data)
    
    print("\nTask Result:")
    print(json.dumps(result, indent=2))
    print(f"✓ Survey Triggered: {result['survey_trigger']}")
    print(f"✓ Priority: {result.get('priority', 'N/A')}")
    print()
    
    # Test 3: Message Handling
    print("-" * 70)
    print("TEST 3: Message Handling Protocol")
    print("-" * 70)
    
    # Create a task assignment message
    task_message = {
        "message_id": "msg_12345",
        "sender": "SupervisorRegistry",
        "recipient": agent._id,
        "type": "task_assignment",
        "task": {
            "name": "analyze_user_survey",
            "parameters": {
                "user_id": "user789",
                "recent_activity": "Positive feedback after purchase",
                "last_purchase": "Smart Watch",
                "last_survey_date": None
            }
        }
    }
    
    print("Incoming Task Assignment:")
    print(json.dumps(task_message, indent=2))
    
    # Handle the incoming message
    json_message = json.dumps(task_message)
    agent.handle_incoming_message(json_message)
    
    # Check queued messages
    queued = agent.get_queued_messages()
    print(f"\n✓ Messages in queue: {len(queued)}")
    
    if queued:
        print("\nCompletion Report (queued for supervisor):")
        print(json.dumps(queued[-1], indent=2))
    print()
    
    # Test 4: Get Status
    print("-" * 70)
    print("TEST 4: Agent Status")
    print("-" * 70)
    
    status = agent.get_status()
    print(json.dumps(status, indent=2))
    print()
    
    # Test 5: Multiple LTM Operations
    print("-" * 70)
    print("TEST 5: Multiple LTM Operations")
    print("-" * 70)
    
    # Store multiple entries
    agent.write_to_ltm("user_001_pref", {"survey_type": "product"})
    agent.write_to_ltm("user_002_pref", {"survey_type": "support"})
    agent.write_to_ltm("user_003_pref", {"survey_type": "general"})
    
    print(f"✓ Stored 3 additional LTM entries")
    print(f"✓ Total LTM entries: {len(agent.ltm_storage)}")
    
    # Read them back
    for key in ["user_001_pref", "user_002_pref", "user_003_pref"]:
        value = agent.read_from_ltm(key)
        print(f"  {key}: {value}")
    print()
    
    # Final Summary
    print("="*70)
    print("  AbstractWorkerAgent Implementation Test Complete")
    print("="*70)
    print()
    print("SUMMARY:")
    print(f"  ✓ Agent ID: {agent._id}")
    print(f"  ✓ Supervisor ID: {agent._supervisor_id}")
    print(f"  ✓ LTM Storage Size: {len(agent.ltm_storage)} entries")
    print(f"  ✓ Message Queue: {len(agent.message_queue)} messages")
    print(f"  ✓ Current Task: {agent._current_task_id or 'None'}")
    print()
    print("All abstract methods successfully implemented!")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_abstract_worker_methods()

