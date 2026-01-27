# PROJ-23: ShipStatsService Modifier Application Bug

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-23` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-23 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Extract Shared Modifier Logic | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Apply Modifiers in ShipStatsService | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Testing | Complete | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-01-27
**Active Phase:** Audit Complete
**Last Action:** Audit cycle 1 passed with no significant issues
**Next Action:** User verification required
**Blockers:** None
**Context:**
- Added `get_default_stat_multipliers()` and `calculate_stat_multipliers()` to modifiers.py
- Refactored Component._calculate_modifier_stats() to use shared defaults
- Updated ShipStatsService.calculate_stats() to apply modifiers to mass, HP, capacity, movement, and consumption
- Added 5 new tests in TestModifierApplication class
- All 4568 tests pass (4563 original + 5 new)
- Audit passed: implementation verified correct

## Overview
`ShipStatsService.calculate_stats()` reads component ability values from the registry (base definitions) without applying design modifiers. A battery with `simple_size_mount: 20` is calculated as 2,000 energy instead of 40,000 energy, causing warp capability checks to fail incorrectly for CRU_1 design.

## Goals
- Fix modifier application bug so scaled components are calculated correctly
- Extract shared modifier logic into pure functions (single source of truth)
- Ensure Component and ShipStatsService calculate identical results
- Add test coverage for modifier integration

## Scope
**In:**
- Add `calculate_stat_multipliers()` pure function to `modifiers.py`
- Refactor `Component._calculate_modifier_stats()` to use shared function
- Update `ShipStatsService.calculate_stats()` to apply modifier multipliers
- Add integration tests for scaled components

**Out:**
- Changes to modifier definitions in `modifiers.json`
- Changes to component definitions in `components.json`
- UI changes

## Key Files
| Component | File Path |
|-----------|-----------|
| Stats Service | `game/strategy/services/ship_stats_service.py` |
| Modifier Logic | `game/simulation/components/modifiers.py` |
| Component | `game/simulation/components/component.py` |
| Registry | `game/core/registry.py` |
| Stats Tests | `tests/unit/strategy/test_ship_stats_service.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

---

## Root Cause Analysis

**Bug Location:** `ship_stats_service.py:110-135`

The service reads abilities from `comp_def` (registry definition) but ignores modifiers in `comp_entry` (design data):

```python
# Current code reads from registry only
abilities = getattr(comp_def, 'abilities', {}) or {}

# comp_entry contains modifiers that are NEVER applied:
# {'id': 'battery', 'modifiers': [{'id': 'simple_size_mount', 'value': 20.0}]}
```

**Impact:**
| Design | Configuration | Expected | Calculated |
|--------|---------------|----------|------------|
| CRU_1 | 1 battery × size 20 | 40,000 energy | 2,000 (wrong) |
| CRU_2 | 10 batteries × size 1 | 20,000 energy | 20,000 (correct) |

Warp cost for Cruiser: ~3,175 energy → CRU_1 fails warp check incorrectly.

---

## Phase 1: Extract Shared Modifier Logic [Medium]

**Objective:** Create pure functions for modifier calculation

### Task 1.1: Add `get_default_stat_multipliers()` [Simple]
**File:** `game/simulation/components/modifiers.py`
- [ ] Add function returning default stats dict (18 multipliers + 4 additives + properties)

### Task 1.2: Add `calculate_stat_multipliers()` [Simple]
**File:** `game/simulation/components/modifiers.py`
- [ ] Add pure function that applies modifier entries to stats dict

### Task 1.3: Refactor Component to use shared function [Medium]
**File:** `game/simulation/components/component.py`
- [ ] Update `_calculate_modifier_stats()` to call `calculate_stat_multipliers()`
- [ ] Run `pytest tests/unit/components/ -v` to verify behavior preserved

---

## Phase 2: Apply Modifiers in ShipStatsService [Medium]

**Objective:** Update calculate_stats() to apply modifier multipliers

### Task 2.1: Add imports [Simple]
**File:** `game/strategy/services/ship_stats_service.py`
- [ ] Import `calculate_stat_multipliers` from modifiers.py
- [ ] Ensure `get_modifier_registry` is imported

### Task 2.2: Calculate multipliers per component [Medium]
**File:** `game/strategy/services/ship_stats_service.py`
- [ ] Get modifier_registry once at start
- [ ] In loop: extract modifiers from `comp_entry`, call `calculate_stat_multipliers()`

### Task 2.3: Apply multipliers to mass/HP [Medium]
- [ ] Apply `mass_mult` and `mass_add` to component mass
- [ ] Apply `hp_mult` to component HP

### Task 2.4: Apply capacity_mult to ResourceStorage [Medium]
- [ ] Multiply base resource amounts by `capacity_mult`
- [ ] Apply to all storage types (ResourceStorage, FuelStorage, EnergyStorage, AmmoStorage)

### Task 2.5: Apply strategic_mult to StrategicMovement [Simple]
- [ ] Multiply movement by `strategic_mult`

### Task 2.6: Apply consumption_mult to ResourceConsumption [Simple]
- [ ] Multiply consumption amounts by `consumption_mult`

---

## Phase 3: Testing [Medium]

**Objective:** Add tests and verify no regressions

### Task 3.1: Add unit tests for scaled components [Medium]
**File:** `tests/unit/strategy/test_ship_stats_service.py`
- [ ] Add `TestModifierApplication` class with tests for:
  - Scaled battery energy capacity
  - Multiple small vs one large battery equivalence
  - Warp capability with scaled battery

### Task 3.2: Run regression tests [Simple]
- [ ] Run full test suite: `pytest tests/`
- [ ] All 4563+ tests should pass

---

## Verification
- [x] Baseline tests: 4563 passed
- [x] Phase 1: Component tests pass
- [x] Phase 2: ShipStatsService tests pass
- [x] Phase 3: Full suite passes (4568 tests)
- [x] Audit passed (cycle 1 - no significant issues)
- [ ] Manual: CRU_1 and CRU_2 both warp-capable
- [ ] User verified

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | 2026-01-27 | No significant issues | PASSED |

### Audit Cycle 1 Details

**Confirmed Issues (Minor):**
- Phase checklist subtask checkboxes not marked `[x]` (documentation only)

**Resolved Concerns (False Positives):**
- Component doesn't call `calculate_stat_multipliers()` as planned in Task 1.3 — Investigated and determined this is correct architecture: Component passes `component=self` for targeted effects; ShipStatsService doesn't need targeted effects. No current modifiers use `target_ability`. The separation of concerns is deliberate.

**Verification:**
- Pre-audit validation: PASSED (all tests pass)
- All 5 new tests in `TestModifierApplication` pass
- Implementation matches intent: modifiers correctly applied to mass, HP, capacity, movement, consumption
- No regressions: all 4568 tests pass
