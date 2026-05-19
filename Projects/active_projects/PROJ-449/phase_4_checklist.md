# Phase 4: Delete `_ship_instance_init_with_legacy_kwargs` + 2 ShipInstance @property/@setter pairs

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-449 4`
> 2. Sharded suite green (`python Tools/test_sharded/test_sharded.py`)
> 3. Update plan.md phase table AND Current State

**Status:** Complete (with scope adjustment matching Phase 3)
**Depends on:** phase_3
**Objective:** Delete the ShipInstance legacy-kwarg wrapper and the 2 `@property`/`@setter` blocks. The Phase 2 audit + sweep covered the test footprint; this phase is a pure dead-code deletion.

**File ownership rule:** This project owns ShipInstance wrapper + property deletion in `game/strategy/data/ship_instance.py`. No engine / facade / UI edits in this phase.

**Source-of-truth findings:** F-A-003 (wrapper), F-A-005 (2 property/setter pairs) — see [findings/PROJ-449_findings.md](findings/PROJ-449_findings.md). Also closes the PROJ-443 Phase 5b deferred deletion-of-record.

---

## Tasks

### Task 4.1: RED — add a failing static guard test [Simple]
**File:** `tests/static_guards/test_no_ship_instance_legacy_kwarg_wrapper.py` (new)
**Tests:** `pytest tests/static_guards/test_no_ship_instance_legacy_kwarg_wrapper.py -q`

- [x] Create a new static-guard test asserting:
  - `not hasattr(ship_instance_module, "_ship_instance_init_with_legacy_kwargs")`
  - `not hasattr(ShipInstance, "consumable_levels")` (the @property goes away — only `_consumable_levels` field remains)
  - `not hasattr(ShipInstance, "cargo_contents")`
- [x] Run the test; expect 3 assertion failures (RED)

**Notes:** Mirror the Phase 3.1 sibling guard for Planet.

### Task 4.2: GREEN — delete `_ship_instance_init_with_legacy_kwargs` [Medium]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/ship_instance/ -n 4 -q` then sharded

- [x] Delete lines 786-833 (the Phase-3f comment block + `_dataclass_init = ShipInstance.__init__` + `_ship_instance_init_with_legacy_kwargs` function + the assignment `ShipInstance.__init__ = _ship_instance_init_with_legacy_kwargs`)
- [x] Run focused unit tests: `pytest tests/unit/strategy/ship_instance/ tests/unit/strategy/data/test_ship_instance_container_views.py -n 4 -q`. Expect them to pass.
- [x] If any test fails: same recovery as Phase 3 Task 3.2 — most likely a missed call site
- [x] Verify Task 4.1's guard now has 2 RED assertions remaining (the property assertions)

### Task 4.3: GREEN — delete the 2 @property/@setter blocks [Medium]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/ship_instance/ tests/unit/strategy/data/test_ship_instance_container_views.py -n 4 -q` then sharded

- [x] Delete the comment block + 2 property/setter pairs at lines 224-262 (`# These properties expose the underlying...` through the `cargo_contents` setter)
- [x] Run focused unit tests. Expect them to pass.
- [x] If any test fails on `ship.consumable_levels` / `ship.cargo_contents` attribute access:
  - Migrate the read to `ship._consumable_levels` / `ship._cargo_contents` OR (better) to the cargo manager API (`ship._cargo_mgr.set_cargo(...)`, `get_all_cargo()`, `total_cargo_units()`, `has_cargo()`)
  - Capture the rewrite pattern in `decisions.md` so PROJ-451's audit (if relevant) doesn't surface the same path again

**Notes:** PROJ-446 Phase 2 already narrowed the *protocol* annotation to `Mapping[str, int]`. This phase deletes the concrete-class setters that were the reason the protocol docstring carried the "not read-only in absolute terms" caveat — Phase 5 then drops that caveat.

### Task 4.4: Confirm Task 4.1 guard is fully GREEN [Simple]
**Tests:** `pytest tests/static_guards/test_no_ship_instance_legacy_kwarg_wrapper.py -q`

- [x] Static guard green
- [x] Commit Tasks 4.1-4.4 as a single phase commit (or 2-3 commits)
- [x] Commit message: `PROJ-449 Phase 4: delete ShipInstance legacy-kwarg wrapper + 2 property/setter pairs (closes F-A-003 + F-A-005; supersedes PROJ-443 Phase 5b deferred)`

### Task 4.5: Measure `ship_instance.py` LOC + record decision [Simple]
**File:** `Projects/active_projects/PROJ-449/decisions.md`
**Measurement command (PowerShell):** `(Get-Content game/strategy/data/ship_instance.py | Measure-Object -Line).Lines`

- [x] After Tasks 4.2 + 4.3 land, measure ship_instance.py LOC using the PowerShell command above
- [x] Expected drop: ~50 LOC (wrapper block ~30 LOC + property cluster ~25 LOC)
- [x] Pre-phase LOC was 839; expected post-phase ~789
- [x] Add a decisions.md row: "Phase 4 closed — ship_instance.py at NNN LOC. Codex r4 follow-up trigger condition (job 11 of redesign) ACTIVE if NNN > 750; NOT triggered if NNN ≤ 750."
- [x] Either way, F-A-007 (the 839→500 LOC reduction) stays out of PROJ-449 scope per Codex r4: "F-A-007 should not be smuggled in as a side quest; if it still sits at 839 LOC after job 1, spin it as its own next-touch project."

### Task 4.6: Run full sharded suite [Medium]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Sharded suite green at the same pre-phase count
- [x] Mark phase complete

---

## Phase Completion Checklist
- [x] Static guard `test_no_ship_instance_legacy_kwarg_wrapper.py` exists and is green
- [x] `_ship_instance_init_with_legacy_kwargs` deleted from `ship_instance.py`
- [x] 2 @property/@setter blocks deleted from `ship_instance.py`
- [x] `ship_instance.py` LOC measured + decision row in `decisions.md`
- [x] Sharded suite green
- [x] PROJ-443 Phase 5b deferred deletion is now closed (note in `decisions.md`)
- [x] Plan.md Quick Status → Complete; Current State updated

## Notes / Risks / Coordination Touchpoints
- **PROJ-443 Phase 5b reversed.** The wrapper retention rationale (2026-05-17 row) was sized for ~18 files. PROJ-449 Phase 0 verified the current count; Phase 2 swept; Phase 4 deletes. Add a decisions.md row referencing the PROJ-443 supersession.
- **Risk: the audit missed a site.** Identical recovery to Phase 3.
- **F-A-007 is out of scope.** Even if `ship_instance.py` lands at 789 LOC after Phase 4, this project does not split the file further. Codex r4 explicitly named that as a separate follow-up project.
- **Protocol cleanup is Phase 5.** The "not read-only in absolute terms" caveat on `IShipInstance.cargo_contents` is the next item.
