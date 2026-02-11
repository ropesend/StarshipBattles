# PROJ-97: Per-Resource Production Rate Limits for Build Queues

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-97` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-97 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. JSON Data & Ability Update | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. BuildQueueSource Per-Resource Rates | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Controller Turn Calc & Tick Capping | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. UI Display Updates | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Remove Shipyard ResourceStorage | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Integration Tests & Verification | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-02-10
**Active Phase:** Phase 5
**Last Action:** Phases 3-4 complete - Controller + UI updates
**Next Action:** Execute Phase 5 - Remove Shipyard ResourceStorage
**Blockers:** None
**Context for Next Agent:** Phases 3-4 complete. _calculate_build_turns() now accepts Dict[str, float] and uses per-resource bottleneck formula. _build_cost_tracking() caps per-tick costs to rate/100. Removed PLANETARY_YARD_BUILD_RATE constant, using get_default_production_rates(). Updated UI display in empire_build_queue_window.py and build_queue_selector.py. 9 new tests added in TestPerResourceBuildRates class. All 7602 tests pass.

## Overview
Change the build queue production system from a single uniform `build_rate: float` to per-resource production rates (`Dict[str, float]`). This allows each resource type to have a different maximum production rate per turn at each build yard. Also remove dead `ResourceStorage` abilities from shipyard components, and add `production_rates` data to the SpaceShipyard ability in JSON.

## Goals
- Per-resource production rate limits (e.g., Metals 3000/turn, Exotics 1500/turn)
- Rates defined in JSON data files, not hardcoded in Python
- Correct multi-turn spreading: 5500 Metals at 3000/turn = 3000 on turn 1, 2500 on turn 2
- Remove dead `ResourceStorage` from shipyard components
- Zero changes to ProductionEngine (it's already rate-agnostic via cost_per_tick)

## Scope
**In:**
- `data/production_rates.json` — new file with default per-resource rates per yard type
- `data/components.json` — add `production_rates` to SpaceShipyard abilities, remove ResourceStorage from shipyards
- `game/simulation/components/abilities/harvester.py` — SpaceShipyardAbility gains production_rates field
- `game/strategy/data/build_queue_source.py` — build_rate float → Dict[str, float]
- `game/ui/panels/build_queue_controller.py` — per-resource turn calc and cost_per_tick capping
- `game/ui/screens/build_queue_selector.py` — UI display of build rate
- `game/ui/screens/empire_build_queue_window.py` — UI display of build rate column
- All tests referencing `build_rate` as float

**Out:**
- ProductionEngine changes (confirmed rate-agnostic, works with cost_per_tick only)
- Planet "hidden complex" or planet ability system (deferred to future project)
- Modifier system for production rates (user stated this comes later)
- Save game migration (saves are disposable per CLAUDE.md)

## Key Files
| Component | File Path |
|-----------|-----------|
| Production rates JSON | `data/production_rates.json` (NEW) |
| Components JSON | `data/components.json` |
| SpaceShipyardAbility | `game/simulation/components/abilities/harvester.py` |
| BuildQueueSource | `game/strategy/data/build_queue_source.py` |
| BuildQueueController | `game/ui/panels/build_queue_controller.py` |
| Queue selector UI | `game/ui/screens/build_queue_selector.py` |
| Empire build queue window | `game/ui/screens/empire_build_queue_window.py` |
| Empire build queue formatter | `game/ui/screens/empire_build_queue_formatter.py` |
| JSON loader utility | `game/core/json_utils.py` (reuse `load_json`) |
| Test: build queue source | `tests/unit/strategy/data/test_build_queue_source.py` |
| Test: controller | `tests/unit/ui/panels/test_build_queue_controller.py` |
| Test: empire window | `tests/unit/ui/screens/test_empire_build_queue_window.py` |
| Test: formatter | `tests/unit/ui/screens/test_empire_build_queue_formatter.py` |
| Test: tick consumption | `tests/unit/strategy/production_engine/test_tick_consumption.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

---

## Phases

### Phase 1: JSON Data & Ability Update [Medium]
**Objective:** Create production_rates.json, update SpaceShipyardAbility, update components.json
**Status:** Not Started

