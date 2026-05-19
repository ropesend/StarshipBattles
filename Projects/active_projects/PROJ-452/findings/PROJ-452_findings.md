# PROJ-452 Findings (consolidated)

Sources:
- `AgentCoordination/discovered_issues/log.jsonl` (DI-2026-05-18-003, -004, -005 — verbatim)
- `Projects/archived_projects/PROJ-446/findings/bucket_c_ui_core_tests_scan.md` (F-C-015 — verbatim)

All file:line references **re-verified against current code on 2026-05-19** before this file was written. The FleetInfo line range has shifted from the originally-cited `:217-226` to `:230-239` because PROJ-444 Phase 1 Task 1.4 (F-A-017 narrow-catch split) inserted ~13 lines earlier in the same method. This file documents the current line range; the linked DI log entry retains the historical citation for traceability.

---

## DI-2026-05-18-003 — `FleetInfo.from_fleet` hardcodes the 8-resource tuple
- **Severity**: medium
- **Category**: bug (silent-loss anti-pattern)
- **File**: `game/strategy/facade/dto/fleet_dto.py:230-239` (current; was `:217-226` at DI logging time 2026-05-18)
- **Symbol**: `FleetInfo.from_fleet`
- **Source**: PROJ-437 Phase 0 finding §4
- **What survived**: `FleetInfo.from_fleet` hardcodes the 8-resource tuple `("metals", "organics", "vapors", "radioactives", "exotics", "fuel", "energy", "ammo")` at lines 230-239 to build `cargo_resources` / `cargo_capacities`. Adding a new resource to `data/resources.json` will silently fail to surface in `FleetInfo.cargo_resources` / `cargo_capacities` until somebody edits this tuple.
- **Why it's a problem**: Same anti-pattern PROJ-436 Phase 7 was designed to delete on the UI side; the leak survived into the DTO surface. PROJ-437's container-driven row builder routes around the FleetInfo DTO (`ContainerSnapshotInfo` is the new SoT), so the DTO leak does not break PROJ-437, but should be cleaned up.
- **Suggested action**: Replace the hardcoded tuples with `tuple((res, fleet.resources.get_fleet_cargo_current(res)) for res in ResourceCatalog.from_json().all_ids())` and the parallel `_capacity` tuple. Same shape as the post-PROJ-436-Phase-7 `transfer_view_model._iter_resource_definitions` pattern (and the existing `empire_dto.py:109` `total_resources` factory).
- **Status as of 2026-05-19**: open. Both hardcoded tuples confirmed present at fleet_dto.py:230-239.

---

