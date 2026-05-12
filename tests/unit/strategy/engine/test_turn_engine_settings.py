"""Unit tests for TurnEngineSettings loader (PROJ-412 Phase 4)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from game.strategy.engine.turn_engine_settings import (
    TurnEngineSettings,
    load_turn_engine_settings,
)


def test_defaults_when_file_missing(tmp_path: Path) -> None:
    settings = load_turn_engine_settings(tmp_path / "does_not_exist.json")
    assert settings == TurnEngineSettings()
    assert settings.progress_callback_interval == 5


def test_defaults_when_file_is_not_a_dict(tmp_path: Path) -> None:
    path = tmp_path / "settings.json"
    path.write_text("[1, 2, 3]", encoding="utf-8")
    settings = load_turn_engine_settings(path)
    assert settings.progress_callback_interval == 5


def test_defaults_when_field_is_garbage(tmp_path: Path) -> None:
    path = tmp_path / "settings.json"
    path.write_text(json.dumps({"progress_callback_interval": "five"}), encoding="utf-8")
    settings = load_turn_engine_settings(path)
    assert settings.progress_callback_interval == 5


def test_reads_valid_integer(tmp_path: Path) -> None:
    path = tmp_path / "settings.json"
    path.write_text(json.dumps({"progress_callback_interval": 10}), encoding="utf-8")
    settings = load_turn_engine_settings(path)
    assert settings.progress_callback_interval == 10


@pytest.mark.parametrize("raw,expected", [(0, 1), (-5, 1), (200, 100), (1, 1), (100, 100)])
def test_clamps_to_sensible_range(tmp_path: Path, raw: int, expected: int) -> None:
    path = tmp_path / "settings.json"
    path.write_text(json.dumps({"progress_callback_interval": raw}), encoding="utf-8")
    settings = load_turn_engine_settings(path)
    assert settings.progress_callback_interval == expected


def test_corrupt_json_falls_back_to_defaults(tmp_path: Path) -> None:
    path = tmp_path / "settings.json"
    path.write_text("{not valid json", encoding="utf-8")
    settings = load_turn_engine_settings(path)
    assert settings.progress_callback_interval == 5
