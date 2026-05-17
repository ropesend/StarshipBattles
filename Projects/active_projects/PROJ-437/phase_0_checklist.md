# Phase 0: Read PROJ-436 Container API; survey current transfer UI

**Status:** Not Started
**Depends on:** none (but recommend waiting until PROJ-436 Phase 6 is stable)
**Review Mode:** lightweight
**Files (planned):**
- `Projects/active_projects/PROJ-437/findings/transfer_ui_migration_map.md` (new)

**Objective:** Research-only phase. Read the `Container` / `Containable` / `ContainerPolicy` API as it currently stands in PROJ-436's landed phases. Audit the current transfer UI (`transfer_dialog.py` + `transfer_controller.py` + `transfer_view_model.py` + `transfer_grid_renderer.py` + `strategy_windows/transfer_dialogs.py`). Produce a per-file migration map documenting which view-model field / controller event / renderer path consumes which legacy storage shape, and what it migrates to under the unified API. No production-code changes this phase.

---

## Tasks

### Task 0.1: Read PROJ-436 Container API [Simple]
**Files:** `game/strategy/data/container.py`, `game/strategy/data/containable.py`, `game/core/resources.py`, `data/resources.json`
**Tests:** none — discovery

- [ ] Read `Container`, `Containable`, `ContainerPolicy`, `ContainableKind` definitions end-to-end
- [ ] Read `Container.add()` / `Container.remove()` / `Container.accepts()` / `Container.contents()` signatures and return types
- [ ] Read the **extended** `game/core/resources.py:ResourceCatalog` (`all_ids()`, `get()`, the new `get_mass_per_unit()` per PROJ-436 Phase 0) — this is the Core-layer single source of truth; no parallel strategy/UI registry
- [ ] Confirm PROJ-436 Phase 6+ has merged (or document which phase the API derives from if reading mid-implementation)
- [ ] Sketch the `ContainerRef` shape — what minimum data does the UI need to address a specific container? (suggested: `(container_id, owning_entity_label, allowed_kinds)`)

### Task 0.2: Audit existing transfer UI surface [Medium]
**Files:** `game/ui/screens/transfer_dialog.py`, `transfer_controller.py`, `transfer_view_model.py`, `transfer_grid_renderer.py`, `strategy_windows/transfer_dialogs.py`
**Tests:** none — discovery

- [ ] Read each file end-to-end
- [ ] Enumerate every reference to legacy storage shapes (`cargo_contents`, `stockpile`, `_fleet_resource_pool`, `consumable_levels`, `bay_inventory.bay` raw accesses, `RESOURCE_TYPES` constant, `VALID_CARGO_TYPES` references)
- [ ] Enumerate every reference to per-entity accessors (`Fleet.cargo_aggregate`, `Planet.get_stockpile`, etc.) — note which become `Container.contents()` queries
- [ ] Identify any code paths that special-case kinds (resources vs items vs population currently)

### Task 0.3: Produce migration map [Medium]
**File:** `Projects/active_projects/PROJ-437/findings/transfer_ui_migration_map.md` (new)
**Tests:** none — documentation

- [ ] Per file, list:
  - Current legacy references (file:line)
  - Target Container API call
  - Phase that migrates it (1, 2, 3, or 4)
  - Test coverage that locks in current behavior (so we know what stays green)
- [ ] Flag any reference where the migration is non-obvious — escalate to PROJ-436 owner for API clarification

### Task 0.4: Resolve open decisions OD1, OD2, OD3 [Simple]
**File:** `decisions.md`

- [ ] OD1 (source/dest enumeration scope): default (a) every container; if Task 0.2 audit suggests (b) or (c) is cleaner, escalate
- [ ] OD2 (cross-kind transfer in one operation): default (a) preserve existing UX
- [ ] OD3 (mass-remaining preview granularity): default (a) per-input; profile if `Container.add()` validation is expensive

---

## Phase Completion Checklist
- [ ] Migration map committed at `findings/transfer_ui_migration_map.md`
- [ ] OD1/OD2/OD3 defaults documented in `decisions.md`
- [ ] No production-code changes this phase
- [ ] Update status at top to Complete; update plan.md + phase_state.json
