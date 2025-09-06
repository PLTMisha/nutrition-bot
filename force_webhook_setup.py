#!/usr/bin/env python3
"""
Force webhook setup script - manually set webhook for the bot
"""
import asyncio
import os
from aiogram import Bot

async def force_webhook_setup():
    """Force webhook setup for the bot"""
    
    # Get bot token from environment
    bot_token = "8224416587:AAFIxU22IhjUhmPei0ebwAlHJK2DWTwHX8o"
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN not found in environment")
        return
    
    bot = Bot(token=bot_token)
    
    try:
        # Get current webhook info
        webhook_info = await bot.get_webhook_info()
        print(f"🔗 Current Webhook Info:")
        print(f"  URL: {webhook_info.url}")
        print(f"  Pending updates: {webhook_info.pending_update_count}")
        print(f"  Last error: {webhook_info.last_error_message}")
        print(f"  Last error date: {webhook_info.last_error_date}")
        
        # Delete current webhook
        print(f"\n🗑️ Deleting current webhook...")
        await bot.delete_webhook(drop_pending_updates=True)
        print("✅ Webhook deleted")
        
        # Wait a moment
        await asyncio.sleep(2)
        
        # Set new webhook
        webhook_url = "https://nutrition-bot.railway.app/webhook"
        print(f"\n🔄 Setting new webhook: {webhook_url}")
        
        result = await bot.set_webhook(
            url=webhook_url,
            allowed_updates=["message", "callback_query"],
            drop_pending_updates=True
        )
        
        if result:
            print("✅ Webhook set successfully")
        else:
            print("❌ Failed to set webhook")
        
        # Verify webhook was set
        await asyncio.sleep(2)
        new_webhook_info = await bot.get_webhook_info()
        print(f"\n✅ New Webhook Info:")
        print(f"  URL: {new_webhook_info.url}")
        print(f"  Pending updates: {new_webhook_info.pending_update_count}")
        
        # Test webhook endpoint
        print(f"\n🧪 Testing webhook endpoint...")
        import aiohttp
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    webhook_url,
                    json={"test": "data"},
                    headers={"Content-Type": "application/json"},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    print(f"  Status: {response.status}")
                    if response.status == 200:
                        print("✅ Webhook endpoint is responding!")
                    else:
                        print(f"❌ Webhook endpoint returned {response.status}")
                        text = await response.text()
                        print(f"  Response: {text[:200]}...")
            except Exception as e:
                print(f"❌ Error testing webhook: {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(force_webhook_setup())
