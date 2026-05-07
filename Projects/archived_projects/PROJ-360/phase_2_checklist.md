# Phase 2: Extract Domain Contributors Behind Current API

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-360 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** phase_1
**Review Mode:** standard
**Files (planned):** game/simulation/entities/ship_stats.py, game/simulation/entities/stat_contributors/{__init__,movement,defense,weapons,command,launch}.py
**Objective:** Extract per-domain stat contributors from `calculate()` while preserving its public API and bit-identical output. Mechanical extraction only — no semantic changes (those land in Phase 3).

---

## Tasks

### Task 2.1: Map current `calculate()` phases to stat domains [Simple]
**File:** Read-only audit of `game/simulation/entities/ship_stats.py`
**Tests:** None

- [x] Walk every block in `calculate()` (lines 111-643) and tag it by domain: movement / defense / weapons / command / launch / resource-cost / phase-coordination
- [x] Note any cross-domain dependencies (e.g., damage check must run before resource allocation)
- [x] Document the map in [decisions.md](decisions.md) — this is the extraction plan

**Notes:**

---

### Task 2.2: Define the contributor protocol [Simple]
**File:** `game/simulation/entities/stat_contributors/__init__.py` (new)
**Tests:** `pytest tests/unit/simulation/entities/stat_contributors/ -v`

- [x] `StatContributor` protocol: `apply(ship: Ship, context: CalculationContext) -> None`
- [x] `CalculationContext`: shared state passed between contributors (component_pool, available_crew, available_life_support, etc.) — what `calculate()` currently keeps as locals
- [x] Module-level registry / list of contributors with explicit ordering (mutation order matters)

**Notes:**

---

### Task 2.3: Extract Movement contributor [Medium]
**File:** `game/simulation/entities/stat_contributors/movement.py` (new)
**Tests:** `pytest tests/unit/simulation/entities/test_ship_stats_golden.py tests/unit/simulation/entities/stat_contributors/test_movement.py -v`

- [x] Move thrust / turn_speed / strategic_movement / drag accumulation into the contributor
- [x] `calculate()` calls the contributor at the same point in its phase order
- [x] Golden tests STILL PASS bit-for-bit
- [x] New domain test verifies movement-only behavior in isolation

**Notes:**

---

### Task 2.4: Extract Defense contributor [Medium]
**File:** `game/simulation/entities/stat_contributors/defense.py` (new)
**Tests:** Same as 2.3

- [x] Shields, regen, repair, armor (emissive + shield-regenerating) into the contributor
- [x] Golden tests PASS bit-for-bit

**Notes:**

---

### Task 2.5: Extract Weapons contributor [Medium]
**File:** `game/simulation/entities/stat_contributors/weapons.py` (new)
**Tests:** Same

- [x] Weapon-derived stats into the contributor
- [x] If PROJ-359 has landed: consume `AttackRequest` family metadata where natural; if not, leave a TODO and use the legacy lookup
- [x] Golden tests PASS bit-for-bit

**Notes:**

---

### Task 2.6: Extract Command contributor [Medium]
**File:** `game/simulation/entities/stat_contributors/command.py` (new)
**Tests:** Same

- [x] Command priority, engine priority, multiplex tracking into the contributor
- [x] Golden tests PASS bit-for-bit

**Notes:**

---

### Task 2.7: Extract Launch contributor [Medium]
**File:** `game/simulation/entities/stat_contributors/launch.py` (new)
**Tests:** Same

- [x] Hangar capacity, fighters_per_wave, launch_cycle, fighter_size_cap into the contributor
- [x] Golden tests PASS bit-for-bit

**Notes:**

---

### Task 2.8: `ship_stats.py` LOC under 500 [Simple]
**File:** `game/simulation/entities/ship_stats.py`

- [x] After all extractions, `ship_stats.py` is the coordinator only
- [x] LOC < 500 (per AGENTS.md convention)
- [x] If still over: surface to user — may indicate a contributor is undersized or a phase wasn't extracted

**Notes:**

---

### Task 2.9: Sharded green [Medium]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Full sharded suite passes
- [x] Pass count = Phase 1 baseline + new domain tests

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
