# Phase 1: Call-Site Audit (Read-Only)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-276 1`
> 2. Only proceed if output shows PASSED

**Status:** Complete — with discrepancy flagged (see findings)
**Objective:** Produce a complete per-site audit of all 47 production occurrences. Classify each as READ or WRITE. Enables Phase 2+ TDD targeting.

---

## Tasks

### Task 1.1: Grep + file-by-file enumeration [Simple]
**File:** `findings/component_damage_callsite_audit.md` (NEW)
**Tests:** N/A

- [x] Run `grep -n "component_damage" game/strategy/data/ship_instance.py game/strategy/services/ship_stats_calculator.py game/strategy/data/ship_instance_bridge.py game/strategy/data/ship_instance_serializer.py game/strategy/data/component_state.py game/strategy/combat/post_battle_hook.py game/simulation/entities/ship_design_stats.py`
- [x] For each occurrence: record file path, line number, code snippet
- [x] Write to `findings/component_damage_callsite_audit.md`

**Notes:** 45 production occurrences (plan said ~47; actual is 45 in `game/` + 1 fixture). Full table and per-file detail in findings.

### Task 1.2: Classify READ vs WRITE per site [Medium]
**File:** `findings/component_damage_callsite_audit.md`
**Tests:** N/A

- [x] For each occurrence classified
- [x] Tabulated per file
- [x] Totals: 13 DEF / 26 READ / 6 WRITE
- [x] Checked against expected pattern

**Notes:** Expectation "stat_calc all READs, post_battle all WRITEs" holds, but **major caveat**: `ship_stats_calculator.py` is dead in production — see Task 1.1 notes + findings `Dead Module Finding` section.

### Task 1.3: Verify `ComponentState` API sufficiency [Medium]
**File:** `game/strategy/data/component_state.py`
**Tests:** N/A (read-only)

- [x] Read `ComponentState` dataclass end-to-end
- [x] Confirm fields: `current_hp` (present), `is_destroyed` (derive from current_hp <= 0), `is_operational` (derive from is_active + current_hp > 0)
- [x] Confirm key helper exists: `component_state_key(component_id, instance_index) -> str` at L23
- [x] No gaps found for current live-code needs — see `findings/component_state_api_gaps.md`
- [x] No Phase 1.5 extension needed

**Notes:** API is sufficient. Reads currently done via `component_damage.get(comp_id)` can be restated as `components[component_state_key(comp_id, idx)].current_hp` with a fallback to `max_hp` when the key is missing.

### Task 1.4: Identify "how does the caller get instance_index?" [Medium]
**File:** Multiple — research
**Tests:** N/A

- [x] Researched: the canonical pattern is a per-`component_id` counter dict, used while walking `ship.layers`
- [x] Three existing implementations verified (ship_instance.py L72-88, ship_instance_bridge.py L91-103 + L150-167, post_battle_hook.py receives index from outcome)
- [x] Pattern documented in `findings/instance_index_pattern.md`
- [x] No helper needed — 4-line pattern, appears in only 4 places total

**Notes:** `instance_index` is zero-based, counted per `component_id` (not per layer, not globally). Only live-production migration site is `ship_design_stats.py::calculate_design_stats` — small enough to inline.

### Task 1.5: Review test impact [Simple]
**File:** `findings/component_damage_test_audit.md` (NEW)
**Tests:** N/A

- [x] 29 test occurrences across 14 files enumerated
- [x] Classified: 4 DELETE, 1 RENAME, 11 REWRITE
- [x] Also: entire `tests/unit/strategy/ship_stats/*` directory becomes deletable if dead module deleted
- [x] Verified: no test asserts lossy-flatten behavior as a feature

**Notes:** Phase 7 test migration is mechanical. Zero tests encode the lossy-flatten behavior as a contract — good news.

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update plan.md
- [x] Run `python Projects/scripts/validate_phase.py PROJ-276 1`

---

## DISCREPANCY FLAGGED — User sign-off requested before Phase 2

`game/strategy/services/ship_stats_calculator.py` has zero production
importers. Full grep trace in
`findings/component_damage_callsite_audit.md`. The plan's "hardest
migration … stat-calc hot path" description of that file is incorrect.

Proposed scope change (clean-sheet per CLAUDE.md Rule 3):

- **Delete** `game/strategy/services/ship_stats_calculator.py` outright
  (Phase 2 becomes "delete dead module" + its tests in
  `tests/unit/strategy/ship_stats/*`).
- **Migrate** the real live hot path `ship_design_stats.py::calculate_design_stats`
  (4 `component_damage` sites) as Phase 2b.
- Phases 3–8 proceed largely as specified, but with a smaller and more
  accurate Phase 2.
