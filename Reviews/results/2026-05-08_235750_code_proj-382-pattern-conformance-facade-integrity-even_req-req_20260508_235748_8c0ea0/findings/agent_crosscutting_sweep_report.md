# PROJ-382 Cross-Cutting Pattern Conformance Sweep

**Agent:** OpenCode (cross-cutting sweep)
**Date:** 2026-05-08
**Scope:** Remaining pattern conformance items in PROJ-382 across 5 phases.

---

## Finding Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 1 |
| MAJOR | 2 |
| MINOR | 3 |
| INFO | 5 |
| **TOTAL** | **11** |

---

## Findings

### FIND-001: CRITICAL — GameSession.from_dict() does not restore mutator services, breaking command handlers after save/load

**File:** `game/strategy/engine/game_session.py:418-550`
**Evidence:** `from_dict()` at line 475 constructs `TurnEngineConfig.create_default()` but passes no mutator kwargs (`fleet_mutator`, `planet_mutator`, `empire_mutator`, `ship_mutator`):

```python
_turn_engine_config = TurnEngineConfig.create_default(
    session._registries,
    ai_factory=ai_factory,
    race_registry=session.race_registry,
    event_bus=session._event_bus,
)
```

Compare with `__init__` at line 130 which threads all four mutators:

```python
_turn_engine_config = TurnEngineConfig.create_default(
    self._registries,
    ai_factory=ai_factory,
    race_registry=self.race_registry,
    event_bus=self._event_bus,
    fleet_mutator=self._fleet_mutator,
    planet_mutator=self._planet_mutator,
    empire_mutator=self._empire_mutator,
    ship_mutator=self._ship_mutator,
)
```

The private mutator fields are never assigned in `from_dict()` (no `session._fleet_mutator = ...` lines).

**Assessment:** Pattern #2 (Protocol + TypeGuard) mutator boundary: the mutator protocols exist but the session doesn't re-create them on load. Any command handler that calls `session.fleet_mutator.set_path()` (via `add_move_order_if_needed` in `game/strategy/engine/handlers/base.py:82`) after deserialization will raise `AttributeError: 'GameSession' object has no attribute '_fleet_mutator'`. This affects all mission commands (superweapon missions, colonization missions) that auto-queue MOVE orders. The `race_registry` property is lazy-initialized and thus survives serialization, but the mutator properties access bare private fields that are never set.

**Recommendation:** Add mutator service construction in `from_dict()` mirroring `__init__` lines 104-123, and pass them to `TurnEngineConfig.create_default()`. Since `from_dict()` already calls `GameSession._resolve_registries()`, at minimum thread a `FleetWriteService(FleetNavigationService())` into `session._fleet_mutator`.

---

### FIND-002: MAJOR — planet_command_handlers.py uses legacy BaseCommandHandler import path instead of canonical

**File:** `game/strategy/engine/planet_command_handlers.py:55,127,149,185`
**Evidence:** Four late-import sites use the legacy shim path:

```python
from game.strategy.engine.command_handlers import BaseCommandHandler
```

The canonical path per Pattern #7 (`docs/02_PATTERNS.md` line 167) is:

```python
from game.strategy.engine.handlers.base import BaseCommandHandler
```

**Assessment:** Pattern #7 (CommandHandlerRegistry) violation. `superweapon_command_handlers.py` was properly re-routed to the canonical path in PROJ-382 Phase 3, but its sibling `planet_command_handlers.py` was not. The shim path still works (the legacy file re-exports), but new code should import from the canonical location. The class also does not subclass `BaseCommandHandler` — it calls `BaseCommandHandler._resolve_player_planet` as a static method, which is a pattern #7 deviation (handlers should subclass `BaseCommandHandler` for consistent resolution helpers).

**Recommendation:** Re-route all 4 imports to `game.strategy.engine.handlers.base`. Consider refactoring `IssuePlanetOrderCommandHandler` and its helper functions to subclass `BaseCommandHandler`.

---

### FIND-003: MAJOR — 3 test files still import BaseCommandHandler from legacy shim path

**File:** 
- `tests/unit/strategy/test_command_handlers.py`
- `tests/unit/strategy/engine/test_command_ownership.py`
- `tests/unit/strategy/engine/test_base_command_handler.py`

**Evidence:** Each file imports:

```python
from game.strategy.engine.command_handlers import BaseCommandHandler
```

**Assessment:** Pattern #7 violation. 3 test files still use the legacy transitional re-export shim. 8 test files overall still have this import pattern. Production tests should exercise the canonical import path to catch regressions if the shim is eventually retired.

**Recommendation:** Update these 3 test imports to the canonical path `game.strategy.engine.handlers.base`. The `test_base_command_handler.py` file is specifically about the base handler — it should absolutely import from the canonical location.

---

### FIND-004: MINOR — design_selector_window.py contains hardcoded vehicle class type lists

**File:** `game/ui/screens/design_selector_window.py:189-191,209-210`
**Evidence:** 

```python
class_options = ["All Classes", "Escort", "Frigate", "Destroyer", "Cruiser",
                "Battlecruiser", "Battleship", "Carrier", "Dreadnought"]
```