#### Task 1.1: Create `data/production_rates.json` [Simple]
**File:** `data/production_rates.json` (NEW)
**Tests:** Manual verification — load with `json.load()`
- [ ] Create `data/production_rates.json` with three keys: `planetary_yard`, `space_shipyard`, `fleet_space_yard`
- [ ] Each key maps to a dict of resource names → max units per turn
- [ ] Planetary yard: all resources at 2000
- [ ] Space shipyard and fleet space yard: all resources at 3000
- [ ] Resource types: Metals, Organics, Radioactives, Vapors, Exotics
**Notes:**

#### Task 1.2: Add `production_rates` field to SpaceShipyardAbility [Simple]
**File:** `game/simulation/components/abilities/harvester.py` (lines 95-128)
**Tests:** `pytest tests/unit/simulation/components/abilities/ -k shipyard`
- [ ] Add `self.production_rates: Dict[str, float]` to `__init__`, parsed from `data.get("production_rates", {})`
- [ ] Add UI row for production rates in `get_ui_rows()` if non-empty
- [ ] Ensure backward compat: if `production_rates` missing from data, default to empty dict
**Notes:**

#### Task 1.3: Update `data/components.json` shipyard entries [Simple]
**File:** `data/components.json`
**Tests:** `pytest tests/ -k "component" --testmon`
- [ ] Add `"production_rates": {"Metals": 3000, "Organics": 3000, "Radioactives": 3000, "Vapors": 3000, "Exotics": 3000}` to `space_shipyard`'s SpaceShipyard ability data
- [ ] Same for `fleet_space_yard`'s SpaceShipyard ability data
- [ ] DO NOT remove ResourceStorage yet (Phase 5)
**Notes:**

#### Task 1.4: Write unit tests for production rate loading [Simple]
**File:** `tests/unit/strategy/data/test_production_rates.py` (NEW)
**Tests:** `pytest tests/unit/strategy/data/test_production_rates.py`
- [ ] Test loading `production_rates.json` via `load_json`
- [ ] Test that all three yard types are present
- [ ] Test each yard type has expected resource keys
- [ ] Test default values (2000 for planetary, 3000 for shipyards)
**Notes:**

---

### Phase 2: BuildQueueSource Per-Resource Rates [Medium]
**Objective:** Change `build_rate` from `float` to `Dict[str, float]` and update all queue discovery
**Status:** Not Started

#### Task 2.1: Update BuildQueueSource dataclass [Simple]
**File:** `game/strategy/data/build_queue_source.py` (line 40)
**Tests:** `pytest tests/unit/strategy/data/test_build_queue_source.py`
- [ ] Change `build_rate: float = 2000.0` to `build_rate: Dict[str, float] = field(default_factory=dict)`
- [ ] Add import for `field` from dataclasses (already imported)
- [ ] Add import for `Dict` from typing (already imported)
**Notes:**

#### Task 2.2: Add production rate loader function [Simple]
**File:** `game/strategy/data/build_queue_source.py`
**Tests:** `pytest tests/unit/strategy/data/test_build_queue_source.py`
- [ ] Add `_load_production_rates() -> Dict` function that loads `data/production_rates.json` via `load_json` with caching
- [ ] Add `get_default_production_rates(yard_type: str) -> Dict[str, float]` public function
- [ ] Yard types: `"planetary_yard"`, `"space_shipyard"`, `"fleet_space_yard"`
- [ ] Fallback: return empty dict if file missing or type unknown
**Notes:** Use `game.core.json_utils.load_json` for loading. Cache at module level.

#### Task 2.3: Update `_get_facility_build_rate` → `_get_facility_production_rates` [Medium]
**File:** `game/strategy/data/build_queue_source.py` (lines 44-65)
**Tests:** `pytest tests/unit/strategy/data/test_build_queue_source.py`
- [ ] Rename to `_get_facility_production_rates(facility) -> Dict[str, float]`
- [ ] Read `production_rates` from SpaceShipyard ability data in facility.design_data
- [ ] If found, apply `construction_speed_bonus` multiplier to all rates
- [ ] If not found, fall back to `get_default_production_rates("space_shipyard")` and apply bonus
- [ ] Return per-resource dict
**Notes:**

#### Task 2.4: Update `collect_build_queues_at_hex()` [Simple]
**File:** `game/strategy/data/build_queue_source.py` (lines 96-168)
**Tests:** `pytest tests/unit/strategy/data/test_build_queue_source.py`
- [ ] Planet base queue (line 129): `build_rate=get_default_production_rates("planetary_yard")`
- [ ] Facility queue (line 146): `build_rate=_get_facility_production_rates(facility)`
- [ ] Fleet queue (line 164): `build_rate=get_default_production_rates("fleet_space_yard")`
**Notes:**

