import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GNANI_API_KEY")

# Gnani Prisma v2.5 speech-to-text REST endpoint (short clips, up to ~60 s)
PRISMA_URL = "https://api.vachana.ai/stt/v3"


def transcribe(audio_path, language_code="hi-IN"):
    """Send a WAV file to Prisma and return the transcript text."""
    if not API_KEY:
        raise RuntimeError("GNANI_API_KEY is not set. Add it to your .env file.")

    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

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