```python
type_options = ["All Types", "Ship", "Fighter", "Satellite", "Planetary Complex", "Drop Pod"]
```

**Assessment:** Pattern #4 (Registry Pattern) and Convention §6.5 ("no hardcoded ability/component name lists") violation. Ship class names and vehicle type names should be derived from `vehicle_classes` registry rather than hardcoded. If a new ship class is added to `data/vehicleclasses.json`, the dropdown will silently exclude it.

**Recommendation:** Derive filter dropdown options from `get_default_registry_provider().get_vehicle_classes()` at filter-build time. The "All Classes" / "All Types" sentinel values are acceptable as UI-only placeholders.

---

### FIND-005: MINOR — stat_getters.py _SUPERWEAPON_LABELS mapping duplicates registry knowledge

**File:** `game/ui/screens/builder/stat_getters.py:303-310`
**Evidence:**

```python
_SUPERWEAPON_LABELS = {
    'DestroyPlanet': 'Planet Imploder',
    'DestroyStar': 'Stellerator',
    'OpenWarpPoint': 'Warp Point Creator',
    'CloseWarpPoint': 'Warp Point Closer',
    'CreateDysonSphere': 'Dyson Sphere Constructor',
    'SelfDestruct': 'Self-Destruct',
}
```

**Assessment:** Pattern #4 (Registry Pattern — avoid hardcoded type lists). While `_superweapon_ability_names()` correctly derives its ability-name list from the SUPERWEAPONS registry (filtering `s.ability_name is not None`), the display labels are a parallel hardcoded dict. The code comment at line 292-294 explicitly acknowledges this: "Display labels remain a UI-side mapping until SuperweaponSpec gains a `display_name` field." The mapping is documented as temporary, but it duplicates the superweapon identity semantics currently owned by the registry.

**Recommendation:** Acceptable as documented UI surface. When `SuperweaponSpec` gains a `display_name` field, replace this dict. Track as tech debt.

---

### FIND-006: MINOR — design_selector_window.py test doesn't thread window_manager= kwarg

**File:** `tests/unit/ui/screens/test_design_selector_window.py`
**Evidence:** Search for `window_manager=` returned NO_MATCHES in this file.

**Assessment:** Pattern #31 (Strategy Modal Window Base Class). The production `DesignSelectorWindow.__init__` at line 63 now accepts `window_manager` as keyword and forwards it to `StrategyModalWindow.__init__`. The tests may be constructing `DesignSelectorWindow` without this kwarg, relying on the default `None` value. While this is technically valid (the window works outside strategy screen), tests should verify the modal registration flow with a non-None `window_manager` to catch regressions in Pattern #31 conformance.

**Recommendation:** Add a test that constructs `DesignSelectorWindow` with a real/mock `StrategyWindowManager` and verifies the modal registers on construction and deregisters on `kill()`. The existing `test_strategy_modal_window.py` likely covers the base class invariants, but a subclass-specific conformance test would catch future subclass deviations.

---

### FIND-007: INFO — Pattern #2 TypeGuard in galaxy_spatial_index.py correctly implemented

**File:** `game/strategy/data/galaxy_spatial_index.py:38`
**Evidence:**

```python
if is_planet(obj):
    return self.get_system_of_planet(obj)
```

The `is_planet` TypeGuard is imported from `game/core/protocols` (line 11) and `is_zone_occupant` is used at line 104. No concrete `Planet` import at runtime.

**Assessment:** Conforming. Pattern #2 (Protocol + TypeGuard) is properly implemented. The TypeGuard `is_planet` replaces the previous concrete isinstance check, and the runtime narrowing avoids importing the concrete `Planet` class. The comment at line 36-37 mentions PROJ-382 Phase 2 (Pattern #2).

**Recommendation:** None. Fully conformant.

---

### FIND-008: INFO — Pattern #10 dual-path event logging correctly collapsed in empire.py and fleet.py

**File:** `game/strategy/data/empire.py:104-116`, `game/strategy/data/fleet.py:401-435`
**Evidence:** Both files now use only the injected `event_bus.log_event(...)` path:

```python
# empire.py:104
if cancelled and event_bus is not None:
    from game.strategy.events.event_types import EventType, EventCategory
    for pursuer in cancelled:
        event_bus.log_event(EventType.FLEET_JOIN_CANCELLED, ...)
```

```python
# fleet.py:401-435
redirected, excluded = self._pursuer_tracker.redirect_pursuers(...)
for pursuer, _old_target in redirected:
    if event_bus is not None:
        event_bus.log_event(EventType.FLEET_JOIN_REDIRECTED, ...)
```

No module-level `log_event` import in either file — only `import logging` for the Python logger.

**Assessment:** Conforming. Pattern #10 (Event Bus) dual-path collapse is complete. Both `remove_fleet` and `merge_with` emit only through the injected `event_bus`. The `event_bus=None` guard is preserved for callers that don't have an EventBus.

**Recommendation:** None. Fully conformant.

---

### FIND-009: INFO — EventBus injection in projectile.py follows Pattern #10 with lazy-default fallback

