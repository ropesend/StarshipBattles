# Phase 1: Inventory Content Contracts and Validation Boundaries

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-439 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Build the authoritative inventory of production content surfaces, load entry points, formula-bearing fields, and boundary-specific failure semantics before any schema helper or runtime validation code is added.

---

## Tasks

### Task 1.1: Inventory authoritative production content inputs [Medium]
**File:** `data/components.json`, `data/modifiers.json`, `data/resources.json`, `data/designs/`, `data/races/`
**Tests:** `python Tools/validate_designs/validate_designs.py`; `pytest tests/unit/quickstart/test_quickstart_designs.py tests/unit/core/resources_registry/test_loading.py`

- [ ] Record which production files are authoritative game inputs versus test-only or tool-only content.
- [ ] Enumerate the fields that currently carry formula strings and mixed-shape payloads, especially under `components[*].abilities`.
- [ ] Verify which content families already have local validation (for example `validate_modifier_v2`) and which have none.
- [ ] Verify: `design.md` captures the inventory and notes the highest-risk schema surfaces.

**Notes:** [Filled during implementation]

### Task 1.2: Map startup, reload, and on-demand loader seams [Medium]
**File:** `game/core/resources.py`, `game/simulation/components/component_loader.py`, `game/simulation/entities/ship_loader.py`, `game/simulation/services/registry_loader.py`, `game/app_bootstrap.py`, `game/strategy/systems/design_repository.py`, `game/ui/services/design_loader_adapter.py`
**Tests:** `pytest tests/unit/test_app_bootstrap_invariants.py tests/unit/core/test_pure_loaders.py tests/unit/strategy/design_repository/test_load_design_data.py tests/unit/ui/services/test_design_loader_adapter.py`

- [ ] Classify each loader by boundary: startup-only, registry reload, tool/validation, on-demand design load, or UI adapter.
- [ ] Capture the current behavior for malformed input at each seam: hard fail, warn and continue, empty fallback, or cache reuse.
- [ ] Identify the minimal shared validation API that all of these call sites can use without introducing new layer violations.
- [ ] Verify: `design.md` and `decisions.md` record the chosen validation entry points with file references.

**Notes:** [Filled during implementation]

### Task 1.3: Decide schema engine and boundary behavior before code lands [Medium]
**File:** `design.md`, `decisions.md`, `manifest.md`
**Tests:** None - planning/documentation checkpoint

- [ ] Decide whether schema consumption uses a new runtime dependency or an in-repo helper approach before Phase 2 edits `requirements.txt` or adds Core helpers.
- [ ] Decide which malformed content should hard-fail startup versus warn and continue at design-tool or reload boundaries.
- [ ] Update `manifest.md` if this decision implies new helper files or new dependency-file touches.
- [ ] Verify: no Phase 2 work begins until these decisions are explicitly logged.

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
