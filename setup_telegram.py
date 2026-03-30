"""
setup_telegram.py — Telegram Login (One-time setup)

Run this file once before starting the project:
    python3 setup_telegram.py

You will be prompted for:
  1. Your phone number
  2. The OTP confirmation code received on Telegram
  3. Two-step verification password if enabled

After registration, the session file will be saved at:
    /home/g7/hti_project/my_account.session

No need to run this file again unless you delete the session file.
"""

from telethon.sync import TelegramClient
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE, SESSION_FILE

print("=" * 50)
print("  Telegram Account Setup — HTI Project")
print("=" * 50)

# Create client and connect
client = TelegramClient(SESSION_FILE, TELEGRAM_API_ID, TELEGRAM_API_HASH)
client.start(phone=TELEGRAM_PHONE)

# Ensure login is successful
me = client.get_me()
print(f"\n✅ Login successful!")
print(f"   Name: {me.first_name}")
print(f"   Phone: {me.phone}")
print(f"   Session file: {SESSION_FILE}.session")
print("\n🚀 You can now run the project: python3 main.py")

client.disconnect()
