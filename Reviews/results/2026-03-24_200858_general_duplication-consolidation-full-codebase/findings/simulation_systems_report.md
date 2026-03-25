# Simulation Systems & Services Duplication Report

**Date:** 2026-03-24
**Scope:** `game/simulation/systems/`, `game/simulation/services/`, `game/simulation/combat/`, `game/simulation/managers/`, `game/simulation/validation/`, and root-level modules under `game/simulation/`
**Files Reviewed:** 22

---

## Summary

The simulation layer is **relatively well-decomposed** thanks to prior refactoring projects (PROJ-29, PROJ-44, PROJ-90, etc.). The major classes have clear responsibilities. However, several patterns of duplication remain:

1. **Three-layer passthrough delegation** (BattleController -> BattleService -> BattleEngine) creates identical method signatures at every level
2. **Two different classes named `BattleConfig`** in different packages, causing confusion
3. **Repeated team-alive counting logic** within BattleEngine itself
4. **Repeated DI guard clause pattern** (PROJ-50 boilerplate) across 10+ classes
5. **Repeated list/tuple validation** in ShipState.from_dict
6. **Duplicate `run_ticks` loop** in BattleController and BattleService

Total findings: 9 (4 MAJOR, 5 MINOR)

---

## Findings

#### MAJOR: Three-Layer Passthrough Delegation Chain
**ID:** DUP-SYS-001
**Location:** `battle_controller.py:523-538`, `services/battle_service.py:266-352`, `systems/battle_engine.py:487-641`
**Issue:** `BattleController` has `is_battle_over()`, `get_winner()`, `get_all_ships()`, `get_alive_ships()` that each do nothing but call the same method on `BattleService`, which in turn does nothing but call the same method on `BattleEngine`. This creates a three-deep delegation chain where the middle layer (`BattleService`) adds no logic whatsoever for these query methods -- it just checks `_engine is None` and delegates.

The `BattleController` query methods are pure passthroughs:
```python
def is_battle_over(self) -> bool:
    return self._service.is_battle_over()

def get_winner(self) -> Optional[int]:
    return self._service.get_winner()

def get_all_ships(self) -> List['Ship']:
    return self._service.get_all_ships()

def get_alive_ships(self) -> List['Ship']:
    return self._service.get_alive_ships()
```

And `BattleService` query methods are also passthroughs:
```python
def is_battle_over(self) -> bool:
    if self._engine is None:
        return True
    return self._engine.is_battle_over()
```

**Impact:** Maintenance burden -- every change to the engine API requires updating three layers. Reading code requires tracing through three files to understand what actually happens. The middle layer's null-check is the only added value.
**Recommendation:** This is an intentional architectural pattern (Facade/Delegate per docs). The overhead is low but consider whether `BattleService` provides enough value to justify its existence, or whether `BattleController` could hold the engine directly. If the layering is intentional, accept this as architectural cost rather than duplication.
**Effort:** Complex (requires architectural decision)

---

#### MAJOR: Duplicate `run_ticks` Loop Implementation
**ID:** DUP-SYS-002
**Location:** `battle_controller.py:287-310` and `services/battle_service.py:239-264`
**Issue:** Both `BattleController.run_ticks()` and `BattleService.run_ticks()` implement the same loop pattern:
```python
for _ in range(count):
    if self._engine.is_battle_over():
        break
    self._engine.update()
```
The `BattleController` version adds retreat processing in the loop, but `BattleService.run_ticks()` is never called from `BattleController.run_ticks()` -- the controller reimplements the loop and calls `self._service.update()` directly instead. This means the two loops can diverge silently.

Additionally, `BattleController.run_headless()` (lines 244-285) contains a THIRD similar loop with progress callbacks and a safety limit check that duplicates the engine's own `absolute_max_ticks` check.
**Impact:** Three places implementing the "run multiple ticks" loop. Bug fixes or behavior changes must be applied to all three. The safety limit in `run_headless` (line 281-282) duplicates the engine's absolute_max_ticks safety ceiling.
**Recommendation:** Have `BattleController.run_ticks()` delegate to `BattleService.run_ticks()` with a pre/post hook for retreat processing, OR consolidate the tick-loop into a single method that accepts optional per-tick callbacks (for retreat and progress reporting).
**Effort:** Medium

---

#### MAJOR: Two Different Classes Named `BattleConfig`
**ID:** DUP-SYS-003
**Location:** `game/core/config.py:111` and `game/simulation/battle_config.py:27`
**Issue:** Two completely different classes share the name `BattleConfig`:
- `game.core.config.BattleConfig` -- Static combat constants (query radii, collision buffers, damage factors, projectile tolerances)
- `game.simulation.battle_config.BattleConfig` -- Per-battle instance configuration (mode, seed, max_ticks, end_mode, retreat settings)

