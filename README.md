# Proactive Survey Agent

An AI-powered agent that analyzes user interactions and triggers personalized feedback surveys using Google's Gemini AI.

## 🚀 Features

- **Intelligent Survey Triggering**: Analyzes user sentiment and activity to determine optimal survey timing
- **AI-Powered Analysis**: Uses Google Gemini AI for sentiment analysis and question generation
- **Fallback Mode**: Works without AI using rule-based logic
- **Long-Term Memory (LTM)**: Stores user interaction history for better decision-making
- **RESTful API**: FastAPI-based HTTP API for easy integration
- **Multi-Agent Support**: Can integrate with supervisor systems

## 📋 Prerequisites

- Python 3.8 or higher
- Gemini API Key (optional, for AI features)
- Vercel account (for deployment)

## 🛠️ Local Development

### Setup

1. **Clone the repository**:
```bash
git clone https://github.com/Hassan-Ilyas-Virk/proactive-survey-agent.git
cd proactive-survey-agent
```

2. **Create `.env` file** with your Gemini API key:
```bash
GEMINI_API_KEY=your_actual_api_key_here
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Run the agent**:
```bash
python main.py
```

The API will be available at `http://localhost:8001`

### API Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `GET /status` - Detailed status
- `POST /analyze` - Analyze user and trigger surveys
- `GET /docs` - Interactive API documentation (Swagger UI)

## ☁️ Deploy to Vercel

### Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Vercel CLI** (optional): Install with `npm i -g vercel`

### Deployment Steps

#### Option 1: Deploy via Vercel Dashboard (Recommended)

1. **Push your code to GitHub** (if not already done):
```bash
git add .
git commit -m "Prepare for Vercel deployment"
git push origin main
```

2. **Import Project on Vercel**:
   - Go to [vercel.com/new](https://vercel.com/new)
   - Click "Import Git Repository"
   - Select your `proactive-survey-agent` repository
   - Vercel will automatically detect the `vercel.json` configuration

3. **Configure Environment Variables**:
   - In the Vercel project settings, go to "Environment Variables"
   - Add the following variable:
     - **Name**: `GEMINI_API_KEY`
     - **Value**: Your Gemini API key
     - **Environment**: Production, Preview, Development (select all)

4. **Deploy**:
   - Click "Deploy"
   - Wait for the build to complete
   - Your API will be live at `https://proactive-survey-agent.vercel.app`

#### Option 2: Deploy via Vercel CLI

1. **Install Vercel CLI**:
```bash
npm i -g vercel
```

2. **Login to Vercel**:
```bash
vercel login
```

3. **Deploy**:
```bash
vercel
```

4. **Set Environment Variables**:
```bash
vercel env add GEMINI_API_KEY
# Enter your API key when prompted
```

5. **Deploy to Production**:
```bash
vercel --prod
```

### Post-Deployment

After deployment, your API will be available at:
- **Production**: `https://proactive-survey-agent.vercel.app`
- **Preview**: `https://proactive-survey-agent-git-branch.vercel.app`

### Testing the Deployed API

```bash
# Health check
curl https://proactive-survey-agent.vercel.app/health

# Test analysis endpoint
curl -X POST https://proactive-survey-agent.vercel.app/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "recent_activity": "Support chat with negative sentiment",
    "last_purchase": "Wireless Earbuds",
    "last_survey_date": "2025-09-20"
  }'
```

## 📁 Project Structure

```
.
├── api.py                 # FastAPI application
├── main.py                # Local development entry point
├── api/
│   └── index.py          # Vercel serverless function entry point
├── agents/
│   └── workers/
│       └── proactive_survey_agent.py  # Main agent logic
├── communication/        # Message models and protocols
├── config/              # Configuration files
├── shared/              # Utilities and AI service
├── vercel.json          # Vercel deployment configuration
└── requirements.txt     # Python dependencies
```

## 🔧 Configuration

### Environment Variables

- `GEMINI_API_KEY` (optional): Google Gemini API key for AI features
- `ALLOWED_ORIGINS` (optional): Comma-separated list of frontend origins for CORS. Example for local dev:
  ```bash
  export ALLOWED_ORIGINS="http://localhost:3000,http://localhost:5173"
  python main.py
  ```
  Set the same variable in your Vercel project settings for production (e.g. `https://your-frontend.vercel.app`).

### Configuration Files

- `config/agent_config.json` - Agent configuration
- `config/settings.yaml` - System settings

## 📚 Documentation

- [AI Features Guide](Docs/AI_FEATURES.md) - Detailed AI integration documentation
- [Integration Guide](Docs/INTEGRATION_GUIDE.md) - How to integrate with other systems
- [Deployment Summary](Docs/DEPLOYMENT_SUMMARY.md) - Deployment overview

## 🧪 Testing

```bash
# Run quick test
python quick_test.py

# Run integration tests
pytest test_integration.py

# Run worker tests
pytest test_abstract_worker.py
```

## 📝 API Example

### Request
```json
POST /analyze
{
  "user_id": "user123",
  "recent_activity": "Support chat with negative sentiment",
  "last_purchase": "Wireless Earbuds",
  "last_survey_date": "2025-09-20"
}
```

### Response
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
  "timestamp": "2025-11-20T17:46:09.615299"
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is part of a university course project.

## 🔗 Links

- **GitHub**: [https://github.com/Hassan-Ilyas-Virk/proactive-survey-agent](https://github.com/Hassan-Ilyas-Virk/proactive-survey-agent)
- **Live API**: [https://proactive-survey-agent.vercel.app](https://proactive-survey-agent.vercel.app)
- **API Docs**: [https://proactive-survey-agent.vercel.app/docs](https://proactive-survey-agent.vercel.app/docs)
