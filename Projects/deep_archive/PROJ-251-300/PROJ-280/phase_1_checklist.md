# Phase 1: Audit duplication across the 5 templates

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-280 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete (verified 2026-04-18)
**Objective:** Quantify the duplication across the 5 templates and identify exactly what should move to the base class. Produce an audit report that drives Phase 2 extraction.

---

## Audit Findings (delegated to Explore agent)

**Real duplication identified:**
1. **`_template_preconditions()`**: All 5 templates duplicate the "ticks > 0" check. 4 templates (Static, Duel, Resource, Propulsion-base) are nearly identical; `PropulsionScenario` adds conditional movement/rotation checks; `ComparisonScenario` has orthogonal A/B validation.
2. **`wire_ships()` pre-amble**: All 5 templates snapshot initial HP/resources and cache ship refs using identical helper calls (`_pre_start_hp`, `_pre_start_resource`). ~8 LOC per template.
3. **`update()`**: Most just call `self._track_tick()` — minimal duplication, deferred.

**Non-duplication (out of scope):**
- `collect_results()`: Wide variance by role count (1-ship PropulsionScenario ~35 LOC vs 2-ship DuelScenario ~50 LOC). No common body.
- Movement policy assignment: Highly divergent flag logic (force_fire binary vs multi-flag thrust/turn logic). Not extractable.

**Concrete scenario overrides:**
- Zero overrides of `_template_preconditions()` — safe to extract
- 6 overrides of `wire_ships()` / `collect_results()` — 2 flagged as BYPASSING template logic (`PropThrustMassRatioScenario`, `ExternalBattleConditionApplied`). These must remain optional.

**Extraction plan (52 LOC saved):**
1. `_common_preconditions()` base method (12 LOC saved)
2. `_snapshot_initial_state()` hook (40 LOC saved)

**Recommended enforcement: Option B (Runtime Sentinel)** — zero invasiveness, first-run detection, clear error message.

---

## Tasks

### Task 1.1: Read all 5 templates [Simple]
**File:** `combat_lab/scenarios/templates.py`
**Tests:** N/A (research)

- [x] Read each template's `__init__`, `wire_ships`, `_template_preconditions`, `collect_results`, and `update` methods
- [x] Note which methods exist on each template (matrix: template × method)
- [x] Note which concrete scenario subclasses override which template methods (look in `combat_lab/scenarios/*_scenarios.py`)

**Notes:** Delegated to an Explore agent to protect main-agent context. Full matrix in `.agent_reports/PROJ-280-audit/template_method_matrix.md`.

### Task 1.2: Diff `_template_preconditions()` across templates [Simple]
**File:** `.agent_reports/PROJ-280-audit/preconditions_diff.md`
**Tests:** N/A

- [x] Side-by-side compare each template's `_template_preconditions()` body
- [x] Highlight common lines vs template-specific lines
- [x] Quantify duplication (lines that are identical or only differ by attribute name)
- [x] Identify which checks belong in `_common_preconditions()`

**Notes:** Identified the "Simulation Ran" (ticks > 0) check as the sole universal assertion. ComparisonScenario's A/B validation is orthogonal and stays template-specific.

### Task 1.3: Diff `wire_ships()` across templates [Simple]
**File:** `.agent_reports/PROJ-280-audit/wire_ships_diff.md`
**Tests:** N/A

- [x] Side-by-side compare each template's `wire_ships()` body
- [x] Highlight common pre-amble (initial state snapshot, role attribute aliasing)
- [x] Highlight template-specific assignments
- [x] Identify the shared pre-amble for extraction into `_snapshot_initial_state()`

**Notes:** The shared phase is "cache role → attribute + snapshot initial HP/resources." Policy assignment stays template-specific (divergent flag logic).

### Task 1.4: Find concrete scenarios that override template internals [Simple]
**File:** `.agent_reports/PROJ-280-audit/concrete_overrides.md`
**Tests:** N/A

- [x] Grep all `combat_lab/scenarios/*_scenarios.py` for `def _template_preconditions`, `def wire_ships`, `def collect_results`
- [x] Document each override with file:line and what it changes
- [x] Flag any overrides that bypass template logic in surprising ways (these will need special migration handling in Phase 4)

**Notes:** Zero overrides of `_template_preconditions` — preconditions extraction is risk-free. 6 overrides of `wire_ships` / `collect_results`; 2 flagged as bypassing template logic. Both are fine with the new `_snapshot_initial_state` hook because it's opt-in.

### Task 1.5: Synthesize extraction targets [Medium]
**File:** `.agent_reports/PROJ-280-audit/extraction_plan.md`
**Tests:** N/A

- [x] List the methods to extract into `TestScenario` base
- [x] For each, specify: signature, body, which templates currently duplicate it
- [x] Identify enforcement mechanism candidates (AST / runtime sentinel / composition API)
- [x] Recommend one for Phase 3 with rationale

**Notes:** Recommended Option B (Runtime Sentinel). Rationale: lowest invasiveness (no class hierarchy changes), first-run detection with clear failure message, covers future templates automatically without new ceremony.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Audit reports saved to `.agent_reports/PROJ-280-audit/`
- [x] Extraction plan drives Phase 2
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2 (extraction)
