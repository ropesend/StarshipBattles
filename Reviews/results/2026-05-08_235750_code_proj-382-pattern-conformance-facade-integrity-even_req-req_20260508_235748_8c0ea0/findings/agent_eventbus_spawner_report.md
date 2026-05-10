# EventBus Rename & ProductionSpawner DI Review

**Review:** PROJ-382 Phase 2+3 — `EventBus` → `WorkshopEventBus` rename + `registries=` required kwarg  
**Date:** 2026-05-08  
**Scope:** `game/ui/screens/builder/event_bus.py`, `game/strategy/engine/production_spawner.py`, all call sites

---

## 1. EventBus → WorkshopEventBus Rename Completeness

### FINDING-01: INFO — Rename is complete, 16 files updated, no missed imports  
**File:** 16 files across `game/ui/screens/` and `tests/`  
**Evidence:** `rg "from.*builder.*import.*EventBus" -g "*.py" game/ tests/` returned 35 matches in 16 distinct files — **every single one imports `WorkshopEventBus`**. No import of the bare `EventBus` name from the builder module exists anywhere.  
**Assessment:** The 15-file fan-out claim is verified (9 production files importing + 1 definition + 6 test files = 16 total, with `event_bus.py` being the definition, the "15" count tracks importing files). The only bare `EventBus` reference in `game/ui/screens/builder/` is the docstring on line 5 of `event_bus.py` which explains the rename to distinguish from the canonical strategy-layer `EventBus` — this is self-documenting, not a bug.  
**Recommendation:** None required. Rename is clean.

### FINDING-02: INFO — WorkshopEventBus class definition is correctly named and scoped  
**File:** `game/ui/screens/builder/event_bus.py:19`  
**Evidence:** `class WorkshopEventBus:` with docstring explicitly noting "PROJ-382 Phase 2 (Pattern #10 / Pattern #6 naming hygiene)."  
**Assessment:** Class is well-documented with rationale for the rename. The subscribe/unsubscribe/emit API is unchanged — this is a pure rename.  
**Recommendation:** None.

---

## 2. ProductionSpawner `registries=` Required Kwarg

### FINDING-03: INFO — registries= is truly required at Python level, None is rejected  
**File:** `game/strategy/engine/production_spawner.py:34-66`  
**Evidence:**
```python
def __init__(
    self,
    *,
    registries: 'GameRegistries',  # no default — Python-enforced required kwarg
    event_bus=None,
    planet_mutator=None,
):
    if registries is None:
        raise TypeError(
            "ProductionSpawner requires registries= (PROJ-382 Phase 3). "
            "Pass session.registries (or a real GameRegistries) at "
            "construction time."
        )
```
**Assessment:** Two layers of enforcement: (1) Python signature with no default value means omitting `registries=` produces `TypeError: __init__() missing 1 required keyword-only argument: 'registries'`. (2) Explicit None check raises a descriptive TypeError if someone passes `registries=None`. This is robust.  
**Recommendation:** None. The guard against explicit `None` is defensive but not redundant — it provides a context-rich error message vs. the opaque error that would occur when `self._registries` is later used while None.

### FINDING-04: INFO — All 2 production + 20+ test call sites pass registries=  
**File:** `game/strategy/engine/production_engine.py:124`, `tests/unit/strategy/engine/test_production_spawner.py`, `tests/unit/strategy/engine/test_production_spawner_staging_yard.py`  
**Evidence:** `rg "ProductionSpawner\(" -g "*.py" game/ tests/` returned 26 results — all pass `registries=` explicitly. The production path (`production_engine.py:124`) uses `ProductionSpawner(registries=registries, event_bus=event_bus)`. All test paths use either `registries=MagicMock()` or `registries=registries`.  
**Assessment:** No call sites omit `registries=`. The test at `test_production_spawner.py:492-503` explicitly verifies that `registries=None` raises TypeError with the expected message.  
**Recommendation:** None.

### FINDING-05: INFO — Eager planet_mutator injection is safe in test contexts  
**File:** `game/strategy/engine/production_spawner.py:68-73`  
**Evidence:**
```python
if planet_mutator is None:
    from game.strategy.services.planet_write_service import (
        PlanetWriteService,
    )
    planet_mutator = PlanetWriteService()
self._planet_mutator = planet_mutator
```
**Assessment:** `PlanetWriteService` has no `__init__` method (class body starts at `planet_write_service.py:32` with methods immediately following) — its constructor is the implicit no-args default. No database handles, filesystem I/O, or side effects. The eager injection is behaviorally identical to the lazy pattern because (a) `PlanetWriteService` is stateless (it mutates planet objects via attribute access, e.g., `planet.facilities.append(facility)`), and (b) the lazy fallback also created a fresh `PlanetWriteService()` on first access.  
**Recommendation:** None for correctness. See FINDING-07 for architectural concern.

