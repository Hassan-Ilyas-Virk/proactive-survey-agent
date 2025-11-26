"""AI Service for Gemini API Integration"""
import os
import logging
import random
from typing import Optional, Dict, List

# Load environment variables (safe for environments without .env)
try:
from dotenv import load_dotenv
load_dotenv()
except Exception:
    pass  # .env file not needed in production (Vercel uses env vars)

logger = logging.getLogger(__name__)

# Try to import Gemini, but continue without it if not available
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    logger.warning("google-generativeai not installed. AI features will use fallback logic.")
    GENAI_AVAILABLE = False
    genai = None

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY and GENAI_AVAILABLE:
    try:
    genai.configure(api_key=GEMINI_API_KEY)
    logger.info("Gemini API configured successfully")
    except Exception as e:
        logger.warning(f"Failed to configure Gemini: {e}")
elif not GEMINI_API_KEY:
    logger.warning("GEMINI_API_KEY not found. AI features will use fallback logic.")
elif not GENAI_AVAILABLE:
    logger.warning("Gemini package not available. AI features will use fallback logic.")


class AIService:
    """Service for AI-powered analysis using Gemini"""
    
    def __init__(self):
        self.model = None
        self.ai_enabled = False
        
        if GEMINI_API_KEY and GENAI_AVAILABLE:
            try:
                self.model = genai.GenerativeModel('gemini-pro')
                self.ai_enabled = True
                logger.info("AI Service initialized with Gemini")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {e}")
                self.ai_enabled = False
        else:
            logger.info("AI Service initialized in fallback mode")
    
    def analyze_sentiment_ai(self, text: str) -> Dict:
        """
        Use AI to analyze sentiment from text
        
        Args:
            text: User activity text to analyze
            
        Returns:
            Dictionary with sentiment, confidence, and reasoning
        """
        if not self.ai_enabled:
            return self._fallback_sentiment(text)
        
        try:
            prompt = f"""Analyze the sentiment of the following user activity text.
Classify it as: positive, negative, or neutral.
Also rate your confidence (0-100) and provide a brief reason.

User Activity: "{text}"

Response format (JSON):
{{
    "sentiment": "positive/negative/neutral",
    "confidence": 85,
    "reason": "brief explanation"
}}"""

            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Parse AI response
            import json
            # Extract JSON from response (handle markdown code blocks)
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(result_text)
            logger.info(f"AI Sentiment Analysis: {result['sentiment']} ({result['confidence']}%)")
            return result
            
        except Exception as e:
            logger.warning(f"AI sentiment analysis failed: {e}. Using fallback.")
            return self._fallback_sentiment(text)
    
    def generate_survey_questions_ai(
        self, 
        user_context: Dict,
        survey_type: str,
        num_questions: int = 3
    ) -> List[str]:
        """
        Use AI to generate personalized survey questions
        
        Args:
            user_context: Dictionary with user_id, activity, purchase info
            survey_type: Type of survey (Product Experience, Support Quality, etc.)
            num_questions: Number of questions to generate
            
        Returns:
            List of personalized survey questions
        """
        if not self.ai_enabled:
            return self._fallback_questions(survey_type, user_context, num_questions)
        
        try:
            prompt = f"""Generate {num_questions} personalized survey questions for a user.

Survey Type: {survey_type}
User Context:
- Recent Activity: {user_context.get('recent_activity', 'N/A')}
- Last Purchase: {user_context.get('last_purchase', 'N/A')}

Requirements:
- Questions should be specific to the user's context
- Keep questions concise and actionable
- Mix rating scales with open-ended questions
- Be empathetic and customer-focused

Generate exactly {num_questions} questions as a JSON array:
["Question 1?", "Question 2?", "Question 3?"]"""

            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Parse AI response
            import json
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            elif "[" in result_text:
                # Extract just the JSON array
                start = result_text.find("[")
                end = result_text.rfind("]") + 1
                result_text = result_text[start:end]
            
            questions = json.loads(result_text)
            logger.info(f"AI Generated {len(questions)} questions")
            return questions
            
        except Exception as e:
            logger.warning(f"AI question generation failed: {e}. Using fallback.")
            return self._fallback_questions(survey_type, user_context, num_questions)
    
    def _fallback_sentiment(self, text: str) -> Dict:
        """Fallback sentiment analysis using keywords"""
        text_lower = text.lower()
        
        negative_keywords = [
            "negative", "complaint", "issue", "problem", "dissatisfied",
            "unhappy", "disappointed", "frustrated", "broken", "defect",
            "unwell", "sick", "ill", "bad", "terrible", "awful", "sad"
        ]
        positive_keywords = [
            "positive", "happy", "satisfied", "great", "excellent",
            "fantastic", "amazing", "love", "awesome", "delighted"
        ]
        
        negative_count = sum(1 for kw in negative_keywords if kw in text_lower)
        positive_count = sum(1 for kw in positive_keywords if kw in text_lower)
        
        if negative_count > positive_count:
            sentiment = "negative"
            confidence = min(60 + (negative_count * 10), 95)
        elif positive_count > negative_count:
            sentiment = "positive"
            confidence = min(60 + (positive_count * 10), 95)
        else:
            sentiment = "neutral"
            confidence = 50
        
        return {
            "sentiment": sentiment,
            "confidence": confidence,
            "reason": "Keyword-based analysis (fallback mode)"
        }
    
    def _fallback_questions(self, survey_type: str, context: Dict, num_questions: int = 3) -> List[str]:
        """Fallback question generation"""
        last_purchase = context.get('last_purchase', 'product')
        
        questions_map = {
            "Product Experience": [
                f"How satisfied are you with your {last_purchase}?",
                "Would you recommend this product to others?",
                "What could we improve about this product?",
                f"What aspects of your {last_purchase} exceeded expectations?",
                "Did the product arrive in the condition you expected?",
                "Is there any feature you wish this product had?"
            ],
            "Support Quality": [
                "How would you rate your support experience?",
                "Was your issue resolved effectively?",
                "What could we do to improve our support?",
                "Did our support team follow up with you in a timely manner?",
                "Is there something that would have made the support process easier?"
            ],
            "General Feedback": [
                "What do you enjoy most about our service?",
                "Would you recommend us to friends?",
                "Any features you'd like to see?",
                "How can we make your overall experience even better?",
                "Is there a feature you rarely use that we could improve?"
            ],
            "Engagement Check": [
                "How has your experience been with us?",
                "Is there anything we can help you with?",
                "What would make your experience better?",
                "Have you noticed any recent changes that you liked or disliked?",
                "What would encourage you to engage with us more often?"
            ]
        }
        
        templates = questions_map.get(survey_type, [
            "How satisfied are you overall?",
            "What can we improve?",
            "Any additional feedback?",
            "Is there anything preventing you from being fully satisfied?",
            "How likely are you to continue using our service?"
        ])

        if num_questions >= len(templates):
            random.shuffle(templates)
            return templates[:num_questions]

        return random.sample(templates, k=num_questions)


# Singleton instance
ai_service = AIService()

