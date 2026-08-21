#!/usr/bin/env python3
"""Build a FineReport internal release ZIP from docs/dev_task.json."""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath


SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def safe_file(project_root: Path, relative: str) -> Path:
    rel = Path(relative)
    if rel.is_absolute() or ".." in rel.parts:
        fail(f"release path must stay inside the project: {relative}")
    resolved = (project_root / rel).resolve()
    try:
        resolved.relative_to(project_root)
    except ValueError:
        fail(f"release path escapes the project: {relative}")
    if not resolved.is_file():
        fail(f"release file does not exist: {resolved}")
    return resolved


def load_task(project_root: Path) -> dict:
    task_path = project_root / "docs" / "dev_task.json"
    if not task_path.is_file():
        fail(f"dev_task.json not found: {task_path}")
    try:
        return json.loads(task_path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read dev_task.json: {exc}")


def collect_files(project_root: Path, task: dict) -> tuple[list[tuple[Path, str]], list[str]]:
    project = task.get("project")
    if not isinstance(project, str) or not project.strip():
        fail("dev_task.json project is required")
    if any(part in project for part in ("/", "\\", "..")):
        fail(f"invalid project name: {project}")

    entries: list[tuple[Path, str]] = []
    listed: list[str] = []

    data_cpt = task.get("data_cpt")
    if data_cpt:
        source = safe_file(project_root, str(data_cpt))
        archive = PurePosixPath("reportlets", project, Path(str(data_cpt)).as_posix()).as_posix()
        entries.append((source, archive))
        listed.append(str(data_cpt))

    release = task.get("release") or {}
    selected_pages = release.get("cpt_files")
    if selected_pages is not None:
        if not isinstance(selected_pages, list) or not selected_pages:
            fail("release.cpt_files must be a non-empty array when specified")
        page_paths = [str(item) for item in selected_pages]
    else:
        pages = task.get("pages")
        if not isinstance(pages, list) or not pages:
            fail("dev_task.json pages[] must not be empty")
        page_paths = []
        for page in pages:
            name = page.get("name") if isinstance(page, dict) else None
            if not isinstance(name, str) or not name.strip():
                fail("every page must have a name")
            filename = name if name.endswith(".cpt") else f"{name}.cpt"
            page_paths.append(f"pages/{filename}")
    for relative in page_paths:
        if not relative.startswith("pages/") or not relative.endswith(".cpt"):
            fail(f"release.cpt_files entries must be pages/*.cpt: {relative}")
        source = safe_file(project_root, relative)
        archive = PurePosixPath("reportlets", project, relative).as_posix()
        entries.append((source, archive))
        listed.append(relative)

    sql_files = release.get("sql_files")
    if sql_files is None or sql_files == []:
        snapshot = project_root / "sql" / "存储过程.sql"
        if snapshot.is_file():
            sql_files = ["sql/存储过程.sql"]
        else:
            snapshot_name = (task.get("database") or {}).get("procedure_snapshot")
            sql_files = [str(snapshot_name)] if snapshot_name else []
    if not isinstance(sql_files, list) or not sql_files:
        fail("every release requires release.sql_files or database.procedure_snapshot")
    sql_names: set[str] = set()
    for relative in sql_files:
        source = safe_file(project_root, str(relative))
        name = source.name
        if name in sql_names:
            fail(f"duplicate SQL filename in release package: {name}")
        sql_names.add(name)
        entries.append((source, PurePosixPath("sql", name).as_posix()))
        listed.append(str(relative))

    change_log = release.get("change_log") or "docs/CHANGELOG.md"
    source = safe_file(project_root, str(change_log))
    entries.append((source, "CHANGELOG.md"))
    listed.append(str(change_log))
    return entries, listed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", required=True, help="Project directory containing docs/dev_task.json")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    if not project_root.is_dir():
        fail(f"project root does not exist: {project_root}")

    task = load_task(project_root)
    version = task.get("version")
    if not isinstance(version, str) or not SEMVER_RE.fullmatch(version):
        fail(f"version must be major.minor.patch: {version!r}")

    entries, listed = collect_files(project_root, task)
    releases_dir = project_root / "releases"
    releases_dir.mkdir(parents=True, exist_ok=True)
    output = releases_dir / f"{task['project']}-{version}.zip"
    if output.exists():
        fail(f"release ZIP already exists: {output}")

    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=releases_dir, suffix=".zip.tmp", delete=False) as temp:
            temp_path = Path(temp.name)
        with zipfile.ZipFile(temp_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for source, arcname in entries:
                archive.write(source, arcname)
        with zipfile.ZipFile(temp_path, "r") as archive:
            broken = archive.testzip()
            if broken:
                fail(f"generated ZIP contains a broken entry: {broken}")
        temp_path.replace(output)
    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()

    cpt_count = sum(1 for _, name in entries if name.endswith(".cpt"))
    sql_count = sum(1 for _, name in entries if name.startswith("sql/"))
    changelog_count = sum(1 for _, name in entries if name == "CHANGELOG.md")
    print(f"Release ZIP: {output}")
    print(f"Version: {version}; CPT: {cpt_count}; SQL: {sql_count}; CHANGELOG: {changelog_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
