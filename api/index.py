"""
Vercel serverless function entry point for FastAPI application
"""
import sys
import os
import traceback
import importlib.util
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set working directory to project root for relative path resolution
try:
    os.chdir(project_root)
except Exception:
    # If chdir fails, continue anyway
    pass

try:
    # Import the FastAPI app from api.py (avoiding conflict with api/ directory)
    spec = importlib.util.spec_from_file_location("api_module", project_root / "api.py")
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load spec from {project_root / 'api.py'}")
    
    api_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(api_module)
    
    # Export the app for Vercel (Vercel Python runtime expects 'app' or 'handler')
    if not hasattr(api_module, 'app'):
        raise AttributeError("api.py does not export 'app'")
    
    app = api_module.app
    handler = app
except Exception as e:
    # Create a minimal error handler app if import fails
    from fastapi import FastAPI, HTTPException
    
    error_app = FastAPI(title="Error Handler")
    error_traceback = traceback.format_exc()
    
    @error_app.get("/")
    @error_app.get("/{path:path}")
    async def error_handler(path: str = ""):
        # In production, don't expose full traceback, but log it
        print(f"Initialization error: {str(e)}")
        print(f"Traceback: {error_traceback}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initialize application: {str(e)}. Check server logs for details."
        )
    
    app = error_app
    handler = app

