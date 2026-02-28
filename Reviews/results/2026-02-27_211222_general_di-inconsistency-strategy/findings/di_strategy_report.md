# DI Strategy Layer Audit Report

**Date:** 2026-02-27
**Scope:** Strategy layer DI violations via `get_default_registry_provider()` usage
**Files Reviewed:** 5

---

## Summary

- **Total issues found:** 8
- **Critical:** 2
- **Major:** 3
- **Minor:** 1
- **Info:** 2

---

## Findings

---

### CRITICAL: ShipInstance.get_calculated_stats() has no registries parameter

**ID:** DI-S-001
**Location:** `game/strategy/data/ship_instance.py:239-271`
**Issue:** `get_calculated_stats()` calls `get_default_registry_provider()` directly on every cache miss (line 258). The method signature accepts only `force_refresh: bool` -- there is no `registries` parameter at all. The class itself (`ShipInstance` dataclass) also has no stored `registries` field.

**Impact:** This is the highest-severity violation in the strategy layer. `get_calculated_stats()` is called pervasively throughout the codebase (20+ call sites across `ShipResourceManager`, `ShipCargoManager`, `ShipDisplayFormatter`, `FleetSpeedCalculator`, `ShipStatsCalculator.has_warp_capability()`, `EnvironmentalHazardEngine`, multiple UI screens, and within `ShipInstance` itself). Every one of these call chains silently relies on global state. This makes unit testing of anything that touches ship stats impossible without configuring the global registry, and creates a hidden coupling from pure data objects to global state.

**Call Chain:** `ShipInstance.get_calculated_stats()` is called by:
- `ShipResourceManager` (4 call sites) -- delegates from `ShipInstance` resource methods
- `ShipCargoManager.get_cargo_capacity()` -- delegates from `ShipInstance` cargo methods
- `ShipDisplayFormatter` (3 call sites) -- delegates from `ShipInstance` display methods
- `FleetSpeedCalculator.calculate_fleet_speed()` -- per-ship stat lookup
- `ShipStatsCalculator.has_warp_capability()` -- static method, no registries context
- `EnvironmentalHazardEngine.process_environmental_tick()` -- per-ship stat lookup
- UI screens: `fleet_data_source.py`, `fleet_report_filters.py`, `strategy_detail_fmt.py`
- `ShipInstance.create()` (line 168) -- during ship creation
- `ShipInstance.get_hp_percentage()` and `ShipInstance.repair()` -- internal self-calls

None of these callers can pass registries because the method does not accept it.

**Recommendation:** Add an optional `registries` parameter to `ShipInstance` (as a field or constructor arg), and thread it through `get_calculated_stats()`. The `ShipInstance.create()` factory and `from_dict()` deserialization paths should accept and store registries. All delegate managers (`ShipResourceManager`, `ShipCargoManager`, `ShipDisplayFormatter`) inherit the registries from their parent `ShipInstance`. The fallback to global should remain temporarily but be marked with a deprecation comment.

**Effort:** Complex -- requires updating `ShipInstance` dataclass, the `create()` factory, `from_dict()`, all three delegate managers, and ideally the `FleetBattleAdapter`/`SimulationAdapter` that create `ShipInstance` objects.

---

### CRITICAL: FleetCapabilityCalculator uses module-level global accessor with no DI path

**ID:** DI-S-002
**Location:** `game/strategy/data/fleet_capability_calculator.py:14-17, 42, 68, 185`
**Issue:** The module-level function `_get_default_component_registry()` (lines 14-17) calls `get_default_registry_provider().get_components()` and is used by 3 methods: `ship_has_spaceyard()` (line 42), `space_shipyard_count` property (line 68), and `ship_has_ability()` (line 185). Neither the class constructor nor any of these methods accept a `registries` or `component_registry` parameter.

**Impact:** `FleetCapabilityCalculator` is instantiated by `Fleet.__init__()` (line 141 of `fleet.py`) without any registries parameter. `Fleet.__init__()` itself has no registries parameter. This means every fleet in the game carries a capability calculator that can only resolve abilities via global state. The static methods `ship_has_spaceyard()` and `ship_has_ability()` are also called directly from UI code (`fleet_data_source.py`, `fleet_report_filters.py`) with no DI option.

**Call Chain:**
- `Fleet.__init__()` -> `FleetCapabilityCalculator(self)` -- no registries passed
- `FleetCapabilityCalculator.ship_has_spaceyard()` -> `_get_default_component_registry()` -> global
- `FleetCapabilityCalculator.space_shipyard_count` -> `_get_default_component_registry()` -> global
- `FleetCapabilityCalculator.ship_has_ability()` -> `_get_default_component_registry()` -> global
- UI calls: `fleet_data_source.py:244-269`, `fleet_report_filters.py:151-320` -- static method calls

**Recommendation:** Add `registries: Optional[GameRegistries] = None` to `FleetCapabilityCalculator.__init__()`, store it, and use it in all methods. Update `Fleet.__init__()` to accept and forward `registries`. For the static methods (`ship_has_spaceyard`, `ship_has_ability`), add an optional `registry` parameter with fallback.

