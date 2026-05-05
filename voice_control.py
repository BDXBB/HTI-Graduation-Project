# Transcribes user voice and recognizes "on" / "off" commands
# to control lights via database

import time
import torch
import numpy as np
import sounddevice as sd
import database
from scipy.signal import resample as scipy_resample

from transformers import (
    Wav2Vec2ForSequenceClassification,
    Wav2Vec2FeatureExtractor,
)


MODEL_PATH = "/home/g7/hti/models"

print("[Voice] Loading voice model...")
model = Wav2Vec2ForSequenceClassification.from_pretrained(MODEL_PATH)
model.eval()

processor = Wav2Vec2FeatureExtractor(
    feature_size=1,
    sampling_rate=16000,
    padding_value=0.0,
    do_normalize=True,
    return_attention_mask=False,
)
print("[Voice] Voice model loaded")


def process_command(word):
    """
    Takes recognized word and controls light.
    on  ← turn light ON
    off ← turn light OFF
    """
    print(f"[Voice] Recognized: {word}")

    if word == "on":
        print("[Voice] Turning light ON")
        database.update_status('light', 'ON')

    elif word == "off":
        print("[Voice] Turning light OFF")
        database.update_status('light', 'OFF')

    else:
        print(f"[Voice] Unknown command: {word}")


# Resample — if recording sample rate differs
# Model requires 16000 Hz
def _resample_to_16k(audio, orig_sr, target_sr=16000):
    """Resamples audio from orig_sr to target_sr (16000)"""
    if orig_sr == target_sr:
        return audio
    num_samples = int(len(audio) * target_sr / orig_sr)
    return scipy_resample(audio, num_samples).astype(np.float32)


def _predict(audio_16k):
    """
    Perform inference on 16 kHz float32 audio.
    Returns tuple (label, confidence).
    """
    inputs = processor(
        audio_16k,
        sampling_rate=16000,
        return_tensors="pt",
        padding=True,
    )

    with torch.no_grad():
        logits = model(**inputs).logits

    probs      = torch.softmax(logits, dim=-1)
    pred_id    = torch.argmax(probs, dim=-1).item()
    confidence = probs[0][pred_id].item()
    label      = model.config.id2label[pred_id]

    return label, confidence


def start_listening():
    """
    Runs in a separate thread.
    - Recording at DEVICE_SR (44100) as supported by the device
    - Resample to 16000 Hz before inference as required by the model
    - THRESHOLD adjusted to prevent background noise triggers
    """
    # --- Settings ---
    DEVICE_ID      = 1        # Microphone device ID
    DEVICE_SR      = 44100    # Device sample rate
    MODEL_SR       = 16000    # Model sample rate
    CHUNK_SECS     = 0.5      # Listening chunk duration to detect sound
    RECORD_SECS    = 3        # Recording duration when voice is detected
    THRESHOLD      = 0.08     # Sound volume threshold
    CONFIDENCE_MIN = 0.85     # Minimum confidence to accept command (85%)
    COOLDOWN       = 2.5      # Cooldown in seconds between commands

    print("[Voice] Voice control active — listening for commands...")
    print(f"[Voice] Device SR={DEVICE_SR}Hz  Model SR={MODEL_SR}Hz  Threshold={THRESHOLD}")

    last_command_time = 0.0

    while True:
        try:
            # --- Listen to short chunk to detect sound ---
            chunk = sd.rec(
                int(CHUNK_SECS * DEVICE_SR),
                samplerate=DEVICE_SR,
                channels=1,
                dtype="float32",
                device=DEVICE_ID,
            )
            sd.wait()
            chunk = chunk.flatten()

            volume = float(np.max(np.abs(chunk)))

            # If sound is too quiet, continue
            if volume < THRESHOLD:
                continue

            # If cooldown is not over, wait
            now = time.time()
            if (now - last_command_time) < COOLDOWN:
                continue

            # --- Record 3 seconds at device sample rate ---
            print(f"[Voice] Sound detected (vol={volume:.3f}), recording {RECORD_SECS}s...")
            full_audio = sd.rec(
                int(RECORD_SECS * DEVICE_SR),
                samplerate=DEVICE_SR,
                channels=1,
                dtype="float32",
                device=DEVICE_ID,
            )
            sd.wait()
            full_audio = full_audio.flatten()

            # --- Resample from 44100 to 16000 before inference ---
            audio_16k = _resample_to_16k(full_audio, DEVICE_SR, MODEL_SR)

            # --- Inference ---
            label, confidence = _predict(audio_16k)
            print(f"[Voice] Prediction: {label}  ({confidence*100:.1f}%)")

            if confidence >= CONFIDENCE_MIN:
                process_command(label)
                last_command_time = time.time()
            else:
                print(f"[Voice] Low confidence ({confidence*100:.1f}%) — ignored")

        except Exception as e:
            print(f"[Voice] Error in voice loop: {e}")
            time.sleep(1)


if __name__ == "__main__":
    start_listening()
