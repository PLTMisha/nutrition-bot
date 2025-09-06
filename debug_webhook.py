#!/usr/bin/env python3
"""
Debug script to check webhook status and manually set it
"""
import asyncio
import os
import sys
from aiogram import Bot
from aiogram.types import WebhookInfo

async def debug_webhook():
    """Debug webhook configuration"""
    
    # Get bot token
    bot_token = "8224416587:AAFIxU22IhjUhmPei0ebwAlHJK2DWTwHX8o"
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN not found in environment variables")
        return
    
    bot = Bot(token=bot_token)
    
    try:
        # Get current webhook info
        print("🔍 Checking current webhook info...")
        webhook_info: WebhookInfo = await bot.get_webhook_info()
        
        print(f"📍 Current webhook URL: {webhook_info.url}")
        print(f"📊 Pending updates: {webhook_info.pending_update_count}")
        print(f"🔗 Max connections: {webhook_info.max_connections}")
        print(f"📝 Allowed updates: {webhook_info.allowed_updates}")
        print(f"❌ Last error date: {webhook_info.last_error_date}")
        print(f"💬 Last error message: {webhook_info.last_error_message}")
        print(f"🔄 Last synchronization error date: {webhook_info.last_synchronization_error_date}")
        
        # Check if webhook URL is correct
        expected_url = "https://nutrition-bot.railway.app/webhook"
        
        if webhook_info.url != expected_url:
            print(f"\n⚠️  Webhook URL mismatch!")
            print(f"Expected: {expected_url}")
            print(f"Current:  {webhook_info.url}")
            
            # Set correct webhook
            print(f"\n🔧 Setting correct webhook URL...")
            await bot.set_webhook(
                url=expected_url,
                allowed_updates=["message", "callback_query", "inline_query"]
            )
            print("✅ Webhook URL updated!")
            
            # Verify the change
            new_webhook_info = await bot.get_webhook_info()
            print(f"✅ New webhook URL: {new_webhook_info.url}")
        else:
            print(f"\n✅ Webhook URL is correct: {webhook_info.url}")
        
        # Test bot info
        print(f"\n🤖 Testing bot connection...")
        bot_info = await bot.get_me()
        print(f"✅ Bot username: @{bot_info.username}")
        print(f"✅ Bot name: {bot_info.first_name}")
        print(f"✅ Bot ID: {bot_info.id}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    # Set bot token for testing
    if len(sys.argv) > 1:
        os.environ['TELEGRAM_BOT_TOKEN'] = sys.argv[1]
    
    asyncio.run(debug_webhook())
