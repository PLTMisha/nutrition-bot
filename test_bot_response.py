#!/usr/bin/env python3
"""
Test script to send a message to the bot and check if it responds
"""
import asyncio
import os
from aiogram import Bot
from aiogram.types import Message

async def test_bot():
    """Test if bot is responding to messages"""
    
    # Get bot token from environment or prompt user
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN not found in environment")
        print("Please set the environment variable or run this on Railway")
        return
    
    bot = Bot(token=bot_token)
    
    try:
        # Get bot info
        bot_info = await bot.get_me()
        print(f"🤖 Bot Info:")
        print(f"  Username: @{bot_info.username}")
        print(f"  Name: {bot_info.first_name}")
        print(f"  ID: {bot_info.id}")
        
        # Get webhook info
        webhook_info = await bot.get_webhook_info()
        print(f"\n🔗 Webhook Info:")
        print(f"  URL: {webhook_info.url}")
        print(f"  Pending updates: {webhook_info.pending_update_count}")
        print(f"  Last error: {webhook_info.last_error_message}")
        print(f"  Last error date: {webhook_info.last_error_date}")
        
        # Check if webhook is set correctly
        expected_webhook = "https://nutrition-bot.railway.app/webhook"
        if webhook_info.url == expected_webhook:
            print("✅ Webhook URL is correct")
        else:
            print(f"❌ Webhook URL mismatch!")
            print(f"  Expected: {expected_webhook}")
            print(f"  Actual: {webhook_info.url}")
        
        # Test webhook endpoint directly
        print(f"\n🧪 Testing webhook endpoint...")
        import aiohttp
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    "https://nutrition-bot.railway.app/webhook",
                    json={"test": "data"},
                    headers={"Content-Type": "application/json"}
                ) as response:
                    print(f"  Status: {response.status}")
                    if response.status == 200:
                        print("✅ Webhook endpoint is responding")
                    else:
                        print(f"❌ Webhook endpoint returned {response.status}")
                        text = await response.text()
                        print(f"  Response: {text}")
            except Exception as e:
                print(f"❌ Error testing webhook: {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(test_bot())
