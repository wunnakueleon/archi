import os
import subprocess
from pathlib import Path
from typing import Optional

from src.data_manager.collectors.utils.git_dates import last_commit_dates


def _git(repo: Path, *args: str, date: Optional[str] = None) -> None:
    env = dict(os.environ)
    if date:
        env["GIT_AUTHOR_DATE"] = date
        env["GIT_COMMITTER_DATE"] = date
    subprocess.run(
        ["git", "-c", "user.name=test", "-c", "user.email=test@example.com", *args],
        cwd=repo,
        env=env,
        check=True,
        capture_output=True,
    )


def _commit(repo: Path, name: str, text: str, date: str) -> None:
    path = repo / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    _git(repo, "add", name)
    _git(repo, "commit", "-m", f"update {name}", date=date)


def test_latest_commit_wins_and_dates_are_utc(tmp_path):
    _git(tmp_path, "init")
    _commit(tmp_path, "a.md", "v1", "2024-01-01T12:00:00+00:00")
    _commit(tmp_path, "docs/b.md", "v1", "2025-06-01T12:00:00+07:00")
    _commit(tmp_path, "a.md", "v2", "2026-03-05T10:12:00-04:00")

    dates = last_commit_dates(tmp_path)

    assert dates["docs/b.md"] == "2025-06-01T05:00:00+00:00"
    assert dates["a.md"] == "2026-03-05T14:12:00+00:00"


def test_uncommitted_file_has_no_date(tmp_path):
    _git(tmp_path, "init")
    _commit(tmp_path, "a.md", "v1", "2024-01-01T12:00:00+00:00")
    (tmp_path / "new.md").write_text("not committed yet")

    dates = last_commit_dates(tmp_path)

    assert "a.md" in dates
    assert "new.md" not in dates


def test_non_git_folder_returns_empty(tmp_path):
    assert last_commit_dates(tmp_path) == {}
