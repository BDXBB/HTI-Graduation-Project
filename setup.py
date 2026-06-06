#!/usr/bin/env python3
"""
setup.py — Project Setup (One-time)
Performs the following:
  1. Creates database, user and tables
  2. Inserts default values
  3. Telegram login and saving session file

Usage:
    python3 setup.py
"""

import sys

DB_HOST     = 'localhost'
DB_USER     = 'g7admin'
DB_PASSWORD = '1234g7'
DB_NAME     = 'hti_Automation'

TELEGRAM_API_ID   = 9200863          # ← Change this
TELEGRAM_API_HASH = 'a1149998106ea2bf2da59115a340ab68'  # ← Change this
TELEGRAM_PHONE    = '+37256280010'  # ← Change this
SESSION_FILE      = '/home/g7/hti/my_account'


def step_database():
    """Create DB + user + tables + default data"""
    try:
        import mysql.connector
    except ImportError:
        print("❌ mysql-connector-python is not installed")
        print("   Run: pip3 install mysql-connector-python")
        return False

    print("\n[1/2] ═══ Setting up database ═══")

    try:
        # Initial connection without database to create database and user
        conn = mysql.connector.connect(
            host=DB_HOST,
            user='root',
            password=''
        )
        cursor = conn.cursor()

        # Create database
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}`")
        print(f"  Database: {DB_NAME}")

        # Create user
        cursor.execute(
            f"CREATE USER IF NOT EXISTS '{DB_USER}'@'localhost' IDENTIFIED BY '{DB_PASSWORD}'"
        )
        cursor.execute(
            f"GRANT ALL PRIVILEGES ON `{DB_NAME}`.* TO '{DB_USER}'@'localhost'"
        )
        cursor.execute("FLUSH PRIVILEGES")
        print(f"  User: {DB_USER}")

        cursor.execute(f"USE `{DB_NAME}`")

        # Create table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS device_status (
                id          INT AUTO_INCREMENT PRIMARY KEY,
                device_name VARCHAR(50) UNIQUE NOT NULL,
                status      VARCHAR(50) NOT NULL
            )
        """)
        print(" Table device_status created")

        # Default values (used by main.py, index.php, api.php)
        defaults = [
            ('light',           'OFF'),
            ('security_system', 'OFF'),
            ('pir_1',           'SAFE'),
            ('gas_sensor',      'SAFE'),
            ('door_sensor',     'CLOSED'),
        ]

        for device, status in defaults:
            cursor.execute(
                "INSERT IGNORE INTO device_status (device_name, status) VALUES (%s, %s)",
                (device, status)
            )

        conn.commit()
        print("  Default values inserted:")
        for device, status in defaults:
            print(f"       • {device:20s} = {status}")

        cursor.close()
        conn.close()
        return True

    except mysql.connector.Error as e:
        print(f"  DB error: {e}")
        print("  Hint: Make sure MariaDB is running: sudo systemctl start mariadb")
        return False


def step_telegram():
    """Telegram login and saving session file"""
    print("\n[2/2] ═══ Setting up Telegram ═══")

    if TELEGRAM_API_ID == 1234567 or TELEGRAM_API_HASH == 'your_api_hash':
        print("  Telegram credentials have not been updated in setup.py")
        print("  → Open setup.py and update TELEGRAM_API_ID, TELEGRAM_API_HASH and TELEGRAM_PHONE")
        return False

    try:
        from telethon.sync import TelegramClient
    except ImportError:
        print("  telethon not installed — run: pip3 install telethon")
        return False

    try:
        client = TelegramClient(SESSION_FILE, TELEGRAM_API_ID, TELEGRAM_API_HASH)
        client.start(phone=TELEGRAM_PHONE)
        me = client.get_me()
        print(f"  Logged in as: {me.first_name} (+{me.phone})")
        print(f"  Session file: {SESSION_FILE}.session")
        client.disconnect()
        return True
    except Exception as e:
        print(f"  Telegram error: {e}")
        return False


if __name__ == "__main__":
    print("=" * 55)
    print("  HTI Smart Home — Project Setup")
    print("=" * 55)

    db_ok  = step_database()
    tg_ok  = step_telegram()

    print("\n" + "=" * 55)
    print("  Setup summary:")
    print(f"  Database  : {'Ready'    if db_ok  else 'Failed'}")
    print(f"  Telegram  : {'Ready'    if tg_ok  else 'Needs setup'}")
    print("=" * 55)

    if db_ok and tg_ok:
        print(" Project is ready to run:")
        print("   python3 main.py")
    elif db_ok:
        print("Database is ready but Telegram needs to be configured.")
        print("   Update Telegram credentials in config.py then re-run setup.py.")
