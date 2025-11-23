# Vercel Deployment Fixes

## Issues Fixed

### 1. Path Resolution Issues
**Problem**: Relative paths didn't work correctly in Vercel's serverless environment where the working directory might be different.

**Fix**: 
- Updated `shared/utils.py` → `load_json_config()` to resolve paths relative to project root
- Updated `api/index.py` to set working directory to project root
- Updated `api.py` to set working directory before loading config

### 2. File System Access
**Problem**: Vercel's serverless functions have a read-only filesystem except for `/tmp`.

**Fix**:
- Updated `LTMFileStorage` class to detect serverless environments (checks for `VERCEL`, `AWS_LAMBDA_FUNCTION_NAME`, or `FUNCTION_TARGET` env vars)
- Automatically uses `/tmp/ltm` for LTM storage in serverless environments

### 3. Error Handling
**Problem**: Import errors weren't being caught, causing cryptic 500 errors.

**Fix**:
- Added comprehensive error handling in `api/index.py`
- Added error handler app that provides better error messages
- Added traceback logging for debugging

## Files Modified

1. **`api/index.py`** - Added error handling and path resolution
2. **`api.py`** - Added working directory setup
3. **`shared/utils.py`** - Fixed path resolution in `load_json_config()` and LTM storage

## Next Steps

1. **Commit and push the fixes**:
   ```bash
   git add .
   git commit -m "Fix Vercel deployment: path resolution and serverless compatibility"
   git push origin main
   ```

2. **Redeploy on Vercel**:
   - If using Vercel dashboard: It will auto-deploy on push
   - If using CLI: Run `vercel --prod`

3. **Check the logs**:
   - Go to Vercel Dashboard → Your Project → Functions → View Logs
   - Look for any initialization errors

4. **Test the endpoints**:
   ```bash
   # Health check
   curl https://proactive-survey-agent.vercel.app/health
   
   # Root endpoint
   curl https://proactive-survey-agent.vercel.app/
   ```

## Troubleshooting

If you still get errors:

1. **Check Vercel Function Logs**:
   - Go to Vercel Dashboard → Your Project → Functions
   - Click on the function to see detailed logs
   - Look for Python tracebacks

2. **Verify Environment Variables**:
   - Make sure `GEMINI_API_KEY` is set (if using AI features)
   - Check Vercel Dashboard → Settings → Environment Variables

3. **Check File Structure**:
   - Ensure `config/agent_config.json` exists in your repository
   - Verify all Python files are present

4. **Test Locally with Vercel CLI**:
   ```bash
   vercel dev
   ```
   This will simulate the Vercel environment locally.

## Expected Behavior

After these fixes:
- ✅ Config files load correctly using absolute paths
- ✅ LTM storage uses `/tmp` in serverless (writable)
- ✅ Better error messages if something fails
- ✅ Supervisor registration failures don't crash the app (they're already handled)

## Notes

- **LTM Storage**: In serverless, LTM data is stored in `/tmp` which is ephemeral (cleared between invocations). For persistent storage, consider using a database or external storage service.
- **Supervisor Registration**: The supervisor auto-registration will fail on Vercel (expected, as supervisor is on localhost). This is handled gracefully and won't affect API functionality.

