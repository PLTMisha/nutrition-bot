# Railway Environment Variables Debug Guide

## Issue Description
Railway service variables are configured correctly in the dashboard but not being loaded by the application at runtime.

## Current Status
✅ Variables configured in Railway dashboard:
- TELEGRAM_BOT_TOKEN
- NEON_DATABASE_URL  
- VERCEL_API_URL
- LANGDOCK_API_KEY
- RAILWAY_ENVIRONMENT
- PORT

❌ Application only loads: railway_environment, port
❌ Missing: telegram_bot_token, neon_database_url, vercel_api_url

## Solution Steps Applied

### 1. Simplified railway.toml Configuration
```toml
[build]
builder = "NIXPACKS"

[deploy]
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "ON_FAILURE"

[[services]]
name = "nutrition-bot"

[variables]
PYTHONPATH = "/app"
```

### 2. Added Debug Logging
Added environment variable debugging to `config/settings.py` to see what Railway actually provides.

### 3. Potential Solutions to Try

#### Option A: Use Railway CLI to Set Variables
```bash
railway login
railway link
railway variables set TELEGRAM_BOT_TOKEN=your_token_here
railway variables set NEON_DATABASE_URL=your_db_url_here
railway variables set VERCEL_API_URL=your_vercel_url_here
railway variables set LANGDOCK_API_KEY=your_langdock_key_here
```

#### Option B: Check Variable Scope
In Railway dashboard:
1. Go to Variables tab
2. Ensure variables are set as "Service Variables" not "Shared Variables"
3. Check that they're in the correct environment (production/development)

#### Option C: Case Sensitivity Fix
Railway might be case-sensitive. Try setting variables in lowercase:
- `telegram_bot_token` instead of `TELEGRAM_BOT_TOKEN`
- `neon_database_url` instead of `NEON_DATABASE_URL`
- `vercel_api_url` instead of `VERCEL_API_URL`
- `langdock_api_key` instead of `LANGDOCK_API_KEY`

#### Option D: Force Environment Variable Loading
Add to `config/settings.py`:
```python
class Settings(BaseSettings):
    # ... existing fields ...
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        # Force loading from environment
        env_file_encoding = 'utf-8'
        extra = "ignore"
```

#### Option E: Manual Environment Variable Access
Replace Pydantic settings with direct os.environ access:
```python
import os

# Direct environment variable access
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN') or os.getenv('telegram_bot_token')
NEON_DATABASE_URL = os.getenv('NEON_DATABASE_URL') or os.getenv('neon_database_url')
VERCEL_API_URL = os.getenv('VERCEL_API_URL') or os.getenv('vercel_api_url')
LANGDOCK_API_KEY = os.getenv('LANGDOCK_API_KEY') or os.getenv('langdock_api_key')

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
```

## Next Steps

1. **Deploy with Debug Logging**: The current version will show all available environment variables
2. **Check Railway Logs**: Look for the debug output to see what variables are actually available
3. **Apply Appropriate Solution**: Based on the debug output, apply one of the solutions above
4. **Test Deployment**: Verify that all required variables are loaded correctly

## Railway Deployment Commands

```bash
# If using Railway CLI
railway login
railway link
railway deploy

# Check logs
railway logs
```

## Expected Debug Output

When the app starts, you should see:
```
=== ENVIRONMENT VARIABLES DEBUG ===
RAILWAY_ENVIRONMENT=production
PORT=8000
TELEGRAM_BOT_TOKEN=123456789:ABC...
NEON_DATABASE_URL=postgresql://...
VERCEL_API_URL=https://...
LANGDOCK_API_KEY=sk-...
=== END DEBUG ===
```

If variables are missing from this output, the issue is with Railway's variable injection, not the application code.
