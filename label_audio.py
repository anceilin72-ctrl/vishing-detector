"""
label_audio.py
--------------
Interactive CLI tool to label your audio files as "human" or "ai".
Run this to build your training dataset.

Usage:
    python label_audio.py

It will:
    1. Scan your training_data/ folder for audio files
    2. Ask you to label each one as human or AI
    3. Save labels to training_data/labels.json

Then run:
    python voice_classifier_trainer.py --train
"""

import os
import json

SAMPLES_DIR = "training_data"
LABELS_FILE = os.path.join(SAMPLES_DIR, "labels.json")
AUDIO_EXTS  = {".wav", ".mp3", ".ogg", ".flac", ".m4a"}


def main():
    os.makedirs(SAMPLES_DIR, exist_ok=True)

    # Load existing labels if any
    if os.path.exists(LABELS_FILE):
        with open(LABELS_FILE) as f:
            labels = json.load(f)
        print(f"📂 Loaded {len(labels)} existing labels\n")
    else:
        labels = {}

    # Find all audio files
    audio_files = [
        f for f in os.listdir(SAMPLES_DIR)
        if os.path.splitext(f)[1].lower() in AUDIO_EXTS
    ]

    if not audio_files:
        print(f"⚠  No audio files found in '{SAMPLES_DIR}/'")
        print(f"   Copy your .wav / .mp3 files there and run again.\n")
        print(f"   Example structure:")
        print(f"     training_data/")
        print(f"       human_call_1.mp3")
        print(f"       ai_voice_1.wav")
        print(f"       whatsapp_audio.mp3")
        return

    unlabeled = [f for f in audio_files if f not in labels]
    print(f"🎵 Found {len(audio_files)} audio files | {len(labels)} labeled | {len(unlabeled)} remaining\n")

    if not unlabeled:
        print("✅ All files are already labeled!")
        _show_summary(labels)
        return

    print("For each file, type:  h = human   a = ai   s = skip\n")
    print("-" * 50)

    changed = False
    for i, filename in enumerate(unlabeled, 1):
        print(f"\n[{i}/{len(unlabeled)}] {filename}")

        while True:
            choice = input("  Label (h/a/s): ").strip().lower()
            if choice == "h":
                labels[filename] = "human"
                print(f"  ✅ Labeled as: HUMAN")
                changed = True
                break
            elif choice == "a":
                labels[filename] = "ai"
                print(f"  🤖 Labeled as: AI")
                changed = True
                break
            elif choice == "s":
                print(f"  ⏭  Skipped")
                break
            else:
                print("  Please type h, a, or s")

    if changed:
        with open(LABELS_FILE, "w") as f:
            json.dump(labels, f, indent=2)
        print(f"\n💾 Labels saved to {LABELS_FILE}")

    _show_summary(labels)

    n_ai    = sum(1 for v in labels.values() if v == "ai")
    n_human = sum(1 for v in labels.values() if v == "human")

    print("\n" + "=" * 50)
    if n_ai >= 5 and n_human >= 5:
        print("🚀 You have enough samples to train!")
        print("   Run: python voice_classifier_trainer.py --train")
    else:
        needed = max(0, 5 - n_ai), max(0, 5 - n_human)
        print(f"⏳ Need {needed[0]} more AI + {needed[1]} more human samples before training.")
        print(f"   Keep adding files to training_data/ and re-run this script.")


def _show_summary(labels: dict):
    n_ai    = sum(1 for v in labels.values() if v == "ai")
    n_human = sum(1 for v in labels.values() if v == "human")
    print(f"\n📊 Current dataset: {n_human} human  |  {n_ai} AI")


if __name__ == "__main__":
    main()