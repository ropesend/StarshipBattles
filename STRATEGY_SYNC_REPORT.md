# Strategy Layer Synchronization Report

**Date:** 2026-04-07
**Scope:** `game/strategy/` (excluding combat simulator, physics, research, tests)
**Standard:** PEP 8, PEP 484 (type hints), PEP 257 (docstrings)

---

## Methodology

Seven parallel verification agents analyzed specific subsystems against documentation.
Each finding was subjected to the **Verification Protocol** (Skeptical Subagent):

1. **Challenge the Hypothesis** - looked for hidden dependencies or design reasons
2. **Validate the Source of Truth** - confirmed whether code or docs were authoritative
3. **Confirm Non-Regression** - ensured changes don't break strategy logic
4. **Final Verdict** - only VERIFIED findings were acted upon

---

## 1. Documentation Updates (Code -> Docs)

All items below were VERIFIED: the code is the current source of truth; docs were stale.

### 1.1 Turn Engine Phase Count (VERIFIED - APPLIED)

**Files modified:**
- `game/strategy/engine/turn_engine.py` (file header + `_process_tick` docstring)
- `docs/systems/strategy_layer.md` (overview count)

**Issue:** The `_process_tick` docstring claimed "Eleven-phase processing" and listed only 11 phases.
The actual code executes **14 phases** per tick. Three phases were missing from the docstring:

| Missing Phase | Engine | Added In |
|---------------|--------|----------|
| Phase 0c1 | `PlanetEnergyEngine` | PROJ-237/238 |
| Phase 1.6 | `PlanetActionEngine` | PROJ-238 |
| Phase 1.7 | `ComponentActivationEngine` | PROJ-253 |

**Skeptical Challenge:** Could these be intentionally excluded (e.g., optional/disabled)?
**Verdict:** No -- all three phases execute unconditionally every tick via `_time_phase()`.
The file header already listed 0c1 and 1.6 but was missing 1.7. The docstring was simply
never updated when these phases were added.

**Fix:** Updated docstring to "Fourteen-phase processing" and listed all 14 phases.
Added Phase 1.7 to the file header comment.

### 1.2 Sub-Engine Interfaces Table (VERIFIED - APPLIED)

**File modified:** `docs/systems/strategy_layer.md` (lines 160-175)

**Issue:** The "Sub-Engine Interfaces" table listed 10 interfaces but `engines.py` defines 13.
Three were missing:

| Missing Interface | Implementation |
|-------------------|---------------|
| `IPlanetEnergyEngine` | `PlanetEnergyEngine` |
| `IPlanetActionEngine` | `PlanetActionEngine` |
| `IComponentActivationEngine` | `ComponentActivationEngine` |

**Skeptical Challenge:** Are these interfaces actually used by TurnEngine?
**Verdict:** Yes -- all three have constructor parameters, private storage, lazy-init properties,
and are called in `_process_tick`. The `engines.py` `__all__` exports all 13.

**Fix:** Added 3 missing rows to the interfaces table. Updated orchestrator count from 11 to 13.

### 1.3 Fleet Delegates Count (VERIFIED - APPLIED)

**File modified:** `docs/systems/strategy_layer.md` (Fleet System section)

**Issue:** Documentation stated "Fleet uses composition with 3 delegates" but the code
initializes **4 delegates** in `Fleet.__init__()`:

1. `FleetConsumableAggregator` (documented)
2. `FleetCapabilityCalculator` (documented)
3. `FleetBattleAdapter` (documented)
4. `FleetPursuerTracker` (MISSING from docs, added in PROJ-222)

**Skeptical Challenge:** Is FleetPursuerTracker a true delegate or just a utility field?
**Verdict:** It follows the same pattern as the other 3: initialized in `__init__`, stored as
private attribute, exposed via property (`fleet.pursuer_tracker`), has its own module file.

**Fix:** Updated count to 4, added `FleetPursuerTracker` section with full API documentation.

---

## 2. Code Refactors (Docs -> Code)

