# Phase 4: Typed Registrars and Loader Models

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-439 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Reduce the highest-churn manual registry surfaces and normalize raw content through typed intermediate models where that increases safety without replacing the runtime object model.

---

## Tasks

### Task 4.1: Replace the manual ability registry with a typed registrar [Complex]
**File:** `game/simulation/components/abilities/__init__.py`, `game/simulation/components/abilities/base.py`, new `game/simulation/components/abilities/registry.py`
**Tests:** `pytest tests/unit/simulation/components/abilities tests/unit/simulation/components/test_ability_manager.py`

- [ ] Introduce a typed registrar API for ability registration while preserving the public `create_ability()` and `get_ability_default_scope()` behavior.
- [ ] Preserve current support for list-valued ability payloads and deferred formula-based ability creation.
- [ ] Add contract tests for duplicate registration, missing metadata, and stable default-scope lookup.
- [ ] Verify: callers outside the abilities package do not need to know how registration is implemented.

**Notes:** [Filled during implementation]

### Task 4.2: Add typed intermediate models for the highest-churn loader inputs [Complex]
**File:** new `game/core/content_models.py`, `game/core/resources.py`, `game/strategy/systems/design_repository.py`, `game/ui/services/design_loader_adapter.py`
**Tests:** `pytest tests/unit/core/test_content_models.py tests/unit/strategy/design_repository/test_load_design_data.py tests/unit/ui/services/test_design_loader_adapter.py`

- [ ] Introduce typed intermediate models for the first content families where raw dict handling is causing the most drift.
- [ ] Normalize loaded payloads through those models before runtime object materialization.
- [ ] Keep the typed models at the content-contract layer rather than turning them into live gameplay objects.
- [ ] Verify: the typed models improve error messages and remove at least one hand-written dict-shape check from each targeted loader.

**Notes:** [Filled during implementation]

### Task 4.3: Expand registrar/model coverage tests [Medium]
**File:** new `tests/unit/simulation/components/abilities/test_registry_contract.py`, new `tests/unit/core/test_content_models.py`, `manifest.md`
**Tests:** `pytest tests/unit/simulation/components/abilities/test_registry_contract.py tests/unit/core/test_content_models.py`

- [ ] Add focused tests for registrar uniqueness, registration ordering, and public-factory compatibility.
- [ ] Add typed-model tests for valid normalization, invalid field coercion, and error surfacing.
- [ ] Update `manifest.md` with any new helper/model/test files added in this phase.
- [ ] Verify: Phase 4 tests characterize behavior that later cleanup projects can safely depend on.

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
