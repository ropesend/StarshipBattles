# Phase 4: Migrate `ship_design_stats.py` (4 sites)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-276 4`

**Status:** Not Started
**Objective:** Small migration — 4 sites. Mirror the Phase 2 pattern.

---

## Tasks

### Task 4.1: Audit the 4 sites [Simple]
**File:** `game/simulation/entities/ship_design_stats.py`
**Tests:** N/A

- [ ] Per Phase 1 audit: identify the 4 sites
- [ ] Verify they're all READs (design stats are computed, not mutated)
- [ ] Understand what design-level aggregation they perform

**Notes:**

### Task 4.2: Migrate per-site [Medium]
**File:** `game/simulation/entities/ship_design_stats.py`
**Tests:** `pytest tests/unit/simulation/systems/test_ship_design_stats.py -v`

- [ ] For each site: migrate to `components` dict
- [ ] Keep single-instance test baseline green
- [ ] Run parity tests — no regression

**Notes:**

### Task 4.3: Verify integration [Simple]
**File:** N/A
**Tests:** `pytest tests/unit/simulation/systems/test_ship_design_stats.py tests/integration/ -n 12`

- [ ] Full run green
- [ ] `grep -n "component_damage" game/simulation/entities/ship_design_stats.py` returns ZERO

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update plan.md
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-276 4`
