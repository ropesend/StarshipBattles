# Phase 2: Schema Assets and Shared Validation Helper

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-439 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Land the first shared Core-layer validation helper and the first production schema assets without changing runtime loader behavior yet.

---

## Tasks

### Task 2.1: Add the shared content-validation helper [Complex]
**File:** `game/core/json_utils.py`, `requirements.txt`, `requirements-dev.txt`, new `game/core/content_validation.py`
**Tests:** `pytest tests/unit/core/test_content_validation.py tests/unit/core/test_pure_loaders.py`

- [ ] Introduce one shared validation helper in the Core layer so startup, strategy loaders, and tools can all call the same API.
- [ ] Keep the helper separate from the JSON file-reading helpers in `json_utils.py` while reusing the existing load flow.
- [ ] If a runtime dependency is adopted, add it in exactly the required requirements file(s) and document the reason in `decisions.md`.
- [ ] Verify: the helper supports both fail-fast and collect-errors modes needed by the chosen boundary behavior.

**Notes:** [Filled during implementation]

### Task 2.2: Author first-pass production schemas [Complex]
**File:** new `data/schemas/resources.schema.json`, `data/schemas/modifiers.schema.json`, `data/schemas/components.schema.json`, `data/schemas/design.schema.json`, `data/schemas/race.schema.json`
**Tests:** `pytest tests/unit/core/test_content_schemas.py tests/unit/core/resources_registry/test_loading.py tests/unit/quickstart/test_quickstart_designs.py`

- [ ] Create production schema files for resources, modifiers, components, designs, and races.
- [ ] Encode current live shapes rather than aspirational future shapes, including bool/scalar/dict/list/formula-string payloads where they are already legal.
- [ ] Reuse the current modifier-schema rules as a reference rather than creating conflicting conventions.
- [ ] Verify: the shipped production data validates cleanly against the new schemas.

**Notes:** [Filled during implementation]

### Task 2.3: Add helper and schema contract tests [Medium]
**File:** new `tests/unit/core/test_content_validation.py`, new `tests/unit/core/test_content_schemas.py`, `manifest.md`
**Tests:** `pytest tests/unit/core/test_content_validation.py tests/unit/core/test_content_schemas.py`

- [ ] Add focused unit tests for helper success/failure behavior, schema loading, and representative invalid payloads.
- [ ] Pin duplicate-key, missing-required-field, and wrong-type failures for the first schema set.
- [ ] Update `manifest.md` with every new helper/schema/test file created in this phase.
- [ ] Verify: Phase 2 tests do not depend on runtime gameplay state or unrelated registries.

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
