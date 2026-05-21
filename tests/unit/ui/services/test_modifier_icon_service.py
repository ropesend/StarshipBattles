"""Tests for ModifierIconService asset resolution."""
from __future__ import annotations

import logging
import os
from unittest.mock import patch

import pygame
import pytest

from game.ui.services.modifier_icon_service import ModifierIconService


@pytest.fixture(autouse=True)
def ensure_pygame_display() -> None:
    if not pygame.get_init():
        pygame.init()
    if pygame.display.get_surface() is None:
        pygame.display.set_mode((1, 1), pygame.NOFRAME)


def test_get_icon_scales_and_caches_mapped_icon(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = ModifierIconService(icon_size=26)
    source = pygame.Surface((64, 32), pygame.SRCALPHA)
    scaled = pygame.Surface((26, 26), pygame.SRCALPHA)

    monkeypatch.setattr(os.path, "exists", lambda _path: True)
    with (
        patch("pygame.image.load", return_value=source) as mock_load,
        patch("pygame.transform.smoothscale", return_value=scaled) as mock_scale,
    ):
        first = service.get_icon("hardened_mount")
        second = service.get_icon("hardened_mount")

    assert first is scaled
    assert second is scaled
    assert mock_load.call_count == 1
    assert mock_scale.call_count == 1
    assert mock_scale.call_args.args[1] == (26, 26)


def test_get_icon_uses_fallback_filename_for_unmapped_modifier(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = ModifierIconService(icon_size=26)
    checked_paths: list[str] = []
    surface = pygame.Surface((26, 26), pygame.SRCALPHA)

    def exists(path: str) -> bool:
        checked_paths.append(path)
        return True

    monkeypatch.setattr(os.path, "exists", exists)
    with patch("pygame.image.load", return_value=surface):
        result = service.get_icon("custom_boost")

    assert result is not None
    assert os.path.basename(checked_paths[-1]) == "mod_custom_boost.png"


def test_get_icon_returns_none_and_logs_when_mapped_file_is_missing(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture,
) -> None:
    service = ModifierIconService(icon_size=26)
    monkeypatch.setattr(os.path, "exists", lambda _path: False)

    with caplog.at_level(logging.WARNING, logger="game.ui.services.modifier_icon_service"):
        result = service.get_icon("hardened_mount")

    assert result is None
    assert "mod_hardened_mount.png" in caplog.text
    assert "hardened_mount" in caplog.text


def test_get_icon_returns_none_when_pygame_load_fails(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture,
) -> None:
    service = ModifierIconService(icon_size=26)
    monkeypatch.setattr(os.path, "exists", lambda _path: True)

    with (
        caplog.at_level(logging.ERROR, logger="game.ui.services.modifier_icon_service"),
        patch("pygame.image.load", side_effect=pygame.error("bad png")),
    ):
        result = service.get_icon("hardened_mount")

    assert result is None
    assert "Error loading modifier icon" in caplog.text
    assert "hardened_mount" not in service._cache


def test_PROJ466_get_icon_returns_none_when_load_raises_oserror(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture,
) -> None:
    """PROJ-466 Phase 2 Task 2.8: an OSError during load is caught (the
    narrowed `(pygame.error, OSError)` tuple) and logged, returning None."""
    service = ModifierIconService(icon_size=26)
    monkeypatch.setattr(os.path, "exists", lambda _path: True)

    with (
        caplog.at_level(logging.ERROR, logger="game.ui.services.modifier_icon_service"),
        patch("pygame.image.load", side_effect=OSError("disk gone")),
    ):
        result = service.get_icon("hardened_mount")

    assert result is None
    assert "Error loading modifier icon" in caplog.text


def test_PROJ466_get_icon_does_not_swallow_unexpected_exception(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """PROJ-466 Phase 2 Task 2.8: the gratuitous `(pygame.error, Exception)`
    catch was narrowed, so an unexpected exception type (e.g. a programming
    error) now propagates instead of being silently turned into None."""
    service = ModifierIconService(icon_size=26)
    monkeypatch.setattr(os.path, "exists", lambda _path: True)

    with patch("pygame.image.load", side_effect=ValueError("unexpected")):
        with pytest.raises(ValueError):
            service.get_icon("hardened_mount")


def test_clear_cache_removes_cached_icons() -> None:
    service = ModifierIconService(icon_size=26)
    service._cache["hardened_mount"] = pygame.Surface((26, 26), pygame.SRCALPHA)

    service.clear_cache()

    assert service._cache == {}
