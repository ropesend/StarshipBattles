# Phase 2: Extract Domain Contributors Behind Current API

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-360 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** phase_1
**Review Mode:** standard
**Files (planned):** game/simulation/entities/ship_stats.py, game/simulation/entities/stat_contributors/{__init__,movement,defense,weapons,command,launch}.py
**Objective:** Extract per-domain stat contributors from `calculate()` while preserving its public API and bit-identical output. Mechanical extraction only — no semantic changes (those land in Phase 3).

---

## Tasks

### Task 2.1: Map current `calculate()` phases to stat domains [Simple]
**File:** Read-only audit of `game/simulation/entities/ship_stats.py`
**Tests:** None

- [ ] Walk every block in `calculate()` (lines 111-643) and tag it by domain: movement / defense / weapons / command / launch / resource-cost / phase-coordination
- [ ] Note any cross-domain dependencies (e.g., damage check must run before resource allocation)
- [ ] Document the map in [decisions.md](decisions.md) — this is the extraction plan

**Notes:**

---

### Task 2.2: Define the contributor protocol [Simple]
**File:** `game/simulation/entities/stat_contributors/__init__.py` (new)
**Tests:** `pytest tests/unit/simulation/entities/stat_contributors/ -v`

- [ ] `StatContributor` protocol: `apply(ship: Ship, context: CalculationContext) -> None`
- [ ] `CalculationContext`: shared state passed between contributors (component_pool, available_crew, available_life_support, etc.) — what `calculate()` currently keeps as locals
- [ ] Module-level registry / list of contributors with explicit ordering (mutation order matters)

**Notes:**

---

### Task 2.3: Extract Movement contributor [Medium]
**File:** `game/simulation/entities/stat_contributors/movement.py` (new)
**Tests:** `pytest tests/unit/simulation/entities/test_ship_stats_golden.py tests/unit/simulation/entities/stat_contributors/test_movement.py -v`

- [ ] Move thrust / turn_speed / strategic_movement / drag accumulation into the contributor
- [ ] `calculate()` calls the contributor at the same point in its phase order
- [ ] Golden tests STILL PASS bit-for-bit
- [ ] New domain test verifies movement-only behavior in isolation

**Notes:**

---

### Task 2.4: Extract Defense contributor [Medium]
**File:** `game/simulation/entities/stat_contributors/defense.py` (new)
**Tests:** Same as 2.3

- [ ] Shields, regen, repair, armor (emissive + shield-regenerating) into the contributor
- [ ] Golden tests PASS bit-for-bit

**Notes:**

---

### Task 2.5: Extract Weapons contributor [Medium]
**File:** `game/simulation/entities/stat_contributors/weapons.py` (new)
**Tests:** Same

- [ ] Weapon-derived stats into the contributor
- [ ] If PROJ-359 has landed: consume `AttackRequest` family metadata where natural; if not, leave a TODO and use the legacy lookup
- [ ] Golden tests PASS bit-for-bit

**Notes:**

---

### Task 2.6: Extract Command contributor [Medium]
**File:** `game/simulation/entities/stat_contributors/command.py` (new)
**Tests:** Same

- [ ] Command priority, engine priority, multiplex tracking into the contributor
- [ ] Golden tests PASS bit-for-bit

**Notes:**

---

### Task 2.7: Extract Launch contributor [Medium]
**File:** `game/simulation/entities/stat_contributors/launch.py` (new)
**Tests:** Same

- [ ] Hangar capacity, fighters_per_wave, launch_cycle, fighter_size_cap into the contributor
- [ ] Golden tests PASS bit-for-bit

**Notes:**

---

### Task 2.8: `ship_stats.py` LOC under 500 [Simple]
**File:** `game/simulation/entities/ship_stats.py`

- [ ] After all extractions, `ship_stats.py` is the coordinator only
- [ ] LOC < 500 (per AGENTS.md convention)
- [ ] If still over: surface to user — may indicate a contributor is undersized or a phase wasn't extracted

**Notes:**

---

### Task 2.9: Sharded green [Medium]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Full sharded suite passes
- [ ] Pass count = Phase 1 baseline + new domain tests

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
