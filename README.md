# Sale Voice Entry

A small tool for shopkeepers who record sales by voice in Hindi, Telugu, or Hinglish.
Speech is transcribed with Gnani Prisma (speech-to-text), and the transcript is turned
into a structured record (item, quantity, unit, amount) and saved to `sales.csv`.

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then put your real key in .env
```

## Usage

Transcribe a clip with Prisma:

```bash
python prisma.py path/to/sale.wav
```

Test the sentence parser (no API key needed):

```bash
python extract.py
```

Connect the two in your own script:

```python
from prisma import transcribe
from extract import parse_sale, save_record

text = transcribe("sale.wav", language_code="hi-IN")
record = parse_sale(text)
save_record(record)
```

## Models used

- **Prisma v2.5** (speech-to-text) via `POST https://api.vachana.ai/stt/v3`

## Known limits

- Parsing is rule-based. It handles sentences with a number, an optional unit, an item
  name, and an amount next to a rupee word.
- Amounts written as words (for example "sau rupaye") are not parsed yet.
- Sentences without a unit or with unusual word order may return `None` for some fields.
