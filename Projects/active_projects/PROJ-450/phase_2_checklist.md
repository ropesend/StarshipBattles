# Phase 2: Substrate widening (`_staging_yard: List[CarriedVehicle | DropPod]`) + serde normalization

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-450 2`
> 2. Sharded suite green (`python Tools/test_sharded/test_sharded.py`)
> 3. Save-load round-trip verified against `tests/fixtures/saves/galaxy_proj372_populated.json`
> 4. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** phase_1 (typed accept + typed pop in place)
**Objective:** Change the substrate type — `_staging_yard: List[Dict[str, Any]]` → `List[CarriedVehicle | DropPod]`. Add `planet_serde._normalize_to_typed()` for save-load round-trip. **Substrate is now typed end-to-end internally**, but a one-phase `staging_yard` dict-projection property stays alive so the UI reader still works until Phase 3 migrates it.

**Silent-mutation risk (2026-05-19 codex audit fix):** Phase 2's bridge returns `[item.to_dict() for item in self._staging_yard]` — a *fresh* list of dicts. In-place mutations on the returned list (e.g. `planet.staging_yard.clear()`, `planet.staging_yard.append(d)`) would silently no-op against `_staging_yard`. Task 2.0 below migrates the one known in-place-mutation caller (`tests/integration/test_fms_a_e2e.py:305` — `planet.staging_yard.clear()`) BEFORE the bridge lands, so the bridge's read-only-projection semantics are correct from the moment it lands. Phase 4 handles the remaining `.append`/`.extend` mutations against typed callers — those are not affected by this risk because they happen on the OLD substrate (Phase 1 still has dict substrate) and will be re-pointed at typed inputs in Phase 4.

**File ownership rule:** Phase 2 touches Planet + planet_serde + galaxy_protocols + production_spawner. No UI / validator / write-service edits — those wait for Phase 3.

**Source-of-truth findings:** F-B-013 (substrate type widening) — see [findings/PROJ-450_findings.md](findings/PROJ-450_findings.md).

---

## Tasks

### Task 2.0: Pre-migrate the in-place `.clear()` caller (silent-mutation prevention) [Simple]
**File:** `tests/integration/test_fms_a_e2e.py`
**Tests:** `pytest tests/integration/test_fms_a_e2e.py -k "test_fms_a_e2e and clear" -q`

- [ ] At line 305, replace `planet.staging_yard.clear()` with an explicit removal call that survives the Phase-2 read-only projection:
  ```python
  # Pre-Phase-2 (line 305):
  planet.staging_yard.clear()

  # Phase 2.0 — explicit, mutation-safe:
  while planet._staging_yard:
      planet.remove_from_staging_yard(0)
  ```
  OR, if the test fixture supports it, construct the planet without any seeded staging entries in the first place.
- [ ] Run the focused test; verify it passes (the substrate is still dict-typed at this point — the migration is mechanical)
- [ ] Confirm no other `.clear()` / `.append(` / `.extend(` against `planet.staging_yard` survives in the production / integration test surface (Phase 4 covers the `.append(` / `.extend(` sites; Phase 4's substrate-aware migration handles them after the typed substrate lands)

**Notes (2026-05-19 codex audit fix):** Codex flagged that Phase 2's `staging_yard` projection property returns a fresh list of dicts — any in-place mutation through the public name silently no-ops against `_staging_yard`. Migrating this single caller before Phase 2's bridge lands eliminates the risk window. Phase 4's `.append`/`.extend` migrations are NOT affected (they operate on the substrate before Phase 2 lands; Phase 4 re-points them at typed inputs after Phase 2).

### Task 2.1: RED — substrate-typing contract tests [Medium]
**File:** `tests/unit/strategy/data/test_planet_staging_yard_typed_api.py` (extend existing)
**Tests:** `pytest tests/unit/strategy/data/test_planet_staging_yard_typed_api.py -q`

- [ ] Add tests:
  - `test_staging_yard_internal_storage_is_typed`: after `add_to_staging_yard(typed)`, assert `planet._staging_yard[0]` is `isinstance(..., (CarriedVehicle, DropPod))` (NOT a dict)
  - `test_save_round_trip_preserves_typed_substrate`: serialize via `planet.to_dict()` (which produces dict shape on disk), deserialize via `Planet.from_dict(...)`, assert the resulting `_staging_yard` is again typed
  - `test_save_format_remains_dict_shape`: assert `planet.to_dict()['staging_yard']` is `List[Dict[str, Any]]` — typed objects are flattened back to dict shape ONLY at the save boundary, not in memory
- [ ] Run; expect 3 failures (substrate is still dict-typed)

### Task 2.2: GREEN — change `_staging_yard` type annotation + storage [Complex]
**File:** `game/strategy/data/planet.py`
**Tests:** `pytest tests/unit/strategy/data/ -n 4 -q`

- [ ] Change the dataclass field annotation:
  ```python
  _staging_yard: List[Dict[str, Any]] = field(default_factory=list)
  ```
  to:
  ```python
  _staging_yard: "List[CarriedVehicle | DropPod]" = field(default_factory=list)
  ```
- [ ] Update `add_to_staging_yard`: when accepting a dict, promote to typed via the existing internal helpers BEFORE appending. Replace the Phase-1 normalization that produced a dict with:
  ```python
  if isinstance(item, dict):
      cv = _staging_yard_carried_vehicle(item)
      if cv is not None:
          typed_item = cv
      else:
          typed_item = _pod_from_dict(item)
  else:
      typed_item = item  # already typed
  item_mass = typed_item.mass if hasattr(typed_item, 'mass') else 0.0
  if self.max_staging_mass > 0 and self.get_staging_mass() + item_mass > self.max_staging_mass:
      return False
  self._staging_yard.append(typed_item)
  return True
  ```
- [ ] Update `get_staging_mass`:
  ```python
  def get_staging_mass(self) -> float:
      return sum(getattr(item, 'mass', 0.0) for item in self._staging_yard)
  ```
- [ ] Update `pop_staging_yard_typed`: now trivially returns the typed entry from the list (no dict→typed promotion required); keep the method as the typed-pop API
- [ ] Update `remove_from_staging_yard`: returns the typed entry (no longer a dict). **Note**: this is a semantic change — callers that expected a dict need to adapt. Per Phase 0 audit, the only production caller of `remove_from_staging_yard` is `pop_staging_yard_typed`, so no change at the call site (it just gets a typed thing now).
- [ ] **Add the temporary dict-projection property** for the UI reader (Phase 3 deletes this):
  ```python
  @property
  def staging_yard(self) -> "list[dict[str, Any]]":
      """TEMPORARY dict-projection for Phase 2 → Phase 3 bridge.

      PROJ-450 Phase 2: the internal _staging_yard substrate is now
      typed (List[CarriedVehicle | DropPod]). This projection property
      returns a list of dict views so the UI reader at
      game/ui/screens/strategy_detail_fmt.py:285-297 still works during
      the one-phase migration window. **Phase 3 deletes this property**
      and migrates the UI reader to use typed attribute access directly.
      """
      return [item.to_dict() for item in self._staging_yard]
  ```

### Task 2.2b: NEW-4 — modernize `IStagingYardHolder` protocol typing (codex r5 NEW-4) [Simple]
**File:** `game/strategy/data/galaxy_protocols.py:189-195`

- [ ] Read the current `IStagingYardHolder.add_to_staging_yard` and `remove_from_staging_yard` signatures at lines 189-196. Currently `Dict[str, Any]` and `Optional[Dict[str, Any]]`.
- [ ] Now that the substrate is typed (Task 2.2 widened `_staging_yard` to `List[CarriedVehicle | DropPod]` and `add_to_staging_yard` accepts the union per Phase 1), tighten the protocol annotations to match:
  ```python
  def add_to_staging_yard(self, item: "CarriedVehicle | DropPod | Dict[str, Any]") -> bool:
      """Add ``item``; return False on insufficient capacity."""
      ...

  def remove_from_staging_yard(
      self, index: int
  ) -> "CarriedVehicle | DropPod | None":
      """Remove by index; return removed item or None."""
      ...
  ```
- [ ] The `Dict[str, Any]` union member stays in `add_to_staging_yard` because Task 2.2 widened the implementation to accept dicts too (back-compat for legacy save load). The `remove_from_staging_yard` return tightens to typed-only because the substrate now returns typed entries.
- [ ] Drop unused `Optional` / `Dict` imports if no other signature in the file needs them
- [ ] Run focused tests: `pytest tests/unit/strategy/data/ -k "galaxy_protocols or planet" -n 4 -q`

### Task 2.3: GREEN — `planet_serde._normalize_to_typed` on load [Medium]
**File:** `game/strategy/data/planet_serde.py`
**Tests:** `pytest tests/integration/save_load/test_roundtrip_planet.py -n 4 -q`

- [ ] Add a new module-level helper:
  ```python
  def _normalize_to_typed(
      items: list,
  ) -> "list[CarriedVehicle | DropPod]":
      """Promote save-shape dicts to typed CarriedVehicle / DropPod entries.

      PROJ-450 Phase 2: invoked by planet_from_dict_kwargs so the loaded
      Planet's _staging_yard is typed even though the on-disk save uses
      dicts. Mirrors the discriminator logic from
      _staging_yard_carried_vehicle / _pod_from_dict in planet.py.
      """
      from game.strategy.data.planet import (
          _staging_yard_carried_vehicle,
          _pod_from_dict,
      )
      result = []
      for item in items:
          if isinstance(item, (CarriedVehicle, DropPod)):
              result.append(item)
              continue
          cv = _staging_yard_carried_vehicle(item)
          if cv is not None:
              result.append(cv)
              continue
          result.append(_pod_from_dict(item))
      return result
  ```
- [ ] Update `planet_from_dict_kwargs` at line 159 (post-PROJ-449 Phase 2 rewrite) to call the normalizer:
  ```python
  _staging_yard=_normalize_to_typed(data.get("staging_yard", [])),
  ```
- [ ] Update `planet_to_dict` to serialize each typed entry to its dict form. Find the line that emits `"staging_yard": planet._staging_yard` (or similar) and change to:
  ```python
  "staging_yard": [item.to_dict() for item in planet._staging_yard],
  ```
- [ ] Run focused save-load round-trip test; verify dict-on-disk + typed-in-memory invariant holds

### Task 2.4: GREEN — widen `IStagingYardHolder` protocol [Simple]
**File:** `game/strategy/data/galaxy_protocols.py`
**Tests:** `pytest tests/unit/strategy/data/test_galaxy_protocols.py -q`

- [ ] Locate `IStagingYardHolder` in `galaxy_protocols.py` (Phase 0 audit showed 4 staging_yard refs in this file)
- [ ] Widen any `staging_yard: List[Dict[str, Any]]` annotation to `staging_yard: List[CarriedVehicle | DropPod]`
- [ ] Verify the matching test file `tests/unit/strategy/data/test_galaxy_protocols.py` still pins the right shape

### Task 2.5: GREEN — `production_spawner.py` typed construction [Medium]
**File:** `game/strategy/engine/production_spawner.py`
**Tests:** `pytest tests/unit/strategy/engine/test_production_spawner_staging_yard.py tests/unit/strategy/engine/test_production_spawner.py -n 4 -q`

- [ ] At lines 347-360 (the dict-construction site flagged by Stage 3 preflight §3.1), replace dict-based construction with typed:
  ```python
  # OLD:
  pod_dict = {
      "design_id": ...,
      "design_data": ...,
      "mass": ...,
      "name": ...,
      "vehicle_type": "...",
  }
  planet.add_to_staging_yard(pod_dict)

  # NEW:
  if vehicle_type in VALID_VEHICLE_TYPES:
      cv = CarriedVehicle(...)
      planet.add_to_staging_yard(cv)
  else:
      pod = DropPod(
          design_id=...,
          design_data=...,
          mass=...,
          payload={"name": ...},
      )
      planet.add_to_staging_yard(pod)
  ```
- [ ] Run focused tests

### Task 2.6: Sharded suite + commit [Medium]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Sharded suite green (count + 3 new tests from Task 2.1)
- [ ] Save-load round-trip integration test green
- [ ] Commit message: `PROJ-450 Phase 2: widen Planet._staging_yard to List[CarriedVehicle | DropPod]; serde normalizes on load (closes F-B-013 substrate half)`

---

## Phase Completion Checklist
- [ ] `_staging_yard` substrate is typed `List[CarriedVehicle | DropPod]`
- [ ] `planet_serde._normalize_to_typed` converts dict → typed on load
- [ ] `planet_to_dict` serializes typed → dict on save
- [ ] `IStagingYardHolder` protocol annotation widened
- [ ] `production_spawner.py` constructs typed objects directly
- [ ] **Temporary dict-projection property `staging_yard` ALIVE** (deleted in Phase 3)
- [ ] Save-load round-trip green against `galaxy_proj372_populated.json`
- [ ] Sharded suite green
- [ ] Plan.md Quick Status → Complete; Current State updated

## Notes / Risks / Coordination Touchpoints
- **The Phase-2 dict-projection property is a *deliberate, single-phase migration bridge*, not a permanent shim.** CLAUDE.md's "no compat shims" rule is interpreted as forbidding enduring shims; Phase 3's first commit deletes this property. The Phase-2 commit message should explicitly call out the bridge: "Phase 3 will delete this temp projection."
- **Save format unchanged.** Old saves load via `_normalize_to_typed`. New saves emit identical dict shape via per-entry `.to_dict()`.
- **Risk: `_normalize_to_typed` discriminator drift.** If a save file contains a typed-looking dict whose `vehicle_type` is missing or unexpected, the normalizer falls back to `_pod_from_dict`. Verify this matches the May 2026 Joint A preflight's expected behavior.
- **Risk: rollback path in `transfer_branches.py:373`.** After Phase 2, `removed` from `remove_from_staging_yard` is a TYPED instance. The rollback `add_to_staging_yard(removed)` should work because `add_to_staging_yard` accepts typed inputs (Phase 1 widening). Verify in `test_transfer_handler.py`'s rollback test cases.
- **PROJ-451 unaffected.** Production resource consumption is orthogonal.
