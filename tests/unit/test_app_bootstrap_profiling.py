"""FEAT-22: bootstrap startup phase profiling.

Locks the contract that `bootstrap()` records timing data for 14 named
sub-phases into `ctx.profiler.records`, emits one `[startup] <name>: X.XXs`
log line per phase, finishes with a `[startup] total bootstrap` line, and
eagerly persists the records via `Profiler.save_history()` before returning.
"""
from __future__ import annotations

import logging
import os
from unittest.mock import patch

import pytest

# Force headless before any pygame import.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")


EXPECTED_PHASE_NAMES = [
    "startup: pygame.init",
    "startup: ctx.create_production",
    "startup: font.init",
    "startup: font.preload",
    "startup: display.detect_resolution",
    "startup: display.set_mode",
    "startup: registry.load_components",
    "startup: registry.load_modifiers",
    "startup: registry.load_resources",
    "startup: registry.initialize_ship_data",
    "startup: registry.build_game_registries",
    "startup: assets.ensure_component_derivatives",
    "startup: assets.load_sprites",
    "startup: input.load_keybindings",
]


def _run_bootstrap_with_save_history_patched():
    """Invoke real `bootstrap()` headless, patching disk writes only.

    Returns (BootstrapResult, save_history_mock). Designed to leave the
    real timing path intact so we can read records and log lines.
    """
    import pygame
    import pygame_gui  # noqa: F401 — imported for side effects
    from game import app_bootstrap as boot
    from game.core.profiling import Profiler

    if not pygame.display.get_surface():
        pygame.display.set_mode((1440, 900), pygame.NOFRAME)

    from argparse import Namespace
    args = Namespace(force_resolution=False)
    with patch("pygame.display.Info") as mock_info, \
         patch.object(Profiler, "save_history") as save_history_mock, \
         patch.object(boot, "ensure_component_derivatives"):
        mock_info.return_value.current_w = 2560
        mock_info.return_value.current_h = 1600
        result = boot.bootstrap(args)
        return result, save_history_mock


def test_bootstrap_records_all_14_subphases():
    """Every named sub-phase appears in ctx.profiler.records."""
    result, _ = _run_bootstrap_with_save_history_patched()
    recorded = [r["name"] for r in result.ctx.profiler.records]
    for name in EXPECTED_PHASE_NAMES:
        assert name in recorded, f"Missing phase: {name} (got {recorded})"


def test_bootstrap_pygame_init_recorded_first():
    """The retroactive pygame.init record is the first entry."""
    result, _ = _run_bootstrap_with_save_history_patched()
    assert result.ctx.profiler.records, "No profiler records captured"
    assert result.ctx.profiler.records[0]["name"] == "startup: pygame.init"


def test_bootstrap_pygame_init_record_has_nonzero_duration():
    """pygame.init was actually timed (duration > 0)."""
    result, _ = _run_bootstrap_with_save_history_patched()
    pygame_init_record = next(
        r for r in result.ctx.profiler.records
        if r["name"] == "startup: pygame.init"
    )
    assert pygame_init_record["duration_ms"] > 0


def test_bootstrap_each_subphase_logged(caplog):
    """Each sub-phase emits one `[startup] <name>: X.XXs` info line."""
    with caplog.at_level(logging.INFO, logger="game.app_bootstrap"):
        _run_bootstrap_with_save_history_patched()
    msgs = [r.message for r in caplog.records]
    for name in EXPECTED_PHASE_NAMES:
        short_name = name.removeprefix("startup: ")
        matching = [m for m in msgs if m.startswith(f"[startup] {short_name}: ")]
        assert matching, (
            f"Missing log line for phase {short_name}; got {msgs}"
        )


def test_bootstrap_total_logged(caplog):
    """Bootstrap emits a single `[startup] total bootstrap: X.XXs` line."""
    with caplog.at_level(logging.INFO, logger="game.app_bootstrap"):
        _run_bootstrap_with_save_history_patched()
    msgs = [r.message for r in caplog.records]
    total_lines = [m for m in msgs if m.startswith("[startup] total bootstrap: ")]
    assert len(total_lines) == 1, (
        f"Expected exactly one '[startup] total bootstrap' line, got {total_lines}"
    )


def test_bootstrap_save_history_called_once():
    """save_history is called exactly once before bootstrap returns."""
    _, save_history_mock = _run_bootstrap_with_save_history_patched()
    assert save_history_mock.call_count == 1
