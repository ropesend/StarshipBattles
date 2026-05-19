# Phase 1: Path A engine-only API cleanup (typed accept + typed pop)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-450 1`
> 2. Sharded suite green (`python Tools/test_sharded/test_sharded.py`)
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** phase_0 (PROJ-449 Phase 3 confirmed; audit re-verified)
**Objective:** Execute Stage 3 preflight §3.1 Path A. Widen `Planet.add_to_staging_yard()` to accept `Dict | CarriedVehicle | DropPod`; add `Planet.pop_staging_yard_typed(index)`; move the 3 helpers from `transfer_branches.py` into `planet.py`. Engine handlers drop their flatten/inflate. **Substrate stays `List[Dict[str, Any]]`** — Phase 2 widens the type. Save format unchanged.

**File ownership rule:** This project owns the full data/engine/UI substrate change. Phase 1 touches Planet + 3 engine files. No UI / validator / write-service / DTO / facade edits in this phase.

**Source-of-truth findings:** F-B-013, DI-2026-05-18-001 substrate half — see [findings/PROJ-450_findings.md](findings/PROJ-450_findings.md).

---

## Tasks

### Task 1.1: RED — write the typed-API contract tests [Medium]
**File:** `tests/unit/strategy/data/test_planet_staging_yard_typed_api.py` (new)
**Tests:** `pytest tests/unit/strategy/data/test_planet_staging_yard_typed_api.py -q`

- [ ] Create the new test file. Cover:
  - `test_add_to_staging_yard_accepts_typed_carried_vehicle`: pass a `CarriedVehicle(...)` instance to `planet.add_to_staging_yard(cv)`; assert it lands in the internal list (currently still dict-shaped — assert via dict-projection)
  - `test_add_to_staging_yard_accepts_typed_drop_pod`: same with `DropPod(...)`
  - `test_add_to_staging_yard_accepts_dict_backward_compat`: pass a legacy dict; assert it still works
  - `test_pop_staging_yard_typed_returns_carried_vehicle`: add a typed CV, pop via `pop_staging_yard_typed(0)`, assert it returns a `CarriedVehicle` instance with correct fields
  - `test_pop_staging_yard_typed_returns_drop_pod`: same with `DropPod`
  - `test_pop_staging_yard_typed_handles_dict_storage`: add a dict, pop via typed API, assert it promotes to typed correctly using vehicle_type discriminator
  - `test_pop_staging_yard_typed_returns_drop_pod_fallback_on_unknown_vehicle_type`: dict with unknown `vehicle_type` → `DropPod` fallback
  - `test_pop_staging_yard_typed_returns_none_on_out_of_range`: invalid index → `None`
