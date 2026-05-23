# PROJ-452 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Phase 1 — Container.remove non-negative guard (DI-005)

### Production files

| File | Type | Notes |
|------|------|-------|
| `game/strategy/data/container.py` | Production | Add `if quantity < 0: raise ValueError(...)` at the top of `Container.remove()` for `ResourceContainable` and `PopulationContainable` branches (line 225+). Mirror exactly the wording used at `:191` and `:213` for `Container.add()`. |

### Test files

| File | Type | Notes |
|------|------|-------|
| `tests/unit/strategy/data/test_container.py` | Test (modified) | Add `test_remove_rejects_negative_resource_quantity` + `test_remove_rejects_negative_population_quantity`. RED before guard; GREEN after. |

---

## Phase 2 — FleetInfo.from_fleet catalog-driven (DI-003)

### Production files

| File | Type | Notes |
|------|------|-------|
| `game/strategy/facade/dto/fleet_dto.py` | Production | Replace the two hardcoded 8-resource tuples at lines 230-239 (`cargo_resources` + `cargo_capacities`) with `ResourceCatalog.from_json().all_ids()` iteration. Pattern: `tuple((res, fleet.resources.get_fleet_cargo_current(res)) for res in ResourceCatalog.from_json().all_ids())`. Matches the existing pattern at `empire_dto.py:109`. |

### Test files

| File | Type | Notes |
|------|------|-------|
| `tests/unit/strategy/facade/test_fleet_dto.py` | Test (modified) | Add `test_fleet_info_cargo_surfaces_full_catalog` — assert `info.cargo_resources` enumerates `ResourceCatalog.from_json().all_ids()` (use `len()` + `set()` comparison, not order-sensitive). Add `test_fleet_info_cargo_surfaces_new_resource_when_catalog_extended` — monkeypatch `ResourceCatalog.from_json` (or override the resources-file path via `game.core.paths.Paths.RESOURCES_FILE`) to return a catalog with one extra resource_id; assert the new id surfaces in `info.cargo_resources` without code change. (A plain in-memory registry fixture is NOT sufficient because `FleetInfo.from_fleet` calls `ResourceCatalog.from_json()` directly, which loads JSON from disk at `game/core/resources.py:85-107`.) See `phase_2_checklist.md` Task 2.1 for the two acceptable monkeypatch approaches. The live test file lives at `tests/unit/strategy/facade/test_fleet_dto.py`, NOT under the `dto/` subdirectory. |

---

## Phase 3 — stat_rows_dynamic LABEL_ABBREV retirement (DI-004 + F-C-015)

### Production files

| File | Type | Notes |
|------|------|-------|
| `game/ui/screens/builder/stat_rows_dynamic.py` | Production | Drop the two `LABEL_ABBREV = {...}` dicts at lines 178-181 (`get_construction_rows`) and 251-254 (`get_strategic_rows`). Add a module-level `_label_for(resource_id: str) -> str` helper that calls `ResourceCatalog.from_json().get(resource_id).name` with a defensive fallback to the raw id. Replace `LABEL_ABBREV.get(res, res)` call sites at lines 189 (construction), 262 (harvesters), 272 (storage) with `_label_for(res)`. |

### Test files

| File | Type | Notes |
|------|------|-------|
| `tests/unit/ui/screens/builder/test_stat_rows_dynamic.py` | Test (modified or new) | Add `test_construction_rows_use_catalog_display_names` — assert the row label for `"radioactives"` is the canonical catalog name (not the abbreviation `"Radact"` that the deleted LABEL_ABBREV dict produced). Add `test_strategic_harvester_row_labels_use_catalog_names`. If the file does not exist, create it. |

---

## Phase 4 — Sweep (catalog-vs-hardcode residue in adjacent UI surfaces)

### Production files (audit; touch only if a hardcoded list is found)

| File | Type | Notes |
|------|------|-------|
| `game/ui/screens/builder/stat_rows_dynamic.py` | Production (possible) | Audit the rest of the file (`get_logistics_rows`, `_discover_resources`, `_get_strategic_abilities`, `get_strategic_rows`) for hardcoded constants. The harvester/storage iteration is dynamic — that's the correct pattern; do not touch. |
| `game/ui/panels/empire_treasury_panel.py` | Production (possible) | Audit functions beyond line 32. Currently only the resource-list helper at :32 is in scope. |
| `game/ui/screens/build_queue_helpers.py` | Production (possible) | Comment at :14 cites the deleted `RESOURCE_TYPES`. Verify no hardcoded list survives. |
| Any UI file surfaced by `rg -n '"metals".*"organics".*"vapors"\|RESOURCE_NAMES\b\|RESOURCE_TYPES\b' game/ui/` | Production (possible) | Treat each match as a candidate; fix only if the hardcode is the same anti-pattern. |

### Test files

| File | Type | Notes |
|------|------|-------|
| Per-fix test in the file's existing unit-test owner | Test (possible) | Only required if Phase 4 produces a production fix. |

### Audit-only artifact

| File | Type | Notes |
|------|------|-------|
| `Projects/active_projects/PROJ-452/decisions.md` | Doc | Even if Phase 4 produces no production fix, commit an audit report describing the files inspected and the absence of hardcodes. |

---

## Cross-bucket conflicts to watch

| File | Other projects touching | Resolution |
|------|------------------------|------------|
| `game/strategy/facade/dto/fleet_dto.py` | None — no other PROJ-452..455 touches the facade DTO layer | No conflict. |
| `game/ui/screens/builder/stat_rows_dynamic.py` | None — UI sweep is PROJ-452 territory | No conflict. |
| `game/strategy/data/container.py` | None — DI-005 is the only outstanding finding on this file | No conflict. |

## File count summary

- **3 production files touched by Phases 1-3** (definite scope)
- **3 production files audited by Phase 4** (touch only if hardcode found; likely zero additional touches)
- **3 test files modified** (one per Phase 1-3)
- **0 new production files**
- **0 new test files expected** (Phase 3 may create `test_stat_rows_dynamic.py` if absent)
- **Total LOC delta:** ≈60-120 lines (Phase 1: ~10, Phase 2: ~20, Phase 3: ~30, Phase 4: 0-50 depending on audit)
