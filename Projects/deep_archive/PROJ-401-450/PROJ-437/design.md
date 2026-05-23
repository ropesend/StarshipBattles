# PROJ-437: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source

This design derives from PROJ-436's `Container` substrate and the existing transfer UI surface in `game/ui/screens/transfer_*.py`.

- Sibling project's design: [Projects/active_projects/PROJ-436/design.md](../../PROJ-436/design.md)
- Inter-agent discussion outcome: [AgentCoordination/Scratchpad/Discussion/20260517T230029Z_post-435-project-creation/](../../../AgentCoordination/Scratchpad/Discussion/20260517T230029Z_post-435-project-creation/)
- User-confirmed design sketch (UI section): [AgentCoordination/Scratchpad/reports/unified_container_design_sketch.md](../../../AgentCoordination/Scratchpad/reports/unified_container_design_sketch.md) §10 phase 8.

## Initial Analysis

### Audit at project-creation time (2026-05-17)

**Existing transfer UI surface (4 main files + 1 alt entry):**

- [game/ui/screens/transfer_dialog.py](../../../game/ui/screens/transfer_dialog.py) — pygame_gui dialog shell.
- [game/ui/screens/transfer_controller.py](../../../game/ui/screens/transfer_controller.py) — event handler wiring; dispatches arrow clicks, Max clicks, confirm.
- [game/ui/screens/transfer_view_model.py](../../../game/ui/screens/transfer_view_model.py) — pure-Python state. `TransferViewModel` owns: `available_sources` / `available_targets` (dropdown options), `current_source` / `current_target` (selections), `pending_transfers: Dict[cargo_key, signed_amount]` (with `MAX_LOAD` / `MAX_DROP` sentinels), `row_data` (grid rows: `{cargo_key, display_name, source_amt, target_amt}`), `filter_empty`, `all_pod_names` (always-show drop-pod design names). Hardcoded `RESOURCE_TYPES` list of 8 strings at lines 26-33.
- [game/ui/screens/transfer_grid_renderer.py](../../../game/ui/screens/transfer_grid_renderer.py) — renders the grid rows.
- [game/ui/screens/strategy_windows/transfer_dialogs.py](../../../game/ui/screens/strategy_windows/transfer_dialogs.py) — alternate entry point in the strategy window family.

**Existing data dependencies (post-PROJ-436 these all change):**

- Reads source amounts from `Fleet.cargo_aggregate()` / `Planet.stockpile.get(resource_type)` / `ship.cargo_contents.get(cargo_type)` etc. — patchwork of per-entity accessors.
- Reads valid cargo types from `TransferValidator.VALID_CARGO_TYPES` hardcoded set.
- Reads valid resource list from local `RESOURCE_TYPES` constant.

**After PROJ-436 Phase 7:**

- Source/dest amounts read from one `Container.contents()` API per container.
- Valid cargo types determined by `Container.accepts(containable)`.
- Valid resource list iterated from `ResourceCatalog.all_ids()` (Core-layer single source of truth).

## Architecture

### Target view model shape

```
TransferViewModel:
  available_sources: List[ContainerRef]   # {container_id, owning_entity_label, content_kinds: Set[ContainableKind]}
  available_targets: List[ContainerRef]
  current_source: Optional[ContainerRef]
  current_target: Optional[ContainerRef]

  pending_transfers: Dict[ContainableKey, SignedAmount]  # ContainableKey = (kind, type_id); SignedAmount handles MAX sentinels
  row_data: List[ContainerRowEntry]
  # ContainerRowEntry = {key, display_name, kind, source_amt, target_amt, mass_per_unit, format_hint}

  filter_empty: bool
  # `all_pod_names` retired — drop-pod designs become items with always-show display_hint.

  # mass-remaining preview
  source_mass_remaining_after: float  # computed from pending_transfers and Container.add() validation
  target_mass_remaining_after: float
```

### Per-kind row presentation

| Kind | source_amt / target_amt | display_name | Special UI |
|---|---|---|---|
| RESOURCE | float (formatted to display_precision per data/resources.json) | resource_id title-cased + icon | mass-equivalent hint on hover |
| ITEM | int count (compressed healthy items + individual damaged items) | design name | damage indicator on damaged items |
| POPULATION | int count per species | species display name + species icon | total mass hint |

### Validation contract

Every staged transfer entry calls `target_container.accepts(containable)` and `target_container.mass_remaining >= staged_amount * mass_per_unit`. If either fails:

- `accepts` False → UI shows inline "Not accepted by target" message; entry styled rejected.
- mass over cap → UI shows "Target full" message + per-row mass-remaining indicator goes red.

No silent ignore. No try/except swallow.

### Existing UX preserved

- Slider per row (or arrow buttons + Max button equivalent — preserve current shape).
- `MAX_LOAD` / `MAX_DROP` sentinels mean "all available at execution time."
- Arrow click after Max resets sentinel to 0, then adds delta.
- Confirm button executes all staged transfers atomically.

## Key Patterns to Reuse

- **MVVM separation** — existing pattern from PROJ-325. View model is pure Python, testable without pygame.
- **Sentinel values for "all available"** — preserved verbatim.
- **`Container.add()` as validation surface** — single source of truth for accept/reject, removing UI-side validation logic.

## Dependencies & Risks

### Hard dependencies

- **PROJ-436 Phase 7 close.** Without `Container.accepts()` being the validation surface and `VALID_CARGO_TYPES` being deleted, this project's Phase 1+ implementation cannot ship.

### Soft dependencies

- **PROJ-436 Phase 6-8 may overlap with PROJ-437 Phase 0.** Phase 0 is research-only.

### Risks

1. **API churn during PROJ-436 implementation.** If `Container` API signatures change between Phase 0 (read) and Phase 1 (build), the migration map gets stale. Mitigation: re-audit at Phase 1 start; flag deltas to PROJ-436 owner before implementation.

2. **Existing transfer integration tests** (`tests/integration/strategy/test_resource_transfer.py`) lock in legacy behaviors. They must stay green throughout migration. Mitigation: incremental sub-phase migration; preserve test fixtures via adapter helpers if needed during sweep.

3. **`strategy_windows/transfer_dialogs.py` is an alternate entry point** — easy to forget. Phase 3 explicitly mirrors changes there.

## Opportunities Discovered

- **`MAX_LOAD` / `MAX_DROP` semantics already abstract** — they translate cleanly to "all available against `Container.contents()`."
- **`pending_transfers` keyed on `cargo_key`** — that key becomes `ContainableKey(kind, type_id)`; existing dict-of-pending math reuses verbatim.
- **`all_pod_names` always-show pattern** — generalizes to a per-design "always_show_in_transfer_ui" flag, useful for any rare-but-important item type.

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.
