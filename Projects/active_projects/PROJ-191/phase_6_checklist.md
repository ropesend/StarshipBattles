# Phase 6: Document & Audit [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-191 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add brief comments explaining WHY remaining getattr patterns are intentional. Final audit.

---

## Tasks

### Task 6.1: Document comp_def dual-format patterns (~12 instances) [Simple]
**Files:** `game/strategy/services/ship_stats_calculator.py`, `game/strategy/engine/harvesting_engine.py`, `game/strategy/engine/resupply_engine.py`, `game/strategy/engine/resource_management_engine.py`, `game/strategy/services/component_inspector.py`, `game/strategy/data/planet.py`
**Tests:** N/A (comment-only changes)

- [ ] Add `# comp_def can be dict (JSON data) or Component object — getattr intentional` comment to each remaining getattr on comp_def.abilities / comp_def.type_str
- [ ] `ship_stats_calculator.py`: Document L192, L331, L339, L358
- [ ] `harvesting_engine.py`: Document L74, L213
- [ ] `resupply_engine.py`: Document L159
- [ ] `resource_management_engine.py`: Document L141
- [ ] `component_inspector.py`: Document L38
- [ ] `planet.py`: Document L93

**Notes:**

### Task 6.2: Final audit [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run `grep -rn "getattr\|hasattr" game/strategy/ --include="*.py"` — count remaining instances
- [ ] Verify all remaining instances are one of: comp_def dual-format (documented), from_dict deserialization, game_session Enum checks
- [ ] Run `pytest tests/ -n 12` — verify baseline (12699+ passed, 6 pre-existing failures from PROJ-189)
- [ ] Verify test count has not decreased from baseline
- [ ] Update plan.md Current State with completion status

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/ -n 12` — full suite matches baseline
- [ ] All remaining getattr/hasattr have explanatory comments
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table — all rows Complete
- [ ] Update plan.md Current State: Project Complete
