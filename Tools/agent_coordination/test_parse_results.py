"""Tests for parse_results.py."""
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent / "parse_results.py"


def run_parse(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(path)],
        capture_output=True, text=True, timeout=10,
    )


def _make_completed_file(tmp_path: Path, extra_fields: dict[str, str] | None = None) -> Path:
    """Create a completed-file with an Option B ## Results section."""
    path = tmp_path / "completed.md"
    content = (
        "# Review Request: Test\n"
        "**Request ID:** req_test_001\n"
        "**PickedUp:** 2026-05-02T00:00:00Z\n"
        "\n"
        "## Scope\n\ntest scope\n\n## Instructions\n\ntest instructions\n"
    )
    results = {"Status": "completed", "Completed": "2026-05-02T01:00:00Z",
               "Report": "reviews/2026-05-02_010000_general_test_req-test/report.md",
               "Findings": "7 total (C: 1, M: 2, m: 3, I: 1)"}
    if extra_fields:
        results.update(extra_fields)
    lines = ["", "", "## Results", ""]
    for k, v in results.items():
        lines.append(f"**{k}:** {v}")
    content += "\n".join(lines) + "\n"
    path.write_text(content)
    return path


def test_round_trip_all_fields(tmp_path: Path) -> None:
    path = _make_completed_file(tmp_path)
    r = run_parse(path)
    assert r.returncode == 0, r.stderr
    data = json.loads(r.stdout)
    assert data["Status"] == "completed"
    assert data["Completed"] == "2026-05-02T01:00:00Z"
    assert "reviews" in data["Report"]
    assert data["Findings"].startswith("7 total")
    assert "review_dir" in data
    assert data["review_dir"] == "reviews/2026-05-02_010000_general_test_req-test"


def test_failure_path_without_report(tmp_path: Path) -> None:
    """Completed file with failure status and no Report field."""
    path = tmp_path / "failed.md"
    content = (
        "# Review Request: Test\n"
        "**Request ID:** req_test_fail\n"
        "**PickedUp:** 2026-05-02T00:00:00Z\n"
        "\n"
        "## Scope\n\ntest\n\n## Instructions\n\ntest\n\n"
        "## Results\n"
        "**Status:** failed\n"
        "**Completed:** 2026-05-02T01:00:00Z\n"
        "**FailureReason:** scope unreachable\n"
    )
    path.write_text(content)
    r = run_parse(path)
    assert r.returncode == 0
    data = json.loads(r.stdout)
    assert data["Status"] == "failed"
    assert data["FailureReason"] == "scope unreachable"
    with pytest.raises(KeyError):
        _ = data["review_dir"]


def test_legacy_flat_field_rejected(tmp_path: Path) -> None:
    """File without ## Results section is rejected."""
    path = tmp_path / "legacy.md"
    path.write_text("**Status:** completed\n**Report:** reviews/x/report.md\n")
    r = run_parse(path)
    assert r.returncode != 0
    assert "No ## Results" in r.stderr or "only Option B" in r.stderr


def test_missing_file(tmp_path: Path) -> None:
    r = run_parse(tmp_path / "nonexistent.md")
    assert r.returncode != 0
