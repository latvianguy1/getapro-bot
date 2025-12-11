"""
Telegram Bot Setup Helper

This script helps you set up your Telegram bot for job notifications.
"""

import requests
import json
from pathlib import Path

CONFIG_FILE = Path(__file__).parent / "config.json"


def get_bot_info(token: str) -> dict:
    """Get bot information to verify token is correct"""
    url = f"https://api.telegram.org/bot{token}/getMe"
    try:
        response = requests.get(url, timeout=10)
        return response.json()
    except Exception as e:
        return {"ok": False, "description": str(e)}


def get_updates(token: str) -> dict:
    """Get recent updates/messages to the bot"""
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    try:
        response = requests.get(url, timeout=10)
        return response.json()
    except Exception as e:
        return {"ok": False, "description": str(e)}


def send_test_message(token: str, chat_id: str) -> dict:
    """Send a test message"""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': '✅ GetaPro Job Monitor ir veiksmīgi konfigurēts!\n\nJūs saņemsiet paziņojumus par jauniem darba pasūtījumiem.',
        'parse_mode': 'HTML'
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        return {"ok": False, "description": str(e)}


def update_config(token: str, chat_id: str):
    """Update the config file with bot credentials"""
    config = {}
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
    
    config['telegram_bot_token'] = token
    config['telegram_chat_id'] = chat_id
    
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Config updated: {CONFIG_FILE}")


def main():
    print("=" * 60)
    print("🤖 GetaPro Job Monitor - Telegram Setup")
    print("=" * 60)
    
    print("""
📋 INSTRUKCIJAS:

1. Atveriet Telegram un meklējiet @BotFather
2. Nosūtiet /newbot un sekojiet instrukcijām
3. Saņemsiet bot token (piem: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz)
4. Atveriet savu jauno botu un nosūtiet /start vai jebkādu ziņu
5. Ievadiet token šeit zemāk
""")
    
    # Get bot token
    token = input("📝 Ievadiet bot token: ").strip()
    
    if not token:
        print("❌ Token nav ievadīts!")
        return
    
    # Verify token
    print("\n🔍 Pārbaudu token...")
    info = get_bot_info(token)
    
    if not info.get('ok'):
        print(f"❌ Nederīgs token: {info.get('description', 'Unknown error')}")
        return
    
    bot_name = info['result']['username']
    print(f"✅ Bot atrasts: @{bot_name}")
    
    # Get chat ID
    print(f"""
📱 Tagad:
1. Atveriet Telegram
2. Meklējiet @{bot_name}
3. Nosūtiet botam jebkādu ziņu (piem: /start vai "hello")
4. Nospiediet Enter šeit...
""")
    
    input("Nospiediet Enter kad esat nosūtījis ziņu botam...")
    
    # Get updates to find chat ID
    updates = get_updates(token)
    
    if not updates.get('ok') or not updates.get('result'):
        print("❌ Nav atrasts nevienas ziņas. Mēģiniet vēlreiz nosūtīt ziņu botam.")
        
        # Manual chat ID entry
        chat_id = input("\n📝 Vai arī ievadiet chat ID manuāli (ja zināt): ").strip()
        if not chat_id:
            return
    else:
        # Find the most recent chat
        messages = updates['result']
        chat_id = None
        
        for msg in reversed(messages):
            if 'message' in msg:
                chat_id = str(msg['message']['chat']['id'])
                chat_name = msg['message']['chat'].get('first_name', 'Unknown')
                print(f"✅ Atrasts chat: {chat_name} (ID: {chat_id})")
                break
        
        if not chat_id:
            print("❌ Nav atrasts chat ID")
            chat_id = input("📝 Ievadiet chat ID manuāli: ").strip()
            if not chat_id:
                return
    
    # Send test message
    print("\n📤 Sūtu testa ziņu...")
    result = send_test_message(token, chat_id)
    
    if result.get('ok'):
        print("✅ Testa ziņa nosūtīta veiksmīgi!")
        
        # Update config
        update_config(token, chat_id)
        
        print("""
🎉 SETUP PABEIGTS!

Tagad varat palaist job monitor:
  python scraper.py

Vai testēt vienu reizi:
  python scraper.py --once

Neaizmirstiet config.json norādīt kategorijas, kuras vēlaties sekot!
""")
    else:
        print(f"❌ Neizdevās nosūtīt ziņu: {result.get('description', 'Unknown error')}")


if __name__ == "__main__":
    main()

