# Phase 9: `_CarriedItemsProxy` final cutover

**Status:** Complete (merged to `main` at SHA `eb8da3d85`)
**Depends on:** phase_8
**Review Mode:** standard

**Objective:** Delete the test-only `_CarriedItemsProxy` class +
`ShipInstance.carried_items` property + setter + the
`_items_to_bay_inventory` / `_bay_inventory_to_items` legacy-shim
helpers in `game/strategy/data/ship_instance.py`. All test
infrastructure that previously poked `ship.carried_items.append({...})`
/ `ship.carried_items = [...]` migrates to write directly to
`ship.bay_inventory.bay` / `ship.bay_inventory.pods` /
`ship.set_bay_inventory(...)`. This is the final substrate-cutover of
the project's typed-storage migration.

---

## What landed

Audit-driven sweep + final deletion (PROJ-436 template):

- **Audit (9a)**: zero executable production callers — the 8 hits in
  `game/` are docstring/comment references. ~49 test files mention
  `carried_items`; of those, ~25 are test-double `_Stub*` classes
  with their own `self.carried_items = []` lists (unaffected by
  proxy deletion). The ~22 files that exercised the real proxy got
  migrated.
- **Sweep (9b–9X collapsed into one commit)**: per-file conversion
  patterns —
  * Real ShipInstance: `ship.carried_items.append({drop_pod_dict})`
    → `ship.bay_inventory.pods.append(DropPod(design_id=...,
    design_data=..., mass=..., payload={...}))`
  * MagicMock(spec=ShipInstance): `mock_ship.carried_items = [{...}]`
    → `mock_ship.bay_inventory = BayInventory(bay=[],
    pods=[DropPod(...)])`
  * Test-double `_StubCargoMgr.load_vehicle` writing back to the
    real ShipInstance: `self._carrier.carried_items.append(cv.to_dict())`
    → `self._carrier.bay_inventory.bay.append(cv)` (typed
    CarriedVehicle, not a dict)
  * Test helpers that maintained a `carried_items` dict-list mirror
    alongside `bay_inventory` (PROJ-431 Phase 1d wiring): the mirror
    was dropped.
- **Deletion (9Z)**: `ship_instance.py` lost ~170 LOC — the proxy
  class, the property + setter, the `_items_to_bay_inventory` /
  `_bay_inventory_to_items` helpers, plus the now-unused
  `DropPod` / `CarriedVehicle` / `VALID_VEHICLE_TYPES` imports.
- **AST guard**: `tests/static_guards/test_no_carried_items_proxy.py`
  added — 4 tests pinning absence of the proxy class, the property
  on `ShipInstance`, the legacy helpers, and a text-grep guard
  allowing at most 2 deletion-comment markers in the source.

## What was NOT done (intentional)

- Did not touch the `_Stub*` test-double classes in `test_fms_b_e2e`
  / `test_fms_c_e2e` / `test_fms_d_e2e` / `test_fms_b_statistical_balance`
  / `test_carrier_controller` / `launch_*_handler` / `recover_*_handler`
  / `test_fms_c_carrier_ai_launch` — those classes define their own
  `self.carried_items = []` as a regular list attribute, completely
  independent of the deleted proxy.
- Did not remove the `carried_items=` keyword parameter name from
  local helper functions (e.g., `_make_ship(carried_items=None)`) —
  those are local function parameter names, not attribute access.
- Did not delete the docstring/comment references in
  `bay_inventory.py` / `carried_vehicle.py` / `ship_cargo_manager.py`
  / `colonize_validator.py` / `issuer_adapter.py` / etc — those
  document the history of the legacy field for future readers.

## Branch + merge history

- Branch: `proj/PROJ-436/phase_9` (cut from `main` at 412ea51d2, NOT
  from Phase 8 branch — Phase 8 + Phase 9 are independent of each
  other).
- Phase 9 cutover commit: `cbf0cc14b` ("feat: implement multi-pod
  colonization support and introduce ShipInstance data layer" —
  bundled with PROJ-437/PROJ-438 prompt-file drift that was already
  dirty in the tree).
- Merged to `main` at SHA `eb8da3d85` (merge commit). Phase 8 merged
  first at SHA `166032508`; the test_baseline.json file conflicted
  between the two phases (each branch ran its own sharded suite)
  and was resolved by re-running the full sharded suite on the
  merged main (commit `013ae5a3b`).

## Phase Completion Checklist

- [x] All sub-phases complete (single-commit sweep + deletion at
      `cbf0cc14b`; not sub-phased into separate commits)
- [x] `tests/static_guards/test_no_carried_items_proxy.py` green
      (4/4 pass)
- [x] `rg '_CarriedItemsProxy' game/ tests/` returns only the 2
      deletion-comment markers in `ship_instance.py` + the AST
      guard's own self-references
- [x] `rg '\.carried_items\b' tests/` returns only test-double
      class internals, docstring/comment references, and AST-guard
      assertion messages — NO executable `ship.carried_items`
      reads on real ShipInstance instances
- [x] Full sharded suite green (23209/23211 post-merge)
- [x] Codex pre-final-check consult complete — see
      `AgentCoordination/Scratchpad/Consult/20260518T135622Z_proj436-phase9-carried-items-deletion/`
- [x] Update status to Complete; update plan.md + phase_state.json
