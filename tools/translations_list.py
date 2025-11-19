# tools/translations_list.py

import csv
import json
from pathlib import Path

# Определяем корень проекта (там, где index.html)
BASE_DIR = Path(__file__).resolve().parents[1]

VOCAB_PATH = BASE_DIR / "content" / "vocab" / "vocab_master.json"
LIST_PATH = BASE_DIR / "content" / "vocab" / "list.txt"
LIST_READY_PATH = BASE_DIR / "content" / "vocab" / "list_ready.txt"


def load_vocab():
    if not VOCAB_PATH.exists():
        print(f"[ERROR] Vocab file not found: {VOCAB_PATH}")
        print("        Run extract_vocab.py first to create vocab_master.json.")
        return None

    with VOCAB_PATH.open("r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print(f"[ERROR] Could not parse JSON in {VOCAB_PATH}")
            return None

    if not isinstance(data, dict):
        print("[ERROR] vocab_master.json must contain a JSON object (dictionary).")
        return None

    return data


def save_vocab(vocab):
    VOCAB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with VOCAB_PATH.open("w", encoding="utf-8") as f:
        json.dump(vocab, f, ensure_ascii=False, indent=2)
    print(f"[INFO] Saved updated vocab to {VOCAB_PATH}")


def apply_list_ready(vocab):
    """
    Если существует list_ready.txt — читаем его, обновляем vocab
    и переименовываем файл в list_ready_used.txt.
    """
    if not LIST_READY_PATH.exists():
        print("[INFO] list_ready.txt not found, skipping import step.")
        return 0

    processed = 0
    print(f"[INFO] Found {LIST_READY_PATH}, applying translations from it...")

    with LIST_READY_PATH.open("r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=";")
        for row in reader:
            if not row or len(row) < 2:
                continue

            key = row[0].strip()
            # пропустим возможную строку заголовка
            if key.lower() in ("key", "#key"):
                continue

            word = row[1].strip() if len(row) > 1 else ""
            tr = row[2].strip() if len(row) > 2 else ""
            emoji = row[3].strip() if len(row) > 3 else ""

            if not key:
                continue

            entry = vocab.get(key)
            if not entry:
                print(f"[WARN] key '{key}' from list_ready.txt not found in vocab, skipping.")
                continue

            # обновляем display слово, если не пустое и отличается
            if word:
                entry["word"] = word

            if tr:
                entry["translation"] = tr
            if emoji:
                entry["emoji"] = emoji

            processed += 1

    # сохраняем обновлённый словарь
    save_vocab(vocab)

    # переименуем list_ready.txt, чтобы не применить его второй раз случайно
    used_path = LIST_READY_PATH.with_name("list_ready_used.txt")
    try:
        LIST_READY_PATH.rename(used_path)
        print(f"[INFO] Renamed list_ready.txt -> {used_path.name}")
    except Exception as e:
        print(f"[WARN] Could not rename list_ready.txt: {e}")

    print(f"[INFO] Applied translations for {processed} entries from list_ready.txt")
    return processed


def build_missing_list(vocab):
    """
    Пересоздаёт list.txt со списком всех слов, у которых нет перевода или эмодзи.
    Формат CSV: key;word;translation;emoji
    """
    missing = []

    for key, entry in vocab.items():
        tr = (entry.get("translation") or "").strip()
        emoji = (entry.get("emoji") or "").strip()
        if not tr or not emoji:
            missing.append((key, entry.get("word") or key, tr, emoji))

    LIST_PATH.parent.mkdir(parents=True, exist_ok=True)

    with LIST_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        # заголовок для удобства
        writer.writerow(["key", "word", "translation", "emoji"])
        for key, word, tr, emoji in sorted(missing, key=lambda x: x[0]):
            writer.writerow([key, word, tr, emoji])

    print(f"[INFO] Rebuilt list.txt with {len(missing)} missing entries.")
    print(f"[INFO] Path: {LIST_PATH}")

    return len(missing)


def main():
    print(f"[INFO] Project root: {BASE_DIR}")
    vocab = load_vocab()
    if vocab is None:
        return

    # 1) если есть list_ready.txt — применяем переводы
    apply_list_ready(vocab)

    # 2) заново пересчитываем недостающие и создаём свежий list.txt
    build_missing_list(vocab)

    print("[INFO] Done.")


if __name__ == "__main__":
    main()
