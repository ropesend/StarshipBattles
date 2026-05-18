# Phase 5: Formula Surface Reduction and Docs Sync

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-439 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Narrow bounded formula usage, keep genuinely dynamic formulas where they are still needed, and update docs/project metadata to match the landed contract.

---

## Tasks

### Task 5.1: Replace bounded formula cases with typed calculators or fixed fields [Complex]
**File:** `data/components.json`, `game/core/formula_evaluator.py`, targeted files under `game/simulation/components/abilities/`
**Tests:** `pytest tests/unit/simulation/components/test_component_stats_calculator.py tests/unit/validation/test_component_definitions.py tests/unit/entities/test_abilities.py`

- [ ] Inventory the remaining formula fields and split them into bounded/static versus genuinely runtime-sensitive categories.
- [ ] Replace bounded/static cases first with typed calculators, enum-like values, or explicit fields.
- [ ] Keep runtime-sensitive formulas only where tests prove the dynamic behavior is still required.
- [ ] Verify: formula-surface reduction does not change the meaning of surviving runtime formulas.

**Notes:** [Filled during implementation]

### Task 5.2: Tighten evaluator assumptions after formula narrowing [Medium]
**File:** `game/core/formula_evaluator.py`, `tests/unit/core/test_formula_evaluator.py`
**Tests:** `pytest tests/unit/core/test_formula_evaluator.py`

- [ ] Remove or tighten evaluator branches that only existed for formula shapes eliminated by Phase 5.1.
- [ ] Add tests for any newly forbidden formula shapes or names.
- [ ] Verify: the evaluator still supports the explicitly retained runtime and load-time formula categories.
- [ ] Verify: no earlier phase silently re-expanded the free-form formula surface.

**Notes:** [Filled during implementation]

### Task 5.3: Sync docs and project metadata to the landed contract [Medium]
**File:** `docs/03_CONVENTIONS.md`, `docs/guides/component_system.md`, `docs/systems/resource_system.md`, `docs/systems/ability_reference.md`, `manifest.md`, `design.md`, `decisions.md`
**Tests:** `python Tools/validate_designs/validate_designs.py`

- [ ] Update docs to describe the new schema-backed content contract, registrar pattern, and narrowed formula rules.
- [ ] Update project metadata files so the final touched-file set and follow-up items are accurate.
- [ ] Keep out-of-scope items explicitly deferred rather than letting docs imply broader architectural work.
- [ ] Verify: docs and project metadata match the implemented behavior before audit begins.

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to indicate audit readiness
