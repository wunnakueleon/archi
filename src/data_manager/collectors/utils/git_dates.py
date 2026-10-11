"""Utility for reading last-commit dates of files in a git repository."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

from git import GitCommandError, InvalidGitRepositoryError, Repo

from src.utils.logging import get_logger

logger = get_logger(__name__)


def last_commit_dates(repo_path: Path) -> Dict[str, str]:
    """Return a mapping of repo-relative file paths to their last commit date (UTC, ISO 8601)."""
    try:
        log_output = Repo(repo_path).git(c="core.quotepath=off").log("--format=@@%cI", "--name-only")
    except (GitCommandError, InvalidGitRepositoryError) as exc:
        logger.warning(f"Could not read git history for {repo_path}: {exc}")
        return {}

    dates: Dict[str, str] = {}
    current_date: Optional[str] = None
    for line in log_output.splitlines():
        if not line:
            continue

        if line.startswith("@@"):
            current_date = datetime.fromisoformat(line[2:]).astimezone(timezone.utc).isoformat()
            continue
        
        if line not in dates:
            dates[line] = current_date

    return dates