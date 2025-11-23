# AI Features - Proactive Survey Agent

## 🤖 AI-Powered Capabilities

This agent uses **Google Gemini AI** to provide intelligent, context-aware survey analysis and generation.

---

## 🧠 AI Features

### 1. **AI Sentiment Analysis**
Instead of simple keyword matching, the agent uses Gemini to:
- Understand context and nuance in user feedback
- Detect emotions beyond positive/negative/neutral
- Provide confidence scores for sentiment predictions
- Explain reasoning behind sentiment classification

**Example:**
```
Input: "The product is okay but support took forever to respond"
AI Output: {
  "sentiment": "negative",
  "confidence": 78,
  "reason": "Mixed sentiment with stronger negative weight on support experience"
}
```

### 2. **Personalized Question Generation**
The AI generates custom survey questions based on:
- User's specific situation and history
- Type of interaction (purchase, support, browsing)
- Detected sentiment and context
- Previous feedback patterns

**Example:**
```
Context: User bought "Wireless Earbuds", negative sentiment about support

AI-Generated Questions:
1. "We're sorry to hear about your support experience. How can we make this right for you?"
2. "Regarding your Wireless Earbuds, what specific issue did you encounter?"
3. "On a scale of 1-10, how would you rate the responsiveness of our support team?"
```

### 3. **Intelligent Priority Assessment**
AI helps determine survey urgency by analyzing:
- Severity of negative sentiment
- Customer lifetime value indicators
- Purchase recency and value
- Support interaction history

---

## ⚙️ How It Works

### Architecture
```
User Activity → AI Sentiment Analysis (Gemini) → Decision Logic → AI Question Generation (Gemini) → Survey Output
                        ↓                                                    ↓
                   LTM Storage                                          LTM Storage
```

### AI Service (`shared/ai_service.py`)
- **`analyze_sentiment_ai()`** - Analyzes text using Gemini
- **`generate_survey_questions_ai()`** - Creates personalized questions
- **Fallback Mode** - Uses rule-based logic if API unavailable

### Integration Points
1. **Sentiment Analysis** - Called in `_analyze_sentiment()`
2. **Question Generation** - Called in `_make_decision()`
3. **LTM Learning** - Stores AI insights for future reference

---

## 🔑 Setup

### 1. Get Gemini API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key

### 2. Configure Agent
Create `.env` file:
```bash
GEMINI_API_KEY=your_api_key_here
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Test AI Features
```bash
python3 quick_test.py
```

You should see:
```
✓ AI Service initialized with Gemini
✓ AI Sentiment Analysis: negative (85%)
✓ AI Generated 3 questions
```

---

## 🔄 Fallback Mode

If no API key is provided or API fails:
- Agent continues to work with rule-based logic
- Uses keyword matching for sentiment
- Uses template-based questions
- No degradation in basic functionality

**Fallback Indicators:**
```python
"ai_enabled": false,
"ai_model": "fallback",
"reason": "Keyword-based analysis (fallback mode)"
```

---

## 📊 AI vs Fallback Comparison

| Feature | AI Mode (Gemini) | Fallback Mode |
|---------|------------------|---------------|
| Sentiment Analysis | Context-aware, nuanced | Keyword-based |
| Confidence Score | AI-calculated | Fixed ranges |
| Question Quality | Personalized, adaptive | Template-based |
| Context Understanding | Deep semantic analysis | Pattern matching |
| Response Time | ~1-2 seconds | <0.1 seconds |
| API Required | Yes | No |

---

## 🧪 Testing AI Features

### Test Sentiment Analysis
```python
from shared.ai_service import ai_service

result = ai_service.analyze_sentiment_ai(
    "The product is great but shipping was slow"
)
print(result)
# Output: {'sentiment': 'neutral', 'confidence': 65, 'reason': '...'}
```

### Test Question Generation
```python
questions = ai_service.generate_survey_questions_ai(
    user_context={
        "recent_activity": "Support chat about defective item",
        "last_purchase": "Headphones"
    },
    survey_type="Product Experience",
    num_questions=3
)
print(questions)
```

---

## 💡 AI Prompt Engineering

The agent uses carefully crafted prompts for:

### Sentiment Analysis Prompt
```
Analyze the sentiment of the following user activity text.
Classify it as: positive, negative, or neutral.
Also rate your confidence (0-100) and provide a brief reason.

User Activity: "{text}"

Response format (JSON): {...}
```

### Question Generation Prompt
```
Generate {num_questions} personalized survey questions for a user.

Survey Type: {survey_type}
User Context:
- Recent Activity: {activity}
- Last Purchase: {purchase}

Requirements:
- Questions should be specific to the user's context
- Keep questions concise and actionable
- Mix rating scales with open-ended questions
- Be empathetic and customer-focused
```

---

## 📈 AI Learning & Improvement

The agent stores AI insights in LTM:
- Sentiment analysis results
- Generated questions
- User responses (when integrated)
- Confidence scores

This data can be used to:
- Improve future predictions
- Identify patterns
- Train custom models
- Optimize question templates

---

## 🔐 Security Best Practices

1. **Never commit `.env` file** - It's in `.gitignore`
2. **Use environment variables** - Never hardcode API keys
3. **Rotate keys regularly** - Update API key periodically
4. **Monitor API usage** - Track costs and limits
5. **Use fallback mode for testing** - No API key needed

---

## 🚀 Advanced Usage

### Custom AI Models
To use different models, edit `shared/ai_service.py`:
```python
self.model = genai.GenerativeModel('gemini-pro')  # or gemini-1.5-pro
```

### Adjust AI Behavior
Modify prompts in `ai_service.py` to:
- Change tone and style
- Add industry-specific context
- Customize question formats
- Adjust confidence thresholds

### Multi-Model Approach
You can integrate multiple AI providers:
- Gemini for sentiment analysis
- OpenAI for question generation
- Claude for response summarization

---

## 📞 Troubleshooting

### "AI Service initialized in fallback mode"
- Check if `.env` file exists
- Verify API key is correct
- Ensure `python-dotenv` is installed

### "AI sentiment analysis failed"
- Check internet connection
- Verify API key has permissions
- Check Gemini API quota limits

### Slow Response Times
- AI calls add 1-2 seconds latency
- Consider caching frequent queries
- Use fallback mode for development

---

## 📚 Additional Resources

- [Google Gemini API Docs](https://ai.google.dev/docs)
- [Python SDK](https://github.com/google/generative-ai-python)
- [Best Practices](https://ai.google.dev/docs/safety_best_practices)

---

**Status:** ✅ AI features fully integrated and tested!

