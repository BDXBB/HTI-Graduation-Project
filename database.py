import mysql.connector
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

# database.py — Connection to MariaDB and reading/writing
# device status

def get_connection():
    """Open database connection"""
    try:
        return mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
    except Exception as e:
        print(f"[DB] Connection error: {e}")
        return None


def update_status(device_name, status):
    """Update device status in the database (Upsert)"""
    conn = get_connection()
    if conn is None:
        return

    cursor = conn.cursor()
    # INSERT if new, UPDATE if already exists to avoid duplicate key error
    cursor.execute(
        """
        INSERT INTO device_status (device_name, status)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE status = VALUES(status)
        """,
        (device_name, status)
    )
    conn.commit()
    cursor.close()
    conn.close()


def get_status(device_name):
    """Read status of a specific device"""
    conn = get_connection()
    if conn is None:
        return None

    cursor = conn.cursor()
    cursor.execute(
        "SELECT status FROM device_status WHERE device_name = %s",
        (device_name,)
    )
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result[0] if result else None


def get_all_status():
    """Read all device statuses at once - used by api.php"""
    conn = get_connection()
    if conn is None:
        return {}

    cursor = conn.cursor()
    cursor.execute("SELECT device_name, status FROM device_status")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    # Returns dictionary: {'light': 'OFF', 'pir_1': 'SAFE', ...}
    return {row[0]: row[1] for row in rows}
