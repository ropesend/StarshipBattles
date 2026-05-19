# PROJ-452 Phase 2: FleetInfo.from_fleet catalog-driven (DI-003)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-452 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Close DI-2026-05-18-003 by replacing the two hardcoded 8-resource tuples in `FleetInfo.from_fleet` (`fleet_dto.py:230-239`) with `ResourceCatalog.from_json().all_ids()` iteration. Mirrors the existing pattern at `empire_dto.py:109` (which `EmpireInfo.total_resources` already uses).

**Cross-bucket file-ownership rule:** This phase touches only `game/strategy/facade/dto/fleet_dto.py` and `tests/unit/strategy/facade/test_fleet_dto.py`. Do NOT touch any file PROJ-453 / PROJ-454 / PROJ-455 owns.

**Source-of-truth findings:** [`findings/PROJ-452_findings.md`](findings/PROJ-452_findings.md) — read DI-003's full text. Note the line-range drift from `:217-226` (archived) to `:230-239` (current) caused by PROJ-444 Phase 1 Task 1.4.

---

## Tasks

### Task 2.1: DI-003 — Replace FleetInfo.from_fleet hardcoded resource tuples with ResourceCatalog iteration [Medium]
**File:** `game/strategy/facade/dto/fleet_dto.py:230-239`
**Tests:** `pytest tests/unit/strategy/facade/test_fleet_dto.py -v` (note: the live test file is `tests/unit/strategy/facade/test_fleet_dto.py`, NOT `tests/unit/strategy/facade/dto/test_fleet_dto.py`; the `dto/` subdir only contains `test_build_queue_dto.py`).

- [ ] Read the current `FleetInfo.from_fleet` factory at lines 130-247 (approximate; the method starts around 130 and returns the dataclass at 211-246). Note the two hardcoded tuples at 230-239:
  ```python
  cargo_resources=tuple(
      (res, fleet.resources.get_fleet_cargo_current(res))
      for res in ("metals", "organics", "vapors", "radioactives", "exotics",
                  "fuel", "energy", "ammo")
  ),
  cargo_capacities=tuple(
      (res, fleet.resources.get_fleet_cargo_capacity(res))
      for res in ("metals", "organics", "vapors", "radioactives", "exotics",
                  "fuel", "energy", "ammo")
  ),
  ```
- [ ] Read the parallel catalog-driven pattern at `game/strategy/facade/dto/empire_dto.py:104-114` (around `total_resources` factory) for the exact iteration shape. Note: `empire_dto.py:109` uses `for rid in ResourceCatalog.from_json().all_ids()`.
- [ ] Verify `ResourceCatalog` is already imported in `fleet_dto.py`. If not, add `from game.core.resources import ResourceCatalog` to the imports block.
- [ ] **RED**: Add two tests to `tests/unit/strategy/facade/test_fleet_dto.py`:
  1. `test_fleet_info_cargo_resources_covers_full_catalog` — build a `Fleet` with a stubbed `resources` object; assert `info.cargo_resources` is a tuple of `(rid, value)` pairs with `len(info.cargo_resources) == len(ResourceCatalog.from_json().all_ids())` and the set of resource IDs matches.
  2. `test_fleet_info_cargo_resources_surfaces_new_resource` — assert that an extra catalog id (e.g., `"plasma"`) surfaces in `info.cargo_resources` without code change. This is the regression-catcher for the DI-003 anti-pattern.

     **Fixture approach (important):** `FleetInfo.from_fleet` calls `ResourceCatalog.from_json()` directly (post-GREEN — see the GREEN block below), and `ResourceCatalog.from_json()` loads the catalog from disk at `game/core/resources.py:85-107`. A plain in-memory "fresh registry" fixture is NOT enough to alter the production catalog seen by `FleetInfo.from_fleet`. Choose ONE of these two approaches for the regression test:

     **Option A — monkeypatch `ResourceCatalog.from_json`** (preferred — smallest surface):
     ```python
     def test_fleet_info_cargo_resources_surfaces_new_resource(monkeypatch):
         from game.core.resources import ResourceCatalog, ResourceDefinition
         baseline = ResourceCatalog.from_json()
         extended = ResourceCatalog({
             **baseline._definitions,
             "plasma": ResourceDefinition(id="plasma", name="Plasma", ...),
         })
         monkeypatch.setattr(
             "game.strategy.facade.dto.fleet_dto.ResourceCatalog.from_json",
             classmethod(lambda cls, *a, **kw: extended),
         )
         # build Fleet, call FleetInfo.from_fleet, assert "plasma" appears in cargo_resources ids
     ```
     Make sure the `setattr` target is the import path *used by* `fleet_dto.py` (e.g., the class itself) so the patch is observed.

     **Option B — explicit test-fixture JSON path** (use only if Option A is awkward):
     1. Author a `tests/data/resources_with_plasma.json` containing baseline + plasma.
     2. Monkeypatch `game.core.paths.Paths.RESOURCES_FILE` to point at the test fixture before invoking `FleetInfo.from_fleet`.

     Document which option you pick in `Notes` below.

  Run both — confirm they FAIL today because the hardcoded tuple is fixed at 8 entries and won't pick up a 9th catalog id.
