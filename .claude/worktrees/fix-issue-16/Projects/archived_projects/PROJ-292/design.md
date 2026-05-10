# PROJ-292: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Audit provenance

This project is the sibling of PROJ-291. Both resolve findings from a dual cross-project audit of PROJ-283..290 (mine + the user's prior 5-skeptic audit + 2 impartial-subagent adjudications). PROJ-291 owns the 3 Critical findings; PROJ-292 owns:

- **3 High** — H1 (PROJ-289 view-kwarg dead in 2 callers), H2 (projector reaches private API), H3 (catch-all exception swallow in net-cell colour code).
- **3 Major** — M1 (UI→engine layer violation), M2 (CachedRaceRegistry invalidation untested + no mtime fallback). M3 (Treasury Upkeep row not e2e tested) is actually closed by PROJ-291 Phase 1 Task 1.3 — leaving it here as a no-op tracker until PROJ-291 lands.
- **11 Minor** — m1, m4-m13 from the dual audit, plus m17 (`projects_index.md` typo).

The 12 cleared false-positives from the prior audit + the M4 cache-rollback concern (cleared by impartial subagent — `TurnStateSnapshot.restore()` does a full deserialization that discards stale planet objects) are NOT in scope.

## Architecture

### H1 fix shape: thread the view kwarg

Reference implementation: [game/ui/screens/strategy_detail_formatter.py:264](game/ui/screens/strategy_detail_formatter.py#L264). PROJ-289 wired the strategy detail panel; PROJ-292 backfills the same wiring into the two other colonized-context callers.

```python
# Before (planet_list_window.py:511, build_queue_panel_factory.py:181):
PlanetReportPanel(..., empire=empire, race_registry=race_registry)

# After:
view = facade.get_colony_demographic_view(planet.id) if planet.owner_id is not None else None
PlanetReportPanel(..., empire=empire, race_registry=race_registry, view=view)
```

Both callers already have access to the facade — `PlanetListWindow` resolves it via the `_race_registry` constructor injection (see line 52 of the file); `BuildQueuePanelFactory` has `self.session.facade` per the build-queue construction context. PlanetSelectionWindow (uncolonized only — colonization-flow filter at line ~140) is intentionally untouched per the impartial subagent verdict.

### H2 fix shape: integration test pinning projector vs engine drain

The risk: `PlanetEconomyProjector._project_yard_drain` calls `_collect_planet_sources` from `build_queue_source.py` (private API). If that function ever refactors signatures, the projector's drain dict diverges silently from what `ProductionEngine` actually drains during a turn tick.

The test:

```python
# tests/integration/strategy/test_projector_drain_matches_engine.py
def test_yard_drain_projection_matches_engine_tick(...):
    planet = _planet_with_one_queued_complex(resource_cost={"metals": 1000})
    economy = EconomyConfig(population_consumption={"organics": 0.001})

    # 1. Project the drain
    projector = PlanetEconomyProjector(registries=..., economy_config=economy, race_registry=...)
    projection = projector.project(planet)
    projected_drain = {r: -projection[r].yard for r in projection if projection[r].yard > 0}

    # 2. Run one tick
    pre_stockpile = dict(planet.stockpile)
    ProductionEngine(registries=...).process_construction_tick(tick=1, empires=[empire], galaxy=None)
    actual_drain = {r: pre_stockpile[r] - planet.stockpile[r] for r in pre_stockpile}

    # 3. Per-turn drain should match (account for habitability scaling — both apply the same multiplier)
    for resource in projected_drain:
        # Engine drains at TICK rate; projector reports per-TURN. Multiply tick by 100.
        assert actual_drain.get(resource, 0) * 100 == pytest.approx(projected_drain[resource], rel=0.01)
```

Tolerance for tick-vs-turn timing scale and for floating-point arithmetic. The test fails loudly if the two paths drift.

### H3 fix shape: narrow the exception

```python
# Before:
try:
    cell.text_colour = color
    cell.rebuild()
except (AttributeError, Exception):
    pass

# After:
try:
    cell.text_colour = color
    cell.rebuild()
except AttributeError:
    # pygame_gui versions vary on text_colour-setter support — accept silent fallback
    pass
```

The `Exception` catch was a defensive over-shoot. The intent was to handle pygame_gui version variance on the `text_colour` setter; the catch-all swallowed everything (programming errors, future API changes, RuntimeError from pygame). Tightening to `AttributeError` only lets real bugs surface.

Test: mock `cell.text_colour =` to raise `RuntimeError`; assert it propagates (not swallowed).

### M1 fix shape: empire_economy_service.py facade

```python
# game/strategy/services/empire_economy_service.py (NEW)
"""Service-layer facade over EmpireEconomyCalculator (PROJ-292 M1).

UI panels must not import from game.strategy.engine directly (per
docs/01_ARCHITECTURE.md layer rules). This facade exposes the read
surface — calculator stays in the engine layer."""
from typing import TYPE_CHECKING
from game.strategy.engine.empire_economy_calculator import (
    EmpireEconomyCalculator, EmpireEconomySnapshot,
)

class EmpireEconomyService:
    def __init__(self, registries, economy_config=None, race_registry=None):
        self._calculator = EmpireEconomyCalculator(...)

    def get_snapshot(self, empire) -> 'EmpireEconomySnapshot':
        return self._calculator.calculate(empire)

__all__ = ["EmpireEconomyService", "EmpireEconomySnapshot"]
```

UI panels import `EmpireEconomyService` (and `EmpireEconomySnapshot` re-exported for typing) from `game.strategy.services.empire_economy_service`. The calculator stays in the engine layer; only the read-only snapshot is consumed by UI.

### M2 fix shape

Two parts:

1. **Test coverage** (`TestCachedRaceRegistryStaleness`): mock the underlying `RaceLibrary.get_race` to return CONFIG_A on first call, CONFIG_B on second call. Assert: `registry.get_race("foo")` returns CONFIG_A. `registry.invalidate("foo")`. `registry.get_race("foo")` returns CONFIG_B. Pin the contract.

2. **Mtime fallback** (USER DECISION POINT — Phase 3 Task 3.3): add an optional `auto_refresh_on_mtime: bool = False` kwarg to `CachedRaceRegistry.__init__`. When True, `get_race` checks the file's mtime and refreshes the cache if the file has been modified since the cache entry was written. **Default: False** (manual invalidation only — preserves PROJ-287's documented behaviour). Recommend the user opt in only if mod-tooling becomes a real concern.

### Minor sweep (Phase 5)

| Minor | Fix |
|---|---|
| m1 (asymmetric `update_planet` semantics) | Document the contract in the docstring (no behaviour change) |
| m4 (`Mapping` mutable in DTO) | Wrap `total_upkeep` with `MappingProxyType` in `ColonyDemographicView.__post_init__` |
| m5 (largest-first sort not enforced in DTO) | `ColonyDemographicView.__post_init__` re-sorts `species` with a sort-stable check (or asserts) |
| m6 (`_resolve_economy_config` silent fallback) | Add `logger.warning("session has no economy_config; falling back to default")` |
| m7 (alphabetical tie-break on uncolonized habitability) | Document in the docstring; no behaviour change unless user wants insertion-order |
| m8 (verify integration tests run on sharded runner) | Read `Tools/test_sharded/test_sharded.py`. If it omits `tests/integration/`, add it |
| m9 (UI assembly test for `_build_projection_grid`) | Mock `UILabel`, call the method, assert label count + no overlapping rects |
| m10 (manual-smoke deferral hand-off) | Doc-only — write a `Projects/active_projects/PROJ-292/MANUAL_SMOKE_CHECKLIST.md` for the user |
| m12 (`population_food_resource` shim) | Auto-fixed by PROJ-291 Phase 3 Task 3.5; just verify post-PROJ-291 |
| m13 (docs claim `format_signed_float(rate * 100, 1)` not exactly found) | Re-grep, align docs to actual code |
| m17 (projects_index.md `w# Projects Index` typo) | Delete the stray `w` |

## Key Patterns to Reuse

- **Service-layer facade** (PROJ-258 ApplicationContext, PROJ-287 `StrategySessionFacade.get_race_registry()`) — M1's new facade follows the established pattern.
- **`Optional[X] = None` kwarg + lazy resolution** — PROJ-285's pattern; H1's view threading mirrors it.
- **MagicMock with explicit `spec`** — for the `_StubRegistry` in M2's invalidation test.
- **Bypass-init test pattern** ([tests/unit/ui/screens/test_food_allocation_editor.py](tests/unit/ui/screens/test_food_allocation_editor.py:38)) — for testing UI methods without pygame_gui setup.

## Dependencies & Risks

1. **PROJ-291 Phase 1 must land before PROJ-292 Phase 2.** Both modify `empire_economy_calculator.py` (PROJ-291 adds the upkeep term; PROJ-292 wraps the calculator in a service). Sequential, not parallel.

2. **H1 changes user-visible UI** in two contexts. Mitigation: incremental — wire one caller, manual smoke, then the other.

3. **M2 mtime fallback is opt-in** to avoid filesystem-noise spam. User decides in Phase 3 Task 3.3.

4. **m11 (`last_food_ratio` rename) is OUT OF SCOPE.** Documented in plan.md § Scope. Touching it cascades through engine docstrings + tests + docs and warrants its own project.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
