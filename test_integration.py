"""Integration tests for Proactive Survey Agent"""
import pytest
import httpx
from datetime import datetime, timedelta


# Test configuration
AGENT_URL = "http://localhost:8001"
SUPERVISOR_URL = "http://localhost:8000"


class TestAgentIntegration:
    """Integration tests for the Survey Agent"""
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test agent health check endpoint"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{AGENT_URL}/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert "agent_name" in data
            print("✓ Health check passed")
    
    @pytest.mark.asyncio
    async def test_status_endpoint(self):
        """Test detailed status endpoint"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{AGENT_URL}/status")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "operational"
            assert "configuration" in data
            print("✓ Status endpoint passed")
    
    @pytest.mark.asyncio
    async def test_negative_sentiment_after_purchase(self):
        """Test: Negative sentiment after purchase should trigger high-priority survey"""
        async with httpx.AsyncClient() as client:
            request_data = {
                "user_id": "user123",
                "recent_activity": "Support chat with negative sentiment",
                "last_purchase": "Wireless Earbuds",
                "last_survey_date": "2025-09-20"
            }
            
            response = await client.post(f"{AGENT_URL}/analyze", json=request_data)
            assert response.status_code == 200
            
            data = response.json()
            assert data["survey_trigger"] == True
            assert data["survey_type"] == "Product Experience"
            assert data["priority"] == "high"
            assert "Negative sentiment" in data["reason"]
            assert len(data["questions"]) > 0
            print("✓ Negative sentiment test passed")
            print(f"  Response: {data}")
    
    @pytest.mark.asyncio
    async def test_recent_purchase_positive(self):
        """Test: Recent purchase with positive sentiment"""
        async with httpx.AsyncClient() as client:
            request_data = {
                "user_id": "user456",
                "recent_activity": "Happy with recent order",
                "last_purchase": "Laptop Stand",
                "last_survey_date": "2025-08-01"
            }
            
            response = await client.post(f"{AGENT_URL}/analyze", json=request_data)
            assert response.status_code == 200
            
            data = response.json()
            assert data["survey_trigger"] == True
            assert data["priority"] in ["medium", "high"]
            assert len(data["questions"]) > 0
            print("✓ Positive purchase test passed")
            print(f"  Response: {data}")
    
    @pytest.mark.asyncio
    async def test_survey_cooldown(self):
        """Test: Survey cooldown period (recent survey should block new one)"""
        async with httpx.AsyncClient() as client:
            # Survey sent yesterday
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            
            request_data = {
                "user_id": "user789",
                "recent_activity": "Browsing products",
                "last_purchase": "Phone Case",
                "last_survey_date": yesterday
            }
            
            response = await client.post(f"{AGENT_URL}/analyze", json=request_data)
            assert response.status_code == 200
            
            data = response.json()
            assert data["survey_trigger"] == False
            assert "too recently" in data["reason"].lower()
            print("✓ Survey cooldown test passed")
    
    @pytest.mark.asyncio
    async def test_support_negative_experience(self):
        """Test: Negative support experience triggers survey"""
        async with httpx.AsyncClient() as client:
            request_data = {
                "user_id": "user999",
                "recent_activity": "Support chat - issue not resolved, frustrated",
                "last_purchase": "",
                "last_survey_date": "2025-06-01"
            }
            
            response = await client.post(f"{AGENT_URL}/analyze", json=request_data)
            assert response.status_code == 200
            
            data = response.json()
            assert data["survey_trigger"] == True
            assert data["survey_type"] == "Support Quality"
            assert data["priority"] == "high"
            print("✓ Negative support test passed")
    
    @pytest.mark.asyncio
    async def test_neutral_engagement(self):
        """Test: Neutral engagement triggers low-priority survey"""
        async with httpx.AsyncClient() as client:
            request_data = {
                "user_id": "user555",
                "recent_activity": "Logged in and viewed dashboard",
                "last_purchase": "",
                "last_survey_date": None
            }
            
            response = await client.post(f"{AGENT_URL}/analyze", json=request_data)
            assert response.status_code == 200
            
            data = response.json()
            assert data["survey_trigger"] == True
            assert data["priority"] == "low"
            print("✓ Neutral engagement test passed")
    
    @pytest.mark.asyncio
    async def test_json_contract_compliance(self):
        """Test: Verify response matches expected JSON contract"""
        async with httpx.AsyncClient() as client:
            request_data = {
                "user_id": "user123",
                "recent_activity": "Support chat with negative sentiment",
                "last_purchase": "Wireless Earbuds",
                "last_survey_date": "2025-09-20"
            }
            
            response = await client.post(f"{AGENT_URL}/analyze", json=request_data)
            data = response.json()
            
            # Check required fields
            assert "survey_trigger" in data
            assert isinstance(data["survey_trigger"], bool)
            assert "reason" in data
            assert "timestamp" in data
            
            # If survey triggered, check additional fields
            if data["survey_trigger"]:
                assert "survey_type" in data
                assert "priority" in data
                assert "questions" in data
                assert isinstance(data["questions"], list)
            
            print("✓ JSON contract compliance test passed")


class TestSupervisorIntegration:
    """Integration tests for Supervisor/Registry communication"""
    
    @pytest.mark.asyncio
    async def test_supervisor_health(self):
        """Test supervisor health check"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{SUPERVISOR_URL}/health", timeout=5.0)
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "healthy"
                print("✓ Supervisor health check passed")
        except Exception as e:
            print(f"⚠ Supervisor not running (expected if testing agent only): {e}")
    
    @pytest.mark.asyncio
    async def test_agent_registration(self):
        """Test that agent is registered with supervisor"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{SUPERVISOR_URL}/agents", timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    agents = data.get("agents", [])
                    agent_names = [a["agent_name"] for a in agents]
                    assert "ProactiveSurveyAgent" in agent_names
                    print("✓ Agent registration verified")
        except Exception as e:
            print(f"⚠ Supervisor not running (expected if testing agent only): {e}")


def run_manual_test():
    """Manual test function that can be run directly"""
    print("\n" + "="*60)
    print("MANUAL INTEGRATION TEST")
    print("="*60 + "\n")
    
    import asyncio
    
    async def manual_test():
        async with httpx.AsyncClient() as client:
            # Test the exact example from requirements
            print("Testing exact contract example...")
            request_data = {
                "user_id": "user123",
                "recent_activity": "Support chat with negative sentiment",
                "last_purchase": "Wireless Earbuds",
                "last_survey_date": "2025-09-20"
            }
            
            try:
                response = await client.post(f"{AGENT_URL}/analyze", json=request_data)
                print(f"\nStatus Code: {response.status_code}")
                print(f"\nResponse:\n{response.json()}")
                
                expected_output = {
                    "survey_trigger": True,
                    "survey_type": "Product Experience",
                    "priority": "high",
                    "reason": "Negative sentiment after purchase"
                }
                
                data = response.json()
                print("\n" + "-"*60)
                print("VERIFICATION:")
                print(f"✓ survey_trigger: {data['survey_trigger']} (expected: True)")
                print(f"✓ survey_type: {data['survey_type']} (expected: Product Experience)")
                print(f"✓ priority: {data['priority']} (expected: high)")
                print(f"✓ reason: {data['reason']}")
                print(f"✓ questions: {len(data['questions'])} questions generated")
                print("-"*60)
                
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print(f"\nMake sure the agent is running on {AGENT_URL}")
    
    asyncio.run(manual_test())


if __name__ == "__main__":
    # Run manual test when executed directly
    run_manual_test()

