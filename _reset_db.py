"""
Demo DB reset script.
Restores demo_app/data/contracts.csv and activities.csv
to their initial snapshot stored in demo_app/data/_initial/.
"""
import shutil
from pathlib import Path

DATA_DIR    = Path(__file__).parent / "demo_app" / "data"
INITIAL_DIR = DATA_DIR / "_initial"

RESET_FILES = ["contracts.csv", "activities.csv"]


def reset() -> None:
    for name in RESET_FILES:
        src = INITIAL_DIR / name
        dst = DATA_DIR / name
        if not src.exists():
            print(f"  [SKIP] 初期スナップショットが見つかりません: {src}")
            continue
        shutil.copy2(src, dst)
        print(f"  [RESET] {dst.relative_to(Path(__file__).parent)}")
    print("DB リセット完了。")


if __name__ == "__main__":
    reset()