**Effort:** Medium -- class is self-contained, but `Fleet.__init__()` needs updating too, and Fleet is created in many places.

---

### MAJOR: TurnEngine constructor falls back to global registry provider

**ID:** DI-S-003
**Location:** `game/strategy/engine/turn_engine.py:161-170`
**Issue:** `TurnEngine.__init__()` accepts `registries: Optional[GameRegistries] = None` (line 104) but falls back to `get_default_registry_provider()` when `None` (lines 164-170). Both creation sites in `GameSession` (lines 85 and 292 of `game_session.py`) call `TurnEngine()` with no arguments, always triggering the fallback.

**Impact:** The fallback pattern means registries are never actually injected in production code. The `GameSession` has no stored registries to pass. This is a "Major" rather than "Critical" because the parameter _exists_ -- the infrastructure is there but unused. The positive note is that once resolved, `TurnEngine` properly propagates its registries to child engines (`ConflictResolutionEngine`, `ResourceManagementEngine`, `ResupplyEngine`, `HarvestingEngine`) via the lazy property initializers.

**Call Chain:**
- `GameSession.__init__()` -> `TurnEngine()` -- no registries
- `GameSession.from_dict()` -> `TurnEngine()` -- no registries
- `create_default_turn_engine()` -> `TurnEngine()` -- no registries

**Recommendation:** `GameSession` should construct a `GameRegistries` instance and pass it: `TurnEngine(registries=registries)`. The registries are already available at `GameSession` init time since `GameInitializer.initialize()` requires them. Make `registries` a required parameter on `TurnEngine` (remove the `Optional` and the fallback).

**Effort:** Simple -- change 2-3 call sites in `GameSession` and the `create_default_turn_engine` factory.

---

### MAJOR: StrategySessionFacade.get_fleet_remaining_pods() uses inline global lookup

**ID:** DI-S-004
**Location:** `game/strategy/facade/strategy_session_facade.py:493-506`
**Issue:** `get_fleet_remaining_pods()` does an inline `get_default_registry_provider()` call (line 502) to get `component_registry`. There is no `registries` parameter on this method, and the facade class has no stored registries. The method also has a broad defensive `try/except` (lines 501-506) that silently swallows registry failures and returns an empty dict.

**Impact:** This facade method is called from UI colonization screens (`strategy_colonization.py:108, 207`). The silent exception swallowing masks real errors -- if the registry is not set up, the user sees no colony pods available with no error indication. The facade wraps `GameSession`, which has a `TurnEngine` that already stores registries (even if via fallback), so there is an existing registries source that could be threaded through.

**Call Chain:**
- `strategy_colonization.py` UI -> `facade.get_fleet_remaining_pods(fleet_id)`
- Inside method: `get_default_registry_provider()` -> global state
- Could instead: `self._session.turn_engine._registries.components`

**Recommendation:** Access registries from the session's turn engine (`self._session.turn_engine._registries.components`) or better, store registries on the facade or session directly. Remove the broad exception handler -- if registries are unavailable, that is a real error, not something to silently swallow.

**Effort:** Simple -- replace inline global lookup with session-owned registries. Remove defensive try/except.

---

### MAJOR: ShipInstance.to_ship() has optional registries with implicit global fallback

**ID:** DI-S-005
**Location:** `game/strategy/data/ship_instance.py:514-570`
**Issue:** `to_ship()` accepts `registries: Optional[GameRegistries] = None` (line 518) but passes it straight to `ShipSerializer.from_dict()` (line 537). The docstring (line 529) explicitly states: _"If None, uses global fallback (transitional - will be required in Phase 6)."_ This "Phase 6" has apparently not been completed -- the parameter is still optional.

**Impact:** In practice, the two production call sites _do_ pass registries:
- `FleetBattleAdapter.to_battle_ships()` passes `registries=registries` (line 73 of `fleet_battle_adapter.py`)
- `SimulationAdapter` passes `registries=registries` (line 157)

So this is a "dormant" violation -- the fallback code path exists but is currently not triggered in production. However, leaving it optional means new callers could omit registries without warning.

**Call Chain:**
- `FleetBattleAdapter.to_battle_ships(registries=registries)` -> `instance.to_ship(pos, team_id, registries=registries)` -- OK
- `SimulationAdapter.resolve_battle(registries=registries)` -> `ship_state.to_ship(registries=registries)` -- OK
- Potential future callers could omit `registries` and silently fall back to global

**Recommendation:** Make `registries` a required parameter (remove `Optional`, remove the `= None` default). The docstring already says this was planned for "Phase 6" -- complete that plan. Update type hint to `GameRegistries` (not Optional).

**Effort:** Simple -- change signature, verify the 2 existing callers already pass it (they do).

---

### MINOR: EmpireEconomyCalculator docstring teaches global registry anti-pattern

