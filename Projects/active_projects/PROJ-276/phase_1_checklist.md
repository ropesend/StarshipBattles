# Phase 1: Call-Site Audit (Read-Only)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-276 1`
> 2. Only proceed if output shows PASSED

**Status:** Not Started
**Objective:** Produce a complete per-site audit of all 47 production occurrences. Classify each as READ or WRITE. Enables Phase 2+ TDD targeting.

---

## Tasks

### Task 1.1: Grep + file-by-file enumeration [Simple]
**File:** `findings/component_damage_callsite_audit.md` (NEW)
**Tests:** N/A

- [ ] Run `grep -n "component_damage" game/strategy/data/ship_instance.py game/strategy/services/ship_stats_calculator.py game/strategy/data/ship_instance_bridge.py game/strategy/data/ship_instance_serializer.py game/strategy/data/component_state.py game/strategy/combat/post_battle_hook.py game/simulation/entities/ship_design_stats.py`
- [ ] For each occurrence: record file path, line number, code snippet
- [ ] Write to `findings/component_damage_callsite_audit.md`

**Notes:**

### Task 1.2: Classify READ vs WRITE per site [Medium]
**File:** `findings/component_damage_callsite_audit.md`
**Tests:** N/A

- [ ] For each occurrence:
  - READ if it accesses `instance.component_damage.get(key)` / `[key]` / `in` for a decision
  - WRITE if it sets `instance.component_damage[key] = value` / `.update(...)` / `.clear()`
  - DEF if it's a field definition or docstring
- [ ] Tabulate results: `ship_stats_calculator.py has N READS, 0 WRITES`
- [ ] Total READs and total WRITEs across production
- [ ] Expected: stat_calc all READs; post_battle_hook all WRITEs (+ 1 READ for update); others mixed

**Notes:**

### Task 1.3: Verify `ComponentState` API sufficiency [Medium]
**File:** `game/strategy/data/component_state.py`
**Tests:** N/A (read-only)

- [ ] Read `ComponentState` dataclass end-to-end
- [ ] Confirm fields: `current_hp`, `is_destroyed` (or derive from hp), `is_operational`
- [ ] Confirm key helper exists: `component_state_key(component_id, instance_index) -> str`
- [ ] If any read-site in `ship_stats_calculator.py` needs data NOT present in `ComponentState`, document in `findings/component_state_api_gaps.md`
- [ ] If gaps exist, add a Phase 1.5 task to extend ComponentState before starting Phase 2

**Notes:**

### Task 1.4: Identify "how does the caller get instance_index?" [Medium]
**File:** Multiple — research
**Tests:** N/A

- [ ] `ship_stats_calculator.py` READ sites use `instance.component_damage.get(component_id)` — they don't care about instance_index today (lossy). To migrate, each read site must know which component instance it's referring to.
- [ ] Research: how does stat_calc iterate components? Usually it walks ship's layers, which yields component *instances* (with order). Instance index corresponds to iteration order.
- [ ] Document the canonical pattern for getting `component_state_key` from an iteration context
- [ ] If the pattern is complex, propose a helper method (e.g., `ShipInstance.get_component_hp(component_id, instance_index) -> int`)
- [ ] Write findings

**Notes:**

### Task 1.5: Review test impact [Simple]
**File:** `findings/component_damage_test_audit.md` (NEW)
**Tests:** N/A

- [ ] Run `grep -n "component_damage" tests/` to find all 29 test occurrences
- [ ] Classify each: is this test asserting the lossy flattening behavior (needs REWRITE), or just happens to use the field name (simple rename)?
- [ ] Enumerate in audit file — Phase 7 will process

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update plan.md
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-276 1`
