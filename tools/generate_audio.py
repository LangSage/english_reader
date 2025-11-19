# tools/generate_audio.py

import os
import json
from pathlib import Path

from gtts import gTTS

# ---- Paths ----
# This file is in: PROJECT_ROOT/tools/generate_audio.py
BASE_DIR = Path(__file__).resolve().parents[1]  # one level up from /tools

VOCAB_PATH = BASE_DIR / "content" / "vocab" / "vocab_master.json"


def main():
    print(f"[INFO] Project root: {BASE_DIR}")

    if not VOCAB_PATH.exists():
        print(f"[ERROR] Vocab file not found: {VOCAB_PATH}")
        print("        Run extract_vocab.py first to generate vocab_master.json.")
        return

    with VOCAB_PATH.open("r", encoding="utf-8") as f:
        try:
            vocab = json.load(f)
        except json.JSONDecodeError:
            print(f"[ERROR] Could not parse JSON in {VOCAB_PATH}")
            return

    if not isinstance(vocab, dict):
        print("[ERROR] vocab_master.json must contain a JSON object (dictionary).")
        return

    created = 0
    total = len(vocab)

    print(f"[INFO] Loaded {total} vocab entries")

    for key, entry in vocab.items():
        # Key like "naruto", "village", ...
        # Ensure we have a display word
        word_text = entry.get("word") or key

        # Ensure the 'audio' field is a relative path inside /audio/
        rel_audio = entry.get("audio") or f"audio/en/{key}.mp3"
        # Normalise to forward slashes for the JSON (so it works nicely in browser)
        rel_audio = rel_audio.replace("\\", "/")
        entry["audio"] = rel_audio

        # Absolute filesystem path for saving the file
        audio_path = BASE_DIR / rel_audio
        audio_dir = audio_path.parent

        if not audio_dir.exists():
            audio_dir.mkdir(parents=True, exist_ok=True)

        if audio_path.exists():
            # Already generated, skip
            continue

        try:
            print(f"[AUDIO] Generating audio for '{word_text}' -> {rel_audio}")
            tts = gTTS(text=word_text, lang="en")
            tts.save(str(audio_path))
            created += 1
        except Exception as e:
            print(f"[WARN] Failed to generate audio for '{word_text}': {e}")

    # Write back updated paths (just in case new audio entries were fixed)
    with VOCAB_PATH.open("w", encoding="utf-8") as f:
        json.dump(vocab, f, ensure_ascii=False, indent=2)

    print(f"[INFO] New audio files created: {created}")
    print(f"[INFO] Vocab file updated: {VOCAB_PATH}")


if __name__ == "__main__":
    main()
