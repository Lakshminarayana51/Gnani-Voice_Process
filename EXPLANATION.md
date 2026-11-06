# Sale Voice Entry: Voice-Based Sales Recording for Small Shopkeepers

**Challenge:** Great Indian AI Internship Challenge 2026 (Gnani AI)
**Team:** Lakshminarayana
**Institution:** Sir C R Reddy College of Engineering, Eluru
**Code (GitHub):** https://github.com/Lakshminarayana51/Gnani-Voice_Process
**Demo video (2-3 min):** [video link]
**LinkedIn post (tags @GnaniAI):** [post link]
## 1. Problem

Many small shopkeepers in Tier-2 and Tier-3 towns record sales by hand or not at all.
They often speak Hindi, Telugu, or Hinglish, and typing on a phone is slow.
Without records, daily totals and restocking depend on memory.

## 2. Solution

A shopkeeper speaks a sale aloud, for example:

> do kilo cheeni becho 60 rupaye ki

The app transcribes the audio, extracts the item, quantity, unit, and amount,
and saves a timestamped record to a sales file. Daily totals can be computed
from the saved records (a built-in total view is a next step).

## 3. Gnani AI Technology Used

- **Prisma v2.5 (speech-to-text):** REST endpoint
  `POST https://api.vachana.ai/stt/v3`, with language codes `hi-IN`, `en-IN`,
  and `te-IN` (all three verified with live recorded audio).
- **Timbre (text-to-speech):** not used in this version.
- **Evon:** not used in this version.

## 4. Who Uses It

Small shopkeepers and the family members who run their counter, in Hindi-,
Telugu-, and English-speaking areas.

## 5. How It Works

1. Record a short voice note on a phone or laptop microphone.
2. Send the audio to Prisma and receive a transcript
   (`audio_file` + `language_code`, `X-API-Key-ID` header).
3. A rule-based parser reads number words, units, and rupee amounts in Hindi,
   Telugu, and English — including Devanagari and Telugu scripts and digits.
4. Save the structured record to a CSV file with a timestamp.
5. Quiet recordings are auto-amplified before upload, so a soft mic does not
   return an empty transcript.

## 6. Measured Results

- **Parser test (no API key needed):** 5 of 5 built-in example sentences
  parsed with all fields (run `python extract.py` to reproduce).
- **Live transcription:** [X] of [N] test clips transcribed correctly
  (fill from `results.md`, written by `python measure_accuracy.py`).
- **Full extraction:** [Y] of [N] sentences with all fields correct
  (fill from `results.md`).
- **Main failures:** [e.g., amounts written as words; sentences without a
  unit] (the experiment includes two designed word-amount failure cases).

## 7. Limits

- Parsing is rule-based and covers common sentence patterns.
- Amounts written as words (for example *sau rupaye*) are not parsed yet.
- A sale spoken as a transliteration in another script (Telugu words written
  in Devanagari) does not parse.
- Unusual item names are stored as spoken.
- The interface is command-line only.

## 8. Next Steps

Amount-word parsing, a larger item and unit vocabulary, transcript correction
before saving, and a daily total view.
