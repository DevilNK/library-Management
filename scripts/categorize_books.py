#!/usr/bin/env python3
"""
Populate 'Category' and 'Category ID' for books.csv using simple keyword rules.

Input:  books.csv (semicolon-delimited)
Output: books_categorized.csv (semicolon-delimited) - same columns with Category and Category ID filled
"""
import csv
from collections import Counter

INFILE = "books.csv"
OUTFILE = "books_categorized.csv"
DELIM = ";"

# Category -> ID mapping
CATEGORY_IDS = {
    "Fiction": 1,
    "Mystery & Thriller": 2,
    "Science Fiction & Fantasy": 3,
    "Romance": 4,
    "Non-Fiction": 5,
    "History & Biography": 6,
    "Children & YA": 7,
    "Cooking & Food": 8,
    "Science & Tech": 9,
    "Religion & Spirituality": 10,
    "Poetry & Drama": 11,
    "Business & Economics": 12,
    "Self-Help": 13,
    "Travel": 14,
    "Classics": 15,
    "General": 0,
}

# Ordered list of (category, keywords). First match wins.
KEYWORD_RULES = [
    ("Children & YA", ["children", "kid", "junior", "baby", "young", "laurel leaf", "scholastic", "animorph", "goosebumps", "narnia", "harperfestival"]),
    ("Science Fiction & Fantasy", ["science fiction", "sci-fi", "fantasy", "dragon", "vampire", "hobbit", "dune", "star trek", "halo", "end", "galaxy", "space", "discworld", "david e.", "discworld"]),
    ("Mystery & Thriller", ["mystery", "murder", "thriller", "detective", "case", "clancy", "grisham", "patterson", "cornwell", "lecarre", "kellerman", "koontz", "child", "suspense"]),
    ("Romance", ["romance", "love", "kissing", "brid", "wedding", "harlequin", "silhouette", "jane austen", "nicholas sparks"]),
    ("Cooking & Food", ["cook", "cooking", "recipe", "kitchen", "culinary", "food", "chef"]),
    ("History & Biography", ["history", "biography", "memoir", "journal", "war", "diary", "life", "story of", "account"]),
    ("Science & Tech", ["science", "physics", "chemistry", "biology", "computer", "programming", "internet", "technology", "engineering", "chemistry", "compu", "linux", "oracle", "cisco"]),
    ("Religion & Spirituality", ["bible", "relig", "spirit", "prayer", "god", "christ", "moses", "buddh", "yoga", "church", "catechism"]),
    ("Business & Economics", ["business", "finance", "wealth", "money", "investment", "management", "leadership", "econom", "stock", "market"]),
    ("Self-Help", ["self", "self-help", "how to", "guide to", "how to be", "habit", "mind", "improve", "motivat"]),
    ("Travel", ["travel", "guide", "journey", "adventure", "trip", "road", "tour", "guidebook"]),
    ("Poetry & Drama", ["poem", "poetry", "play", "drama", "poet", "verse"]),
    ("Classics", ["classic", "penguin", "everyman's", "dover", "wordsworth", "austen", "dickens", "tolstoy", "shakespeare", "homer", "huck"]),
    ("Non-Fiction", ["essay", "report", "investig", "study", "manual", "handbook", "reference", "guidebook", "how-to"]),
]

def classify_text(text: str):
    t = text.lower()
    for cat, keywords in KEYWORD_RULES:
        for kw in keywords:
            if kw in t:
                return cat
    return "General"

def process():
    counts = Counter()
    with open(INFILE, newline='', encoding="utf-8", errors="replace") as inf, \
         open(OUTFILE, "w", newline='', encoding="utf-8") as outf:
        reader = csv.DictReader(inf, delimiter=DELIM)
        # ensure header contains Category and Category ID
        fieldnames = list(reader.fieldnames) if reader.fieldnames else []
        if "Category" not in fieldnames:
            fieldnames.append("Category")
        if "Category ID" not in fieldnames:
            fieldnames.append("Category ID")
        writer = csv.DictWriter(outf, fieldnames=fieldnames, delimiter=DELIM, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()

        for row in reader:
            # if a category already present, keep it; otherwise infer
            existing_cat = (row.get("Category") or "").strip()
            if existing_cat:
                category = existing_cat
            else:
                text = " ".join([row.get("Book-Title",""), row.get("Book-Author",""), row.get("Publisher","")])
                category = classify_text(text)
            row["Category"] = category
            row["Category ID"] = str(CATEGORY_IDS.get(category, 0))
            counts[category] += 1
            writer.writerow(row)

    print("Wrote:", OUTFILE)
    print("Summary:")
    for cat, cnt in counts.most_common():
        print(f"  {cat}: {cnt}")

if __name__ == "__main__":
    process()