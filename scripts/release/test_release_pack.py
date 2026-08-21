from __future__ import annotations

import importlib.util
import tempfile
from pathlib import Path


SCRIPT = Path(__file__).with_name("release_pack.py")
SPEC = importlib.util.spec_from_file_location("release_pack", SCRIPT)
assert SPEC and SPEC.loader
release_pack = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release_pack)


def test_collects_every_data_cpt() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "docs").mkdir()
        (root / "data" / "nested").mkdir(parents=True)
        (root / "pages").mkdir()
        (root / "sql").mkdir()
        (root / "data" / "one.cpt").write_text("one", encoding="utf-8")
        (root / "data" / "nested" / "two.cpt").write_text("two", encoding="utf-8")
        (root / "pages" / "page.cpt").write_text("page", encoding="utf-8")
        (root / "sql" / "存储过程.sql").write_text("select 1", encoding="utf-8")
        (root / "docs" / "CHANGELOG.md").write_text("history", encoding="utf-8")
        task = {
            "project": "demo",
            "version": "1.0.0",
            "pages": [{"name": "page"}],
            "database": {"procedure_snapshot": "sql/存储过程.sql"},
        }

        entries, _ = release_pack.collect_files(root, task)
        archive_names = [archive for _, archive in entries]

        assert "reportlets/demo/data/one.cpt" in archive_names
        assert "reportlets/demo/data/nested/two.cpt" in archive_names


if __name__ == "__main__":
    test_collects_every_data_cpt()
    print("PASS: release data CPT coverage")