All items below were VERIFIED: the documentation/PEP standards define the contract; the code violated it.

### 2.1 Missing Package Exports - interfaces/__init__.py (VERIFIED - APPLIED)

**File modified:** `game/strategy/interfaces/__init__.py`

**Issue:** The `__init__.py` only imported and exported 5 of 13 engine interfaces
(IMovementEngine, IProductionEngine, IOrderProcessor, IConflictEngine, IConsumableEngine).
The remaining 8 were defined in `engines.py` with proper `__all__` but not re-exported
from the package.

**Skeptical Challenge:** Could selective exports be intentional (hiding internal interfaces)?
**Verdict:** No -- all 13 interfaces are used by TurnEngine's public constructor. They are
part of the public DI API for testing. The `engines.py` module exports all 13 via `__all__`.

**Fix:** Added all 8 missing interfaces to the import and `__all__` list.

### 2.2 Missing Package Export - PlanetOrderValidator (VERIFIED - APPLIED)

**File modified:** `game/strategy/validation/__init__.py`

**Issue:** `PlanetOrderValidator` was not imported or exported from the validation package,
unlike the other 3 validators (ColonizeValidator, TransferValidator, SuperweaponValidator).

**Skeptical Challenge:** Is PlanetOrderValidator imported directly by consumers, making
the package export unnecessary?
**Verdict:** While consumers do import directly, the package `__init__.py` serves as the
public API declaration. All other validators are exported. Consistency requires this one too.

**Fix:** Added import and `__all__` entry.

### 2.3 Missing __all__ on Facade Package (VERIFIED - APPLIED)

**File modified:** `game/strategy/facade/__init__.py`

**Issue:** The facade `__init__.py` had only a docstring, no imports or `__all__`.
`StrategySessionFacade` is the public API per `docs/01_ARCHITECTURE.md` and
`docs/02_PATTERNS.md`, but the package didn't declare it.

**Skeptical Challenge:** Could this cause circular imports?
**Verdict:** No -- `StrategySessionFacade` imports from `engine` and `data`, not vice versa.
The top-level `game/strategy/__init__.py` already imports it without issues.

**Fix:** Added import and `__all__ = ['StrategySessionFacade']`.

### 2.4 Missing Type Hints - DesignValidator (VERIFIED - APPLIED)

**File modified:** `game/strategy/services/design_validator.py`

**Issue:** 6 methods were missing PEP 484 return type annotations:

| Method | Added Annotation |
|--------|-----------------|
| `DesignValidationResult.add_error()` | `-> None` |
| `DesignValidationResult.add_warning()` | `-> None` |
| `DesignValidator.__init__()` | `(registries: 'GameRegistries') -> None` |
| `DesignValidator._check_components_exist()` | `-> None` |
| `DesignValidator._check_crew_and_life_support()` | `-> None` |
| `DesignValidator._check_layer_mass()` | `-> None` |

**Skeptical Challenge:** Are these genuinely missing or intentionally omitted?
**Verdict:** All other services in the strategy layer have complete type hints.
This is the only service with gaps. PEP 484 compliance is a project requirement per CLAUDE.md.

**Fix:** Added all 6 return type annotations. Added `TYPE_CHECKING` import for `GameRegistries`.

### 2.5 Missing Return Type - Fleet.add_ship() (VERIFIED - APPLIED)

**File modified:** `game/strategy/data/fleet.py`

**Issue:** `add_ship(self, ship: ShipInstance)` was missing `-> None` return type.
All other Fleet public methods (`remove_ship`, `trigger_speed_recalculation`,
`add_order`, `pop_order`, `clear_orders`) have explicit return types.

**Fix:** Added `-> None`.

---

## 3. Architectural Ambiguity

Items where the Skeptical Subagent could not reach a definitive verdict.

### 3.1 Shield Events Defined But Never Generated -- RESOLVED

**Status:** RESOLVED via implementation (TDD).

