# Vercel Deployment Guide

## ✅ What's Been Set Up

1. **`vercel.json`** - Vercel configuration file that routes all requests to the Python serverless function
2. **`api/index.py`** - Serverless function entry point that imports and exports your FastAPI app
3. **Updated `README.md`** - Includes deployment instructions

## 🚀 Quick Deployment Steps

### Method 1: Via Vercel Dashboard (Easiest)

1. **Push to GitHub** (if not already done):
   ```bash
   git add .
   git commit -m "Add Vercel deployment configuration"
   git push origin main
   ```

2. **Go to Vercel**:
   - Visit [vercel.com/new](https://vercel.com/new)
   - Click "Import Git Repository"
   - Select your repository: `Hassan-Ilyas-Virk/proactive-survey-agent`
   - Click "Import"

3. **Configure Project**:
   - Vercel will auto-detect the configuration
   - **Framework Preset**: Leave as "Other" or "Python"
   - **Root Directory**: `./` (default)
   - Click "Deploy"

4. **Add Environment Variable**:
   - After first deployment, go to Project Settings → Environment Variables
   - Add: `GEMINI_API_KEY` = `your_api_key_here`
   - Select all environments (Production, Preview, Development)
   - Redeploy if needed

5. **Done!** Your API will be live at `https://proactive-survey-agent.vercel.app`

### Method 2: Via Vercel CLI

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Login**:
   ```bash
   vercel login
   ```

3. **Deploy**:
   ```bash
   vercel
   ```

4. **Add Environment Variable**:
   ```bash
   vercel env add GEMINI_API_KEY
   # Enter your API key when prompted
   ```

5. **Deploy to Production**:
   ```bash
   vercel --prod
   ```

## 🧪 Test Your Deployment

After deployment, test your API:

```bash
# Health check
curl https://proactive-survey-agent.vercel.app/health

# Test analyze endpoint
curl -X POST https://proactive-survey-agent.vercel.app/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "recent_activity": "Support chat",
    "last_purchase": "Product X",
    "last_survey_date": "2025-01-01"
  }'

# View API docs
# Open in browser: https://proactive-survey-agent.vercel.app/docs
```

## 📝 Important Notes

1. **Environment Variables**: Make sure to add `GEMINI_API_KEY` in Vercel dashboard
2. **File Storage**: LTM file storage works in serverless, but files are ephemeral (reset on each deployment)
3. **Supervisor Registration**: The supervisor auto-registration will fail on Vercel (this is expected and won't break the API)
4. **Cold Starts**: First request after inactivity may take 1-2 seconds (normal for serverless)

## 🔧 Troubleshooting

### Build Fails
- Check that all dependencies are in `requirements.txt`
- Verify Python version compatibility (Vercel uses Python 3.9+)

### 500 Errors
- Check Vercel function logs in the dashboard
- Verify environment variables are set correctly
- Ensure `GEMINI_API_KEY` is added (if using AI features)

### Import Errors
- Verify `api/index.py` can import from `api.py`
- Check that all file paths are correct

## 📚 Resources

- [Vercel Python Documentation](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- Your API Docs: [https://proactive-survey-agent.vercel.app/docs](https://proactive-survey-agent.vercel.app/docs)

