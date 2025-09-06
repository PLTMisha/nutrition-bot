#!/usr/bin/env python3
"""
Test script to check Railway environment detection
"""
import os
import sys

print("=== RAILWAY ENVIRONMENT TEST ===")

# Check Railway-specific variables
railway_vars = ['RAILWAY_PROJECT_ID', 'RAILWAY_SERVICE_ID', 'RAILWAY_DEPLOYMENT_ID']
print("\nRailway-specific variables:")
for var in railway_vars:
    value = os.getenv(var)
    print(f"  {var}: {'✅ SET' if value else '❌ NOT SET'}")
    if value:
        print(f"    Value: {value[:20]}...")

# Check other relevant variables
other_vars = ['PORT', 'RAILWAY_PUBLIC_DOMAIN', 'RAILWAY_STATIC_URL']
print("\nOther Railway variables:")
for var in other_vars:
    value = os.getenv(var)
    print(f"  {var}: {'✅ SET' if value else '❌ NOT SET'}")
    if value:
        print(f"    Value: {value}")

# Test environment detection logic
is_railway = any(os.getenv(var) for var in railway_vars)
environment = "production" if is_railway else "development"

print(f"\n🔍 Environment Detection:")
print(f"  Is Railway: {'✅ YES' if is_railway else '❌ NO'}")
print(f"  Environment: {environment}")
print(f"  Mode: {'WEBHOOK' if environment == 'production' else 'POLLING'}")

# Import and test settings
try:
    sys.path.append('.')
    from config.settings import settings
    print(f"\n⚙️ Settings:")
    print(f"  Railway Environment: {settings.railway_environment}")
    print(f"  Port: {settings.port}")
except Exception as e:
    print(f"\n❌ Error importing settings: {e}")

print("\n=== END TEST ===")