**Original Issue:** Three EventType enum values (`SHIELD_ACTIVATED`, `SHIELD_DEACTIVATED`,
`SHIELD_AUTO_DEACTIVATED`) were defined but no engine ever generated them.

**Resolution:** Implemented event logging following existing patterns:

| Event | Engine | Hook |
|-------|--------|------|
| `SHIELD_ACTIVATED` | `PlanetActionEngine._initiate_activation()` | On activation start |
| `SHIELD_DEACTIVATED` | `PlanetActionEngine._initiate_deactivation()` | On deactivation start or activation cancel |
| `SHIELD_AUTO_DEACTIVATED` | `PlanetEnergyEngine._cancel_all_draining_components()` | On energy depletion |

**Files modified:**
- `game/strategy/engine/planet_action_engine.py` -- added `event_bus` parameter, logging in activation/deactivation
- `game/strategy/engine/planet_energy_engine.py` -- added `event_bus` parameter, logging in auto-deactivation
- `game/strategy/engine/turn_engine.py` -- wired `event_bus` to both engines in lazy init

**Tests added (TDD):**
- `tests/unit/strategy/engine/test_planet_action_engine.py::TestPlanetActionEngineEvents` (4 tests)
- `tests/unit/strategy/engine/test_planet_energy_engine.py::TestPlanetEnergyEngineEvents` (3 tests)

**Full suite result:** 14731 passed, 0 failed.

### 3.2 Services Package Sparse Exports

**File:** `game/strategy/services/__init__.py`

**Issue:** Only `CargoTransferService` is exported from the package. The other 10 services
(ActionTimeResolver, AreaEffectManager, ComponentInspector, DesignCostCalculator,
DesignValidator, FleetCargoProjector, FleetNavigationService, FleetSpeedCalculator,
ModifierResolver, ShipStatsCalculator, StrategicAbilityScanner) are only importable
via direct module paths.

**Skeptical Challenge:** Would adding all exports create circular import issues?
**Verdict:** AMBIGUOUS. Some services import from `game.simulation` which may transitively
import from `game.strategy`. Without a full import graph analysis, expanding the `__init__.py`
carries circular import risk. The current pattern (direct module imports) works and is
consistently used across all consumers.

**Recommendation:** Leave as-is until a deliberate refactor pass. The direct import pattern
is functional and avoids import ordering issues.

---

## 4. Suboptimal Approaches

Items verified as genuinely suboptimal (not just stylistic).

### 4.1 BuildQueueSourceDTO Mutable Containers in Frozen Dataclass

**File:** `game/strategy/facade/dto/build_queue_dto.py` (lines 15, 19)

**Issue:** `BuildQueueSourceDTO` is decorated with `@dataclass(frozen=True)` but contains
mutable container fields:
- `construction_queue: List[Dict[str, Any]]`
- `build_rate: Dict[str, float]`

While `frozen=True` prevents field reassignment, the contents of these containers can be
mutated by UI code. The `from_domain()` classmethod does create shallow copies, which
protects the original domain object, but the DTO's own copy remains mutable.

**Skeptical Challenge:** Is this actually exploited by any UI code?
**Verdict:** VERIFIED SUBOPTIMAL. No UI code currently mutates these, so this is a
defense-in-depth concern rather than an active bug. However, it violates the documented
CQRS-lite contract that DTOs are "immutable" (docs/02_PATTERNS.md line 487).

**Impact:** LOW -- the shallow copy in `from_domain()` protects domain state.
**Risk of fixing:** MEDIUM -- changing to `Tuple` types would require updating all consumers
that iterate `construction_queue` or access `build_rate` keys.

**Recommendation:** Accept current shallow-copy defense. If true immutability is needed,
convert to `tuple(tuple(item.items()) for item in queue)` in `from_domain()` and use
`Tuple` field types, but scope this as a separate refactor.

### 4.2 Event Dataclass Type Hint Asymmetry

**File:** `game/strategy/events/event_log.py` (lines 23-24)

