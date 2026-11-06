"""Check mic levels and re-record with louder detection."""
import sys
sys.stdout.reconfigure(encoding="utf-8")

import os
import numpy as np
import sounddevice as sd
import wave

from prisma import transcribe
from extract import parse_sale, save_record

DURATION = 7
SAMPLE_RATE = 16000

# Check existing file
if os.path.exists("test_sale.wav"):
    print(f"Current test_sale.wav size: {os.path.getsize('test_sale.wav')} bytes")

# Test mic levels first
print("\nTesting mic for 2 seconds to check levels...")
test_audio = sd.rec(int(2 * SAMPLE_RATE), samplerate=SAMPLE_RATE,
                    channels=1, dtype="int16")
sd.wait()
peak = np.max(np.abs(test_audio))
rms = np.sqrt(np.mean(test_audio.astype(float)**2))
print(f"  Peak level: {peak}")
print(f"  RMS level:  {rms:.1f}")

if peak < 100:
    print("\n  WARNING: Mic levels are very low! Check if your mic is muted.")
    print("  Continuing anyway...\n")
else:
    print(f"  Mic is working (peak={peak})\n")

# Now record
print(f"  RECORDING for {DURATION} seconds... SPEAK NOW!")
print("  Say: 'do kilo cheeni 60 rupaye'\n")
audio = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE,
               channels=1, dtype="int16")
sd.wait()

peak = np.max(np.abs(audio))
rms = np.sqrt(np.mean(audio.astype(float)**2))
print(f"  Recording done! Peak={peak}, RMS={rms:.1f}")

# Save
wf = wave.open("test_sale.wav", "w")
wf.setnchannels(1)
wf.setsampwidth(2)
wf.setframerate(SAMPLE_RATE)
wf.writeframes(audio.tobytes())
wf.close()
print(f"  Saved test_sale.wav ({os.path.getsize('test_sale.wav')} bytes)\n")

if peak < 200:
    print("  Audio is nearly silent. Your mic may be muted or not picking up sound.")
    print("  Check Windows Settings > System > Sound > Input\n")
    sys.exit(1)

# Transcribe
print("  Sending to Prisma...")
text = transcribe("test_sale.wav", language_code="hi-IN")
print(f"  Transcript: {text}\n")

# Parse
record = parse_sale(text)
print("  Parsed record:")
print(f"   Item:   {record['item']}")
print(f"   Qty:    {record['qty']}")
print(f"   Unit:   {record['unit']}")
print(f"   Amount: {record['amount']}")
print(f"   Raw:    {record['raw_text']}\n")

save_record(record)
print("  Saved to sales.csv!")