**File:** `game/simulation/entities/projectile.py:8-17,37-39`
**Evidence:**

```python
def _default_event_logger(event_type: str, **kwargs: Any) -> None:
    """...Resolved lazily so the projectile module no longer holds a top-level import..."""
    from game.core.event_logging import log_event
    log_event(event_type, **kwargs)
```

```python
self._event_logger: Callable[..., None] = kwargs.get(
    "event_logger", _default_event_logger
)
```

**Assessment:** Conforming. The injectable `_event_logger` pattern replaces the old top-level `from game.core.event_logging import log_event` with a lazy-resolved default. The top-level import is gone; only the function-body lazy import remains for backward-compatible default dispatch. The comment at line 9-15 explicitly documents the PROJ-382 Phase 2 (Pattern #10) change.

**Recommendation:** None. Fully conformant for the stated goal. Future consideration: if all call sites pass an `event_logger` kwarg, the `_default_event_logger` and its nested import become dead code.

---

### FIND-010: INFO — production_spawner.py registries= is properly required (raises TypeError on None)

**File:** `game/strategy/engine/production_spawner.py:60-65`
**Evidence:**

```python
if registries is None:
    raise TypeError(
        "ProductionSpawner requires registries= (PROJ-382 Phase 3). "
        ...
    )
```

Test at `tests/unit/strategy/engine/test_production_spawner.py:503` verifies:
```python
ProductionSpawner(registries=None)  # expected to raise TypeError
```

**Assessment:** Conforming. Pattern #3 (Registry DI) tightening is properly implemented. The constructor enforces `registries` as required keyword-only. All 22 test instantiations pass `registries=`. The `_get_planet_mutator()` accessor is kept as a thin wrapper with the lazy-fallback collapsed into eager construction (line 68-73).

**Recommendation:** None. Fully conformant.

---

### FIND-011: INFO — superweapon_command_handlers.py uses canonical BaseCommandHandler import path

**File:** `game/strategy/engine/superweapon_command_handlers.py:15`
**Evidence:**

```python
from game.strategy.engine.handlers.base import BaseCommandHandler, add_move_order_if_needed
```

**Assessment:** Conforming. Pattern #7 (CommandHandlerRegistry) canonical import path correctly used. All 11 handler subclasses in this file extend `BaseCommandHandler` from the canonical `handlers/base.py` location, not the legacy shim.

**Recommendation:** None. This file serves as the reference example for other handler modules that still use the legacy path.

---

## Items Verified as Conformant (No Finding)

1. **simulation/components/__init__.py** — Intentionally empty namespace marker with clear docstring directing importers to submodules. No fake re-exports, no pattern violations.

2. **game_session.py tautology guard** — PROJ-382 Phase 3 removed the unreachable `if command.type == CommandType.ISSUE_ORDER:` conditional at line 370-373. Comment at line 369-371 confirms the removal.

3. **stat_rows_dynamic.py** — `get_superweapon_rows()` at line 492 correctly imports `_superweapon_ability_names` from `stat_getters.py`, which derives from the SUPERWEAPONS registry. No hardcoded ability name list in this file.

4. **Test baseline for new constructor signatures** — No tests pass `session=` as kwarg where it shouldn't be (confirmed by `rg "session=" --include="*test*.py" game/ tests/` returning NO_MATCHES). ProductionSpawner tests properly pass `registries=` and verify None rejection.

5. **design_selector_window.py Pattern #31 conformance** — Correctly subclasses `StrategyModalWindow` (line 47), forwards `window_manager` kwarg to `super().__init__()` (line 135), and supports `window_manager=None` for non-strategy-screen usage (line 64). The modal register/unregister flow is inherited from the base class — no manual slot wiring needed.

6. **stat_getters.py registry integration** — `_superweapon_ability_names()` at line 313 correctly derives ability names from `SUPERWEAPONS` tuple (from `game.strategy.services.superweapon_registry`), with documented manual addenda for `DestroyStar` and `SelfDestruct`.

---

## Cross-Cutting Observations

### Pattern #7 (CommandHandlerRegistry) — incomplete migration
`superweapon_command_handlers.py` was re-routed to the canonical import path, but `planet_command_handlers.py` was left behind. Additionally, 8 test files still import from the legacy shim. A project-wide import cleanup pass would eliminate the transitional re-export shim in `game/strategy/engine/command_handlers.py`.

### Pattern #2 (Protocol + TypeGuard) — mutator boundary gap in deserialization
The mutator services are properly constructed and injected in `GameSession.__init__` but not restored in `GameSession.from_dict()`. This is a pattern conformance gap: the same session object should function identically whether freshly constructed or deserialized. All other services (registries, EventBus, TurnEngine, command registry, race registry) are restored in `from_dict()` — the mutators are the only missing piece.

### Pattern #4 (Registry) — hardcoded list residue
Two hardcoded type lists remain that should be registry-derived:
1. Ship class names in `design_selector_window.py` dropdown (13 vehicle classes in `vehicleclasses.json` not represented)
2. Vehicle type names in the same file

The SUPERWEAPONS display label mapping is a lighter concern (documented as temporary) since ability names ARE derived from the registry.
