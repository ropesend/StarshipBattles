# PROJ-437 File Manifest

> Generated during charter creation as sibling subproject to PROJ-436. Updated as implementation discovers additional files.

## Files

### Production — modified (Phase 1)

| File | Type | Notes |
|------|------|-------|
| `game/ui/screens/transfer_view_model.py` | Production | `available_sources` / `available_targets` enumeration changes from "FleetInfo / PlanetInfo DTOs" to a `Container` list query against the selected entity. The DTOs may still feed the dropdown labels but the source-of-truth shifts to Container identity. |
| `game/ui/screens/transfer_controller.py` | Production | Source/destination selection wiring updated to address `Container` instances. |
| `game/ui/screens/fleet_data_source.py` | Production | Enumerate fleet ship containers + planet facility containers as source/dest options. |

### Production — modified (Phase 2)

| File | Type | Notes |
|------|------|-------|
| `game/ui/screens/transfer_view_model.py` | Production | Pending-transfer math (`apply_arrow`, `apply_max`) calls `Container.add()` validation to compute mass-remaining preview. Existing `MAX_LOAD` / `MAX_DROP` sentinels preserved. |
| `game/ui/screens/transfer_grid_renderer.py` | Production | Render mass-remaining indicator + per-row policy-rejection messaging. |
| `game/ui/screens/transfer_dialog.py` | Production | Wire validation messages into dialog status area. |

### Production — modified (Phase 3)

| File | Type | Notes |
|------|------|-------|
| `game/ui/screens/transfer_view_model.py` | Production | Row construction reads from unified `Container.contents()` yielding mixed kinds; specialized per-kind formatting hooks (resource: float + icon; item: count + name + damage; population: count + species label). |
| `game/ui/screens/transfer_grid_renderer.py` | Production | Per-kind row rendering specialization. |
| `game/ui/screens/strategy_windows/transfer_dialogs.py` | Production | Mirror Phase 3 changes in the other transfer entry point. |
| `game/ui/screens/transfer_view_model.py` | Production | Drop-pod-name handling (currently `all_pod_names` field) folds into items-row presentation. |

### Production — modified (Phase 4)

| File | Type | Notes |
|------|------|-------|
| `game/ui/screens/transfer_dialog.py` | Production | Re-export at lines 39-43 deleted if PROJ-436 Phase 7 didn't already cover it. |
| `game/ui/screens/transfer_view_model.py` | Production | Any residual `RESOURCE_TYPES` reference cleaned up; final iteration via `ResourceCatalog.all_ids()` (Core-layer single source of truth). |
| Other UI consumers | Production | Anything still referencing the deleted hardcoded list, found via grep audit. |

### Tests — added

| File | Type | Notes |
|------|------|-------|
| `tests/unit/ui/screens/test_transfer_view_model_container.py` | Test (new) | Phase 1. Container-driven source/dest enumeration. |
| `tests/unit/ui/screens/test_transfer_mass_preview.py` | Test (new) | Phase 2. Mass-remaining preview math; policy-rejection messaging. |
| `tests/unit/ui/screens/test_transfer_mixed_content.py` | Test (new) | Phase 3. Resource + item + population rendering through one row model. |
| `tests/integration/ui/test_transfer_container_e2e.py` | Test (new) | Phase 3. End-to-end transfer flow with mixed-content source and destination. |
| `tests/static_guards/test_no_resource_types_constant.py` | Test (new) | Phase 4 gate. AST guard that `RESOURCE_TYPES` is gone from UI code. |

### Tests — modified

Existing `tests/unit/ui/screens/test_transfer_view_model.py` and `tests/integration/strategy/test_resource_transfer.py` will need updates as the view model and validator surfaces change. Enumerated phase-by-phase in each checklist.

### Findings — added (Phase 0)

| File | Type | Notes |
|------|------|-------|
| `Projects/active_projects/PROJ-437/findings/transfer_ui_migration_map.md` | Findings (new) | Phase 0. Per-file map of what changes per phase; produced before any production-code edit. |

### Docs

No doc changes in this project. PROJ-436 Phase 10 owns the broader doc refresh including any transfer-related documentation.
