"""Regression tests for the repo-local Codex configuration."""

from __future__ import annotations

from pathlib import Path
import tomllib


def _repo_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "pyproject.toml").exists() and (parent / ".codex").is_dir():
            return parent
    raise RuntimeError("Could not locate repository root from test path")


def test_gpt_5_4_project_config_sets_documented_context_window() -> None:
    config_path = _repo_root() / ".codex" / "config.toml"
    config = tomllib.loads(config_path.read_text(encoding="utf-8"))

    assert config["model"] == "gpt-5.4"
    assert config["model_context_window"] == 1_050_000