Both are imported within `game/simulation/` files:
- `projectile_manager.py` and `battle_engine.py` import `game.core.config.BattleConfig`
- `battle_controller.py`, `battle_mode_handler.py`, `battle_state_manager.py` import `game.simulation.battle_config.BattleConfig`

**Impact:** Naming confusion. A developer seeing `BattleConfig.PROJECTILE_HIT_TOLERANCE` vs `BattleConfig(mode=BattleMode.MANUAL)` has to check which import is in use. This creates a maintenance trap where the wrong `BattleConfig` could be accidentally imported.
**Recommendation:** Rename `game.core.config.BattleConfig` to `CombatConstants` or `CombatConfig` since it holds static constants, not per-battle configuration. This distinguishes it from the per-instance `BattleConfig` dataclass.
**Effort:** Simple (rename + update imports)

---

#### MAJOR: Repeated Team-Alive Counting in BattleEngine
**ID:** DUP-SYS-004
**Location:** `systems/battle_engine.py:520-530` and `systems/battle_engine.py:635-636`
**Issue:** The pattern of counting alive ships per team is duplicated within BattleEngine itself:

In `is_battle_over()` (HP_BASED mode):
```python
team1_alive = sum(
    1 for s in self.ships
    if s.team_id == 0 and s.is_alive
    and (not self.end_condition.check_derelict or not s.is_derelict)
)
team2_alive = sum(
    1 for s in self.ships
    if s.team_id == 1 and s.is_alive
    and (not self.end_condition.check_derelict or not s.is_derelict)
)
```

In `get_winner()`:
```python
team1_alive = sum(1 for s in self.ships if s.team_id == 0 and s.is_alive)
team2_alive = sum(1 for s in self.ships if s.team_id == 1 and s.is_alive)
```

