"""
Proactive Survey Agent - AI-Powered Worker Implementation

This agent uses AI (Gemini) to analyze user interactions and automatically 
decides when to send feedback surveys. It uses advanced sentiment analysis and 
generates personalized survey questions based on user context.
"""
import logging
import json
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dateutil import parser
import httpx

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from agents.worker_base import AbstractWorkerAgent
from shared.utils import setup_logging, load_json_config, LTMFileStorage, get_timestamp
from shared.ai_service import ai_service

# Configuration
CONFIG_PATH = "config/agent_config.json"
config = load_json_config(CONFIG_PATH)

AGENT_NAME = config.get("agent_name", "ProactiveSurveyAgent")
AGENT_VERSION = config.get("version", "1.0.0")
MIN_DAYS_BETWEEN_SURVEYS = config.get("business_logic", {}).get("survey_cooldown_days", 30)

# Setup logging
logger = setup_logging(AGENT_NAME, level=config.get("logging", {}).get("level", "INFO"))

# Sentiment keywords
NEGATIVE_KEYWORDS = [
    "negative", "complaint", "issue", "problem", "dissatisfied",
    "unhappy", "disappointed", "frustrated", "broken", "defect"
]
POSITIVE_KEYWORDS = ["positive", "happy", "satisfied", "great", "excellent"]


