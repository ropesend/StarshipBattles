# Phase 5: Drop `IShipInstance.cargo_contents` caveat + tighten `IFacility.consumable_levels`

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-449 5`
> 2. Sharded suite green (`python Tools/test_sharded/test_sharded.py`)
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** phase_4 (concrete-class setter deletion)
**Objective:** Drop the F-C-014 "not read-only in absolute terms" caveat in `IShipInstance.cargo_contents` docstring (now actually read-only — Phase 4 deleted the setter). Tidy the parallel `IFacility.consumable_levels` docstring to remove any "until PROJ-444 lands" cross-references that no longer apply.

**File ownership rule:** Protocol-only doc edits in `game/core/protocols/strategy_domain.py`. No production logic changes.

**Source-of-truth findings:** F-C-014 — see [findings/PROJ-449_findings.md](findings/PROJ-449_findings.md).

---

## Tasks

### Task 5.1: Rewrite `IShipInstance.cargo_contents` docstring [Simple]
**File:** `game/core/protocols/strategy_domain.py`
**Tests:** `pytest tests/static_guards/test_no_legacy_protocol_names.py tests/unit/core/protocols/ -n 4 -q`

- [x] At lines 208-233, locate the existing docstring (post-PROJ-446 Phase 2 narrowed it to `Mapping[str, int]`)
- [x] Delete lines 213-224 (the "PROJ-436 Phase 3f:" block + "PROJ-446 Phase 2 (F-C-014):" block describing the "not read-only in absolute terms" caveat and the **stale "PROJ-444 Phase 3" cross-reference** — codex r5 NEW-1 verified this stale project ID is in the live docstring; the current retirement project is PROJ-449 itself)
- [x] Replace with a tight current-behavior docstring:
  ```python
      @property
      def cargo_contents(self) -> Mapping[str, int]:
          """Cargo contents (cargo_type -> current amount), read-only view.

          PROJ-449 Phase 5 (F-C-014 closure): the concrete-class setter
          was retired alongside the legacy-kwarg constructor wrapper, so
          this property is now read-only end-to-end. Writers should use
          the cargo manager API on the concrete class:
          ``ship._cargo_mgr.set_cargo`` / ``get_all_cargo`` /
          ``total_cargo_units`` / ``has_cargo``.
          """
          ...
  ```
- [x] Run focused tests; verify `test_no_legacy_protocol_names.py` still pins what it should pin (the absence of legacy *names*, not the caveat text)
- [x] Run any test in `tests/unit/core/protocols/` if present

**Notes:** The annotation `Mapping[str, int]` is already in place from PROJ-446 Phase 2; this task is pure docstring cleanup.

### Task 5.2: Tighten `IFacility.consumable_levels` docstring [Simple]
**File:** `game/core/protocols/strategy_domain.py`
**Tests:** `pytest tests/static_guards/test_no_legacy_protocol_names.py -q`

- [x] At lines 146-166, locate the existing F-C-013 docstring
- [x] Confirm: the "kept as `dict[str, float]` rather than `Mapping[str, float]`" framing is a deliberate-design choice (PROJ-436 Phase 0 D1). DO NOT change the annotation.
- [x] Drop any reference to "PROJ-444 wrapper retirement" if present (the cross-reference was implicit; verify by reading the current docstring)
- [x] Confirm the static-guard test `test_ifacility_still_declares_consumable_levels` still passes (it pins the *presence* of the writable annotation by deliberate choice)

**Notes:** This task is mostly verification, not edit. The F-C-013 finding categorized the writable dict as "tech debt that's deliberately preserved." PROJ-449 doesn't change that classification — it only ensures the docstring doesn't mention now-deleted wrappers.

### Task 5.3: Run focused + sharded suite [Medium]
**Tests:** focused, then `python Tools/test_sharded/test_sharded.py`

- [x] Focused: `pytest tests/static_guards/test_no_legacy_protocol_names.py tests/unit/strategy/ship_instance/ -n 4 -q`
- [x] Sharded suite green
- [x] Commit message: `PROJ-449 Phase 5: drop IShipInstance.cargo_contents 'not read-only' caveat (closes F-C-014)`

---

## Phase Completion Checklist
- [x] `IShipInstance.cargo_contents` docstring rewritten — no "not read-only in absolute terms" caveat, no "until PROJ-444" reference
- [x] `IFacility.consumable_levels` docstring verified clean (no PROJ-444 cross-references)
- [x] Focused + sharded suites green
- [x] F-C-014 closed (completes the protocol-side half that PROJ-446 Phase 2 started)
- [x] Plan.md Quick Status → Complete; Current State updated

## Notes / Risks / Coordination Touchpoints
- **Phase 4 is the precondition.** This phase only makes sense after the concrete-class setter is gone; running it before Phase 4 would create a lying protocol docstring.
- **No annotation change.** Both protocols already have the correct annotations from PROJ-446 Phase 2. This is pure docstring cleanup.
- **F-C-013 stays open by design.** PROJ-436 Phase 0 D1 chose to keep `IFacility.consumable_levels` writable. PROJ-449 does not reverse that choice.
