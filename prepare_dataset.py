import json
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATASET_ROOT = ROOT / "dataset"
SOURCE_TRASHNET = DATASET_ROOT / "dataset-resized"
SOURCE_EWASTE = DATASET_ROOT / "modified-dataset"
TARGET = DATASET_ROOT
MERGE_CARDBOARD_PAPER = True
MERGE_EWASTE = False

EWASTE_SUBTYPES = [
    "Battery", "Keyboard", "Microwave", "Mobile", "Mouse",
    "PCB", "Player", "Printer", "Television", "Washing Machine"
]
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"}

TARGET.mkdir(parents=True, exist_ok=True)


def copy_images(src_folder, dst_folder, prefix=""):
    dst_folder.mkdir(parents=True, exist_ok=True)
    count = 0
    for f in sorted(os.listdir(src_folder)):
        src_file = Path(src_folder) / f
        if src_file.is_file() and src_file.suffix.lower() in IMAGE_EXTENSIONS:
            new_name = f"{prefix}{f}" if prefix else f
            shutil.copy2(src_file, dst_folder / new_name)
            count += 1
    return count


def clear_folder(folder):
    if folder.exists():
        for child in folder.iterdir():
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()


categories = ["glass", "metal", "plastic", "trash"]
for cat in categories:
    src = SOURCE_TRASHNET / cat
    dst = TARGET / cat
    if src.exists():
        clear_folder(dst)
        n = copy_images(src, dst)
        print(f"[OK] {cat}: {n} images")
    else:
        print(f"[SKIP] {cat} not found")

if MERGE_CARDBOARD_PAPER:
    dst = TARGET / "paper-cardboard"
    total = 0
    for cat in ["cardboard", "paper"]:
        src = SOURCE_TRASHNET / cat
        if src.exists():
            total += copy_images(src, dst, prefix=f"{cat}_")
    print(f"[OK] paper-cardboard (merged): {total} images")

if MERGE_EWASTE:
    ewaste_dst = TARGET / "e-waste"
    total = 0
    for split in ["train", "val", "test"]:
        split_dir = SOURCE_EWASTE / split
        if not split_dir.exists():
            continue
        for subtype in EWASTE_SUBTYPES:
            subtype_dir = split_dir / subtype
            if subtype_dir.exists():
                total += copy_images(subtype_dir, ewaste_dst, prefix=f"{subtype}_{split}_")
    print(f"[OK] e-waste (merged): {total} images")
else:
    print("[SKIP] e-waste merge skipped. Set MERGE_EWASTE=True to include it.")

summary = []
for category_dir in sorted(TARGET.iterdir()):
    if category_dir.is_dir() and category_dir.name not in {"dataset-resized", "modified-dataset"}:
        image_files = [
            f.name for f in category_dir.iterdir()
            if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS
        ]
        summary.append({
            "name": category_dir.name,
            "imageCount": len(image_files),
            "sampleImages": image_files[:5],
        })

summary_path = ROOT / "dataset_summary.json"
summary_path.write_text(json.dumps({"categories": summary}, indent=2), encoding="utf-8")
print(f"\nDone! Final categories: {[item['name'] for item in summary]}")
print(f"Dataset summary saved to {summary_path}")