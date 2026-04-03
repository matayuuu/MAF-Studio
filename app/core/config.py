from __future__ import annotations

from pathlib import Path

APP_NAME = "MAF Workflow Studio"
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
SKILLS_DIR = DATA_DIR / "skills"
STATE_FILE = DATA_DIR / "studio_state.json"
UPLOADS_DIR = DATA_DIR / "uploads"
AGENTS_DIR = DATA_DIR / "agents"
HANDOFFS_DIR = DATA_DIR / "handoffs"

for directory in (DATA_DIR, SKILLS_DIR, UPLOADS_DIR, AGENTS_DIR, HANDOFFS_DIR):
    directory.mkdir(parents=True, exist_ok=True)
