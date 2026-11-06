import os
import sys
import wave

import numpy as np
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GNANI_API_KEY")

# Gnani Prisma v2.5 speech-to-text REST endpoint (short clips, up to ~60 s)
PRISMA_URL = "https://api.vachana.ai/stt/v3"

# Recordings quieter than this peak (out of 32767) are boosted before upload.
QUIET_PEAK_THRESHOLD = 12000


def normalize_wav(audio_path):
    """Return the path to a louder copy if the recording is too quiet, else the original."""
    with wave.open(audio_path, "rb") as wf:
        sr, nch, sw = wf.getframerate(), wf.getnchannels(), wf.getsampwidth()
        if sw != 2:
            return audio_path
        data = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)

    if len(data) == 0:
        return audio_path
    peak = int(np.max(np.abs(data)))
    if peak >= QUIET_PEAK_THRESHOLD:
        return audio_path

    gain = (0.9 * 32767) / peak
    boosted = np.clip(data.astype(float) * gain, -32767, 32767).astype(np.int16)
    out_path = audio_path.rsplit(".", 1)[0] + "_boosted.wav"
    with wave.open(out_path, "wb") as wfo:
        wfo.setnchannels(nch)
        wfo.setsampwidth(2)
        wfo.setframerate(sr)
        wfo.writeframes(boosted.tobytes())
    return out_path


def transcribe(audio_path, language_code="hi-IN"):
    """Send a WAV file to Prisma and return the transcript text."""
    if not API_KEY:
        raise RuntimeError("GNANI_API_KEY is not set. Add it to your .env file.")

    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    audio_path = normalize_wav(audio_path)

    with open(audio_path, "rb") as f:
        try:
            resp = requests.post(
                PRISMA_URL,
                headers={"X-API-Key-ID": API_KEY},
                files={"audio_file": f},
                data={"language_code": language_code},
                timeout=60,
            )
        except requests.RequestException as e:
            raise RuntimeError(f"Network error calling Prisma: {e}") from e

    if resp.status_code != 200:
        raise RuntimeError(f"Prisma returned HTTP {resp.status_code}: {resp.text}")

    data = resp.json()
    if not data.get("success"):
        raise RuntimeError(f"Prisma reported failure: {data}")

    return data.get("transcript", "")


if __name__ == "__main__":
    audio = sys.argv[1] if len(sys.argv) > 1 else "test_sale.wav"
    try:
        print("Transcript:", transcribe(audio))
    except (RuntimeError, FileNotFoundError) as e:
        print(f"ERROR: {e}")
        sys.exit(1)
