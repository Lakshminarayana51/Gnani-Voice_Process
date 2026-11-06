import csv
import os
import re
from datetime import datetime

NUMBER_WORDS = {
    "ek": 1, "do": 2, "teen": 3, "char": 4, "paanch": 5, "panch": 5,
    "chhe": 6, "saat": 7, "aath": 8, "nau": 9, "das": 10,
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
}
UNIT_WORDS = {
    "kg": "kg", "kilo": "kg", "kilogram": "kg",
    "g": "g", "gram": "g",
    "l": "l", "litre": "l", "liter": "l",
    "packet": "packet", "piece": "piece", "dozen": "dozen",
}
RUPEE_WORDS = {"rupees", "rupee", "rupaye", "rupay", "rupaiye", "rs"}
FILLERS = {"ka", "ki", "ke", "ko", "for", "sold", "becho", "bechi", "becha"}


def to_number(token):
    if token.isdigit():
        return int(token)
    return NUMBER_WORDS.get(token)


def parse_sale(text):
    t = text.lower().replace("₹", " rs ")
    tokens = re.findall(r"[a-z]+|\d+", t)

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
                item = w
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
