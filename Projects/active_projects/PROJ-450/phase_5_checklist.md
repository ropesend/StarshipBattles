# Phase 5: Static guard updates (type-pin tightening)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-450 5`
> 2. Sharded suite green
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** phase_4
**Objective:** Tighten the static guard at `tests/static_guards/test_no_legacy_storage_fields.py` to pin the new typed substrate. Add an AST or runtime assertion that every entry in `_staging_yard` is `CarriedVehicle` or `DropPod` — no dicts permitted.

**File ownership rule:** Phase 5 owns the static-guard update + any related ratchet test. No production changes.

**Source-of-truth findings:** Stage 3 preflight §6 — see [findings/PROJ-450_findings.md](findings/PROJ-450_findings.md).

---

## Tasks

### Task 5.1: Read current static guard [Simple]
**File:** `tests/static_guards/test_no_legacy_storage_fields.py`
**Tests:** none (research task)

- [ ] Read the existing file. Identify what it currently pins:
  - Per Phase 0 audit + the PROJ-446 finding context: "test_no_legacy_storage_fields.py: re-check; current text doesn't pin the TYPE, but the comment at line 9 mentions `staging_yard` as a dataclass field shape"
- [ ] Confirm whether the guard pins the absence of a public `staging_yard` field (the dataclass form) and whether it pins the type of `_staging_yard`

### Task 5.2: RED — write the tightened guard [Simple]
**File:** `tests/static_guards/test_no_legacy_storage_fields.py` (extend)
**Tests:** `pytest tests/static_guards/test_no_legacy_storage_fields.py -q`

- [ ] Add a new test case:
  ```python
  def test_planet_staging_yard_substrate_is_typed_not_dict(fresh_registries):
      """PROJ-450 Phase 5: pin the typed substrate.

      After PROJ-450 widening, Planet._staging_yard holds typed
      CarriedVehicle | DropPod entries only. A regression that re-adds
      raw dicts via .append(legacy_dict) is caught here.
      """
      from game.strategy.data.planet import Planet
      from game.strategy.data.carried_vehicle import CarriedVehicle
      from game.strategy.data.drop_pod import DropPod  # verify path
      planet = Planet(
          name="GuardPlanet",
          location=HexCoord(0, 0),
          # ... minimal valid construction
      )
      # Inject a typed entry via the public API
      planet.add_to_staging_yard(CarriedVehicle(
          design_id="x",
          vehicle_type="mine",
          design_data={"name": "M"},
          mass=1.0,
      ))
      # Verify substrate stores it as typed
      assert all(
          isinstance(item, (CarriedVehicle, DropPod))
          for item in planet._staging_yard
      ), f"_staging_yard must hold typed entries only, got: {[type(x).__name__ for x in planet._staging_yard]}"
  ```
- [ ] Optional: add an AST guard that scans `game/strategy/data/planet.py` for the substrate annotation `List[CarriedVehicle | DropPod]`
- [ ] Run; expect green (Phase 2 made the substrate typed)

### Task 5.3: Verify ASTguard tests [Simple]
**File:** `tests/unit/strategy/data/test_mutator_boundary_ast_guard.py`, `tests/unit/strategy/data/test_mutator_boundary_ast_guard_self_test.py`
**Tests:** `pytest tests/unit/strategy/data/test_mutator_boundary_ast_guard.py -q`

- [ ] Verify the mutator-boundary AST guard still passes (it checks that production code mutates planet state ONLY through write services; typed substrate doesn't change that contract)
- [ ] If the guard depends on specific method signatures that changed (e.g. `add_to_staging_yard(item: Dict)` → `add_to_staging_yard(item: Dict | CarriedVehicle | DropPod)`), update the guard expectations

### Task 5.4: Update test_no_legacy_protocol_names.py if needed [Simple]
**File:** `tests/static_guards/test_no_legacy_protocol_names.py`
**Tests:** `pytest tests/static_guards/test_no_legacy_protocol_names.py -q`

- [ ] Verify this static guard, which pins the protocol-side shapes, still passes after `IStagingYardHolder` was widened in Phase 2
- [ ] If any assertion pins the dict shape of `staging_yard`, update to the new typed shape

### Task 5.5: Run full sharded suite + commit [Medium]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Sharded suite green
- [ ] Commit message: `PROJ-450 Phase 5: tighten static guards to pin typed staging-yard substrate (closes F-B-013)`

---

## Phase Completion Checklist
- [ ] Static guard `test_no_legacy_storage_fields.py` extended with typed-substrate assertion
- [ ] Mutator-boundary AST guard verified green (or updated to match new signatures)
- [ ] `test_no_legacy_protocol_names.py` verified green (or updated for protocol widening)
- [ ] Sharded suite green
- [ ] F-B-013 fully closed
- [ ] Plan.md Quick Status → Complete; Current State updated → project ready for end-of-project Codex consult

## Notes / Risks / Coordination Touchpoints
- **This is the closure phase.** After Phase 5, F-B-013 is fully closed and DI-2026-05-18-001 substrate half is fully closed.
- **No new code paths.** Phase 5 is pure static guard tightening — defensive against regressions.
- **PROJ-451 unaffected.** Production resource consumption is orthogonal.
- **Codex r4 job 11 unblocked.** "Strategy data LOC extractions" lists PROJ-450 as a precondition; after this phase, job 11's `planet.py` work can plan around the typed substrate.
