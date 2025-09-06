#!/usr/bin/env python3
"""
Test if Railway has deployed our latest changes
"""
import requests
import json

def test_railway_deployment():
    """Test Railway deployment status"""
    
    print("🔍 Testing Railway deployment status...")
    
    try:
        # Test health endpoint
        print("\n1. Testing health endpoint...")
        response = requests.get("https://nutrition-bot.railway.app/health", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            health_data = response.json()
            print(f"   Service: {health_data.get('status', 'unknown')}")
            print(f"   Database: {health_data.get('database', 'unknown')}")
            print(f"   Bot: {health_data.get('bot', 'unknown')}")
            print(f"   Bot Username: {health_data.get('bot_username', 'unknown')}")
        
        # Test root endpoint
        print("\n2. Testing root endpoint...")
        response = requests.get("https://nutrition-bot.railway.app/", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            root_data = response.json()
            print(f"   Service: {root_data.get('service', 'unknown')}")
            print(f"   Version: {root_data.get('version', 'unknown')}")
            print(f"   Status: {root_data.get('status', 'unknown')}")
        
        # Test webhook endpoint
        print("\n3. Testing webhook endpoint...")
        response = requests.post(
            "https://nutrition-bot.railway.app/webhook",
            json={"test": "data"},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 404:
            print("   ❌ Webhook endpoint not found - Railway is likely in POLLING mode")
        elif response.status_code == 200:
            print("   ✅ Webhook endpoint responding - Railway is in WEBHOOK mode")
        else:
            print(f"   ⚠️ Unexpected status: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
        
        # Test if we can determine the deployment mode
        print("\n4. Analyzing deployment mode...")
        if response.status_code == 404:
            print("   🔍 Analysis: Railway is running in POLLING mode")
            print("   📝 This means our environment detection is not working")
            print("   💡 Solution: Railway needs to be forced into WEBHOOK mode")
        
        print("\n" + "="*50)
        print("CONCLUSION:")
        if response.status_code == 404:
            print("❌ Railway is NOT using our latest code changes")
            print("❌ Bot is running in POLLING mode instead of WEBHOOK mode")
            print("💡 Need to force Railway to redeploy or add FORCE_WEBHOOK_MODE=true")
        else:
            print("✅ Railway deployment is working correctly")
            
    except Exception as e:
        print(f"❌ Error testing deployment: {e}")

if __name__ == "__main__":
    test_railway_deployment()
