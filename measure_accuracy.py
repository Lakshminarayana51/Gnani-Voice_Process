"""Guided accuracy experiment: speak each test sentence, transcribe with
Prisma, parse, and compare against expected fields. Writes results.md.

Usage:
    python measure_accuracy.py            # all cases
    python measure_accuracy.py 3 5        # only cases 3..5 (1-based, inclusive)

Each case: say the SENTENCE aloud in the shown language during the 8 s window.
The script auto-boosts quiet audio, so raise your voice a little anyway.
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")

import os
import time
import wave
from datetime import date

import numpy as np
import sounddevice as sd

from prisma import transcribe
from extract import parse_sale

LANG_LABEL = {"hi-IN": "Hindi", "en-IN": "English", "te-IN": "Telugu",
              "hi-HI": "Hindi (Devanagari transcript expected)"}
DURATION = 8
SAMPLE_RATE = 16000

# item lists = acceptable transcripts for that field ("*" = accept whatever
# non-empty item the parser found, used for failure cases where only the
# amount is expected to fail)
CASES = [
    # --- Hindi (spoken in Hinglish, romanized) ---
    dict(s="do kilo cheeni becho 60 rupaye ki", lang="hi-IN", exp=dict(item=["sugar", "cheeni"], qty=2, unit="kg", amount=60)),
    dict(s="teen kilo aata 90 rupaye", lang="hi-IN", exp=dict(item=["aata"], qty=3, unit="kg", amount=90)),
    dict(s="paanch packet doodh 150 rupaye", lang="hi-IN", exp=dict(item=["doodh"], qty=5, unit="packet", amount=150)),
    dict(s="do litre tel 200 rupees", lang="hi-IN", exp=dict(item=["tel", "oil"], qty=2, unit="l", amount=200)),
    dict(s="ek kilo cheeni 40 rupaye ka", lang="hi-IN", exp=dict(item=["sugar", "cheeni"], qty=1, unit="kg", amount=40)),
    dict(s="das kilo chawal 800 rupaye", lang="hi-IN", exp=dict(item=["chawal", "rice"], qty=10, unit="kg", amount=800)),
    # --- Hindi, expect transcript in Devanagari ---
    dict(s="do kilo cheeni 60 rupaye", lang="hi-IN", script="दो किलो चीनी 60 रुपये", exp=dict(item=["sugar", "cheeni"], qty=2, unit="kg", amount=60)),
    # --- English ---
    dict(s="two kg sugar for 120 rupees", lang="en-IN", exp=dict(item=["sugar"], qty=2, unit="kg", amount=120)),
    dict(s="three litre oil 350 rupees", lang="en-IN", exp=dict(item=["oil"], qty=3, unit="l", amount=350)),
    dict(s="five packet milk 150 rupees", lang="en-IN", exp=dict(item=["milk"], qty=5, unit="packet", amount=150)),
    dict(s="ten kg rice 800 rupees", lang="en-IN", exp=dict(item=["rice"], qty=10, unit="kg", amount=800)),
    dict(s="one litre oil 90 rupees", lang="en-IN", exp=dict(item=["oil"], qty=1, unit="l", amount=90)),
    # --- Telugu (say it as: rendu kilo chakker 60 rupalu) ---
    dict(s="rendu kilo chakker 60 rupalu", lang="te-IN", exp=dict(item=["sugar", "చక్కెర", "chakker"], qty=2, unit="kg", amount=60)),
    dict(s="aaru kilo biyyam 500 rupalu", lang="te-IN", exp=dict(item=["rice", "బియ్యం", "biyyam"], qty=6, unit="kg", amount=500)),
    dict(s="moodu litre noone 400 rupalu", lang="te-IN", exp=dict(item=["oil", "నూనె", "noone"], qty=3, unit="l", amount=400)),
    dict(s="aaru kilo uppu 30 rupalu", lang="te-IN", exp=dict(item=["salt", "ఉప్పు", "uppu"], qty=6, unit="kg", amount=30)),
    dict(s="okati litre chakker 50 rupalu", lang="te-IN", exp=dict(item=["sugar", "చక్కెర", "chakker"], qty=1, unit="l", amount=50)),
    # --- Hinglish ---
    dict(s="ek packet doodh becho 30 rupaye", lang="hi-IN", exp=dict(item=["doodh"], qty=1, unit="packet", amount=30)),
    # --- Expected failures: amount spoken as a word (known limit) ---
    dict(s="do kilo cheeni sau rupaye", lang="hi-IN", expect_fail=True, exp=dict(item=None, qty=2, unit="kg", amount=None)),
    dict(s="teen kilo cheeni pachas rupaye", lang="hi-IN", expect_fail=True, exp=dict(item=None, qty=3, unit="kg", amount=None)),
]


def beep():
    try:
        if sys.platform == "win32":
            import winsound
            winsound.Beep(880, 300)
        else:
            sys.stdout.write("\a")
            sys.stdout.flush()
    except Exception:
        pass


def record_audio(filename):
    for i in range(3, 0, -1):
        print(f"    {i}...", flush=True)
        time.sleep(1)
    print("    SPEAK THE SENTENCE NOW!", flush=True)
    sys.stdout.flush()
    beep()
    audio = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE,
                   channels=1, dtype="int16")
    sd.wait()
    peak = int(np.max(np.abs(audio)))
    with wave.open(filename, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio.tobytes())
    return peak


def compare(record, exp):
    """Score the parsed record against expectations. Returns (hits, details)."""
    details = {}
    hits = 0
    for field in ("item", "qty", "unit", "amount"):
        got = record[field]
        if field == "item":
            want = exp["item"]
            ok = (got is not None) if want is None else (got in want)
        else:
            ok = got == exp[field]
        if ok:
            hits += 1
        details[field] = "ok" if ok else f"got {got!r}, wanted {exp[field]!r}"
    return hits, details


def write_results(rows):
    n = len(rows)
    full = sum(1 for r in rows if r["hits"] == 4)
    trans_ok = sum(1 for r in rows if r["transcript"])
    open("results.md", "w", encoding="utf-8").write(
        "# Accuracy results\n\n"
        f"Measured on {date.today().isoformat()} with the Gnani Prisma API "
        "(`POST /stt/v3`) on live microphone recordings by the author. "
        f"{n} test sentences (spoken one at a time), each sent to Prisma and "
        "parsed. Full extraction = all four fields correct.\n\n"
        f"- Transcripts received: {trans_ok}/{n}\n"
        f"- Full extraction: {full}/{n}\n\n"
        "| # | Sentence (spoken) | Language | Transcript | Fields correct |\n"
        "|---|---|---|---|---|\n"
    )
    with open("results.md", "a", encoding="utf-8") as f:
        for r in rows:
            t = r["transcript"].replace("|", "/") or "(none)"
            f.write(f"| {r['no']} | {r['spoken']} | {LANG_LABEL[r['lang']].split(' ')[0]} "
                    f"| {t} | {r['hits']}/4 |\n")
        fails = [r for r in rows if r["hits"] < 4]
        f.write("\n## Failures\n\n")
        if not fails:
            f.write("None recorded.\n")
        for r in fails:
            f.write(f"- #{r['no']} `{r['spoken']}` -> `{r['transcript']}` "
                    f"({r['hits']}/4)\n")


def main():
    start, end = 1, len(CASES)
    if len(sys.argv) > 2:
        start, end = int(sys.argv[1]), int(sys.argv[2])
    elif len(sys.argv) == 2:
        start, end = int(sys.argv[1]), int(sys.argv[1])

    rows = []
    for no, case in enumerate(CASES, 1):
        if not (start <= no <= end):
            continue
        spoken = case.get("script") or case["s"]
        print("\n" + "=" * 60)
        print(f"  CASE {no}/{len(CASES)}  [{LANG_LABEL[case['lang']]}]")
        print(f"  Say: '{case['s']}'")
        if case.get("script"):
            print(f"  (accepted transcript e.g.: {case['script']})")
        if case.get("expect_fail"):
            print("  (expected to FAIL on amount - known limit, say it anyway)")
        print("=" * 60)
        peak = record_audio("_measure.wav")
        print(f"    saved (peak={peak})")
        try:
            text = transcribe("_measure.wav", language_code=case["lang"])
        except RuntimeError as e:
            print(f"    ERROR: {e}")
            text = ""
        record = parse_sale(text)
        print(f"    Transcript: {text!r}")
        hits, details = compare(record, case["exp"])
        print(f"    Fields correct: {hits}/4")
        for f_, d in details.items():
            if d != "ok":
                print(f"      {f_}: {d}")
        rows.append(dict(no=no, spoken=case["s"], lang=case["lang"],
                         transcript=text, hits=hits))

    write_results(rows)
    print("\nresults.md written. Full summary:")
    n = len(rows)
    print(f"  Full extraction: {sum(1 for r in rows if r['hits'] == 4)}/{n}")
    print(f"  Transcripts received: {sum(1 for r in rows if r['transcript'])}/{n}")


if __name__ == "__main__":
    main()
