"""PROJ-411 Task 1.2/1.3: Strategy panel `profile_action()` spans.

Phase 1 instruments the open paths of all five strategy-layer panels with
named `profile_action()` spans so Phase 1 Scalene runs (Task 1.10) can
correlate line-level CPU evidence with high-level panel operations.

This file asserts that each of the 12 planned spans is wired by checking
that the target's source contains a `profile_action("Panel: ...")`
decorator. It also runs a small set of easy spans (module-level
functions exercised by the smoke scenario) and asserts the named
records appear in the Profiler.
"""
from __future__ import annotations

import inspect
import os
import tempfile

import pytest

from game.core.profiling import (
    Profiler,
    get_default_profiler,
    set_default_profiler,
)


# --------------------------------------------------------------------------
# Test 1: introspection — every span's decorator is wired in source.
# --------------------------------------------------------------------------

# (module path, attribute path inside module, span name)
_INSTRUMENTED_TARGETS: list[tuple[str, str, str]] = [
    # Build Queue
    (
        "game.ui.screens.build_queue_list_window",
        "BuildQueueRowCollector.collect",
        "Panel: BuildQueue.collect_rows",
    ),
    (
        "game.ui.screens.build_queue_list_window",
        "BuildQueueListUiBuilder.build",
        "Panel: BuildQueue.rebuild_ui_labels",
    ),
    (
        "game.strategy.systems.design_repository",
        "DesignRepository.scan_designs",
        "Panel: BuildQueue.scan_designs",
    ),
    # Empire Overview
    (
        "game.ui.panels.empire_treasury_panel",
        "load_resource_icons",
        "Panel: EmpireOverview.load_resource_icons",
    ),
    (
        "game.ui.screens.empire_panel_window",
        "EmpirePanelWindow._build_treasury_tab",
        "Panel: EmpireOverview.build_treasury_tab",
    ),
    # Planet Registry
    (
        "game.ui.screens.planet_list_filters",
        "gather_planets",
        "Panel: PlanetRegistry.gather_planets",
    ),
    (
        "game.ui.screens.planet_list_filters",
        "compute_planet_effect_keys",
        "Panel: PlanetRegistry.compute_effect_keys",
    ),
    (
        "game.ui.screens.planet_list_window",
        "build_effect_columns",
        "Panel: PlanetRegistry.build_effect_columns",
    ),
    # Star Registry
    (
        "game.ui.screens.star_list_filters",
        "gather_stars",
        "Panel: StarRegistry.gather_stars",
    ),
    (
        "game.ui.screens.star_list_filters",
        "compute_star_ranges",
        "Panel: StarRegistry.compute_ranges",
    ),
    # Event Log
    (
        "game.ui.screens.event_log_window",
        "EventLogWindow.__init__",
        "Panel: EventLog.init",
    ),
    (
        "game.ui.screens.event_log_window",
        "EventLogWindow._rebuild_list",
        "Panel: EventLog.rebuild_data_source",
    ),
]


def _resolve_attr(module: object, dotted_attr: str) -> object:
    obj = module
    for part in dotted_attr.split("."):
        obj = getattr(obj, part)
    return obj


@pytest.mark.parametrize(
    "module_path,attr_path,span_name",
    _INSTRUMENTED_TARGETS,
    ids=[t[2] for t in _INSTRUMENTED_TARGETS],
)
def test_target_is_decorated_with_profile_action(
    module_path: str, attr_path: str, span_name: str
) -> None:
    """Each target's source must contain the matching `@profile_action("...")`."""
    module = __import__(module_path, fromlist=[""])
    target = _resolve_attr(module, attr_path)
    # `inspect.getsourcefile(target)` returns the location of the wrapping
    # closure (inside `profiling.py`) when `target` is decorated, because
    # `functools.wraps` copies `__name__`/`__module__` but the wrapper's
    # own code object still lives in profiling.py. Unwrap first so we get
    # the original function's file.
    target_unwrapped = inspect.unwrap(target)
    file_path = inspect.getsourcefile(target_unwrapped)
    assert file_path is not None
    line_no = target_unwrapped.__code__.co_firstlineno
    with open(file_path, "r", encoding="utf-8") as fh:
        lines = fh.readlines()
    # Walk backwards from the def line to find any decorators that apply.
    # `co_firstlineno` is 1-based and may point at the @decorator or `def`.
    decorator_window = "".join(lines[max(0, line_no - 5): line_no + 1])
    assert f'profile_action("{span_name}")' in decorator_window, (
        f"Target `{attr_path}` in {module_path} is not decorated with "
        f"`@profile_action(\"{span_name}\")`.\n"
        f"File: {file_path}\n"
        f"Decorator window (lines {line_no - 4}..{line_no}):\n"
        f"{decorator_window}"
    )


# --------------------------------------------------------------------------
# Test 2: runtime — module-level spans fire under the smoke scenario.
# --------------------------------------------------------------------------

@pytest.fixture
def _active_profiler():
    """Activate a fresh Profiler as the module-level default."""
    profiler = Profiler()
    profiler.start()
    previous = get_default_profiler()
    set_default_profiler(profiler)
    yield profiler
    profiler.stop()
    set_default_profiler(previous)


def test_module_level_spans_fire_under_smoke(smoke_turn1_scenario, _active_profiler):
    """The 7 module-level spans fire when their targets are called."""
    from game.ui.screens.planet_list_filters import (
        compute_planet_effect_keys,
        gather_planets,
    )
    from game.ui.screens.planet_list_window import build_effect_columns
    from game.ui.screens.star_list_filters import (
        compute_star_ranges,
        gather_stars,
    )
    from game.ui.panels.empire_treasury_panel import load_resource_icons
    from game.strategy.systems.design_repository import DesignRepository

    session, galaxy, empires = smoke_turn1_scenario
    empire = empires[0]

    planets = list(gather_planets(galaxy, empire))
    keys = compute_planet_effect_keys(planets)
    build_effect_columns(keys)

    stars = list(gather_stars(galaxy))
    compute_star_ranges(stars)

    load_resource_icons()

    with tempfile.TemporaryDirectory() as tmpdir:
        os.makedirs(os.path.join(tmpdir, "designs", "empire_0"), exist_ok=True)
        DesignRepository(tmpdir, empire_id=0).scan_designs()

    span_names = {r["name"] for r in _active_profiler.records}
    expected = {
        "Panel: PlanetRegistry.gather_planets",
        "Panel: PlanetRegistry.compute_effect_keys",
        "Panel: PlanetRegistry.build_effect_columns",
        "Panel: StarRegistry.gather_stars",
        "Panel: StarRegistry.compute_ranges",
        "Panel: EmpireOverview.load_resource_icons",
        "Panel: BuildQueue.scan_designs",
    }
    missing = expected - span_names
    assert not missing, (
        f"these module-level spans did NOT fire: {missing}.\n"
        f"All recorded spans: {sorted(span_names)}"
    )
