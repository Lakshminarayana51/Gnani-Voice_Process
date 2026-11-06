# Sale Voice Entry

Voice-based sales recording for small shopkeepers in Tier-2 and Tier-3 towns.

Shopkeepers speak a sale in Hindi, Telugu or Hinglish (e.g. "do kilo cheeni becho 60 rupaye ki").
The app transcribes the audio with **Gnani Prisma**, extracts item / quantity / unit / amount, and saves it to a daily sales table (`sales.csv`).

Built for the **Great Indian AI Internship Challenge 2026**.

---

## Problem

Many small shopkeepers still write sales by hand or keep them only in their head.
Typing on a phone is slow, especially when they speak Hindi / Telugu / Hinglish.
Daily totals and restocking become difficult.

## Solution

1. Record a short voice note on phone or laptop
2. Transcribe with Gnani Prisma v2.5 (REST API)
3. Rule-based trilingual parser extracts structured fields
4. Save to a timestamped CSV (`sales.csv`); a daily total can be computed from the CSV,
   but a built-in total view is a next step (see Known limits)

---

## Demo

[Add your YouTube / Drive demo video link here]

---

## Setup

```bash
git clone https://github.com/Lakshminarayana51/Gnani-Voice_Process.git
cd Gnani-Voice_Process

python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # then put your real Gnani API key in .env
```

`.env` is git-ignored, so the API key never reaches GitHub.
`sales.csv` and `*.wav` are git-ignored too because they hold only local demo data.

## Usage

Record from the microphone and run the full pipeline (transcribe + parse + save)
in all three languages at once. Input is the standard microphone via `sounddevice`
(no OS-specific speech command, works on Windows/macOS/Linux):

```bash
python test_all_langs.py        # speaks prompts on screen, records 7 s, tri-language run
python record_and_test.py       # single-language (hi-IN) mic test with level check
python test_pipeline.py         # older 5 s single-pipeline test, saves recording.wav
```

Transcribe an existing WAV clip:

```bash
python prisma.py path/to/sale.wav
```

Test the sentence parser only (no API key needed):

```bash
python extract.py
```

Use it in your own script:

```python
from prisma import transcribe
from extract import parse_sale, save_record

text = transcribe("sale.wav", language_code="hi-IN")   # also en-IN, te-IN
record = parse_sale(text)
save_record(record)
```

## How it works

1. `prisma.py` loads a 16 kHz mono WAV, auto-normalizes it if it is too quiet,
   and sends it to Prisma (`X-API-Key-ID` header, `audio_file` +
   `language_code` fields).
2. Prisma returns `{"success": true, "transcript": "..."}`.
3. `extract.py` turns the transcript into `{item, qty, unit, amount}` using
   trilingual word lists and writes it to `sales.csv` with a timestamp.

Quiet recordings are handled automatically: any clip whose peak sample is below
12000 (of 32767 full scale, about 36%) is amplified before upload, so a
too-soft mic never comes back as an empty transcript.

## Tech Stack

- **Speech-to-Text**: Gnani Prisma v2.5 (POST `https://api.vachana.ai/stt/v3`)
- Language codes confirmed working on this endpoint: `hi-IN`, `en-IN`, `te-IN`
- Python 3.10+, `requests`
- Rule-based extractor for Hindi / Telugu / English number words, units and
  rupee amounts, in Devanagari, Telugu and Latin scripts
- Simple CSV storage (`sales.csv`)

## Example transcripts parsed

All rows are reproducible output: run `python extract.py` and compare.

| Language | Sentence | Parsed record |
|---|---|---|
| Hindi (Devanagari) | दो किलो चीनी 60 रुपये | sugar, qty 2, kg, ₹60 |
| Telugu | రెండు కిలోలు చక్కెర 60 రూపాయలు | sugar, qty 2, kg, ₹60 |
| English | two kg sugar sold for 120 rupees | sugar, qty 2, kg, ₹120 |

## Known limits

- Parsing is rule-based: it handles sentences with a number, an optional unit,
  an item name, and an amount next to a rupee word. Free-form sentences may
  return `None` for some fields.
- Amounts written as words (for example "sau rupaye") are not parsed yet.
- A sale spoken as a transliteration in another script (for example Telugu words
  written in Devanagari) does not parse.
- Only the item words listed in `extract.py` are mapped to English; unusual
  items are stored as spoken.
- No built-in total view yet — a daily total can be computed from the CSV.
- Next steps: amount-word mapping, more item/unit vocabulary, and a
  shopkeeper-facing UI with transcription correction and daily totals.
