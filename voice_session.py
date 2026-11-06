"""Voice-activated 3-clip recording session (te/hi/en) -> transcribe -> parse.

Per clip: beep -> wait up to 14 s for sustained voice -> record 8 s from
voice start -> save -> Prisma -> parse -> print.
"""
import sys, time, wave
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np
import sounddevice as sd
from prisma import transcribe
from extract import parse_sale

SAMPLE_RATE = 16000
SETTLE = 0.3        # extra seconds recorded after voice is detected
MAX_WAIT_WINDOW = 14
VAD_BLOCK = 1600    # 100 ms frames
VAD_FRAMES = 3      # consecutive frames above threshold = speech
RMS_TRIGGER = 450   # your ambient is ~150; speech measured 500-950

CLIPS = [
    ("telugu", "te-IN", "rendu kilo chakker 60 rupalu"),
    ("hindi", "hi-IN", "do kilo cheeni 60 rupaye"),
    ("english", "en-IN", "two kg sugar for 120 rupees"),
]


def beep():
    import winsound
    winsound.Beep(880, 400)


def stream_pause(seconds):
    listen = sd.rec(int(seconds * SAMPLE_RATE), samplerate=SAMPLE_RATE,
                    channels=1, dtype="int16")
    sd.wait()
    return listen


def record_when_speaking(name, i_out):
    print(f"    waiting for your voice (up to {MAX_WAIT_WINDOW}s)...", flush=True)
    waited = 0.0
    while waited < MAX_WAIT_WINDOW:
        block = stream_pause(0.25)
        rms = np.sqrt(np.mean(block.astype(float) ** 2))
        if rms > RMS_TRIGGER // 3:  # anything rising above ambient
            burst = stream_pause(0.3)
            peaks = np.sqrt(np.mean(burst.astype(float) ** 2))
            if peaks > RMS_TRIGGER:
                print(f"    voice detected!", flush=True)
                tail = stream_pause(8)
                audio = np.concatenate([block, burst, tail])
                fn = f"clip_{name}_{i_out}.wav"
                with wave.open(fn, "w") as wf:
                    wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SAMPLE_RATE)
                    wf.writeframes(audio.tobytes())
                peak = int(np.max(np.abs(audio)))
                print(f"    saved {fn} (peak={peak})", flush=True)
                return fn
        waited += 0.25
    print("    NO voice detected in window!", flush=True)
    return None


results = []
force = "--force" in sys.argv or "force" in sys.argv[1:]
for i, (name, lang, sent) in enumerate(CLIPS, 1):
    print(f"\nCLIP {i}/3 [{name}] say: '{sent}'", flush=True)
    if force:
        print("    force mode: recording right now for 8 s!", flush=True)
        time.sleep(1)
    beep()
    if force:
        audio = stream_pause(8)
        fn = f"clip_{name}_{i}.wav"
        with wave.open(fn, "w") as wf:
            wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SAMPLE_RATE)
            wf.writeframes(audio.tobytes())
        print(f"    saved {fn} (peak={int(np.max(np.abs(audio)))})", flush=True)
    else:
        fn = record_when_speaking(name, i)
    if fn is None:
        results.append((name, lang, sent, fn, "", {}))
        continue
    try:
        text = transcribe(fn, language_code=lang)
    except RuntimeError as e:
        text = f"ERROR: {e}"
    rec = parse_sale(text)
    fields = {k: rec[k] for k in ("item", "qty", "unit", "amount")}
    print(f"    transcript: {text!r}", flush=True)
    print(f"    parsed: {fields}", flush=True)
    results.append((name, lang, sent, fn, text, fields))
    if i < len(CLIPS):
        print("    next beep in 4s...", flush=True)
        time.sleep(4)

print("\n===== SUMMARY =====", flush=True)
for name, lang, sent, fn, text, fields in results:
    print(f"{fn} | {sent} | transcript={text!r} | fields={fields}", flush=True)
