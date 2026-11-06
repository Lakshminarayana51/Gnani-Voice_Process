import csv
import os
import re
from datetime import datetime

NUMBER_WORDS = {
    "ek": 1, "do": 2, "teen": 3, "char": 4, "paanch": 5, "panch": 5,
    "chhe": 6, "saat": 7, "aath": 8, "nau": 9, "das": 10,
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    # Hindi (Devanagari digits are handled by isdigit())
    "एक": 1, "दो": 2, "तीन": 3, "चार": 4, "पाँच": 5, "पांच": 5,
    "छह": 6, "सात": 7, "आठ": 8, "नौ": 9, "दस": 10,
    # Telugu
    "ఒకటి": 1, "రెండు": 2, "మూడు": 3, "నాలుగు": 4, "ఐదు": 5,
    "ఆరు": 6, "ఏడు": 7, "ఎనిమిది": 8, "తొమ్మిది": 9, "పది": 10,
}
UNIT_WORDS = {
    "kg": "kg", "kilo": "kg", "kilogram": "kg",
    "g": "g", "gram": "g",
    "l": "l", "litre": "l", "liter": "l",
    "packet": "packet", "piece": "piece", "dozen": "dozen",
    # Hindi
    "किलो": "kg", "किलोग्राम": "kg", "ग्राम": "g", "ग्राम्म": "g",
    "लीटर": "l", "पैकेट": "packet", "दर्जन": "dozen",
    # Telugu
    "కిలో": "kg", "కిలోలు": "kg", "గ్రాము": "g", "లీటరు": "l",
    "లీటర్": "l", "ప్యాకెట్": "packet",
}
RUPEE_WORDS = {
    "rupees", "rupee", "rupaye", "rupay", "rupaiye", "rs",
    # Hindi
    "रुपये", "रुपया", "रु",
    # Telugu
    "రూపాయలు", "రూపాయి", "రూ",
}
FILLERS = {"ka", "ki", "ke", "ko", "for", "sold", "becho", "bechi", "becha",
           "का", "की", "के", "को",
           "కి", "కు"}
ITEM_WORDS = {
    # optional cleanup: map common item words to English for the CSV
    "चीनी": "sugar", "चीनि": "sugar", "आटा": "flour", "दूध": "milk",
    "चावल": "rice", "नून": "salt", "नमक": "salt", "तेल": "oil",
    "చక్కెర": "sugar", "పాలు": "milk", "బియ్యం": "rice",
    "ఉప్పు": "salt", "నూనె": "oil", "పసుపు": "turmeric",
}


def to_number(token):
    if token.isdigit():
        return int(token)
    return NUMBER_WORDS.get(token)


def parse_sale(text):
    t = text.lower().replace("₹", " rs ")
    # \w alone drops Devanagari/Telugu vowel signs (matras), so match the
    # full script ranges explicitly: Latin digits + both Unicode blocks.
    tokens = re.findall(r"[A-Za-z0-9\u0900-\u097F\u0C00-\u0C7F]+", t)

    qty = unit = item = amount = None

    # Quantity, optional unit, then item name
    for i, tok in enumerate(tokens):
        n = to_number(tok)
        if n is not None:
            qty = n
            nxt = i + 1
            if nxt < len(tokens) and tokens[nxt] in UNIT_WORDS:
                unit = UNIT_WORDS[tokens[nxt]]
                nxt += 1
            for w in tokens[nxt:]:
                if w in FILLERS or to_number(w) is not None:
                    continue
                if w in RUPEE_WORDS:
                    break
                item = ITEM_WORDS.get(w, w)
                break
            break

    # Amount: a number right before or right after a rupee word
    for i, tok in enumerate(tokens):
        if tok in RUPEE_WORDS:
            if i > 0 and tokens[i - 1].isdigit():
                amount = int(tokens[i - 1])
            elif i + 1 < len(tokens) and tokens[i + 1].isdigit():
                amount = int(tokens[i + 1])
            break

    return {"item": item, "qty": qty, "unit": unit, "amount": amount, "raw_text": text}


def save_record(record, path="sales.csv"):
    fields = ["time", "item", "qty", "unit", "amount", "raw_text"]
    new_file = not os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        if new_file:
            writer.writeheader()
        writer.writerow({
            "time": datetime.now().isoformat(timespec="seconds"),
            **{k: record[k] for k in fields[1:]},
        })


if __name__ == "__main__":
    samples = [
        "do kilo cheeni becho 60 rupaye ki",
        "two kg sugar sold for 120 rupees",
        "ek packet doodh 30 rupees",
    ]
    for s in samples:
        print(parse_sale(s))
