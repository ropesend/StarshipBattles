from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_scalene_workflow_files_are_documented() -> None:
    """Scalene profiling must stay discoverable for humans and agents."""
    requirements = _read("requirements-dev.txt")
    assert "scalene>=2.2.1" in requirements

    docs_index = _read("docs/README.md")
    assert "[performance_profiling.md](guides/performance_profiling.md)" in docs_index

    profiling_guide = _read("docs/guides/performance_profiling.md")
    assert "Scalene" in profiling_guide
    assert "Tools/profiling/run_scalene.py" in profiling_guide
    assert "output/profiles/scalene/" in profiling_guide
    assert "Do not optimize from a single profile" in profiling_guide

    tools_index = _read("Tools/README.md")
    assert "[profiling](profiling/)" in tools_index

    tool_readme = _read("Tools/profiling/README.md")
    assert "python Tools/profiling/run_scalene.py" in tool_readme
    assert "No production code imports this tool" in tool_readme

    skill = _read(".agents/skills/codex-starship-performance-profiling/SKILL.md")
    assert "name: codex-starship-performance-profiling" in skill
    assert "Tools/profiling/run_scalene.py" in skill
    assert "docs/guides/performance_profiling.md" in skill


def test_run_scalene_dry_run_builds_repeatable_pytest_command() -> None:
    script = ROOT / "Tools" / "profiling" / "run_scalene.py"
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "pytest",
            "--mode",
            "cpu",
            "--pytest-target",
            "tests/unit/core",
            "--pytest-filter",
            "sample_case",
            "--timestamp",
            "20260428T000000",
            "--dry-run",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "python -m scalene run --cpu-only" in result.stdout
    assert "-o output/profiles/scalene/20260428T000000-pytest-cpu.json" in result.stdout
    assert "-m pytest tests/unit/core -k sample_case" in result.stdout
    assert "-n 0" in result.stdout
