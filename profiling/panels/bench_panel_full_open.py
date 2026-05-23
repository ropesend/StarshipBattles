"""PROJ-411 Task 1.10: Full-panel-open benchmark.

Unlike ``tests/performance/test_panel_loadtime_benchmark.py`` (which loops
module-level data-gathering functions in isolation), this benchmark
constructs each of the five strategy panel windows end-to-end. That
captures the **user-visible** open cost — pygame_gui widget construction,
window shell rasterization, VirtualTable build, plus the data-gathering
work already covered by the existing benchmark.

PROJ-478 Phase 2 relocated this module from
``tests/performance/test_panel_full_open_benchmark.py`` to
``profiling/panels/bench_panel_full_open.py``. The original "test_*"
functions performed zero assertions (CAT-2 tests-nothing-real) — they
exist purely to populate Profiler spans and pretty-print medians. As
profiling scripts rather than tests they are no longer collected by
pytest's default discovery; invoke explicitly:

    python -m pytest profiling/panels/bench_panel_full_open.py -n 0 -s

For Scalene line-level data:

    python Tools/profiling/run_scalene.py pytest --mode cpu \\
        --pytest-target profiling/panels/bench_panel_full_open.py
"""
from __future__ import annotations

from collections import defaultdict
from statistics import median
from unittest.mock import MagicMock

import pygame
import pygame_gui
import pytest

from game.core.profiling import (
    Profiler,
    get_default_profiler,
    set_default_profiler,
)


_OPEN_ITERATIONS = 10  # full-window construction is much heavier than data gather


@pytest.fixture(scope="module")
def display_surface():
    """Ensure a real pygame display is available for pygame_gui."""
    if not pygame.display.get_surface():
        pygame.display.set_mode((1920, 1080))
    return pygame.display.get_surface()


@pytest.fixture
def ui_manager(display_surface):
    """A fresh pygame_gui UIManager per test."""
    manager = pygame_gui.UIManager((1920, 1080))
    yield manager
    manager.clear_and_reset()


@pytest.fixture
def active_profiler():
    profiler = Profiler()
    profiler.start()
    previous = get_default_profiler()
    set_default_profiler(profiler)
    yield profiler
    profiler.stop()
    set_default_profiler(previous)


def _print_span_medians(profiler: Profiler, label: str) -> None:
    by_name: dict[str, list[float]] = defaultdict(list)
    for r in profiler.records:
        by_name[r["name"]].append(r["duration_ms"])

    print(f"\n--- {label} ({len(profiler.records)} records) ---")
    for name in sorted(by_name):
        ds = by_name[name]
        print(
            f"  {name:48s}  n={len(ds):3d}  "
            f"median={median(ds):8.3f} ms  "
            f"max={max(ds):8.3f} ms  "
            f"total={sum(ds):9.2f} ms"
        )


def _build_planet_list_window(ui_manager, world, empire, *, facade_state):
    from game.ui.screens.planet_list_window import PlanetListWindow

    rect = pygame.Rect(100, 100, 1600, 800)
    facade = MagicMock()
    facade.facade_state = facade_state
    # PROJ-477 Phase 4: PlanetListWindow takes the scene.world live seam.
    window = PlanetListWindow(
        rect, ui_manager, world, empire,
        window_manager=None,
        facade=facade,
    )
    return window


def _build_star_list_window(ui_manager, world, *, facade_state):
    from game.ui.screens.star_list_window import StarListWindow

    rect = pygame.Rect(100, 100, 1600, 800)
    # PROJ-477 Phase 4: StarListWindow takes the scene.world live seam.
    window = StarListWindow(
        rect, ui_manager, world,
        window_manager=None,
        facade_state=facade_state,
    )
    return window


def _build_empire_window(ui_manager, empire, registries, *, facade_state):
    from game.ui.screens.empire_panel_window import EmpirePanelWindow

    rect = pygame.Rect(100, 100, 1400, 800)
    window = EmpirePanelWindow(
        rect, ui_manager, empire,
        window_manager=None,
        registries=registries,
        facade_state=facade_state,
    )
    return window


def _build_event_log_window(ui_manager):
    from game.ui.screens.event_log_window import EventLogWindow

    rect = pygame.Rect(100, 100, 1400, 800)
    window = EventLogWindow(
        rect, ui_manager, [],
        window_manager=None,
        empire_name="Test Empire",
    )
    return window


def bench_full_window_open_uncached(
    smoke_turn1_scenario, ui_manager, active_profiler
):
    """BEFORE state: ``facade_state=None`` — every open does full work."""
    from game.ui.screens.strategy_world_access import StrategyWorldAccess
    session, galaxy, empires = smoke_turn1_scenario
    empire = empires[0]
    registries = session.registries
    world = StrategyWorldAccess(lambda: session)  # PROJ-477 Phase 4

    for _ in range(_OPEN_ITERATIONS):
        w = _build_planet_list_window(ui_manager, world, empire, facade_state=None)
        w.kill()
        w = _build_star_list_window(ui_manager, world, facade_state=None)
        w.kill()
        w = _build_empire_window(ui_manager, empire, registries, facade_state=None)
        w.kill()
        w = _build_event_log_window(ui_manager)
        w.kill()

    _print_span_medians(active_profiler, "FULL OPEN — uncached")


def bench_full_window_open_with_cache(
    smoke_turn1_scenario, ui_manager, active_profiler
):
    """AFTER state: ``facade_state`` supplied — caches active across opens."""
    from game.strategy.facade.slices._facade_state import FacadeSessionState

    from game.ui.screens.strategy_world_access import StrategyWorldAccess
    session, galaxy, empires = smoke_turn1_scenario
    empire = empires[0]
    registries = session.registries
    state = FacadeSessionState(session=session)
    world = StrategyWorldAccess(lambda: session)  # PROJ-477 Phase 4

    for _ in range(_OPEN_ITERATIONS):
        w = _build_planet_list_window(ui_manager, world, empire, facade_state=state)
        w.kill()
        w = _build_star_list_window(ui_manager, world, facade_state=state)
        w.kill()
        w = _build_empire_window(ui_manager, empire, registries, facade_state=state)
        w.kill()
        w = _build_event_log_window(ui_manager)
        w.kill()

    _print_span_medians(active_profiler, "FULL OPEN — cached")
