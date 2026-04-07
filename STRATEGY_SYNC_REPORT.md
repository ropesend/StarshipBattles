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

### 3.1 Shield Events Defined But Never Generated

**Files:** `game/strategy/events/event_types.py` (lines 24-26)

**Issue:** Three EventType enum values are defined but no engine ever generates them:
- `SHIELD_ACTIVATED`
- `SHIELD_DEACTIVATED`
- `SHIELD_AUTO_DEACTIVATED`

**Where they should be logged:**
- `PlanetActionEngine._initiate_activation()` / `_initiate_deactivation()` -- handles
  shield toggle but doesn't log events
- `PlanetEnergyEngine` -- auto-deactivates shields on energy depletion but doesn't log

All 14 other EventType values ARE generated in their respective engines.

**Skeptical Challenge:** Are these planned for future implementation?
**Verdict:** AMBIGUOUS. They were likely added as part of PROJ-238 (planet actions) with the
intention of logging shield state changes, but the logging code was never written.
Two valid resolutions:
1. **Implement the logging** in PlanetActionEngine and PlanetEnergyEngine (matches the
   apparent design intent)
2. **Remove the enum values** if shield events are not needed by the UI event log

**Recommendation:** Implement the logging -- the enum values, category mapping, and event
infrastructure are all in place. The PlanetActionEngine already has the exact activation/
deactivation hooks where events should be appended.

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

### Items Verified - No Action Taken

| # | Category | Reason |
|---|----------|--------|
| 3.1 | Ambiguity | Shield events: user decision needed (implement logging vs remove enums) |
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