#### Task 2.5: Update `collect_all_build_queues_for_empire()` [Simple]
**File:** `game/strategy/data/build_queue_source.py` (lines 171-236)
**Tests:** `pytest tests/unit/strategy/data/test_build_queue_source.py`
- [ ] Planet base queue (line 199): `build_rate=get_default_production_rates("planetary_yard")`
- [ ] Facility queue (line 216): `build_rate=_get_facility_production_rates(facility)`
- [ ] Fleet queue (line 232): `build_rate=get_default_production_rates("fleet_space_yard")`
**Notes:**

#### Task 2.6: Update existing build_queue_source tests [Medium]
**File:** `tests/unit/strategy/data/test_build_queue_source.py`
**Tests:** `pytest tests/unit/strategy/data/test_build_queue_source.py`
- [ ] Update `_make_shipyard_facility` helper to include `production_rates` in SpaceShipyard data
- [ ] Update assertions: `source.build_rate == 2000.0` → `source.build_rate == {"Metals": 2000, ...}`
- [ ] Update test at line 494 (base queue rate)
- [ ] Update test at line 509 (default shipyard rate)
- [ ] Update test at line 538 (shipyard with bonus — 4500.0 → per-resource * 1.5)
- [ ] Update test at line 550 (fleet rate)
- [ ] Add new test: facility with explicit `production_rates` in design_data
**Notes:**

---

### Phase 3: Controller Turn Calc & Tick Capping [Medium]
**Objective:** Update BuildQueueController to use per-resource rates for turn calculation and cost_per_tick capping
**Status:** Not Started