- [ ] **GREEN**: Replace the two hardcoded tuples with catalog iteration:
  ```python
  cargo_resources=tuple(
      (res, fleet.resources.get_fleet_cargo_current(res))
      for res in ResourceCatalog.from_json().all_ids()
  ),
  cargo_capacities=tuple(
      (res, fleet.resources.get_fleet_cargo_capacity(res))
      for res in ResourceCatalog.from_json().all_ids()
  ),
  ```
- [ ] Run targeted tests; confirm both new tests now pass and the existing `test_fleet_dto.py` tests still pass.
- [ ] **Verify stability**: the catalog returns IDs in a deterministic order (per PROJ-436 Phase 7's contract). If any existing test asserts on the exact order of `cargo_resources`, verify it still passes — if not, that test's assertion was order-dependent and should be re-pointed at a set comparison.
- [ ] Update DI-2026-05-18-003 in `AgentCoordination/discovered_issues/log.jsonl` with `"status": "resolved"` and a `"resolution_note"` referencing PROJ-452 Phase 2.

**Notes:** [Filled during implementation.]

---

### Task 2.2: Verify no other hardcoded 8-tuple residue in fleet_dto.py [Simple]
**File:** `game/strategy/facade/dto/fleet_dto.py` (full file)

- [ ] `rg -n '"metals".*"organics".*"vapors"' game/strategy/facade/dto/fleet_dto.py` — should return zero matches after Task 2.1.
- [ ] Read through the full `fleet_dto.py` file and confirm no other field uses a hardcoded resource ID list. (Pre-audit per Codex 2026-05-19: the 8-tuple at 230-239 is the only known site; this task is a backstop.)
- [ ] If a second site is found, treat it as in-scope for this phase and apply the same `ResourceCatalog.from_json().all_ids()` transformation.

**Notes:** [Filled during implementation.]

---

## Phase Completion Checklist

When all tasks above are checked off:

- [ ] DI-2026-05-18-003 marked `resolved` in `log.jsonl`
- [ ] Both new tests in `test_fleet_dto.py` green
- [ ] `pytest tests/unit/strategy/facade/test_fleet_dto.py -v` green
- [ ] Full sharded suite green (`python Tools/test_sharded/test_sharded.py`)
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-452 2` — PASSED
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3

## Notes / Deferrals

- **`FleetInfo.passenger_capacity` / `passengers_current`** at lines 227-228 — these reference a single `"passengers"` slot; not in scope for DI-003 (which targets the cargo_resources / cargo_capacities tuples specifically).
- **`carried_items_summary` / `carried_vehicles_by_type`** — these are separate helpers on the same DTO; pre-audit shows they iterate dynamically over ship `bay_inventory` contents, not over a hardcoded resource list. Out of scope.
- **`ContainerSnapshotInfo`** (PROJ-437's new SoT for the transfer UI) — already catalog-driven; do not retouch.