These are almost identical but differ in the derelict check. The `get_winner()` version doesn't account for derelict ships, which could produce inconsistent results when `check_derelict=True`.
**Impact:** Potential logic inconsistency: `is_battle_over()` might trigger (because derelict ships are counted as defeated) but `get_winner()` would report a draw (because it doesn't exclude derelicts). Also, any change to the alive-counting logic must be made in two places.
**Recommendation:** Extract a `_count_alive_ships(team_id, check_derelict=False)` helper method and use it in both `is_battle_over()` and `get_winner()`. The `get_winner()` method should respect the same derelict settings as `is_battle_over()`.
**Effort:** Simple

---

#### MINOR: Repeated DI Guard Clause Boilerplate (PROJ-50 Pattern)
**ID:** DUP-SYS-005
**Location:** `services/design_loader.py:52-57`, `services/vehicle_design_service.py:69-74`, `services/modifier_service.py:53-58`, `validation/ship_validator.py:284-289`, `validation/ship_validator.py:395-400`, `battle_state.py:345-350`
**Issue:** At least 6 constructors in the simulation layer repeat this exact pattern:
```python
if registries is None:
    raise ValidationException(
        "registries is required for <ClassName>",
        code=ErrorCode.MISSING_DEPENDENCY.value,
        context={"class": "<ClassName>", "parameter": "registries"}
    )
```
The only difference between instances is the class name string.
**Impact:** Low -- this is boilerplate, but it's a constructor guard clause that's unlikely to drift. However, it's 6 lines repeated 6+ times (36+ lines of near-identical code).
**Recommendation:** Create a `require_registries(registries, class_name: str)` helper function in `game.core.validation_helpers` that encapsulates this pattern. Each constructor would then call `require_registries(registries, "ClassName")` in one line.
**Effort:** Simple

---

#### MINOR: Repeated List/Tuple Format Validation in ShipState.from_dict
**ID:** DUP-SYS-006
**Location:** `battle_state.py:196-235`
**Issue:** Three nearly identical validation blocks for `color`, `position`, and `velocity` fields:
```python
color = data['color']
if not isinstance(color, (list, tuple)) or len(color) < 3:
    raise PersistenceException(
        f"ShipState: color must be a list/tuple with at least 3 elements, got {type(color).__name__}",
        code=ErrorCode.CORRUPT_DATA.value,
        context={
            "source": "ShipState",
            "field": "color",
            "value": str(color)[:100],
            "expected": "list or tuple with >= 3 elements"
        }
    )
```
This pattern repeats for `position` (min 2 elements) and `velocity` (min 2 elements).
**Impact:** 40 lines of repetitive validation that makes the method harder to read.
**Recommendation:** Extract a `_validate_sequence_field(data, field_name, min_length, source="ShipState")` helper that validates and raises the appropriate `PersistenceException`. Reduces ~40 lines to ~3 calls.
**Effort:** Simple

---

#### MINOR: State Capture Duplication Between BattleController and BattleStateManager
**ID:** DUP-SYS-007
**Location:** `battle_controller.py:206-212` and `managers/battle_state_manager.py:33-64`
**Issue:** `BattleController.start()` calls `BattleState.capture_from_engine()` directly (line 206) for initial state capture, while `BattleController.save_state()` delegates to `BattleStateManager.capture_state()` which also calls `BattleState.capture_from_engine()`. Both pass the same config fields (`mode`, `seed`, `allow_retreat`, `allow_reinforcements`).

The initial capture in `start()` bypasses the `BattleStateManager` entirely, creating two code paths for the same operation.
**Impact:** If capture parameters change, the `start()` direct call might not be updated to match the `BattleStateManager` version.
**Recommendation:** Have `BattleController.start()` use `self._state_manager.capture_state()` for initial state capture instead of calling `BattleState.capture_from_engine()` directly.
**Effort:** Simple

---

#### MINOR: Repeated "No Active Battle" Guard Pattern in BattleService
**ID:** DUP-SYS-008
**Location:** `services/battle_service.py:115-117, 149-151, 188-189, 227-229, 251-253`
**Issue:** Five methods in `BattleService` repeat the same guard clause pattern:
```python
if self._engine is None:
    errors.append("No active battle - call create_battle() first")
    return BattleServiceResult(success=False, errors=errors)
```
With slight variations in the error message. Two more methods check `self._is_started` with similar patterns.
**Impact:** Low -- these are standard guard clauses and each has a slightly different context message. However, the pattern adds ~4 lines per method.
**Recommendation:** Extract a `_require_engine()` helper that raises or returns an error result, and a `_require_started()` helper. This is a marginal improvement; could also be left as-is since the messages vary slightly.
**Effort:** Simple

---

#### MINOR: `BattleController.run_headless` Safety Limit Duplicates Engine Ceiling
**ID:** DUP-SYS-009
**Location:** `battle_controller.py:281-282` and `systems/battle_engine.py:505`
**Issue:** `BattleController.run_headless()` has its own safety limit:
```python
if tick >= max_ticks:
    logger.warning(f"Battle reached max ticks limit: {max_ticks}")
    break
```
But `BattleEngine.is_battle_over()` already has `absolute_max_ticks` as a safety ceiling (line 505). These two mechanisms can conflict -- the controller's limit uses `config.max_ticks` which may be different from the engine's `absolute_max_ticks`.
**Impact:** Potential confusion about which limit applies. If `config.max_ticks` is lower than `absolute_max_ticks`, the controller exits early. If higher, the engine exits first. The dual-limit design is not well documented.
**Recommendation:** Either rely solely on the engine's `absolute_max_ticks` ceiling (remove the controller's duplicate check), or document clearly that the controller limit is intentionally separate and serves a different purpose (e.g., headless-specific timeout vs engine safety ceiling).
**Effort:** Simple

---

## Top 5 Priority List

| Priority | ID | Severity | Title | Effort |
|----------|----|----------|-------|--------|
| 1 | DUP-SYS-004 | MAJOR | Repeated Team-Alive Counting (potential logic bug with derelicts) | Simple |
| 2 | DUP-SYS-003 | MAJOR | Two Classes Named `BattleConfig` (naming confusion) | Simple |
| 3 | DUP-SYS-002 | MAJOR | Duplicate `run_ticks` Loop (three implementations) | Medium |
| 4 | DUP-SYS-007 | MINOR | State Capture Duplication (bypass of manager) | Simple |
| 5 | DUP-SYS-005 | MINOR | Repeated DI Guard Clause Boilerplate | Simple |

DUP-SYS-001 is intentional architecture (Facade/Delegate pattern per docs) and should be left as-is unless the team decides to flatten the layers.

---

## Notes

- The combat subsystem (`game/simulation/combat/`) is **well-decomposed** with clean separation between `DamageCalculator`, `TargetingSystem`, and `WeaponFiringSystem`. No significant duplication found there.
- The validation subsystem (`game/simulation/validation/`) effectively uses the template method pattern to reduce duplication. The base classes (`ValidationRule`, `DesignValidationRule`, `AdditionValidationRule`) eliminate repeated guard clauses.
- `physics_constants.py` defines K_SPEED, K_THRUST, K_TURN which are used in `ship_stats.py` and `ship_physics.py` -- this is properly centralized with no duplication.
- The `BattleModeHandler` hierarchy uses the Strategy pattern correctly. The four concrete handlers (Manual, Test, Strategy, Hypothetical) have different return values, not duplicated logic.
- `ResourceManager` (`resource_manager.py`) and `RetreatManager` (`retreat_manager.py`) are well-isolated with no duplication with other modules.