#### Task 3.1: Update `_calculate_build_turns()` [Medium]
**File:** `game/ui/panels/build_queue_controller.py` (lines 196-214)
**Tests:** `pytest tests/unit/ui/panels/test_build_queue_controller.py`
- [ ] Change signature: `build_rate: float` → `build_rate: Dict[str, float]`
- [ ] New formula: `turns = max(1, max(ceil(cost[res] / rate) for res, rate in build_rate.items() if cost.get(res, 0) > 0 and rate > 0))`
- [ ] Handle edge case: resource in cost but not in rates → treat as unbounded (1 turn)
- [ ] Handle edge case: rate is 0 → skip (don't divide by zero)
- [ ] Handle empty cost or empty rates → return 1
**Notes:**

#### Task 3.2: Update `_build_cost_tracking()` to cap per-resource [Medium]
**File:** `game/ui/panels/build_queue_controller.py` (lines 216-234)
**Tests:** `pytest tests/unit/ui/panels/test_build_queue_controller.py`
- [ ] Accept `build_rate: Dict[str, float]` parameter (add parameter)
- [ ] Calculate `max_per_tick = {res: rate / 100 for res, rate in build_rate.items()}`
- [ ] Cap each resource's per-tick cost: `min(amount / total_ticks, max_per_tick.get(res, float('inf')))`
- [ ] This ensures no resource exceeds its rate limit within a single turn
**Notes:** The key insight: when turns > 1, cost_per_tick is already < max_per_tick for the bottleneck resource. But for non-bottleneck resources that would finish in fewer turns, we cap them to prevent front-loading.

#### Task 3.3: Update all callers to pass Dict build_rate [Simple]
**File:** `game/ui/panels/build_queue_controller.py`
**Tests:** `pytest tests/unit/ui/panels/test_build_queue_controller.py`
- [ ] `_add_to_single_queue()` (line 389): already reads `source.build_rate`, now a dict
- [ ] `_add_to_single_queue()` (line 391): pass dict to `_calculate_build_turns`
- [ ] `_add_item_with_target_planet()` (line 432): same pattern
- [ ] `_add_to_multiple_queues()` (line 476): pass `source.build_rate` dict
- [ ] `_add_to_fallback()` (line 516): replace `PLANETARY_YARD_BUILD_RATE` constant with `get_default_production_rates("planetary_yard")`
- [ ] Pass `build_rate` to `_build_cost_tracking()` calls
- [ ] Remove `PLANETARY_YARD_BUILD_RATE = 2000.0` constant (line 18) — no longer needed
**Notes:**

#### Task 3.4: Update controller tests [Medium]
**File:** `tests/unit/ui/panels/test_build_queue_controller.py`
**Tests:** `pytest tests/unit/ui/panels/test_build_queue_controller.py`
- [ ] Update `_make_source()` helper to accept `build_rate` as dict (currently passes float)
- [ ] Update test at line 383: `build_rate=2000.0` → `build_rate={"Metals": 2000.0, ...}`
- [ ] Update test at line 401: `build_rate=3000.0` → `build_rate={"Metals": 3000.0, ...}`
- [ ] Update test at line 416-417: slow/fast sources with dict rates
- [ ] Update test at line 425: fallback rate test
- [ ] Add new test: per-resource bottleneck (5500 Metals at 3000/turn, 1000 Organics at 3000/turn → 2 turns from Metals)
- [ ] Add new test: different per-resource rates (Metals 3000, Exotics 1500 → Exotics is bottleneck)
- [ ] Add new test: cost_per_tick is capped per-resource
**Notes:**

---

### Phase 4: UI Display Updates [Simple]
**Objective:** Update UI components that display build_rate as a scalar
**Status:** Not Started

#### Task 4.1: Update build_queue_selector.py display [Simple]
**File:** `game/ui/screens/build_queue_selector.py` (line 102)
**Tests:** Manual visual check
- [ ] Change `int(source.build_rate)` to display summary (e.g., `max(source.build_rate.values())` if all rates equal, or "varies" if different)
- [ ] Example: `f"{max(source.build_rate.values()):.0f}/turn"` when all rates are equal
**Notes:**

#### Task 4.2: Update empire_build_queue_window.py build_rate column [Simple]
**File:** `game/ui/screens/empire_build_queue_window.py` (line 549)
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`
- [ ] Change `f"{int(source.build_rate)}/turn"` to handle dict (same logic as 4.1)
**Notes:**

#### Task 4.3: Update UI tests [Simple]
**File:** `tests/unit/ui/screens/test_empire_build_queue_window.py`, `tests/unit/ui/screens/test_empire_build_queue_formatter.py`
**Tests:** `pytest tests/unit/ui/screens/`
- [ ] Update test at line 475 (build rate column test): mock `source.build_rate` as dict
- [ ] Update formatter test at line 34: `source.build_rate = 10` → `source.build_rate = {"Metals": 10}`
- [ ] Verify all empire build queue window tests pass with dict build_rate
**Notes:**

---

### Phase 5: Remove Shipyard ResourceStorage [Simple]
**Objective:** Remove dead ResourceStorage abilities from shipyard components
**Status:** Not Started

#### Task 5.1: Remove ResourceStorage from components.json [Simple]
**File:** `data/components.json`
**Tests:** `pytest tests/ -n 12`
- [ ] Remove `"ResourceStorage": {"Metals": 1000, "Organics": 500}` from `space_shipyard` abilities
- [ ] Remove `"ResourceStorage": {"Metals": 500, "Organics": 250}` from `fleet_space_yard` abilities
- [ ] Run full test suite to confirm zero breakage
**Notes:** Confirmed dead code by swarm analysis: never read by any engine, UI, or test.

---

### Phase 6: Integration Tests & Verification [Medium]
**Objective:** End-to-end testing and full verification
**Status:** Not Started

#### Task 6.1: Write integration tests [Medium]
**File:** `tests/integration/strategy/test_production_rates.py` (NEW)
**Tests:** `pytest tests/integration/strategy/test_production_rates.py`
- [ ] Test: Build queue item with Metals cost 5500 at rate 3000/turn takes 2 turns
- [ ] Test: After 100 ticks (turn 1), no more than 3000 Metals consumed
- [ ] Test: After 200 ticks (turn 2), all 5500 Metals consumed and item completes
- [ ] Test: Mixed resources with different rates — bottleneck resource determines turns
- [ ] Test: Shipyard with construction_speed_bonus 1.5 multiplies all per-resource rates
**Notes:**

#### Task 6.2: Full test suite verification [Simple]
**Tests:** `pytest tests/ -n 12`
- [ ] Run complete test suite
- [ ] Verify 7595+ tests pass with zero failures
- [ ] Document any new test count
**Notes:**

---

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (`pytest tests/ -n 12`)
- [ ] Per-resource rates loaded from JSON correctly
- [ ] Turn calculation uses per-resource bottleneck formula
- [ ] Cost_per_tick respects per-resource caps (3000/turn → 30/tick max per resource)
- [ ] ResourceStorage removed from shipyard components with no breakage
- [ ] Audit passed
- [ ] User verified
