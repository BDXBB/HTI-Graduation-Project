import time
import subprocess


UDP_PORT     = 5554
_stream_proc = None


def _find_cmd(suffix):
    """Find libcamera-X or rpicam-X command on the system"""
    for prefix in ['libcamera', 'rpicam']:
        cmd = f'{prefix}-{suffix}'
        r = subprocess.run(['which', cmd], capture_output=True)
        if r.returncode == 0:
            return cmd
    return None


def _kill_camera_procs():
    """Kill running libcamera-vid and ffmpeg processes"""
    subprocess.run(['pkill', '-f', 'libcamera-vid'], capture_output=True)
    subprocess.run(['pkill', '-f', 'rpicam-vid'],    capture_output=True)
    subprocess.run(['pkill', '-9', '-f', 'libcamera-vid'], capture_output=True)
    subprocess.run(['pkill', '-9', '-f', 'rpicam-vid'],    capture_output=True)
    time.sleep(1.5)   # Wait for the camera to release


def get_camera_stream_source():
    """
    Starts libcamera-vid and streams MPEGTS over UDP:5554.
    Returns the UDP address for pytgcalls, or None if failed.
    """
    global _stream_proc

    cmd = _find_cmd('vid')
    if not cmd:
        print("[Camera] libcamera-vid not found")
        return None

    # Stop previous stream and wait for camera release
    if _stream_proc and _stream_proc.poll() is None:
        _stream_proc.terminate()

    _kill_camera_procs()   # Kill leftover pipeline processes

    udp_url  = f'udp://127.0.0.1:{UDP_PORT}'
    pipeline = (
        f'{cmd} --nopreview --output - --timeout 0 '
        f'--codec h264 --inline '
        f'--width 640 --height 480 --framerate 30 --bitrate 1500000 2>/dev/null | '
        f'ffmpeg -loglevel quiet -fflags nobuffer -i pipe:0 -c:v copy -f mpegts -flush_packets 1 {udp_url}'
    )

    # Try to start stream (up to 2 attempts)
    for attempt in range(1, 3):
        _stream_proc = subprocess.Popen(
            pipeline,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        time.sleep(2.0)

        if _stream_proc.poll() is None:
            print(f"[Camera] ✅ Camera streaming live (attempt {attempt})")
            return udp_url

        print(f"[Camera] ⚠️  Stream failed — attempt {attempt}/2, retrying...")
        _kill_camera_procs()

    print("[Camera] ❌ Camera failed to start after two attempts")
    return None


def stop_stream():
    """Stop camera streaming"""
    global _stream_proc 
    if _stream_proc and _stream_proc.poll() is None:
        _stream_proc.terminate()
        _stream_proc = None
    _kill_camera_procs()   # Ensure camera process stops
    print("[Camera] ⏹️  Stream stopped")
