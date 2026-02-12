
# --- Database Configurations ---
DB_HOST     = 'localhost'
DB_USER     = 'g7admin'
DB_PASSWORD = '1234g7'
DB_NAME     = 'hti_Automation'

# --- Telegram Configurations (Real user account, not bot) ---
# API_ID and API_HASH can be obtained from https://my.telegram.org
TELEGRAM_API_ID   = 9200863           # ← Change this
TELEGRAM_API_HASH = 'a1149998106ea2bf2da59115a340ab68'   # ← Change this

# Real phone number with country code
TELEGRAM_PHONE    = '+37256280010'   # ← Change this

# Account that receives alerts
TELEGRAM_TARGET       = 6461764860      # ← User ID (from @userinfobot)
TELEGRAM_TARGET_PHONE = '+9647861478404' # ← Target phone number (resolves access_hash issues)

# Path to session file (saved after first login)
SESSION_FILE = '/home/g7/hti/my_account'

# --- GPIO Pin Numbers (BCM System) ---
PIN_RELAY_LIGHT = 17   # Relay

PIN_PIR_1 = 27         # PIR Motion Sensor - Zone 1
PIN_GAS   = 22         # MQ-2 Gas Sensor
PIN_DOOR  = 2          # MC-38 Door Sensor (Magnetic)
