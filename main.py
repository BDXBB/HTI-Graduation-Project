import time
import threading
import database
import camera_handler
import telegram_alerts
import voice_control
from config import (
    PIN_RELAY_LIGHT,
    PIN_PIR_1,
    PIN_GAS, PIN_DOOR
)


try:
    import RPi.GPIO as GPIO
    IS_RPI = True
    print("[System] ✅ Running on real Raspberry Pi")
except ImportError:
    IS_RPI = False
    print("[System] ⚠️  Simulation mode (standard PC)")


def setup_gpio():
    if not IS_RPI:
        return

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    GPIO.setup(PIN_RELAY_LIGHT, GPIO.OUT)  # Relay

    GPIO.setup(PIN_PIR_1, GPIO.IN) # PIR Sensor

    GPIO.setup(PIN_GAS, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Gas Sensor

    GPIO.setup(PIN_DOOR, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Door Sensor
    
def read_sensors():
    if IS_RPI:
        gas_raw = GPIO.input(PIN_GAS)
        gas = 1 if gas_raw == 0 else 0
        return {
            'pir_1': GPIO.input(PIN_PIR_1),
            'gas': gas,
            'door':  GPIO.input(PIN_DOOR),
        }
    return {'pir_1': 0, 'gas': 0, 'door': 0}


def control_light():
    if not IS_RPI:
        return
    light_on = database.get_status('light') == 'ON'
    GPIO.output(PIN_RELAY_LIGHT, GPIO.HIGH if light_on else GPIO.LOW)


def handle_motion_alert(zone):
    print(f"[ALARM] 🚨 Motion detected in {zone}")

    # 1. Send Telegram alert message
    telegram_alerts.send_alert_message(
        f"🚨 Warning! Motion detected in {zone}!\n"
        f"📞 Calling you now..."
    )

    # 2. P2P call with live camera stream
    cam_source = camera_handler.get_camera_stream_source()
    if cam_source:
        telegram_alerts.call_with_live_stream(cam_source, duration=60)
    else:
        print("[Camera] ⚠️  No camera available")


def handle_gas_alert():
    print("[ALARM] ⚠️  Gas detected!")

    # 1. Send urgent Telegram alert
    telegram_alerts.send_alert_message(
        "🚨 Danger! Gas leak detected!\n"
        "⚠️  Evacuate the area immediately!\n"
        "📞 Calling you now..."
    )

    # 2. P2P call with live camera stream
    cam_source = camera_handler.get_camera_stream_source()
    if cam_source:
        telegram_alerts.call_with_live_stream(cam_source, duration=60)
    else:
        print("[Camera] ⚠️  No camera available")


def main_loop():
    print("[System] 🚀 Starting system...")
    setup_gpio()

    # Start voice control listener in a separate thread
    t_voice = threading.Thread(target=voice_control.start_listening, daemon=True)
    t_voice.start()
    print("[System] 🎙️ Voice control thread started")

    last_alert_time = 0   # To prevent duplicate alerts
    alert_cooldown  = 90  # Cooldown in seconds between alerts

    try:
        while True:
            sensors = read_sensors()
            print(sensors)

            # Update sensor states in DB — read by the web interface
            database.update_status('pir_1',       'DETECTED' if sensors['pir_1'] else 'SAFE')
            database.update_status('door_sensor', 'OPEN'     if sensors['door']  else 'CLOSED')

            # Gas: only writes DETECTED — does not auto-return to SAFE.
            # User must reset from interface.
            if sensors['gas']:
                database.update_status('gas_sensor', 'DETECTED')

            security_on = database.get_status('security_system') == 'ON'
            now = time.time()
            can_alert = (now - last_alert_time) > alert_cooldown

            if can_alert:

                # --- Gas Alert (Always active, regardless of Security status) ---
                if sensors['gas']:
                    t = threading.Thread(target=handle_gas_alert, daemon=True)
                    t.start()
                    last_alert_time = now

                # --- Security Alert (Active only when Security is ON) ---
                elif security_on:

                    if sensors['pir_1']:
                        zone = "Zone One"
                        t = threading.Thread(target=handle_motion_alert, args=(zone,), daemon=True)
                        t.start()
                        last_alert_time = now

                    elif sensors['door']:
                        print("[ALARM] 🚪 Door opened!")
                        t = threading.Thread(target=handle_motion_alert, args=("at the door",), daemon=True)
                        t.start()
                        last_alert_time = now

            # Control light based on DB status
            control_light()
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n[System] Shutting down system...")
        if IS_RPI:
            GPIO.cleanup()


if __name__ == "__main__":
    main_loop()