## DI-2026-05-18-004 — `stat_rows_dynamic.py` hardcodes resource ID / display-name mappings
- **Severity**: medium
- **Category**: bug (silent-loss anti-pattern — IDs side; complements F-C-015's labels side)
- **File**: `game/ui/screens/builder/stat_rows_dynamic.py:178-181, 251-254` (current; was `:179`, `:252` at DI logging time)
- **Symbol**: `get_construction_rows` / `get_strategic_rows` (the `LABEL_ABBREV` constants are loop-local)
- **Source**: PROJ-437 Phase 0 finding §4
- **What survived**: Two separate `LABEL_ABBREV` dicts hardcoding 5 resource-id → display-name pairs (`"metals": "Metals"`, `"organics": "Organics"`, `"vapors": "Vapors"`, `"radioactives": "Radact"`, `"exotics": "Exotics"`). The IDs side is **already** catalog-driven at line 177 (`PLANET_RESOURCE_NAMES = [d.id for d in ResourceCatalog.from_json().by_display_group("planetary")]`) — verified 2026-05-19. The live gap is the labels side (covered by F-C-015 below).
- **Why it's a problem**: Adding a 6th planetary resource produces a row whose getter works but whose label silently falls back to the raw resource_id (because `LABEL_ABBREV.get(res, res)` returns the id when no abbreviation is found). The two dicts duplicate the same 5-entry mapping with identical content.
- **Suggested action**: Replace the hardcoded constants with `ResourceCatalog.from_json().all_definitions()` iteration; use `ResourceDefinition.name` for display labels (canonical source of truth). A single module-level `_label_for(resource_id)` helper that wraps the catalog lookup once per render is cleaner than calling `ResourceCatalog.from_json()` inside the row loop.
- **Status as of 2026-05-19**: open on the labels side; closed-by-accident on the IDs side. Treat DI-004 + F-C-015 as one fix.

---

## DI-2026-05-18-005 — `Container.remove` does not enforce non-negative quantity
- **Severity**: low
- **Category**: bug (invariant gap; no active production impact)
- **File**: `game/strategy/data/container.py:225` (verified 2026-05-19)
- **Symbol**: `Container.remove`
- **Source**: PROJ-436 Phase 11 end-of-project Codex consult
- **What survived**: `Container.remove()` does not enforce non-negative quantity, mirroring the check that `Container.add()` applies at `container.py:191` (resource) and `:213` (population). Codex reproduced: `remove(ResourceContainable('metals'), -3.0)` grows stored value 10.0 to 13.0; `remove(PopulationContainable('human'), -2)` grows 5 to 7. No production caller currently passes negative removals (Codex traced this end-to-end during the PROJ-436 Phase 11 consult), so this is a cosmetic invariant gap / safety hardening rather than an active bug. Risk is forward-contract drift if a future caller passes a negative value.
- **Suggested action**: Mirror `Container.add()`'s `if quantity < 0: raise ValueError(...)` check at the top of `Container.remove()` for the `ResourceContainable` and `PopulationContainable` branches. Add unit-test coverage in `tests/unit/strategy/data/test_container.py` for the negative-quantity rejection.
- **Codex consult artifact**: `AgentCoordination/Scratchpad/Consult/20260518T145950Z_proj436-phase11-end-of-project/response.md` captures the original reproduction.
- **Status as of 2026-05-19**: open. Verified the `Container.remove` method at lines 225-256 still has no non-negative guard. The `Container.add` guards at lines 191 and 213-214 are unchanged and serve as the mirror template.

---

## F-C-015 — `stat_rows_dynamic.py` hardcoded `PLANET_RESOURCE_NAMES` plus `LABEL_ABBREV` reach into resource catalog twice
- **Severity**: medium
- **Category**: obsolete-code (label-side residue; the IDs-side is already catalog-driven)
- **File**: `game/ui/screens/builder/stat_rows_dynamic.py:178-181` (Construction section), `:251-254` (Strategic section) — current line numbers
- **Symbol**: `get_construction_rows` / `get_strategic_rows` (LABEL_ABBREV constants are loop-local)
- **Source refactor**: PROJ-435 / PROJ-436 Phase 7
- **What survived**: Two separate `LABEL_ABBREV` dicts hardcoding 5 resource-id → display-name pairs. `PLANET_RESOURCE_NAMES` correctly iterates `ResourceCatalog.from_json().by_display_group("planetary")` (post-PROJ-436), but the display labels still come from a hardcoded dict instead of `ResourceDefinition.name`.
- **Why it's a problem**: Adding a 6th planetary resource produces a row whose getter works but whose label silently falls back to the raw resource_id. Same anti-pattern as the already-logged log.jsonl entry DI-2026-05-18-004 (which names this exact file but only flags the IDs side). This finding is the **label-side** companion — the IDs are now driven by the catalog, but display labels still aren't.
- **Suggested action**: Drop the two `LABEL_ABBREV` dicts; use `ResourceCatalog.from_json().get(res).name` (or a single helper `_label_for(resource_id)` that wraps the catalog lookup once per render).
- **Effort**: tiny
- **Status as of 2026-05-19**: open. Same lines as DI-004; lands in the same Phase 3 PR.

---

## Out-of-scope clarifications (not closed by this project)

- **DI-2026-05-18-001 ActionExecutionEngine half** — owned by PROJ-455.
- **DI-2026-05-18-002 (CommandRegistry.serializer_codec_for)** — closed by archived PROJ-445 Phase 2 (recorded as `resolved` in `log.jsonl`).
- **DI-2026-05-18-001 transfer half** — closed by archived PROJ-445 Phase 2 (recorded as `resolved`).
- **DI-2026-05-18-002 transfer_dialog 523-LOC overflow** — UI-bucket; deferred to a future UI sweep project.
- **DI-2026-05-18-006 + DI-2026-05-18-007** — production engine semantics; partial-resolved by PROJ-444/445; remaining UX gap belongs to a future engine project.
- **F-A-019 PlanetInfo.stockpile catalog order** — already closed by archived PROJ-444 Phase 1 Task 1.6 (verified 2026-05-19 at `planet_dto.py:55` — `catalog_ids = ResourceCatalog.from_json().all_ids()`).
- **F-A-018 EmpireInfo.total_resources** — already closed by archived PROJ-444 Phase 1 Task 1.5 (verified 2026-05-19 at `empire_dto.py:109`).

---

## Sweep targets (Phase 4 — audit-then-decide)

These are not findings per se; they are candidate files for the Phase 4 sweep. Each entry will be audited at the start of Phase 4 and either fixed (if a hardcoded list / label is found) or documented as already-catalog-driven in `decisions.md`.

| File | Reason for audit |
|------|------------------|
| `game/ui/screens/builder/stat_rows_dynamic.py` (sections beyond `get_construction_rows` / `get_strategic_rows`) | We're already on the file in Phase 3; sweep the rest for any other hardcoded constants |
| `game/ui/panels/empire_treasury_panel.py` | Comment at :28 mentions module-level `ResourceCatalog.from_json()` call; verify all functions in the file are catalog-driven |
| `game/ui/screens/build_queue_helpers.py` | Comment at :14 cites the deleted `RESOURCE_TYPES`; verify no hardcoded list survives |
| Any file surfaced by `rg -n '"metals".*"organics".*"vapors"\|RESOURCE_NAMES\b\|RESOURCE_TYPES\b' game/ui/ game/strategy/` | Backstop grep |
