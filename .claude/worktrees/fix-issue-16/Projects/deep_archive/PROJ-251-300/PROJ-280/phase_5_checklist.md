# Phase 5: Author guidelines doc + new-template checklist

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-280 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete (verified 2026-04-18)
**Objective:** Document the template authoring rules + extraction points + anti-rebloat checklist so future template authors know the conventions.

---

## Tasks

### Task 5.1: Add "Template Authoring Rules" section to simulation_testing.md [Medium]
**File:** `docs/guides/simulation_testing.md`
**Tests:** N/A

- [x] Added new section `## 2.4 Template Authoring Rules (PROJ-280)` — positioned right before the existing §2.5 Scenario Role Labels section
- [x] Documented the `_template_preconditions` + `_common_preconditions` contract including enforcement mechanism details (runtime sentinel)
- [x] Documented the `_snapshot_initial_state` extraction pattern with canonical code example
- [x] Added anti-rebloat checklist for new templates (5 items)

**Notes:** The doc section is ~80 lines. Deliberately concrete with code examples so authors can copy-paste-modify. Cross-referenced from the base class docstrings.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] New docs section is discoverable (sits alongside the other authoring-rule sections)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to closure
