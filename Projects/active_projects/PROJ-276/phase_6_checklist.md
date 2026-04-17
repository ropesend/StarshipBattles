# Phase 6: Delete Field + Dual-Write

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-276 6`

**Status:** Not Started
**Objective:** The pass-point. Remove `component_damage` field from `ShipInstance`. Delete dual-write in post_battle_hook. Full test suite must be green.

---

## Tasks

### Task 6.1: Pre-check — confirm zero remaining production reads/writes [Simple]
**File:** N/A
**Tests:** Grep

- [ ] Run `grep -rn "component_damage" game/strategy/services/ game/strategy/data/ship_instance_bridge.py game/simulation/entities/ship_design_stats.py game/strategy/data/ship_instance_serializer.py` — ZERO results expected
- [ ] If any remain, go back and finish migration before proceeding

**Notes:**

### Task 6.2: Delete post_battle_hook dual-write [Simple]
**File:** `game/strategy/combat/post_battle_hook.py`
**Tests:** `pytest tests/unit/strategy/combat/test_post_battle_hook.py -v`

- [ ] Locate L155-162 (per audit — may have shifted)
- [ ] Delete the `component_damage` rebuild loop — keep only the `instance.components = new_components` write at L152
- [ ] Run hook tests — pass (tests may need update in Phase 7 if they verified dual-write)

**Notes:**

### Task 6.3: Delete the field from ShipInstance [Medium]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/ship_instance/ -n 12`

- [ ] Remove `component_damage: Dict[str, int] = field(default_factory=dict)` at L113
- [ ] Remove surrounding comment about "legacy; single-instance granularity"
- [ ] Update the `components` field docstring — remove "kept in sync for backwards-compatible stat calculations during the PROJ-269 transition"; instead write "Authoritative source for battle round-trip and stat calculation (PROJ-269 Phase 2 closed by PROJ-276)."
- [ ] Run ship_instance tests — any failures indicate a missed call site or test to update in Phase 7

**Notes:**

### Task 6.4: Full-repo grep check [Simple]
**File:** N/A
**Tests:** Grep

- [ ] Run `grep -rn "component_damage" game/` — ZERO production results expected
- [ ] Run `grep -rn "component_damage" docs/` — document-only references; Phase 8 handles docs
- [ ] Run `grep -rn "component_damage" tests/` — test-only references; Phase 7 handles tests
- [ ] Run `grep -rn "component_damage" Projects/` — project docs may reference; leave alone

**Notes:**

### Task 6.5: Full test suite [Medium]
**File:** N/A
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Full pytest sharded runner
- [ ] Some tests will FAIL (tests that use `component_damage` attribute) — that's expected; Phase 7 fixes them
- [ ] Production code should have ZERO failures
- [ ] Document the list of failing tests as Phase 7 input

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update plan.md
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-276 6`
- [ ] **After this phase, `component_damage` does not exist anywhere in production code.**