**Issue:** `Event.event_type` and `Event.category` are typed as `str`, but
`EventLog.get_events_by_category()` accepts `Union[str, EventCategory]`. The Event
dataclass stores the `.value` (string) of the enum, which is correct for serialization,
but the type annotation doesn't reflect that enum values are also accepted at construction.

**Skeptical Challenge:** Would changing to `Union[str, EventType]` break serialization?
**Verdict:** VERIFIED SUBOPTIMAL but low-risk. The `to_dict()` / `from_dict()` methods
handle strings, and all event creation sites pass enum `.value` strings. Changing the
type hint would improve accuracy but is cosmetic.

**Recommendation:** Leave as-is. The serialization behavior is correct and the mismatch
is purely at the type annotation level.

---

## 5. Verification Summary

### Items Verified and Applied

| # | Category | File(s) | Change |
|---|----------|---------|--------|
| 1.1 | Docs Update | turn_engine.py | Docstring: 11->14 phases, added 0c1/1.6/1.7 |
| 1.2 | Docs Update | strategy_layer.md | Added 3 missing interfaces to table |
| 1.3 | Docs Update | strategy_layer.md | Fleet delegates 3->4, added FleetPursuerTracker |
| 2.1 | Code Fix | interfaces/__init__.py | Exported 8 missing engine interfaces |
| 2.2 | Code Fix | validation/__init__.py | Exported PlanetOrderValidator |
| 2.3 | Code Fix | facade/__init__.py | Added __all__ with StrategySessionFacade |
| 2.4 | Code Fix | design_validator.py | Added 6 missing type hints + TYPE_CHECKING import |
| 2.5 | Code Fix | fleet.py | Added `-> None` to `add_ship()` |
| 3.1 | Resolved | planet_action_engine.py, planet_energy_engine.py, turn_engine.py | Implemented shield event logging (TDD, +7 tests) |

### Items Verified - No Action Taken

| # | Category | Reason |
|---|----------|--------|
| 3.2 | Ambiguity | Services exports: circular import risk, current pattern works |
| 4.1 | Suboptimal | BuildQueueSourceDTO: shallow copy sufficient, fix would break consumers |
| 4.2 | Suboptimal | Event type hints: cosmetic, serialization is correct |

### Systems Verified Clean (No Discrepancies)

| System | Agent | Result |
|--------|-------|--------|
| Order System | verify-order-system | All 17 OrderTypes handled, all 31 commands registered |
| Protocol Compliance | verify-protocols | All 5 domain classes implement protocols fully |
| Production Flow | verify-production-fleet | Algorithm matches documentation |
| Generation Pipeline | verify-events-gen | DensityMap, placement strategies, storm gen all correct |
| CQRS Query Methods | verify-facade-dtos | All public facade queries return DTOs, never domain objects |
| Habitability Formulas | verify-events-gen | All functions have complete type hints and docstrings |

---

## 6. QA Session Changes (Post-Report)

Changes driven by QA session `20260407_145344`, applied after the initial sync report.

### 6.1 Fleet Position Projection and Transfer Colony Resolution

**Problem:** Transfer dialog showed empty Target dropdown when fleet had MOVE orders
queued to a colony. The system only checked the fleet's current location for colonies.

**Files modified:**
- `game/strategy/services/cargo_transfer_service.py` — added `project_fleet_position()` utility,
  updated `resolve_colonies()` with projected position fallback
- `game/ui/screens/transfer_dialog.py` — `_populate_initial_data()` checks projected position
- `tests/unit/strategy/services/test_cargo_transfer_service.py` — +9 tests

### 6.2 Transfer Dialog UI Layout Overhaul

**Problem:** Bottom buttons clipped off screen, arrow buttons too narrow, only 3 arrows
per direction, insufficient space for large transfer amounts.

**Files modified:**
- `game/ui/screens/transfer_dialog.py` — 5 arrow gradations per direction (1/10/1000/10K/100K),
  uniform 38px button width, pending area widened to 120px, bottom buttons raised,
  Max button labels simplified
