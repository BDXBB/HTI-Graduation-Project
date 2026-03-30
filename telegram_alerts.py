import asyncio
from telethon import TelegramClient
from telethon.tl.functions.contacts import ImportContactsRequest
from telethon.tl.types import InputPhoneContact
from config import (
    TELEGRAM_API_ID, TELEGRAM_API_HASH,
    TELEGRAM_PHONE, TELEGRAM_TARGET,
    TELEGRAM_TARGET_PHONE, SESSION_FILE
)



def _make_client():
    return TelegramClient(SESSION_FILE, TELEGRAM_API_ID, TELEGRAM_API_HASH)


async def _get_entity(client):
    """
    Get the target entity and resolve access_hash issues.
    """
    # Attempt 1: Directly from cache
    try:
        return await client.get_entity(TELEGRAM_TARGET)
    except Exception:
        pass

    # Attempt 2: Add as temporary contact to resolve access_hash using phone number
    try:
        result = await client(ImportContactsRequest([
            InputPhoneContact(
                client_id=0,
                phone=TELEGRAM_TARGET_PHONE,
                first_name="Alert",
                last_name="Target"
            )
        ]))
        if result.users:
            return result.users[0]
    except Exception:
        pass

    # Attempt 3: Load all dialogs and search
    await client.get_dialogs()
    return await client.get_entity(TELEGRAM_TARGET)


def send_alert_message(text):
    async def _run():
        async with _make_client() as client:
            target = await _get_entity(client)
            await client.send_message(target, text)

    try:
        asyncio.run(_run())
        print(f"[Telegram] ✉️  Message sent")
    except Exception as e:
        print(f"[Telegram] ❌ Error sending message: {e}")



def call_with_live_stream(camera_source, duration=60):
    """
    Calls the user and streams the camera directly in the call.

    camera_source: '/dev/video0'
    duration: stream duration in seconds
    """
    async def _run():
        from pytgcalls import PyTgCalls
        from pytgcalls.types import MediaStream, VideoQuality

        async with _make_client() as client:
            target = await _get_entity(client)
            print(f"[Telegram] 📞 Calling {getattr(target, 'first_name', 'target')}...")

            app = PyTgCalls(client)
            await app.start()

            # Important: ffmpeg parameters for V4L2 device
            # audio_flags=IGNORE: RPi usually has no microphone connected
            # camera_source = 'udp://127.0.0.1:5554' (MPEGTS from libcamera-vid)
            # MPEGTS metadata contains stream parameters -> ntgcalls auto-detects them
            stream = MediaStream(
                camera_source,
                video_parameters=VideoQuality.SD_480p,
                ffmpeg_parameters='-fflags nobuffer -flags low_delay -strict experimental',
                audio_flags=MediaStream.Flags.IGNORE,
            )

            # pytgcalls v2.2.12 — play() method is used to start streaming
            await app.play(target.id, stream)
            print(f"[Telegram] 📡 Live streaming... ({duration}s)")

            await asyncio.sleep(duration)

            await app.leave_call(target.id)
            print("[Telegram] ⏹️  Call ended")

            # Stop camera streaming
            try:
                import camera_handler
                camera_handler.stop_stream()
            except Exception:
                pass

    try:
        asyncio.run(_run())
    except ImportError:
        print("[Telegram] ⚠️  pytgcalls not installed")
    except Exception as e:
        print(f"[Telegram] ❌ Call error: {e}")
