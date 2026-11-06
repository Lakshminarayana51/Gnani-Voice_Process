"""Record from microphone, transcribe with Prisma, parse, and save to CSV."""
import sys
import wave
import struct

import numpy as np
import sounddevice as sd

from prisma import transcribe
from extract import parse_sale, save_record

# Fix Windows console encoding for Hindi/Devanagari output
sys.stdout.reconfigure(encoding="utf-8")

DURATION = 5        # seconds to record
SAMPLE_RATE = 16000 # 16 kHz mono (good for speech)

def record_audio(filename="recording.wav", duration=DURATION):
    print(f"\n🎙️  Recording for {duration} seconds... SPEAK NOW!")
    print("   (Say something like: 'do kilo cheeni 60 rupaye')\n")
    audio = sd.rec(int(duration * SAMPLE_RATE), samplerate=SAMPLE_RATE,
                   channels=1, dtype="int16")
    sd.wait()  # block until recording is done
    print("✅ Recording complete!\n")

    with wave.open(filename, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio.tobytes())

    return filename


if __name__ == "__main__":
    # Step 1: Record
    wav_file = record_audio()

    # Step 2: Transcribe with Prisma
    print("📡 Sending to Gnani Prisma for transcription...")
    try:
        text = transcribe(wav_file, language_code="hi-IN")
        print(f"📝 Transcript: {text}\n")
    except RuntimeError as e:
        print(f"❌ Transcription error: {e}")
        sys.exit(1)

    # Step 3: Parse the sale
    record = parse_sale(text)
    print("📊 Parsed record:")
    print(f"   Item:   {record['item']}")
    print(f"   Qty:    {record['qty']}")
    print(f"   Unit:   {record['unit']}")
    print(f"   Amount: {record['amount']}")
    print(f"   Raw:    {record['raw_text']}\n")

    # Step 4: Save to CSV
    save_record(record)
    print("💾 Saved to sales.csv!")
