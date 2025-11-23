"""
Vercel serverless function entry point for FastAPI application
"""
import sys
import os
import importlib.util
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the FastAPI app from api.py (avoiding conflict with api/ directory)
spec = importlib.util.spec_from_file_location("api_module", project_root / "api.py")
api_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api_module)

# Export the app for Vercel (Vercel Python runtime expects 'app' or 'handler')
app = api_module.app
handler = app