**ID:** DI-S-006
**Location:** `game/strategy/engine/empire_economy_calculator.py:59-68`
**Issue:** The class docstring's "Usage" example demonstrates calling `get_default_registry_provider()` to construct registries before passing them to the calculator. While the calculator itself properly accepts `registries` via constructor injection, the docstring teaches callers to resolve from global state. The UI caller (`empire_panel_window.py:185-193`) follows this exact pattern.

**Impact:** Low direct impact -- the calculator itself is clean. However, the docstring normalizes the anti-pattern for future developers. Every caller will copy this example and bake in the global lookup.

**Call Chain:**
- `empire_panel_window.py:185` -> `get_default_registry_provider()` -> construct `GameRegistries` -> `EmpireEconomyCalculator(registries=registries)` -- caller does the global access, not the calculator

**Recommendation:** Update the docstring to show proper DI from a session or parent context. In the UI caller, access registries from the session/facade rather than calling `get_default_registry_provider()` directly. Example: `registries = self._session.registries` (after adding a registries property to GameSession).

**Effort:** Simple -- docstring change + UI caller update.

---

### INFO: TurnEngine docstring describes Optional registries fallback pattern

**ID:** DI-S-007
**Location:** `game/strategy/engine/turn_engine.py:128-129`
**Issue:** The docstring for the `registries` parameter explicitly documents the fallback: _"Falls back to get_default_registry_provider() if None."_ This documents the current behavior accurately but enshrines the fallback as part of the API contract.

**Impact:** Documentation-only. When the fallback is removed per DI-S-003, this docstring should be updated.

**Recommendation:** Update docstring when making `registries` required.

**Effort:** Simple -- part of DI-S-003 fix.

---

### INFO: EmpireEconomyCalculator constructor accepts Optional registries without fallback

**ID:** DI-S-008
**Location:** `game/strategy/engine/empire_economy_calculator.py:79-86`
**Issue:** The constructor accepts `registries: Optional[GameRegistries] = None` and stores it as-is (line 86). There is _no_ internal fallback to `get_default_registry_provider()`. If `None` is passed, `self._registries` is `None`, and downstream calls to `get_harvester_info(comp, self._registries)` (line 157) receive `None`.

**Impact:** This is actually a _good_ pattern -- no hidden global fallback. The only caller (`empire_panel_window.py`) always passes registries. However, the `Optional` type on the constructor means a caller _could_ omit registries, and the behavior when `None` depends on whether `get_harvester_info()` handles `None` gracefully. This should be made required to make the contract explicit.

**Recommendation:** Make `registries` a required parameter (change `Optional[GameRegistries] = None` to just `GameRegistries`). This prevents accidental omission and makes the DI contract clear.

**Effort:** Simple -- signature change, verify caller.

---

## Top 5 Priority Issues

1. **DI-S-001 (Critical): ShipInstance.get_calculated_stats() -- no registries parameter.**
   This is the most impactful violation. `get_calculated_stats()` is called from 20+ sites across 10+ files. It is the single largest source of hidden global state coupling in the strategy layer. Fixing this unblocks proper DI for `ShipResourceManager`, `ShipCargoManager`, `ShipDisplayFormatter`, `FleetSpeedCalculator`, and all UI stat displays.

2. **DI-S-002 (Critical): FleetCapabilityCalculator -- completely hardcoded to global.**
   No DI path exists at all. Every fleet capability query (spaceyards, abilities, warp) silently hits global state. This affects fleet management, build validation, and combat readiness checks.

3. **DI-S-003 (Major): TurnEngine registries fallback -- parameter exists but never used.**
   The infrastructure is there but `GameSession` never passes registries. Fixing this is simple and unlocks proper DI propagation to all sub-engines (which already accept registries from TurnEngine).

4. **DI-S-004 (Major): StrategySessionFacade.get_fleet_remaining_pods() -- inline global + silent error swallowing.**
   The silent exception handler is particularly concerning -- it masks real initialization failures.

5. **DI-S-005 (Major): ShipInstance.to_ship() -- optional registries planned to be required.**
   Low risk today (callers pass it), but completing the "Phase 6" plan prevents future regression.

---

## Remediation Strategy

The recommended fix order minimizes churn:

1. **Add `registries` property to `GameSession`** -- single source of truth for the session
2. **Fix DI-S-003** -- `GameSession` passes registries to `TurnEngine` (simple, high leverage)
3. **Fix DI-S-004** -- Facade reads from session registries (simple)
4. **Fix DI-S-005** -- Make `to_ship()` registries required (simple)
5. **Fix DI-S-008** -- Make `EmpireEconomyCalculator` registries required (simple)
6. **Fix DI-S-001** -- Add registries to `ShipInstance` (complex, highest impact)
7. **Fix DI-S-002** -- Add registries to `FleetCapabilityCalculator` and `Fleet` (medium)
8. **Fix DI-S-006/DI-S-007** -- Update docstrings (trivial, do alongside fixes)

Steps 1-5 can be done in a single focused session. Steps 6-7 require broader refactoring.
