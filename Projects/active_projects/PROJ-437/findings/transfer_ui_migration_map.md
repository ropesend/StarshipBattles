# PROJ-437 Phase 0 — Transfer UI Migration Map

> **Created:** 2026-05-18. Research-only deliverable for PROJ-437 Phase 0.
> No production-code changes accompany this document. Phases 1-4
> reference its per-file rows when planning sub-phase scope.

## 1. Repository state baseline

- Working branch: `main` at HEAD `6bd11e444` ("fix: update test baseline with correct git SHA and results").
- PROJ-436 Phase 7 landed at `48a6c0983` ("PROJ-436 Phase 7: Codex consult
  findings + phase closure") — the substrate this project consumes.
- Since Phase 7, PROJ-443 ran Phases 0-6 (test-discovery + triage) and is
  the source of the "fix test baseline" commit. PROJ-443 Phase 4
  (`e12603992`) flipped `pytest.ini norecursedirs` so the previously
  hidden 1953 tests under `tests/unit/strategy/data/` are now visible —
  the Phase 0 prompt's "NOT YOURS TO FIX" warning about the
  `norecursedirs` issue is **moot**.
- `tests/static_guards/test_no_legacy_storage_fields.py` pins absence of
  the deleted seams ([Phase 7 guards in
  `tests/static_guards/test_no_legacy_storage_fields.py:195-265`](../../../tests/static_guards/test_no_legacy_storage_fields.py#L195-L265)).
- `Projects/active_projects/PROJ-437/phase_state.json` records the
  Phase 7-era baseline (`4177fef361ec7857f32492a8f829777b0e1de41b`,
  21132 passed). The baseline needs to advance to the current `main`
  HEAD before Phase 1 begins; that update is part of starting Phase 1,
  not Phase 0.

## 2. Stable post-Phase-7 API surfaces this project builds on

| Surface | Module | Notes |
|---|---|---|
| `Container` (mass-capped storage) | [`game/strategy/data/container.py`](../../../game/strategy/data/container.py) | `add(containable, qty) -> AddResult`, `remove(...) -> RemoveResult`, `accepts(containable) -> bool`, `contents() -> Iterator[ContainerEntry]`, `mass_used` / `mass_remaining`, `to_dict` / `from_dict`. |
| `ContainerPolicy` | [`container.py:50-62`](../../../game/strategy/data/container.py#L50-L62) | `allowed_kinds: frozenset[ContainableKind]`, optional `allowed_type_ids`. |
| `ContainerEntry` (unified read row) | [`container.py:64-72`](../../../game/strategy/data/container.py#L64-L72) | `(kind, type_id, quantity, mass_total)`. |
| `Containable` variants | [`game/strategy/data/containable.py`](../../../game/strategy/data/containable.py) | `ResourceContainable(resource_id)` / `ItemContainable(item_ref)` / `PopulationContainable(species_id)`; `ContainableKind` enum. |
| `ResourceCatalog` | [`game/core/resources.py`](../../../game/core/resources.py) | Core SoT. `all_ids()`, `all_definitions()`, `get(rid)`, `has(rid)`, `get_mass_per_unit(rid)`. UI may call `ResourceCatalog.from_json()` directly. |
| `TransferValidator` (post-Phase-7) | [`game/strategy/validation/transfer_validator.py`](../../../game/strategy/validation/transfer_validator.py) | `_is_known_cargo_type(ct)` consults `ResourceCatalog.has()` + the `_CATEGORICAL_CARGO_TYPES = {"passengers", "drop_pod", "vehicle"}` frozenset. **No more `VALID_CARGO_TYPES`** class attr. |

## 3. Current transfer UI surface (audit, file by file)

> Convention: "PX → " marks the phase that migrates the row. Test
> coverage column lists the file(s) that currently lock in behavior.

### 3.1 [`game/ui/screens/transfer_view_model.py`](../../../game/ui/screens/transfer_view_model.py)

Pure-Python `TransferViewModel` — already substantially MVVM-clean
from PROJ-328 Phase C and PROJ-436 Phase 7. `RESOURCE_TYPES` /
`RESOURCE_DISPLAY_NAMES` are **already deleted**; the module iterates
`_iter_resource_definitions()` (lazy `ResourceCatalog.from_json().all_definitions()`).

| Line(s) | Current shape | Phase | Target shape |
|---|---|---|---|
| `26-36` lazy `_resource_catalog` + `_get_resource_catalog()` | OK as-is. | — | Keep. (Same pattern as `transfer_validator.py:45-56` and `container.py:74-95`.) |
| `39-53` `_iter_resource_definitions() -> list[ResourceDefinition]` | Returns catalog list in display order. | — | Keep. P4 audit may shift the per-row build into a kind-agnostic loop over `Container.contents()`, at which point this helper becomes one of three iteration paths rather than the sole resource-row driver. |
| `82-85` `MAX_LOAD`/`MAX_DROP` sentinels | OK. | — | Preserved by spec (decisions.md 2026-05-17 row 3). |
| `87-95` ctor: `pending_transfers: Dict[str, Any]`, `row_data: List[dict]`, `all_pod_names: List[str]`, etc. | str cargo_key is `<resource_id>` \| `passengers` \| `passengers_<species>` \| `drop_pod:<name>` \| `vehicle:<name>`. | P3 | Augment with `ContainerRef`-keyed state (per design.md §Architecture). Existing string `cargo_key` becomes a structured `ContainableKey(kind, type_id)`. `all_pod_names` retired (decisions.md 2026-05-17 last row). |
| `101-128` `apply_arrow` / `apply_max` / `set_pending_zero` / `clear_all_pending` / `reset_pending` / `get_pending` | Pure dict math. | P2 | Stays largely intact; the dict gains a per-key mass cap check feeding the `source_mass_remaining_after` / `target_mass_remaining_after` preview (design.md §Architecture). |
| `148-159` `format_pending` | Format helpers. | — | Keep. |
| `217-242` `get_amounts(info_obj)` | Pulls `FleetInfo.cargo_resources` (tuple of `(rid, amt)` per the DTO hardcoded list — see §4 below), `FleetInfo.passengers_current`, `PlanetInfo.stockpile`, `PlanetInfo.population_details`. | P1 | Replace with a `Container.contents()` iteration over the selected source/target's `ContainerRef`. Drops dependence on DTO-shaped accumulator tuples. |
| `244-285` `build_row_data` | Hardcodes "8 resources, then species, then pod rows" ordering; iterates `_iter_resource_definitions()` for the resource block. | P1 (substrate) → P3 (cutover) | Drive the row list directly from `Container.contents()` on each side; the union of `(kind, type_id)` keys becomes the row set. Per-kind formatting hooks (design.md §Per-kind row presentation) replace the three special-case loops. |
| `287-337` `_build_pod_rows` | Resolves drop-pod & vehicle rows from `PlanetInfo.staging_yard_summary` + `FleetInfo.carried_items_summary`. `vehicle_type ∈ {mine, fighter, satellite}` chooses `"vehicle:"` vs `"drop_pod:"` prefix. | P3 | Folded into the unified row builder. The kind=`ITEM` rows from `Container.contents()` already carry design identity; the `vehicle_type` lookup moves to a per-item formatting hint. |
| `339-345` `visible_rows()` filter-empty | OK. | — | Keep. |

**Tests pinning current behavior:**
[`tests/unit/ui/screens/test_transfer_view_model.py`](../../../tests/unit/ui/screens/test_transfer_view_model.py) (unit),
[`tests/unit/ui/screens/test_transfer_dialog_characterization.py`](../../../tests/unit/ui/screens/test_transfer_dialog_characterization.py)
(integration characterization).

### 3.2 [`game/ui/screens/transfer_controller.py`](../../../game/ui/screens/transfer_controller.py)

Side-effect boundary: facade queries + `IssueTransferCommand` dispatch.

| Line(s) | Current shape | Phase | Target shape |
|---|---|---|---|
| `30-56` `ConfirmResult` dataclass | OK. | — | Keep. |
| `79-136` `collect_sources_and_targets(source_fleet, hex_coord)` | Queries `facade.fleets.at_hex` + `facade.planets.at_hex`. Emits `{label, type ∈ {fleet, colony, planet}, id}` dicts. Falls through to the fleet's projected position when no planets at primary hex. | P1 | Same outer shape, but each entry gains an `available_containers: list[ContainerRef]` field (OD1 = (a) "every container on the entity" — confirmed below). For fleets that means per-ship containers (bay + pods + resources + population slot via `BayInventory.container_view`); for planets that means stockpile + staging_yard + per-facility component containers (post-Phase-8 once `ProductionEngine.context_type` is gone — for now planets show one aggregated stockpile container, consistent with the legacy single-`stockpile` accessor). |
| `138-168` `discover_pod_designs(scene)` | Pulls drop-pod design names from `session.services.design_catalogs_by_empire[empire_id]`. | P3 | Drives the "always show" set on the unified item rows; equivalent path under the design-flag generalization (`always_show_in_transfer_ui` per design.md §Opportunities). |
| `174-184` `fetch_dto(entry)` | `facade.fleets.get(entry["id"])` or `facade.planets.get(entry["id"])`. Returns `FleetInfo` / `PlanetInfo` DTO. | P1 | Augmented to return a Container snapshot (or the DTO-plus-container pair) keyed by `ContainerRef`. Concrete container objects do NOT cross the facade — the DTO surface gains a `containers: tuple[ContainerSnapshotInfo, ...]` field, or P1 introduces a parallel `facade.fleets.get_containers(id)` / `facade.planets.get_containers(id)` accessor. Sub-phase decision deferred to Phase 1 substrate step. |
| `190-209` `_parse_cargo_key(cargo_key)` | Parses string keys (`drop_pod:<name>` / `vehicle:<name>` / `passengers` / `passengers_<species>` / bare resource_id). | P3 | When `pending_transfers` shifts to `ContainableKey(kind, type_id)` (design.md §Architecture), this method collapses into a serialize-for-command helper. The IssueTransferCommand surface itself is unchanged (Phase 4 stretch). |
| `211-243` `_resolve_endpoints` / `_direction` | Fleet-centric: handles fleet↔planet (both directions), fleet↔fleet, rejects planet↔planet. | P1 | Unchanged — facade contract stays. ContainerRefs route through to the same fleet_id / planet_id resolution. |
| `245-354` `confirm_pending()` | Iterates `vm.pending_transfers.items()`, builds an `IssueTransferCommand` per non-zero entry, surfaces first rejection. | P2 | Same outer flow; the per-entry rejection path additionally lights up the per-row "Not accepted by target" or "Target full" styling (design.md §Validation contract). |

**Tests pinning current behavior:**
[`tests/unit/ui/screens/test_transfer_controller.py`](../../../tests/unit/ui/screens/test_transfer_controller.py),
[`tests/integration/strategy/test_resource_transfer.py`](../../../tests/integration/strategy/test_resource_transfer.py),
[`tests/integration/test_transfer_container_validation.py`](../../../tests/integration/test_transfer_container_validation.py).

### 3.3 [`game/ui/screens/transfer_dialog.py`](../../../game/ui/screens/transfer_dialog.py)

pygame_gui shell; mostly delegate-wiring + back-compat property
shims. The `RESOURCE_TYPES` / `RESOURCE_DISPLAY_NAMES` re-export at
lines 39-43 is **already deleted** in Phase 7 — the AST guard at
[`tests/static_guards/test_no_legacy_storage_fields.py:248-265`](../../../tests/static_guards/test_no_legacy_storage_fields.py#L248-L265)
pins absence.

| Line(s) | Current shape | Phase | Target shape |
|---|---|---|---|
| `48-159` `__init__` two-stage construction | OK. | — | Keep. |
| `191-253` legacy property shims (`available_sources`, `pending_transfers`, `_row_data`, `_filter_empty`, `_current_source`, `_current_target`, `_all_pod_names`) | Pass-through to view model. | P3 | `_all_pod_names` removed when `all_pod_names` retires; other shims kept while existing callers depend on them. |
| `259-281` `populate_initial_data` | Calls controller, sets initial source/target. | P1 | Renamed inputs (`available_sources` carries ContainerRef list) but flow unchanged. |
| `300-305` `_add_pod_rows` | Appends pod rows in-place. | P3 | Retired — `view_model.build_row_data` already returns the full mixed-content list. |
| `311-345` event handlers (`_on_source_changed`, `_on_target_changed`, `_build_grid`, etc.) | Wire source/target selection to view-model + renderer. | P1 | Unchanged shape; pass-through. |
| `346-455` button/keyboard dispatch (`_on_arrow_click`, `_on_max_click`, `_on_filter_toggle`, `_on_clear_all`, `_on_confirm`, `process_event`) | Wire button IDs to view-model mutators + renderer label refresh. | P2 | Same flow; per-row mass-remaining indicator + rejection-message styling routed through renderer. |
| `458-480` `handle_external_selection(obj)` | External-pick target swap (`Fleet`, `Planet`). | P1 | Keep. ContainerRef list is the new lookup target. |

**Tests pinning current behavior:**
[`tests/unit/ui/screens/test_transfer_dialog.py`](../../../tests/unit/ui/screens/test_transfer_dialog.py),
[`tests/unit/ui/screens/test_transfer_dialog_characterization.py`](../../../tests/unit/ui/screens/test_transfer_dialog_characterization.py),
[`tests/unit/ui/screens/test_transfer_dialog_enhanced.py`](../../../tests/unit/ui/screens/test_transfer_dialog_enhanced.py),
[`tests/unit/ui/screens/test_transfer_dialog_keeps_open_on_abort.py`](../../../tests/unit/ui/screens/test_transfer_dialog_keeps_open_on_abort.py).

### 3.4 [`game/ui/screens/transfer_grid_renderer.py`](../../../game/ui/screens/transfer_grid_renderer.py)

`pygame_gui` widget tree builder.

| Line(s) | Current shape | Phase | Target shape |
|---|---|---|---|
| `38-41` `ARROW_INCREMENTS_LOAD`/`_DROP` + labels | OK. | — | Keep. |
| `58-79` layout constants | OK. | — | Keep. |
| `85-179` `build_chrome` | Source/Target dropdowns + filter button + column headers + scrolling grid + bottom buttons. | — | Header set may gain a "Mass remaining" indicator column (P2). |
| `185-200` `recreate_dropdown` | Kill + recreate (`UIDropDownMenu` has no dynamic update). | P1 | Same. |
| `214-240` `build_grid` | Iterates `view_model.visible_rows()`, calls `_add_row`. | P3 | Same outer shape; per-row builder dispatches on `row["kind"]` (P3 introduces a `kind` field on the row dict). |
| `242-321` `_add_row` | Builds the 1+1+1+5+1+1+5+1+1 = 16 widgets per row. | P3 | Per-kind specialization (resource: float + icon; item: count + design name + damage indicator; population: count + species label). Hooks fed from view-model row entries. |
| `327-344` `update_pending_label` / `set_filter_button_text` | Per-row label refresh. | P2 | Same + adds mass-remaining indicator and rejection-message styling. |
| `347-356` `TransferDialogUiBuilder.build` | One-shot chrome + tooltips + initial data. | — | Keep. |

**Tests pinning current behavior:**
[`tests/unit/ui/screens/test_transfer_grid_renderer.py`](../../../tests/unit/ui/screens/test_transfer_grid_renderer.py).

### 3.5 [`game/ui/screens/strategy_windows/transfer_dialogs.py`](../../../game/ui/screens/strategy_windows/transfer_dialogs.py)

Lifecycle registrar — opens `TransferDialog` and the quick-dialog
variant from the strategy-window manager. Pure construction, no
storage references.

| Line(s) | Current shape | Phase | Target shape |
|---|---|---|---|
| `24-51` `TransferDialogRegistrar.open` | Closes any prior `c.transfer_dialog`, opens a fresh `TransferDialog(relative_rect, manager, source_fleet, hex_coord, scene, window_manager=c, input_mapper=c._mapper)`. | P3 | No change expected. The Phase 3 manifest entry that lists this file is precautionary — touch only if the constructor signature changes when ContainerRef enumeration lands. |
| `53-79` `open_quick(direction)` | Opens the `CargoQuickDialog` variant. | — | Out of scope for PROJ-437 (the quick-dialog has its own controller / view model surface; flag if Phase 2 rejection-message work needs to mirror there too). |

**Tests pinning current behavior:** indirect — exercised through
[`tests/unit/ui/screens/test_strategy_window_manager.py`](../../../tests/unit/ui/screens/test_strategy_window_manager.py)
where it intersects with the manager. Direct registrar tests likely
none (registrar is thin construction glue).

### 3.6 [`game/ui/screens/fleet_data_source.py`](../../../game/ui/screens/fleet_data_source.py) — **manifest entry is wrong**

This file is the **fleet-report `VirtualTable` data source**, not a
source/target enumerator for the transfer dialog. It produces ship
rows for the fleet report table (`portrait`, `topdown`, `serial`, …,
`cargo` columns) and has no relationship to transfer dialog options.

The transfer-dialog source/target enumeration lives in
[`transfer_controller.py:79-136::collect_sources_and_targets`](../../../game/ui/screens/transfer_controller.py#L79-L136).
The PROJ-437 manifest's Phase 1 row pointing to `fleet_data_source.py`
is mis-targeted and should be corrected when Phase 1 plan is finalized
(manifest update, not a Phase 0 production change).

Note: this file *does* touch `ship._cargo_mgr.get_cargo_capacity` /
`get_current_cargo` / `total_cargo_units` (`_format_transport`,
`_format_cargo`). Those are the stable PROJ-436 Phase 3b manager API,
not legacy shapes — no migration needed here.

## 4. Tangential finding (out-of-scope for PROJ-437; flagging for visibility)

[`game/strategy/facade/dto/fleet_dto.py:217-226`](../../../game/strategy/facade/dto/fleet_dto.py#L217-L226)
hardcodes the resource tuple `("metals", "organics", "vapors",
"radioactives", "exotics", "fuel", "energy", "ammo")` to build
`FleetInfo.cargo_resources` / `cargo_capacities`. This is the same
anti-pattern PROJ-436 Phase 7 was set up to delete on the UI side —
it leaked into the DTO surface. Adding a new resource to
`data/resources.json` will silently fail to surface in
`FleetInfo.cargo_resources` until somebody edits this tuple.

This is **not** PROJ-437 scope. It is a one-line tuple replacement
with `ResourceCatalog.all_ids()` and probably belongs in PROJ-436
Phase 7 cleanup (or a tiny TD ticket). PROJ-437 Phase 1's controller
rework will route around it (Container snapshots are the new SoT), so
the DTO leak does not block PROJ-437 — but it should not survive
Phase 4 final-grep cleanup. Documenting here so it is not lost.

[`game/ui/screens/builder/stat_rows_dynamic.py:179,252`](../../../game/ui/screens/builder/stat_rows_dynamic.py#L179)
also hardcodes resource display-name mappings; that's the build-queue
panel surface, again outside PROJ-437 scope, but a sibling
opportunity. Flag for the same TD ticket if filed.

## 5. Open decisions OD1/OD2/OD3 — Phase 0 resolution

Per decisions.md (2026-05-17), all three are implementer-choice with
documented defaults. Phase 0 audit confirmed:

- **OD1 (source/dest enumeration scope) → (a) every container.** The
  legacy `collect_sources_and_targets` already enumerates per-entity
  (fleet / colony / planet); option (a) is the natural extension. A
  fleet right-click on the transfer dialog should expose the
  per-ship containers it contains so the user can stage targeted
  transfers between specific ships. The "noisy when 5 cargo holds"
  worry from decisions.md is mitigated by the existing filter-empty
  toggle.

- **OD2 (cross-kind transfer in one operation) → (a) all three at
  once.** The existing UX already moves resources + items
  (drop_pod/vehicle) + passengers in a single confirm pass through
  `pending_transfers`; preserving that is the path of least
  surprise per the decisions.md "preserve existing slider/arrow/Max
  UX" row.

- **OD3 (mass-remaining preview granularity) → (a) per-input.**
  `Container.add()` is O(1) over a hash plus a sum of the three
  internal slice maps — cheap enough that per-arrow-click recompute
  is well within frame budget at the row counts the dialog
  realistically renders (≤ 50 rows). Profile only if a future
  capacity bump puts row counts in the hundreds.

All three defaults stand. `decisions.md` will get a 2026-05-18 row
confirming them.

## 6. Phase 1 scope decision: single commit vs. sub-phases

Phase 1's claimed manifest is `transfer_view_model.py` +
`transfer_controller.py` + `fleet_data_source.py` (already
identified as misrouted — actual second touched file will be a
small augmentation to the fleet/planet info DTO surface OR a new
parallel `facade.fleets.get_containers(id)` / `planets.get_containers(id)`
accessor).

The blast radius:

- `transfer_view_model.py::get_amounts` + `build_row_data` are
  touched by ~6 unit tests + 1 characterization test.
- `transfer_controller.py::collect_sources_and_targets` +
  `fetch_dto` are touched by ~4 unit tests + 2 integration tests.
- A new DTO/facade accessor adds 1-2 files.

Sub-phase recommendation: **two sub-phases.**

1. **Phase 1a (substrate, additive):** introduce `ContainerRef` +
   `ContainerSnapshotInfo` types and the parallel facade accessor
   (`get_containers(id)` returns a tuple of `ContainerSnapshotInfo`).
   Land the projection alongside the existing DTO. Zero callers
   migrate. RED→GREEN against a new `tests/unit/ui/screens/test_transfer_view_model_container.py`
   focused on the projection shape.
2. **Phase 1b (cutover):** migrate `transfer_view_model.get_amounts`
   / `build_row_data` and `transfer_controller.fetch_dto` /
   `collect_sources_and_targets` to read through `ContainerSnapshotInfo`.
   Update or delete now-redundant FleetInfo accumulator fields if
   safe; if not, leave them as parallel projections — defer cleanup
   to Phase 4's final-grep pass. Re-run sharded suite green.

If during Phase 1a the new accessor turns out to be a 30-line patch
with no breaking surface, collapse to a single commit — PROJ-436
Phase 4f/5f/6b/7 set the "small phase = single cutover" precedent
explicitly.

Phases 2 and 3 should each be reassessed at their start with this
same rubric. Phase 2 is likely single-commit (mass-preview is a
read-only addition + a couple of styling tweaks). Phase 3 likely
needs sub-phases (mixed-content row presentation touches the view
model + grid renderer + the alt entry point in
`strategy_windows/transfer_dialogs.py`).

## 7. Heads-up to user (Ross) — UI label change pending review

PROJ-436 Phase 7 accepted the default that
`ResourceDefinition.name` from `data/resources.json` is the single
source of truth for UI resource labels. With the current JSON, the
ammo cargo row reads **"Ammunition"** (the JSON `name`) instead of
the legacy **"Ammo"** hardcoded mapping. All other seven labels
(Metals / Organics / Vapors / Radioactives / Exotics / Fuel /
Energy) are unchanged.

If "Ammo" is preferred, the fix is a one-line edit to
`data/resources.json`'s ammo entry — not a UI change. Flag for
user review before Phase 5 ship.

## 8. Phase 0 → Phase 1 handoff summary

- Migration map written (this document).
- OD1/OD2/OD3 defaults confirmed.
- Manifest correction needed: `fleet_data_source.py` is the wrong
  Phase 1 target; the real targets are
  `transfer_view_model.py`, `transfer_controller.py`, and a new
  DTO/facade surface (chosen at Phase 1a start).
- Phase 1 likely splits 1a/1b along the substrate-then-cutover line.
- Phase 0 produces no production-code changes (per spec).

Phase 1 implementation gated on: (1) this map reviewed; (2)
PROJ-436 Phase 7 verified intact (it is — guards green); (3)
phase_state.json baseline advanced to current HEAD.
