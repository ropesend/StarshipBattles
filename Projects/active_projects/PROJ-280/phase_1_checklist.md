# Phase 1: Audit duplication across the 5 templates

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-280 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Quantify the duplication across the 5 templates and identify exactly what should move to the base class. Produce an audit report that drives Phase 2 extraction.

---

## Tasks

### Task 1.1: Read all 5 templates [Simple]
**File:** `combat_lab/scenarios/templates.py`
**Tests:** N/A (research)

- [ ] Read each template's `__init__`, `wire_ships`, `_template_preconditions`, `collect_results`, and `update` methods
- [ ] Note which methods exist on each template (matrix: template × method)
- [ ] Note which concrete scenario subclasses override which template methods (look in `combat_lab/scenarios/*_scenarios.py`)

**Notes:**

### Task 1.2: Diff `_template_preconditions()` across templates [Simple]
**File:** `.agent_reports/PROJ-280-audit/preconditions_diff.md` (NEW)
**Tests:** N/A

- [ ] Side-by-side compare each template's `_template_preconditions()` body
- [ ] Highlight common lines vs template-specific lines
- [ ] Quantify duplication (lines that are identical or only differ by attribute name)
- [ ] Identify which checks belong in `_common_preconditions()`

**Notes:**

### Task 1.3: Diff `wire_ships()` across templates [Simple]
**File:** `.agent_reports/PROJ-280-audit/wire_ships_diff.md` (NEW)
**Tests:** N/A

- [ ] Side-by-side compare each template's `wire_ships()` body
- [ ] Highlight common pre-amble (initial state snapshot, role attribute aliasing)
- [ ] Highlight template-specific assignments
- [ ] Identify the shared pre-amble for extraction into `_snapshot_initial_state()`

**Notes:**

### Task 1.4: Find concrete scenarios that override template internals [Simple]
**File:** `.agent_reports/PROJ-280-audit/concrete_overrides.md` (NEW)
**Tests:** N/A

- [ ] Grep all `combat_lab/scenarios/*_scenarios.py` for `def _template_preconditions`, `def wire_ships`, `def collect_results`
- [ ] Document each override with file:line and what it changes
- [ ] Flag any overrides that bypass template logic in surprising ways (these will need special migration handling in Phase 4)

**Notes:**

### Task 1.5: Synthesize extraction targets [Medium]
**File:** `.agent_reports/PROJ-280-audit/extraction_plan.md` (NEW)
**Tests:** N/A

- [ ] List the methods to extract into `TestScenario` base
- [ ] For each, specify: signature, body, which templates currently duplicate it
- [ ] Identify enforcement mechanism candidates (AST / runtime sentinel / composition API)
- [ ] Recommend one for Phase 3 with rationale

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Audit reports saved to `.agent_reports/PROJ-280-audit/`
- [ ] Extraction plan reviewed by user (recommended) before Phase 2 starts
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2 (extraction)
