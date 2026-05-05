"""Tests for the GameSettings service."""
from __future__ import annotations

from typing import Any

import pytest

import game.ui.services.game_settings as game_settings
from game.ui.services.game_settings import DEFAULTS, GameSettings


@pytest.fixture(autouse=True)
def reset_default_game_settings() -> None:
    game_settings._default_game_settings = None
    yield
    game_settings._default_game_settings = None


@pytest.fixture
def saved_payloads(monkeypatch: pytest.MonkeyPatch) -> list[tuple[str, dict[str, Any]]]:
    payloads: list[tuple[str, dict[str, Any]]] = []
    monkeypatch.setattr(game_settings, "SETTINGS_FILE", "unit_settings.json")
    monkeypatch.setattr(game_settings, "load_json", lambda path, default=None: {})
    monkeypatch.setattr(
        game_settings,
        "save_json",
        lambda path, data: payloads.append((path, dict(data))),
    )
    return payloads


def test_init_merges_saved_settings_over_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        game_settings,
        "load_json",
        lambda path, default=None: {
            "background_brightness": 0.75,
            "custom_setting": "kept",
        },
    )

    settings = GameSettings()

    assert settings.get("background_brightness") == 0.75
    assert settings.get("custom_setting") == "kept"
    assert settings.get("unknown") is None


def test_set_updates_value_and_persists(saved_payloads: list[tuple[str, dict[str, Any]]]) -> None:
    settings = GameSettings()

    settings.set("background_brightness", 0.5)

    assert settings.get("background_brightness") == 0.5
    assert saved_payloads == [
        ("unit_settings.json", {"background_brightness": 0.5}),
    ]


def test_background_brightness_clamps_before_saving(
    saved_payloads: list[tuple[str, dict[str, Any]]],
) -> None:
    settings = GameSettings()

    settings.background_brightness = 5.0
    settings.background_brightness = -1.0

    assert settings.background_brightness == 0.0
    assert saved_payloads[-2:] == [
        ("unit_settings.json", {"background_brightness": 1.0}),
        ("unit_settings.json", {"background_brightness": 0.0}),
    ]


def test_reset_to_defaults_removes_custom_values(
    saved_payloads: list[tuple[str, dict[str, Any]]],
) -> None:
    settings = GameSettings()
    settings.set("custom_setting", "temporary")

    settings.reset_to_defaults()

    assert settings.get("custom_setting") is None
    assert settings.get("background_brightness") == DEFAULTS["background_brightness"]
    assert saved_payloads[-1] == ("unit_settings.json", DEFAULTS)


def test_default_game_settings_accessors_accept_injected_instance() -> None:
    settings = object()

    game_settings.set_default_game_settings(settings)

    assert game_settings.get_default_game_settings() is settings

