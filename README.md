# Sale Voice Entry

A voice bookkeeping tool for small shopkeepers: instead of writing down each sale,
they speak it ("do kilo cheeni 60 rupaye"), and the app turns the audio into a
structured record — item, quantity, unit, amount — saved to `sales.csv`.

Speech is transcribed with **Gnani Prisma** (speech-to-text) and the transcript is
parsed into a sale record with a rule-based parser supporting Hindi, Telugu and
English, in Latin, Devanagari and Telugu scripts.

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then put your real Gnani API key in .env
```

`.env` is git-ignored, so your API key never reaches GitHub.

## Usage

Record from the microphone and run the full pipeline (transcribe + parse + save)
in all three languages at once:

```bash
python test_all_langs.py        # speaks prompts, records 7 s, tri-language run
python record_and_test.py       # single-language (hi-IN) mic test with level check
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

`sales.csv` is git-ignored because it holds only local demo data.

## How it works

1. `prisma.py` records/loads a 16 kHz mono WAV, auto-normalizes it if it is too
   quiet, and sends it to Prisma (`X-API-Key-ID` header, `audio_file` +
   `language_code` fields).
2. Prisma returns `{"success": true, "transcript": "..."}`
3. `extract.py` turns the transcript into `{item, qty, unit, amount}` using
   trilingual word lists and writes it to `sales.csv` with a timestamp.

Quiet recordings are handled automatically: any clip whose peak is below
~36% of full scale is boosted before upload, so a too-soft mic never comes back
as an empty transcript.

## Gnani models used

- **Prisma v2.5** (speech-to-text) via `POST https://api.vachana.ai/stt/v3`

Language codes confirmed working on this endpoint: `hi-IN`, `en-IN`, `te-IN`.

## Example transcripts parsed

| Language | Sentence | Parsed record |
|---|---|---|
| Hindi | दो किलो चीनी 60 रुपये | sugar, qty 2, kg, ₹60 |
| Telugu | రెండు కిలోలు చక్కెర 60 రూపాయలు | sugar, qty 2, kg, ₹60 |
| English | two kg sugar sold for 120 rupees | sugar, qty 2, kg, ₹120 |

## Known limits

- Parsing is rule-based: it handles sentences with a number, an optional unit,
  an item name, and an amount next to a rupee word. Free-form sentences may
  return `None` for some fields.
- Amounts written as words (for example "sau rupaye") are not parsed yet.
- Only the item words in `extract.py` are mapped to English; unusual items are
  stored as spoken.
- Suggested next steps: amount-word mapping, more item/unit vocabulary, and a
  shopkeeper-facing UI.