- [ ] Run; expect 7+ failures (methods don't exist yet — RED is correct)

### Task 1.2: GREEN — move the 3 helpers from `transfer_branches.py` into `planet.py` [Medium]
**Files:** `game/strategy/data/planet.py`, `game/strategy/engine/order_handlers/transfer_branches.py`
**Tests:** `pytest tests/unit/strategy/data/test_planet_staging_yard_typed_api.py tests/unit/strategy/engine/ -n 4 -q`

- [ ] Move `_is_carried_vehicle_dict` from `transfer_branches.py:41-52` to `planet.py` (module-level private helper)
- [ ] Move `_pod_from_dict` from `transfer_branches.py:55-73` to `planet.py`
- [ ] Move `_staging_yard_carried_vehicle` from `transfer_branches.py:76-87` to `planet.py`
- [ ] In `transfer_branches.py`, remove the 3 helper definitions; replace internal call sites with imports from `planet.py` (or, where Phase 1.3 deletes them, drop entirely)
- [ ] Verify focused tests pass

**Notes:** These helpers are private and module-level — keep the leading underscore. Use them inside Planet methods only.

### Task 1.3: GREEN — widen `Planet.add_to_staging_yard()` + add `pop_staging_yard_typed()` [Medium]
**File:** `game/strategy/data/planet.py`
**Tests:** `pytest tests/unit/strategy/data/test_planet_staging_yard_typed_api.py -q`

- [ ] Locate `add_to_staging_yard` at lines 316-322 (post-PROJ-449 Phase 3). Change signature from:
  ```python
  def add_to_staging_yard(self, item: Dict[str, Any]) -> bool:
  ```
  to:
  ```python
  def add_to_staging_yard(self, item: Dict[str, Any] | CarriedVehicle | DropPod) -> bool:
  ```
- [ ] In the body, normalize the input to dict (since the substrate is still dict-typed in Phase 1):
  ```python
  if isinstance(item, (CarriedVehicle, DropPod)):
      item_dict = item.to_dict()
  else:
      item_dict = item
  item_mass = item_dict.get('mass', 0.0)
  if self.max_staging_mass > 0 and self.get_staging_mass() + item_mass > self.max_staging_mass:
      return False
  self._staging_yard.append(item_dict)
  return True
  ```
- [ ] Add `pop_staging_yard_typed(self, index: int) -> CarriedVehicle | DropPod | None`:
  ```python
  def pop_staging_yard_typed(self, index: int) -> "CarriedVehicle | DropPod | None":
      """Pop and return the item at `index` as a typed CarriedVehicle or DropPod."""
      raw = self.remove_from_staging_yard(index)
      if raw is None:
          return None
      cv = _staging_yard_carried_vehicle(raw)
      if cv is not None:
          return cv
      return _pod_from_dict(raw)
  ```
- [ ] Run Task 1.1's tests; they should all pass

### Task 1.4: GREEN — drop flatten/inflate calls in `transfer_branches.py` [Medium]
**File:** `game/strategy/engine/order_handlers/transfer_branches.py`
**Tests:** `pytest tests/unit/strategy/engine/test_pod_transfer.py tests/unit/strategy/engine/order_handlers/test_transfer_handler.py -n 4 -q`

- [ ] At line 412, change:
  ```python
  if planet.add_to_staging_yard(cv.to_dict()):
  ```
  to:
  ```python
  if planet.add_to_staging_yard(cv):
  ```
- [ ] At lines 454-460, drop the `pod_dict = dict(pod.payload); pod_dict["design_id"] = ...; planet.add_to_staging_yard(pod_dict)` flatten block; change to:
  ```python
  if planet.add_to_staging_yard(pod):
  ```
- [ ] In `_dispatch_drop_pod_load` at lines 200-250, replace `_pod_from_dict(removed)` calls with `planet.pop_staging_yard_typed(i)` — change the loop so it pops via the typed API rather than calling `remove_from_staging_yard` then `_pod_from_dict`
- [ ] Similar migration in `_dispatch_carried_vehicle_load` at lines 340-380 — pop via `pop_staging_yard_typed` instead of `_staging_yard_carried_vehicle(item)` after `remove_from_staging_yard`
- [ ] Run focused tests; expect them to pass (transparent change to engine semantics)

### Task 1.5: GREEN — drop `vehicle.to_dict()` flatten in `issuer_adapter.py` [Simple]
**File:** `game/strategy/engine/issuer_adapter.py`
**Tests:** `pytest tests/unit/strategy/engine/test_issuer_adapter.py -n 4 -q`

- [ ] At line 363, change:
  ```python
  return bool(self._planet.add_to_staging_yard(vehicle.to_dict()))
  ```
  to:
  ```python
  return bool(self._planet.add_to_staging_yard(vehicle))
  ```
- [ ] Run focused tests

### Task 1.6: Production_spawner integration test [Simple]
**File:** `tests/integration/strategy/facade/test_fleet_to_fleet_drop_pod.py` (new — recommended in Stage 3 preflight §4.1)
**Tests:** `pytest tests/integration/strategy/facade/test_fleet_to_fleet_drop_pod.py -q`

- [ ] Create the integration test that verifies the PROJ-445 Phase 2 fleet-to-fleet pod path continues to work after Phase 1's engine cleanup
- [ ] Fleet A unloads a `DropPod` to planet; planet `pop_staging_yard_typed(0)` returns a `DropPod` instance with original `design_id` / `mass` / `payload`
- [ ] Run; verify green

### Task 1.7: Full sharded suite + commit [Medium]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Sharded suite green at the pre-phase count + new test count (Task 1.1 added 7+ tests; Task 1.6 added 1+)
- [ ] Commit message: `PROJ-450 Phase 1: Path A engine API cleanup — typed accept + typed pop (centralizes dict↔typed helpers in Planet)`

---

## Phase Completion Checklist
- [ ] 3 helpers moved from transfer_branches.py to planet.py
- [ ] `Planet.add_to_staging_yard` accepts typed inputs
- [ ] `Planet.pop_staging_yard_typed` exists and returns typed views
- [ ] `transfer_branches.py` flatten blocks at 412 + 454-460 dropped
- [ ] `issuer_adapter.py:363` flatten dropped
- [ ] New unit + integration tests green
- [ ] Sharded suite green
- [ ] Plan.md Quick Status → Complete; Current State updated
- [ ] **Note in plan.md**: substrate is still `List[Dict[str, Any]]` — Phase 2 changes the type

## Notes / Risks / Coordination Touchpoints
- **PROJ-451 has no dependency here.** It can run in parallel.
- **Save format unchanged.** Dict shape on disk continues; the dict↔typed conversion now happens inside Planet, not at every engine boundary.
- **`production_spawner.py` not yet migrated.** Per preflight §3.1: "Decision: keep dict for now; cleaner once substrate is fully typed." Phase 2 takes this on.
- **`_dispatch_drop_pod_load` and `_dispatch_carried_vehicle_load` semantics preserved.** The migration from "pop via `remove_from_staging_yard` then `_pod_from_dict`" to "pop via `pop_staging_yard_typed`" must be exact — both forms produce the same typed value.
- **Risk: engine handlers' rollback paths.** `transfer_branches.py:373` re-appends `removed` via `add_to_staging_yard(removed)`. After Phase 1, `removed` is no longer typed (it's still the raw `remove_from_staging_yard` dict). Verify the rollback path is exercised by tests, and that re-adding the dict goes through the now-widened `add_to_staging_yard`.
