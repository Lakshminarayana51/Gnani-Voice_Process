"""Record once, transcribe with Prisma in hi-IN / en-IN / te-IN, parse each, save to CSV."""
import sys
sys.stdout.reconfigure(encoding="utf-8")

import os
import wave

import numpy as np
import sounddevice as sd

from prisma import transcribe
from extract import parse_sale, save_record

LANGS = ["hi-IN", "en-IN", "te-IN"]
LABELS = {"hi-IN": "Hindi", "en-IN": "English", "te-IN": "Telugu"}
DURATION = 7
SAMPLE_RATE = 16000

PHRASES = [
    "Hindi:   'do kilo cheeni 60 rupaye'",
    "English: 'two kg sugar for 60 rupees'",
    "Telugu:  'rendu kilo chakker 60 rupalu'",
]


def record_audio(filename):
    print("\n" + "=" * 60)
    print("  SPEAK ONE SALE SENTENCE, e.g.:")
    for p in PHRASES:
        print(f"   {p}")
    print("=" * 60)
    print(f"  Recording for {DURATION} seconds... SPEAK NOW!")
    audio = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE,
                   channels=1, dtype="int16")
    sd.wait()
    peak = int(np.max(np.abs(audio)))
    print(f"  Saved {filename} (peak={peak})\n")
    with wave.open(filename, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio.tobytes())
    if peak < 100:
        print("  WARNING: nearly silent. Check Windows sound input settings first.")
        sys.exit(1)
    return filename


def main():
    audio = sys.argv[1] if len(sys.argv) > 1 else record_audio("test_sale.wav")
    print(f"Using audio file: {audio}\n")

    for lang in LANGS:
        print(f"--- {LABELS[lang]} ({lang}) ---")
        try:
            text = transcribe(audio, language_code=lang)
        except RuntimeError as e:
            print(f"  ERROR: {e}\n")
            continue
        print(f"  Transcript: {text}")
        record = parse_sale(text)
        print(f"  Parsed: item={record['item']} qty={record['qty']} "
              f"unit={record['unit']} amount={record['amount']}\n")
        if record["item"] or record["amount"]:
            save_record(record)
            print("  -> saved to sales.csv\n")


if __name__ == "__main__":
    main()
