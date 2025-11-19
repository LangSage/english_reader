# tools/extract_vocab.py

import os
import re
import json
from pathlib import Path

# ---- Paths ----
# This file is in: PROJECT_ROOT/tools/extract_vocab.py
BASE_DIR = Path(__file__).resolve().parents[1]  # one level up from /tools

TEXT_DIR = BASE_DIR / "content" / "texts"
VOCAB_PATH = BASE_DIR / "content" / "vocab" / "vocab_master.json"

WORD_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")

def read_all_text_from_html(path: Path) -> str:
    """Very simple: read HTML and strip tags -> plain text."""
    with path.open("r", encoding="utf-8") as f:
        html = f.read()
    text = re.sub(r"<[^>]+>", " ", html)
    return text

def collect_words() -> set:
    words = set()

    if not TEXT_DIR.exists():
        print(f"[ERROR] Text directory not found: {TEXT_DIR}")
        return words

    print(f"[INFO] Scanning texts in: {TEXT_DIR}")

    for path in TEXT_DIR.glob("*.html"):
        print(f"  - Reading {path.name}")
        text = read_all_text_from_html(path)
        for match in WORD_RE.finditer(text):
            words.add(match.group(0))

    print(f"[INFO] Total unique raw words found: {len(words)}")
    return words

def load_vocab() -> dict:
    if VOCAB_PATH.exists():
        with VOCAB_PATH.open("r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                print(f"[INFO] Loaded existing vocab from {VOCAB_PATH}")
                return data
            except json.JSONDecodeError:
                print(f"[WARN] Could not parse JSON in {VOCAB_PATH}, starting fresh.")
                return {}
    else:
        print(f"[INFO] No vocab file found yet, starting new one.")
        return {}

def save_vocab(vocab: dict) -> None:
    VOCAB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with VOCAB_PATH.open("w", encoding="utf-8") as f:
        json.dump(vocab, f, ensure_ascii=False, indent=2)
    print(f"[INFO] Vocab saved to: {VOCAB_PATH}")

def main():
    print(f"[INFO] Project root: {BASE_DIR}")
    words = collect_words()
    if not words:
        print("[INFO] No words found (or text dir missing). Nothing to do.")
        return

    vocab = load_vocab()

    added = 0
    for word in sorted(words, key=str.lower):
        key = word.lower()
        if key not in vocab:
            vocab[key] = {
                "word": word,   # display form
                "translation": "",
                "emoji": "",
                "audio": f"audio/en/{key}.mp3"
            }
            added += 1

    save_vocab(vocab)
    print(f"[INFO] Unique English words in texts: {len(words)}")
    print(f"[INFO] New words added to vocab: {added}")

if __name__ == "__main__":
    main()
