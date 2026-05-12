"""PROJ-411 Phase 3 Task 3.1: count-based regression gates.

These are hard pass/fail gates protecting the PROJ-411 cache invariants
against silent regression. They complement the function-level unit tests
shipped with Phase 1 by exercising the **production entry points** —
``StrategySessionFacade.invalidate_all`` (the actual turn-advance call),
the module-level ``_RESOURCE_ICON_CACHE`` short-circuit, and the wiring
between the strategy panels and ``FacadeSessionState``.

Coverage map (cross-reference — DO NOT duplicate these tests here):

* ``test_gather_planets_caching.py`` — function-level cache for
  ``gather_planets`` / ``gather_stars`` (Task 1.5/1.7).
* ``test_scan_designs_caching.py`` — function-level cache for
  ``DesignLibrary.scan_designs`` (Task 1.3), including
  ``test_save_design_invalidates_per_empire_cache_entry`` and
  ``test_cache_isolated_per_empire``.
* ``test_empire_economy_caching.py`` — function-level cache for
  ``EmpireEconomyService.get_snapshot`` (Task 1.7).
* ``test_facade_state_proj411_caches.py`` — slice-level invariants on
  ``FacadeSessionState`` (Task 1.2): each cache's reset value and
  ``invalidate_all`` per-cache wiping.
* ``test_event_log_no_copy.py`` — ``EventLogWindow.all_events`` is the
  facade list by identity (Task 1.9).
* ``test_empire_panel_lazy_load.py`` — Population tab not built until
  first show (Task 1.8).

This file adds gates the above don't cover:

* Facade-level invalidate path (production turn-advance entry point).
* ``load_resource_icons`` module-level cache.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.performance


def test_facade_process_turn_clears_all_proj411_caches(
    smoke_turn1_scenario,
) -> None:
    """``StrategySessionFacade.process_turn`` (the turn-advance entry
    point used by the UI) must clear every PROJ-411 cache slice on
    ``FacadeSessionState``.

    The slice-level tests (``test_facade_state_proj411_caches.py``)
    exercise ``FacadeSessionState.invalidate_all`` directly. This gate
    exercises the production call path — a future refactor that
    quietly stops calling ``self._state.invalidate_all()`` from
    ``process_turn`` would fail this test.
    """
    from game.strategy.facade.strategy_session_facade import StrategySessionFacade

    session, _galaxy, empires = smoke_turn1_scenario
    facade = StrategySessionFacade(session)
    state = facade.facade_state

    # Seed every PROJ-411 cache so we can assert clearing.
    state.designs_by_empire[empires[0].id] = ["sentinel-design"]
    state.planets_for_empire_cache[empires[0].id] = ["sentinel-planet"]
    state.stars_cache_new = ["sentinel-star"]
    state.empire_economy_snapshot[empires[0].id] = {"sentinel": "snapshot"}

    facade.process_turn()

    assert state.designs_by_empire == {}
    assert state.planets_for_empire_cache == {}
    assert state.stars_cache_new is None
    assert state.empire_economy_snapshot == {}


def test_load_resource_icons_module_cache_short_circuits_second_call() -> None:
    """``load_resource_icons`` (Task 1.7) caches at the module level so
    repeat calls don't re-load image files.

    The cache lives on the module attribute ``_RESOURCE_ICON_CACHE``;
    the second invocation must return the SAME dict by identity (cache
    hit), not a freshly-built one. A regression that rebuilds per call
    would silently re-pay the icon-load cost.
    """
    from game.ui.panels import empire_treasury_panel

    # Reset so the test is order-independent.
    empire_treasury_panel._RESOURCE_ICON_CACHE = None

    first = empire_treasury_panel.load_resource_icons()
    second = empire_treasury_panel.load_resource_icons()

    assert first is second, (
        "load_resource_icons must return the same cached dict on repeat "
        "calls; got two distinct objects (cache short-circuit broken)."
    )
    # The cache itself must hold the result.
    assert empire_treasury_panel._RESOURCE_ICON_CACHE is first
