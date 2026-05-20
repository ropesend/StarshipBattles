"""Concurrency + atomicity tests for create_project / index_manager.

The project index (`projects_index.md`) is shared mutable state: creating a
project reads the "Next Project ID", reserves a directory, then rewrites the
index. Without a lock, parallel creators (e.g. several `claude-proj-from-*`
subagents finishing at once) interleave the read-modify-write and collide on
the same PROJ id. These tests pin the lock + rollback behaviour.
"""
import sys
import time
import threading
from pathlib import Path

import pytest

PROJECTS_SCRIPTS = Path(__file__).parent.parent.parent / "Projects" / "scripts"
sys.path.insert(0, str(PROJECTS_SCRIPTS))

import create_project as cp  # noqa: E402
from utils import index_manager as im  # noqa: E402

INDEX_TEMPLATE = """# Projects Index

Next Project ID: PROJ-01

## Active Projects
| ID | Title | Status | Started | Last Updated |
|----|-------|--------|---------|--------------|

## Archived Projects
| ID | Title | Status | Started | Completed |
|----|-------|--------|---------|----------|
"""


@pytest.fixture
def isolated_index(tmp_path, monkeypatch):
    """Redirect the index + project dirs (and thus the lockfile) into tmp_path."""
    active = tmp_path / "active_projects"
    archived = tmp_path / "archived_projects"
    active.mkdir()
    archived.mkdir()
    index = tmp_path / "projects_index.md"
    index.write_text(INDEX_TEMPLATE, encoding="utf-8")

    monkeypatch.setattr(im, "INDEX_FILE", index)
    monkeypatch.setattr(im, "ACTIVE_DIR", active)
    monkeypatch.setattr(im, "ARCHIVED_DIR", archived)
    monkeypatch.setattr(cp, "ACTIVE_DIR", active)
    return tmp_path


def test_concurrent_create_project_unique_ids(isolated_index, monkeypatch):
    """Parallel create_project calls must reserve distinct ids, no crashes."""
    n = 4

    # Widen the reserve->commit window so the race is deterministic. The sleep
    # runs *inside* whatever critical section create_project establishes, so a
    # correct lock still serialises (no deadlock); only the unlocked code races.
    real_next = im.get_next_project_id

    def slow_next() -> str:
        pid = real_next()
        time.sleep(0.15)
        return pid

    monkeypatch.setattr(cp, "get_next_project_id", slow_next)

    results: dict[int, str] = {}
    errors: dict[int, str] = {}

    def worker(i: int) -> None:
        try:
            results[i] = cp.create_project(f"Concurrent {i}")
        except BaseException as exc:  # SystemExit included — a crash is a failure
            errors[i] = repr(exc)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(n)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors, f"concurrent creators failed: {errors}"
    ids = list(results.values())
    assert len(set(ids)) == n, f"duplicate PROJ ids under contention: {sorted(ids)}"

    entries = im.parse_project_entries(im.read_projects_index())
    indexed = {e.project_id for e in entries}
    assert indexed == set(ids), f"index rows {sorted(indexed)} != created {sorted(ids)}"


def test_index_write_failure_is_fatal_and_rolls_back(isolated_index, monkeypatch):
    """A failed index write must not silently succeed nor leave an orphan dir."""
    def boom(*_args, **_kwargs):
        raise RuntimeError("simulated index write failure")

    monkeypatch.setattr(cp, "add_project_to_index", boom)

    with pytest.raises(Exception):  # noqa: B017 — must NOT swallow + report success
        cp.create_project("Doomed")

    # No orphaned project directory should remain.
    leftover = list((isolated_index / "active_projects").iterdir())
    assert leftover == [], f"orphaned project dir(s) left behind: {leftover}"
