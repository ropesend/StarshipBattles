# Phase 3: Tooling and Load-Pipeline Enforcement

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-439 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Thread the new validation layer through runtime and tool entry points so malformed content is rejected or reported at the correct boundary.

---

## Tasks

### Task 3.1: Integrate validation into registry and startup loaders [Complex]
**File:** `game/core/resources.py`, `game/core/registry.py`, `game/simulation/components/component_loader.py`, `game/simulation/entities/ship_loader.py`, `game/simulation/services/registry_loader.py`, `game/app_bootstrap.py`
**Tests:** `pytest tests/unit/core/resources_registry/test_loading.py tests/unit/core/test_pure_loaders.py tests/unit/simulation/components/test_component_loader.py tests/unit/test_app_bootstrap_invariants.py`

- [ ] Validate raw resources/components/modifiers/vehicle-class payloads before instantiating runtime objects or hydrating registries.
- [ ] Preserve the existing Core -> Simulation dependency direction while threading the shared helper into Simulation-owned loaders.
- [ ] Convert boundary behavior to the chosen strict/warn policy from Phase 1 instead of letting each loader keep ad hoc semantics.
- [ ] Verify: invalid fixture data produces deterministic, tested loader outcomes.

**Notes:** [Filled during implementation]

### Task 3.2: Integrate validation into design and UI-facing load paths [Medium]
**File:** `Tools/validate_designs/validate_designs.py`, `game/strategy/systems/design_repository.py`, `game/ui/services/design_loader_adapter.py`
**Tests:** `pytest tests/unit/strategy/design_repository/test_load_design_data.py tests/unit/ui/services/test_design_loader_adapter.py tests/unit/quickstart/test_quickstart_designs.py`

- [ ] Make the design-validation tool consume the shared schema/helper layer instead of validating only downstream object behavior.
- [ ] Validate on-demand design loads in `DesignRepository.load_design_data()` before they enter strategy or UI consumers.
- [ ] Ensure the UI adapter surfaces actionable validation failures without inventing fallback data.
- [ ] Verify: quickstart and design-loader tests still pass with the new behavior.

**Notes:** [Filled during implementation]

### Task 3.3: Add integration/characterization coverage for boundary behavior [Medium]
**File:** new `tests/integration/content/test_loader_validation_boundaries.py`, `manifest.md`
**Tests:** `pytest tests/integration/content/test_loader_validation_boundaries.py`

- [ ] Add integration coverage for one startup-style load, one registry reload, and one on-demand design load using intentionally bad input fixtures.
- [ ] Pin the exact behavior chosen in Phase 1 so future loader changes do not silently change strictness.
- [ ] Update `manifest.md` with any new integration fixture/test files created in this phase.
- [ ] Verify: the characterization tests fail if a loader regresses to silently accepting invalid content.

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