---

## 3. Architecture & Hygiene Findings

### FINDING-06: MINOR — `_get_planet_mutator()` thin wrapper retained after eager conversion  
**File:** `game/strategy/engine/production_spawner.py:75-79`  
**Evidence:**
```python
def _get_planet_mutator(self):
    # PROJ-382 Phase 3: kept as a thin accessor; the lazy-fallback
    # has been collapsed into eager construction-time defaulting
    # above, so this just returns the field.
    return self._planet_mutator
```
**Assessment:** After collapsing the lazy fallback into eager construction-time injection, `_get_planet_mutator()` is a trivial return-self-field method. However, this pattern (private accessor wrapping a field that always exists post-construction) is used consistently across 7 strategy-layer engines (`atmosphere_engine.py`, `planet_modifier_effect_engine.py`, `harvesting_engine.py`, `order_handlers/base.py`, `planet_energy_engine.py`, `organics_consumption_engine.py`, `production_spawner.py`). The other 6 engines still use the lazy pattern, so removing the accessor from just `ProductionSpawner` would create an inconsistency.  
**Recommendation:** Defer removal — wait until all 7 engines converge on eager injection, then inline `_get_planet_mutator()` accessors uniformly. The thin wrapper is harmless and consistent with sibling classes for now.

### FINDING-07: MINOR — Dead-code else branch in `_spawn_to_staging_yard` after registries became required  
**File:** `game/strategy/engine/production_spawner.py:287-292`  
**Evidence:**
```python
# Calculate mass from design using simulation Ship (single source of truth)
total_mass = 0.0
if self._registries:
    from game.simulation.entities.ship_design_stats import calculate_design_stats
    stats = calculate_design_stats(design_data, self._registries)
    total_mass = stats.get('mass', 0.0)
```
**Assessment:** `self._registries` can no longer be falsy because `__init__` rejects `None` (lines 60-65) and the Python signature has no default. A `MagicMock` is truthy. The `if self._registries:` guard will always evaluate to `True` — the `else` path (`total_mass = 0.0`) is dead code. This is a leftover from the pre-PROJ-382 era when `registries` could be `None`. The test `test_production_spawner_requires_registries` (line 492) confirms that None is rejected at construction time.  
**Recommendation:** Remove the `if self._registries:` guard and always execute the mass-calculation path. The test `test_spawn_to_staging_yard_reaches_into_simulation_for_mass_calculation` (line 462) already validates the positive path and will catch any regression.

### FINDING-08: MINOR — ProductionEngine does not thread `planet_mutator` to ProductionSpawner  
**File:** `game/strategy/engine/production_engine.py:124`, `game/strategy/engine/turn_engine_config.py:208-210`  
**Evidence:**
```python
# production_engine.py:124 — ProductionEngine creates spawner without planet_mutator
self._spawner = ProductionSpawner(registries=registries, event_bus=event_bus)

# turn_engine_config.py:208-210 — ProductionEngine itself gets no planet_mutator
production_engine=ProductionEngine(
    registries=registries, event_bus=event_bus,
),

# Contrast with HarvestingEngine at line 220-224, which DOES get planet_mutator:
harvesting_engine=HarvestingEngine(
    registries=registries,
    planet_mutator=planet_mutator,
    empire_mutator=empire_mutator,
),
```
**Assessment:** `TurnEngineConfig.create_default()` threads the shared `planet_mutator` to `HarvestingEngine` but not to `ProductionEngine` (and by extension, not to `ProductionSpawner`). ProductionSpawner creates its own `PlanetWriteService()` instance via the eager default. Functionally harmless because `PlanetWriteService` is stateless (all mutations are direct attribute writes/append on the passed `planet` object). However, this is architecturally inconsistent with the DI pattern used by peer engines. If `PlanetWriteService` ever gains shared state (e.g., a write-ahead log, audit trail), this split would cause divergence.  
**Recommendation:** Add `planet_mutator` parameter to `ProductionEngine.__init__` and thread it through to `ProductionSpawner`. Update `TurnEngineConfig.create_default()` to pass `planet_mutator=planet_mutator` to `ProductionEngine(...)`. This aligns with the composition path already documented in ProductionSpawner's docstring: "the approach already taken by the `TurnEngineConfig.create_default` composition path."

---

## Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 0 |
| MAJOR    | 0 |
| MINOR    | 3 |
| INFO     | 5 |
| **Total** | **8** |

**Verdict:** The `EventBus` → `WorkshopEventBus` rename is complete and correct across all 16 files. The `registries=` required-kwarg contract is enforced at two levels and all 26+ call sites comply. Three minor hygiene issues identified: a dead-code guard in `_spawn_to_staging_yard`, a thin accessor wrapper retained for sibling-class consistency, and a missing `planet_mutator` DI thread from `TurnEngineConfig` to `ProductionSpawner`. None are blocking.
