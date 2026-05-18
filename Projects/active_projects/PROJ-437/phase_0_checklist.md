# Phase 0: Read PROJ-436 Container API; survey current transfer UI

**Status:** Complete (2026-05-18)
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

- [x] Read `Container`, `Containable`, `ContainerPolicy`, `ContainableKind` definitions end-to-end
- [x] Read `Container.add()` / `Container.remove()` / `Container.accepts()` / `Container.contents()` signatures and return types
- [x] Read the **extended** `game/core/resources.py:ResourceCatalog` (`all_ids()`, `get()`, the new `get_mass_per_unit()` per PROJ-436 Phase 0) — this is the Core-layer single source of truth; no parallel strategy/UI registry
- [x] Confirm PROJ-436 Phase 6+ has merged — Phase 7 landed at `48a6c0983`; current HEAD `6bd11e444` is post-PROJ-443 cleanup.
- [x] Sketch the `ContainerRef` shape — captured in [design.md §Architecture](design.md#architecture) (target view model shape) + [findings/transfer_ui_migration_map.md §3.2](findings/transfer_ui_migration_map.md#32-gameuiscreenstransfer_controllerpy) (per-entity enumeration). Detailed type design lands in Phase 1a substrate step.

### Task 0.2: Audit existing transfer UI surface [Medium]
**Files:** `game/ui/screens/transfer_dialog.py`, `transfer_controller.py`, `transfer_view_model.py`, `transfer_grid_renderer.py`, `strategy_windows/transfer_dialogs.py`
**Tests:** none — discovery

- [x] Read each file end-to-end
- [x] Enumerate every reference to legacy storage shapes — captured per file in [findings/transfer_ui_migration_map.md §3](findings/transfer_ui_migration_map.md#3-current-transfer-ui-surface-audit-file-by-file). `RESOURCE_TYPES` / `RESOURCE_DISPLAY_NAMES` / `VALID_CARGO_TYPES` are already gone post-Phase-7 (AST-guard pinned).
- [x] Enumerate per-entity accessors — DTOs (`FleetInfo.cargo_resources`, `PlanetInfo.stockpile`, etc.) become `Container.contents()` queries via new `get_containers(id)` accessor (Phase 1a target). Mapped per file in §3.1, §3.2 of the migration map.
- [x] Identify any code paths that special-case kinds — the three-arm split in `transfer_view_model.build_row_data` (resources / passengers / pod rows) is the single special-casing site; Phase 3 collapses to a unified `Container.contents()` walk with per-kind formatting hooks.

### Task 0.3: Produce migration map [Medium]
**File:** `Projects/active_projects/PROJ-437/findings/transfer_ui_migration_map.md` (new)
**Tests:** none — documentation

- [x] Per file, list current legacy refs / target API / phase / test coverage — see [findings/transfer_ui_migration_map.md §3](findings/transfer_ui_migration_map.md#3-current-transfer-ui-surface-audit-file-by-file).
- [x] Flag any reference where the migration is non-obvious — the `fetch_dto` → `ContainerSnapshotInfo` projection path is the one open design choice (new DTO field vs. parallel facade accessor); decision deferred to Phase 1a substrate step. No escalation to PROJ-436 owner required — the substrate API is stable.

### Task 0.4: Resolve open decisions OD1, OD2, OD3 [Simple]
**File:** `decisions.md`

- [x] OD1 → (a) every container per entity (decisions.md 2026-05-18).
- [x] OD2 → (a) cross-kind transfer in one operation (decisions.md 2026-05-18).
- [x] OD3 → (a) per-input mass-remaining preview (decisions.md 2026-05-18).

---

## Phase Completion Checklist
- [x] Migration map committed at `findings/transfer_ui_migration_map.md`
- [x] OD1/OD2/OD3 defaults documented in `decisions.md`
- [x] No production-code changes this phase
- [x] Update status at top to Complete; update plan.md + phase_state.json
