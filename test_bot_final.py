#!/usr/bin/env python3
"""
Final test script to verify bot functionality after middleware fix
"""
import asyncio
import os
import sys
from datetime import datetime

import aiohttp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TEST_CHAT_ID = os.getenv('TEST_CHAT_ID', '1234567890')  # Replace with your chat ID

async def send_test_message():
    """Send a test message to the bot"""
    if not TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN not found in environment")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    test_message = f"🧪 Bot Test - {datetime.now().strftime('%H:%M:%S')}\n\nTesting bot functionality after middleware fix."
    
    payload = {
        'chat_id': TEST_CHAT_ID,
        'text': test_message,
        'parse_mode': 'HTML'
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get('ok'):
                        print(f"✅ Test message sent successfully!")
                        print(f"Message ID: {result['result']['message_id']}")
                        return True
                    else:
                        print(f"❌ Telegram API error: {result.get('description', 'Unknown error')}")
                        return False
                else:
                    print(f"❌ HTTP error: {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Error sending test message: {e}")
        return False

async def get_bot_info():
    """Get bot information to verify it's working"""
    if not TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN not found in environment")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get('ok'):
                        bot_info = result['result']
                        print(f"✅ Bot is active!")
                        print(f"Bot name: @{bot_info['username']}")
                        print(f"Bot ID: {bot_info['id']}")
                        print(f"First name: {bot_info['first_name']}")
                        return True
                    else:
                        print(f"❌ Telegram API error: {result.get('description', 'Unknown error')}")
                        return False
                else:
                    print(f"❌ HTTP error: {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Error getting bot info: {e}")
        return False

async def check_railway_health():
    """Check Railway deployment health"""
    railway_url = "https://nutrition-bot-production.up.railway.app/health"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(railway_url, timeout=10) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Railway deployment is healthy!")
                    print(f"Status: {result.get('status', 'unknown')}")
                    print(f"Database: {result.get('db', 'unknown')}")
                    return True
                else:
                    print(f"❌ Railway health check failed: {response.status}")
                    return False
    except asyncio.TimeoutError:
        print("❌ Railway health check timed out")
        return False
    except Exception as e:
        print(f"❌ Error checking Railway health: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 Starting bot functionality test...")
    print("=" * 50)
    
    # Test 1: Check bot info
    print("\n1. Checking bot information...")
    bot_active = await get_bot_info()
    
    # Test 2: Check Railway deployment
    print("\n2. Checking Railway deployment...")
    railway_healthy = await check_railway_health()
    
    # Test 3: Send test message (optional)
    print("\n3. Sending test message...")
    if TELEGRAM_BOT_TOKEN and TEST_CHAT_ID != '1234567890':
        message_sent = await send_test_message()
    else:
        print("⚠️  Skipping test message (TEST_CHAT_ID not configured)")
        message_sent = None
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS:")
    print(f"Bot Active: {'✅' if bot_active else '❌'}")
    print(f"Railway Healthy: {'✅' if railway_healthy else '❌'}")
    if message_sent is not None:
        print(f"Test Message: {'✅' if message_sent else '❌'}")
    
    if bot_active and railway_healthy:
        print("\n🎉 Bot is ready for testing!")
        print("\nTo test manually:")
        print("1. Open Telegram")
        print("2. Search for @mishatgtestbot")
        print("3. Send /start command")
        print("4. Try sending a food name like 'apple' or 'яблоко'")
        return True
    else:
        print("\n❌ Bot has issues that need to be resolved")
        return False

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