- `game/ui/screens/strategy_window_manager.py` — window widened 900→940px

### 6.3 Drop Pod Rows Always Visible

**Problem:** Drop pods only appeared in transfer grid when present on either side.
Should always show as transferable items.

**Files modified:**
- `game/ui/screens/transfer_dialog.py` — added `_discover_pod_designs()` using DesignLibrary
  to find all `vehicle_type == "Drop Pod"` designs; `_add_pod_rows()` merges discovered
  designs with actual pod counts. Filter Empty toggle still hides 0/0 rows.

### 6.4 Colonize Target Path Preview Line

**Problem:** No preview line drawn from fleet to cursor during colonize target selection.

**Files modified:**
- `game/ui/screens/strategy_renderer.py` — added `COLONIZE_TARGET` to preview line condition,
  refactored `_draw_move_preview()` to use `project_fleet_position()` (handles MOVE+WARP chains)

### 6.5 Order Editing (MOVE and TRANSFER)

**Problem:** No way to modify queued orders without delete+re-create.

**Files modified:**
- `game/ui/screens/orders_window.py` — "E" button for editable order types, `EDITABLE_ORDER_TYPES` set, `edit_order_callback`
- `game/ui/screens/strategy_screen.py` — `on_edit_order()`, MOVE edit flow (ghost hex + camera pan + in-place update), TRANSFER edit flow (remove + re-open dialog)
- `game/ui/screens/strategy_click_dispatcher.py` — `EDIT_MOVE` mode handler
- `game/ui/screens/strategy_renderer.py` — `_draw_ghost_hex()` (yellow outline for old MOVE destination)
- `game/ui/screens/strategy_fleet_command_router.py` — ESC cancel for EDIT_MOVE
- `game/ui/screens/strategy_input_handler.py` — EDIT_MOVE in fleet context mode list
- `game/ui/screens/strategy_window_manager.py` — wired edit_order_callback

### 6.6 Per-Component Activation Architecture (Major Refactor)

**Problem:** `planet.active_abilities` was `Dict[str, bool]` keyed by ability name —
collapsed multiple component instances into a single boolean. System Geologic Stabilizer
was invisible in the abilities panel because a lower-tier Geologic Stabilizer was found first
and the dedup check dropped the second.

**Root cause:** Three levels of the system (planet data, validator, UI panel) all keyed by
ability_name instead of component_key.

**Solution:** Clean-sheet refactor to per-component granularity:

**Files modified:**
- `game/strategy/data/planet.py` — `active_abilities` changed from stored field to derived
  property scanning `facility.component_states`; removed from serialization; deleted `set_ability_active()`
- `game/strategy/engine/component_activation_engine.py` — removed `planet.active_abilities` writes
- `game/strategy/engine/planet_energy_engine.py` — removed `planet.active_abilities` writes,
  deleted `_set_ability_active()` helper
- `game/strategy/validation/planet_order_validator.py` — validates by `component_key` when
  provided; allows multiple instances of same ability
- `game/strategy/engine/commands.py` — added `component_key` field to `IssuePlanetOrderCommand`
- `game/strategy/engine/planet_command_handlers.py` — passes `component_key` into order target
- `game/ui/screens/planet_abilities_window.py` — per-component rows (no dedup), numbered labels
  for multiple instances, status from component_state, commands carry component_key
- `game/ui/screens/strategy_fleet_command_router.py` — hotkey toggle uses component_key
- `tests/unit/strategy/data/test_planet_active_abilities.py` — +11 new tests for derived property
- `tests/unit/strategy/engine/test_component_activation_engine.py` — updated to check component_states
- `tests/unit/strategy/engine/test_planet_energy_engine.py` — removed stale active_abilities mock setup

### 6.7 Documentation Updates

- `docs/systems/strategy_layer.md` — per-component activation architecture section,
  fleet position projection section, shield event generation note
- `docs/systems/orders_system.md` — order editing section, key files table updated

### Test Results

All changes: **14752 tests passed, 0 failed** (full sharded suite).