class ProactiveSurveyAgent(AbstractWorkerAgent):
    """
    AI-Powered worker agent that analyzes user interactions and triggers surveys.
    Uses Gemini AI for sentiment analysis and question generation.
    Inherits from AbstractWorkerAgent for supervisor communication.
    """
    
    def __init__(self, agent_id: str = None, supervisor_id: str = "SupervisorRegistry"):
        # Initialize parent class
        agent_id = agent_id or AGENT_NAME
        super().__init__(agent_id, supervisor_id)
        
        self.agent_name = AGENT_NAME
        self.version = AGENT_VERSION
        
        # Initialize LTM storage (file-based) with error handling
        try:
        self.ltm = LTMFileStorage(
            agent_name=self.agent_name,
            base_path=config.get("ltm_config", {}).get("base_directory", "shared/LTM")
        )
        except Exception as e:
            logger.warning(f"Failed to initialize LTM storage: {e}. Agent will continue without persistent storage.")
            # Create a dummy LTM object that doesn't persist
            self.ltm = None
        
        # Message queue for supervisor communication
        self.message_queue = []
        
        # AI service
        self.ai_service = ai_service
        
        ai_status = "enabled" if self.ai_service.ai_enabled else "fallback mode"
        ltm_status = "enabled" if self.ltm else "disabled"
        logger.info(f"Initialized {self.agent_name} v{self.version} with AI {ai_status}, LTM {ltm_status}")
    
    # --- Implement Abstract Methods ---
    
    def process_task(self, task_data: dict) -> dict:
        """
        Process a survey analysis task.
        
        Args:
            task_data: Dictionary containing user_id, recent_activity, etc.
        
        Returns:
            Dictionary with survey decision and details
        """
        logger.info(f"Processing task for user: {task_data.get('user_id')}")
        
        # Use the core analysis logic
        result = self.analyze_request(task_data)
        
        # Store analysis in LTM for future reference
        user_id = task_data.get('user_id')
        if user_id:
            self.write_to_ltm(f"last_analysis_{user_id}", {
                "timestamp": get_timestamp(),
                "result": result
            })
        
        return result
    
    def send_message(self, recipient: str, message_obj: dict):
        """
        Sends a message to the supervisor or other agents.
        
        Args:
            recipient: Recipient agent/supervisor ID
            message_obj: Message dictionary to send
        """
        logger.info(f"Sending message to {recipient}: {message_obj.get('type')}")
        
        # Store in queue for async processing
        self.message_queue.append({
            "recipient": recipient,
            "message": message_obj,
            "timestamp": get_timestamp()
        })
        
        logger.debug(f"Message queued: {json.dumps(message_obj, indent=2)}")
        
        # Attempt to send to supervisor via HTTP if available
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(self._send_to_supervisor_http(message_obj))
        except Exception as e:
            logger.debug(f"HTTP send not available: {e}")
    
    async def _send_to_supervisor_http(self, message_obj: dict):
        """Helper to send message via HTTP to supervisor"""
        supervisor_config = config.get("supervisor", {})
        supervisor_url = f"http://{supervisor_config.get('host', 'localhost')}:{supervisor_config.get('port', 8000)}"
        
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{supervisor_url}/messages",
                    json=message_obj,
                    timeout=5.0
                )
        except Exception as e:
            logger.debug(f"Could not send to supervisor via HTTP: {e}")
    
    def write_to_ltm(self, key: str, value: Any) -> bool:
        """
        Writes a key-value pair to Long-Term Memory.
        
        Args:
            key: Storage key
            value: Value to store
        
        Returns:
            True on success, False otherwise
        """
        if self.ltm is None:
            logger.debug("LTM not available, skipping write")
            return False
        try:
            success = self.ltm.write(key, value)
            if success:
                logger.debug(f"LTM Write: {key}")
            return success
        except Exception as e:
            logger.error(f"LTM Write Error: {e}")
            return False
    
    def read_from_ltm(self, key: str) -> Optional[Any]:
        """
        Reads a value from Long-Term Memory.
        
        Args:
            key: Storage key
        
        Returns:
            Stored value or None if not found
        """
        if self.ltm is None:
            logger.debug("LTM not available, returning None")
            return None
        try:
            value = self.ltm.read(key)
            if value:
                logger.debug(f"LTM Read: {key}")
            return value
        except Exception as e:
            logger.error(f"LTM Read Error: {e}")
            return None
    
    # --- Core Survey Analysis Logic ---
    
    def analyze_request(self, request_data: Dict) -> Dict:
        """
        Main analysis method that processes user data and decides on survey triggers.
        
        Args:
            request_data: Dictionary containing user_id, recent_activity, 
                         last_purchase, last_survey_date
        
        Returns:
            Dictionary with survey decision and details
        """
        logger.info(f"Analyzing request for user: {request_data.get('user_id')}")
        
        try:
            user_id = request_data.get("user_id")
            recent_activity = request_data.get("recent_activity", "")
            last_purchase = request_data.get("last_purchase", "")
            last_survey_date = request_data.get("last_survey_date")
            
            # Check LTM for previous analyses
            previous_analysis = self.read_from_ltm(f"last_analysis_{user_id}")
            if previous_analysis:
                logger.debug(f"Found previous analysis in LTM for {user_id}")
            
            # Check if enough time has passed since last survey
            if not self._should_send_survey(last_survey_date):
                logger.info(f"Survey cooldown active for user {user_id}")
                return self._create_response(
                    survey_trigger=False,
                    reason="Survey sent too recently"
                )
            
            # Analyze sentiment and context using AI
            sentiment_analysis = self._analyze_sentiment(recent_activity)
            sentiment = sentiment_analysis["sentiment"]
            confidence = sentiment_analysis["confidence"]
            has_recent_purchase = bool(last_purchase)
            
            logger.info(f"AI Sentiment for {user_id}: {sentiment} (confidence: {confidence}%)")
            
            # Decision logic with AI insights
            response = self._make_decision(
                sentiment=sentiment,
                sentiment_confidence=confidence,
                recent_activity=recent_activity,
                has_recent_purchase=has_recent_purchase,
                last_purchase=last_purchase,
                user_id=user_id
            )
            
            logger.info(f"Decision for user {user_id}: {response['survey_trigger']}")
            return response
            
        except Exception as e:
            logger.error(f"Error analyzing request: {str(e)}")
            raise
    
    def _should_send_survey(self, last_survey_date: Optional[str]) -> bool:
        """Check if enough time has passed since the last survey"""
        if not last_survey_date:
            return True
        
        try:
            last_date = parser.parse(last_survey_date)
            days_since = (datetime.now() - last_date).days
            return days_since >= MIN_DAYS_BETWEEN_SURVEYS
        except Exception as e:
            logger.warning(f"Error parsing date: {e}")
            return True
    
    def _analyze_sentiment(self, text: str) -> Dict:
        """
        Analyze sentiment from text using AI
        Returns dict with sentiment, confidence, and reason
        """
        result = self.ai_service.analyze_sentiment_ai(text)
        
        # Store sentiment analysis in LTM for learning
        sentiment_key = f"sentiment_{hash(text) % 10000}"
        self.write_to_ltm(sentiment_key, {
            "text": text[:100],  # Store snippet
            "sentiment": result["sentiment"],
            "confidence": result["confidence"],
            "timestamp": get_timestamp()
        })
        
        return result
    
    def _make_decision(
        self, 
        sentiment: str,
        sentiment_confidence: int,
        recent_activity: str,
        has_recent_purchase: bool,
        last_purchase: str,
        user_id: str
    ) -> Dict:
        """Make survey decision based on AI-analyzed data"""
        
        # Prepare context for AI question generation
        user_context = {
            "user_id": user_id,
            "recent_activity": recent_activity,
            "last_purchase": last_purchase,
            "sentiment": sentiment,
            "confidence": sentiment_confidence
        }
        
        # High priority: Negative sentiment after purchase
        if sentiment == "negative" and has_recent_purchase:
            questions = self.ai_service.generate_survey_questions_ai(
                user_context=user_context,
                survey_type="Product Experience",
                num_questions=3
            )
            return self._create_response(
                survey_trigger=True,
                survey_type="Product Experience",
                priority="high",
                reason=f"Negative sentiment detected after purchase (AI confidence: {sentiment_confidence}%)",
                questions=questions
            )
        
        # High priority: Support interaction with negative sentiment
        if sentiment == "negative" and "support" in recent_activity.lower():
            questions = self.ai_service.generate_survey_questions_ai(
                user_context=user_context,
                survey_type="Support Quality",
                num_questions=3
            )
            return self._create_response(
                survey_trigger=True,
                survey_type="Support Quality",
                priority="high",
                reason=f"Negative support experience detected (AI confidence: {sentiment_confidence}%)",
                questions=questions
            )
        
        # Other negative sentiment cases
        if sentiment == "negative":
            questions = self.ai_service.generate_survey_questions_ai(
                user_context=user_context,
                survey_type="Engagement Check",
                num_questions=3
            )
            return self._create_response(
                survey_trigger=True,
                survey_type="Engagement Check",
                priority="medium",
                reason=f"Negative sentiment detected (AI confidence: {sentiment_confidence}%)",
                questions=questions
            )
        
        # Default: No survey
        return self._create_response(
            survey_trigger=False,
            reason=f"No survey needed for {sentiment} sentiment (AI confidence: {sentiment_confidence}%)"
        )
    
    def _create_response(
        self,
        survey_trigger: bool,
        survey_type: str = "",
        priority: str = "low",
        reason: str = "",
        questions: List[str] = None
    ) -> Dict:
        """Create standardized response dictionary"""
        response = {
            "survey_trigger": survey_trigger,
            "reason": reason,
            "timestamp": get_timestamp()
        }
        
        if survey_trigger:
            response.update({
                "survey_type": survey_type,
                "priority": priority,
                "questions": questions or []
            })
        
        return response
    
    def get_status(self) -> Dict:
        """Return agent health status"""
        ltm_keys = len(self.ltm.list_keys()) if hasattr(self.ltm, 'list_keys') else 0
        
        return {
            "agent_id": self._id,
            "agent_name": self.agent_name,
            "version": self.version,
            "status": "healthy",
            "ai_enabled": self.ai_service.ai_enabled,
            "ai_model": "gemini-pro" if self.ai_service.ai_enabled else "fallback",
            "supervisor_id": self._supervisor_id,
            "current_task_id": self._current_task_id,
            "ltm_keys": ltm_keys,
            "queued_messages": len(self.message_queue),
            "timestamp": get_timestamp()
        }
    
    def get_queued_messages(self) -> List[Dict]:
        """Get all queued messages (for inspection/testing)"""
        return self.message_queue.copy()
    
    def clear_message_queue(self):
        """Clear the message queue"""
        self.message_queue.clear()

