import asyncio
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

async def check_webhook_status():
    """Check webhook status and bot availability"""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN not found in environment")
        return False
    
    try:
        async with aiohttp.ClientSession() as session:
            # Check webhook info
            webhook_url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
            async with session.get(webhook_url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data['ok']:
                        webhook_info = data['result']
                        print("✅ Webhook Status:")
                        print(f"   URL: {webhook_info.get('url', 'Not set')}")
                        print(f"   Has custom certificate: {webhook_info.get('has_custom_certificate', False)}")
                        print(f"   Pending updates: {webhook_info.get('pending_update_count', 0)}")
                        print(f"   Last error date: {webhook_info.get('last_error_date', 'None')}")
                        print(f"   Last error message: {webhook_info.get('last_error_message', 'None')}")
                        print(f"   Max connections: {webhook_info.get('max_connections', 'Default')}")
                        return True
                    else:
                        print(f"❌ Webhook check failed: {data}")
                        return False
                else:
                    print(f"❌ HTTP error {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Error checking webhook: {e}")
        return False

async def test_bot_response():
    """Test if bot responds to getMe"""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN not found")
        return False
    
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://api.telegram.org/bot{bot_token}/getMe"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data['ok']:
                        bot_info = data['result']
                        print("✅ Bot Info:")
                        print(f"   Name: {bot_info.get('first_name')}")
                        print(f"   Username: @{bot_info.get('username')}")
                        print(f"   ID: {bot_info.get('id')}")
                        print(f"   Can join groups: {bot_info.get('can_join_groups')}")
                        print(f"   Can read all group messages: {bot_info.get('can_read_all_group_messages')}")
                        return True
                    else:
                        print(f"❌ Bot check failed: {data}")
                        return False
                else:
                    print(f"❌ HTTP error {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Error checking bot: {e}")
        return False

async def main():
    print("🔍 Checking Telegram Bot Status...")
    print("=" * 50)
    
    bot_ok = await test_bot_response()
    print()
    webhook_ok = await check_webhook_status()
    
    print("\n" + "=" * 50)
    if bot_ok and webhook_ok:
        print("✅ Bot is configured and webhook is active")
        print("🚀 Bot should be receiving messages on Railway")
    else:
        print("❌ Issues detected with bot configuration")

if __name__ == "__main__":
    asyncio.run(main())
