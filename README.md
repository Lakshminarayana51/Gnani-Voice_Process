# Sale Voice Entry

Voice-based sales recording for small shopkeepers in Tier-2 and Tier-3 towns.

Shopkeepers speak a sale in Hindi, Telugu or Hinglish (e.g. “do kilo cheeni becho 60 rupaye ki”).  
The app transcribes the audio with **Gnani Prisma**, extracts item / quantity / unit / amount, and saves it to a daily sales table.

Built for the **Great Indian AI Internship Challenge 2026**.

---

## Problem

Many small shopkeepers still write sales by hand or keep them only in their head.  
Typing on a phone is slow, especially when they speak Hindi / Telugu / Hinglish.  
Daily totals and restocking become difficult.

## Solution

1. Record a short voice note on phone or laptop  
2. Transcribe with Gnani Prisma v2.5 (REST API)  
3. Rule-based parser extracts structured fields  
4. Save to CSV + show today’s running total  
5. Shopkeeper can correct the transcript before saving

---

## Demo

[Add your YouTube / Drive demo video link here]

---

## Tech Stack

- **Speech-to-Text**: Gnani Prisma v2.5 (POST `/stt/v3`, language `hi-IN`)
- Python 3.10+
- Rule-based extractor for Hindi / Telugu / English number words, units and rupee amounts
- Simple CSV storage (`sales.csv`)

---

## Setup

```bash
git clone https://github.com/Lakshminarayana51/Gnani-Voice_Process.git
cd Gnani-Voice_Process

python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Add your Gnani API key in .env
