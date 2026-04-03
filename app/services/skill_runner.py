from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable

from fastapi import UploadFile
from agent_framework import Skill, SkillScript, SkillsProvider

from app.core.config import SKILLS_DIR
from app.models import SkillRecord, SkillScriptInfo

_FRONTMATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", value.strip().lower()).strip("-")
    return slug or "skill"


def parse_skill_markdown(skill_md: Path) -> tuple[str, str]:
    if not skill_md.exists():
        return skill_md.parent.name, ""

    content = skill_md.read_text(encoding="utf-8")
    name = skill_md.parent.name
    description = ""
    match = _FRONTMATTER_PATTERN.match(content)
    if match:
        for line in match.group(1).splitlines():
            if line.startswith("name:"):
                name = line.split(":", 1)[1].strip().strip('"')
            if line.startswith("description:"):
                description = line.split(":", 1)[1].strip().strip('"')
    elif content.strip():
        first_line = next((line.strip("# ") for line in content.splitlines() if line.strip()), name)
        description = first_line

    return name, description


def scan_skill_dir(skill_dir: Path, source_type: str = "folder") -> SkillRecord | None:
    if not skill_dir.exists() or not skill_dir.is_dir():
        return None

    skill_md = skill_dir / "SKILL.md"
    name, description = parse_skill_markdown(skill_md)
    scripts = [
        SkillScriptInfo(name=path.stem, path=str(path.relative_to(skill_dir)).replace('\\', '/'))
        for path in sorted(skill_dir.rglob("*.py"))
    ]
    resources = [
        str(path.relative_to(skill_dir)).replace('\\', '/')
        for path in sorted(skill_dir.rglob("*"))
        if path.is_file() and path.name != "SKILL.md" and path.suffix.lower() not in {".py", ".pyc"}
    ]
    return SkillRecord(
        id=safe_slug(skill_dir.name),
        name=name,
        description=description,
        path=str(skill_dir),
        source_type=source_type if source_type in {"folder", "files", "sample"} else "folder",
        has_skill_md=skill_md.exists(),
        scripts=scripts,
        resources=resources,
    )


def discover_skills() -> list[SkillRecord]:
    records: list[SkillRecord] = []
    for child in sorted(SKILLS_DIR.iterdir() if SKILLS_DIR.exists() else []):
        record = scan_skill_dir(child, source_type="sample" if child.name == "unit-converter" else "folder")
        if record:
            records.append(record)
    return records


async def save_uploaded_skill(
    skill_name: str,
    files: list[UploadFile],
    relative_paths: Iterable[str] | None = None,
    source_type: str = "files",
) -> SkillRecord:
    slug = safe_slug(skill_name)
    target_dir = SKILLS_DIR / slug
    if target_dir.exists():
        shutil.rmtree(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    normalized_paths = list(relative_paths or [])
    if len(normalized_paths) != len(files):
        normalized_paths = [upload.filename or f"file-{index}" for index, upload in enumerate(files)]

    for upload, rel_path_text in zip(files, normalized_paths, strict=False):
        rel_path = Path((rel_path_text or upload.filename or "upload.bin").replace('\\', '/'))
        if rel_path.is_absolute() or ".." in rel_path.parts:
            raise ValueError(f"Unsafe upload path: {rel_path}")

        if len(rel_path.parts) > 1 and safe_slug(rel_path.parts[0]) == slug:
            rel_path = Path(*rel_path.parts[1:])

        destination = target_dir / rel_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(await upload.read())

    skill_md = target_dir / "SKILL.md"
    if not skill_md.exists():
        skill_md.write_text(
            f"---\nname: {slug}\ndescription: Uploaded file-based skill for {skill_name}.\nlicense: Apache-2.0\n---\n\n# {skill_name}\n\nUse this skill when the user asks for {skill_name}.\n",
            encoding="utf-8",
        )

    record = scan_skill_dir(target_dir, source_type=source_type)
    if not record:
        raise ValueError("Failed to parse uploaded skill.")
    return record


def subprocess_script_runner(skill: Skill, script: SkillScript, args: dict[str, Any] | None = None) -> str:
    if not skill.path:
        return f"Error: Skill '{skill.name}' has no directory path."
    if not script.path:
        return f"Error: Script '{script.name}' has no file path."

    script_path = Path(skill.path) / script.path
    if not script_path.is_file():
        return f"Error: Script file not found: {script_path}"

    cmd = [sys.executable, str(script_path)]
    if args:
        for key, value in args.items():
            if isinstance(value, bool):
                if value:
                    cmd.append(f"--{key}")
            elif value is not None:
                cmd.extend([f"--{key}", str(value)])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(script_path.parent),
        )
    except subprocess.TimeoutExpired:
        return f"Error: script '{script.name}' timed out after 30 seconds."

    output = result.stdout.strip()
    if result.stderr:
        output = f"{output}\nStderr:\n{result.stderr.strip()}".strip()
    if result.returncode != 0:
        output = f"{output}\nScript exited with code {result.returncode}".strip()
    return output or "(no output)"


def build_skills_provider(skill_ids: list[str]) -> SkillsProvider | None:
    skill_paths = [SKILLS_DIR / safe_slug(skill_id) for skill_id in skill_ids if (SKILLS_DIR / safe_slug(skill_id)).exists()]
    if not skill_paths:
        return None
    return SkillsProvider(skill_paths=skill_paths, script_runner=subprocess_script_runner)


def run_local_skill_script(skill_id: str, script_name: str, args: dict[str, Any] | None = None) -> dict[str, Any]:
    skill_dir = SKILLS_DIR / safe_slug(skill_id)
    record = scan_skill_dir(skill_dir)
    if not record:
        raise FileNotFoundError(f"Skill '{skill_id}' was not found.")

    matching = next((item for item in record.scripts if item.name == script_name or item.path == script_name), None)
    if not matching:
        raise FileNotFoundError(f"Script '{script_name}' was not found in skill '{skill_id}'.")

    output = subprocess_script_runner(
        Skill(name=record.name, description=record.description, content="", path=str(skill_dir)),
        SkillScript(name=matching.name, description="", path=matching.path),
        args or {},
    )

    parsed_json: Any | None = None
    try:
        parsed_json = json.loads(output)
    except json.JSONDecodeError:
        parsed_json = None

    return {
        "skill": record,
        "script": matching,
        "output": output,
        "json": parsed_json,
    }
