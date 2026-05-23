# Phase 3: Delete `_planet_init_with_legacy_kwargs` + 3 Planet @property/@setter pairs

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-449 3`
> 2. Sharded suite green (`python Tools/test_sharded/test_sharded.py`)
> 3. Update plan.md phase table AND Current State
> 4. PROJ-450 Phase 0 verifies the precondition by direct code inspection (no cross-project write required from this side)

**Status:** Complete (with scope adjustment — see decisions.md)
**Depends on:** phase_2 (sweep complete, wrapper bodies unreached)
**Objective:** Delete the Planet legacy-kwarg wrapper and the 3 `@property`/`@setter` blocks that exist for the same rationale. Update `planet_serde.planet_to_dict` to read `_stockpile` / `_max_stockpile` / `_staging_yard` directly. After this phase, `planet.py` carries no Phase-4f shim residue — the surface is clean for **PROJ-450** to widen `_staging_yard` to a typed substrate.

**File ownership rule:** This project owns Planet wrapper + property deletion in `game/strategy/data/planet.py` and the matching `planet_serde.py` read paths. No engine / facade / UI edits in this phase.

**Source-of-truth findings:** F-A-002 (wrapper), F-A-004 (3 property/setter pairs) — see [findings/PROJ-449_findings.md](findings/PROJ-449_findings.md).

---

## Tasks

### Task 3.1: RED — add a failing static guard test [Simple]
**File:** `tests/static_guards/test_no_planet_legacy_kwarg_wrapper.py` (new)
**Tests:** `pytest tests/static_guards/test_no_planet_legacy_kwarg_wrapper.py -q`

- [x] Create a new static-guard test asserting:
  - `not hasattr(planet_module, "_planet_init_with_legacy_kwargs")`
  - `not hasattr(Planet, "stockpile")` (the @property goes away — only `_stockpile` field remains)
  - `not hasattr(Planet, "max_stockpile")`
  - `not hasattr(Planet, "staging_yard")`
- [x] Run the test; expect 4 assertion failures (RED — the wrapper and properties still exist)
- [x] Commit RED test in its own commit OR fold into Task 3.2's commit; choose per repo discipline
- [x] Verify the test file follows the sibling guards' pattern (see `tests/static_guards/test_no_legacy_storage_fields.py` for an existing pattern)

**Notes:** This guard pins the *absence* of the wrapper after deletion. The sibling `tests/static_guards/test_no_legacy_storage_fields.py` already pins the absence of the dataclass field names; this new guard adds the post-deletion property absence.

### Task 3.2: GREEN — delete `_planet_init_with_legacy_kwargs` [Medium]
**File:** `game/strategy/data/planet.py`
**Tests:** `pytest tests/unit/strategy/data/ -n 4 -q` then sharded

- [x] Delete lines 381-420 (the Phase-4f comment block + `_dataclass_init = Planet.__init__` + `_planet_init_with_legacy_kwargs` function + the assignment `Planet.__init__ = _planet_init_with_legacy_kwargs`)
- [x] Run focused unit tests: `pytest tests/unit/strategy/data/ -n 4 -q`. Expect them to pass — Phase 2 migrated every caller to private kwargs.
- [x] If any test fails:
  - Most likely cause: missed call site in Phase 2 audit
  - Fix the test's constructor call (legacy kwarg → private kwarg)
  - Add to `findings/phase_2_followups.md` for completeness
- [x] Verify: the static guard from Task 3.1 still has 3 RED assertions remaining (the property assertions)

### Task 3.3: GREEN — delete the 3 @property/@setter blocks [Medium]
**File:** `game/strategy/data/planet.py`
**Tests:** `pytest tests/unit/strategy/data/ -n 4 -q` then sharded

- [x] Delete the comment block + 3 property/setter pairs at lines 218-262 (`# These properties expose the underlying...` through the `staging_yard` setter)
- [x] Run focused unit tests: `pytest tests/unit/strategy/data/ tests/unit/strategy/facade/ -n 4 -q`. Expect them to pass.
- [x] If any test fails on `planet.stockpile` / `planet.max_stockpile` / `planet.staging_yard` attribute access:
  - Verify it's a test (not production)
  - Migrate the read to `planet._stockpile` / `planet._max_stockpile` / `planet._staging_yard` OR (better, where applicable) to the manager API (`planet.get_stockpile(rt)`, `planet.add_to_stockpile(rt, amt)`)
  - PROJ-450 will eventually want a typed-substrate read path; do NOT introduce a new `staging_yard` property here

**Notes:** Production code already routes through `add_to_stockpile` / `consume_from_stockpile` / `IPlanetMutator.set_stockpile_amount`; the @property setters are exclusively a test surface per the audit.

### Task 3.4: GREEN — update `planet_serde.planet_to_dict` to read private fields directly [Simple]
**File:** `game/strategy/data/planet_serde.py`
**Tests:** `pytest tests/integration/save_load/test_roundtrip_planet.py -n 4 -q`

- [x] Locate `planet_to_dict` at lines 30-90 (approximate; verify against current HEAD)
- [x] Change reads of `planet.stockpile` / `planet.max_stockpile` / `planet.staging_yard` (lines ~53-55) to `planet._stockpile` / `planet._max_stockpile` / `planet._staging_yard`
- [x] Run focused test; verify save-load round-trip green
- [x] **Save format unchanged.** The save dict keys stay `"stockpile"` / `"max_stockpile"` / `"staging_yard"` — only the source attribute being read changes.

### Task 3.5: Confirm Task 3.1 guard is fully GREEN [Simple]
**Tests:** `pytest tests/static_guards/test_no_planet_legacy_kwarg_wrapper.py -q`

- [x] Run the static guard
- [x] Expect: green — all 4 assertions pass
- [x] If green, commit Tasks 3.1-3.5 as a single phase commit (or 2-3 commits per the repo discipline)
- [x] Commit message: `PROJ-449 Phase 3: delete Planet legacy-kwarg wrapper + 3 property/setter pairs (closes F-A-002 + F-A-004)`

### Task 3.6: Run full sharded suite [Medium]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Sharded suite green
- [x] Expected count: same as pre-phase (no tests added or removed; deletions are pure dead-code removal)
- [x] If green, mark phase complete and signal PROJ-450

### Task 3.7: Verify PROJ-450 Phase 0 precondition is observable [Simple]
**File:** (read-only) `game/strategy/data/planet.py`

- [x] Confirm `_planet_init_with_legacy_kwargs` is gone from `planet.py` (the deletion from Task 3.2 + 3.3 is the canonical signal)
- [x] Confirm `Planet.staging_yard` @property/@setter pair is gone (Task 3.3 deletion is the canonical signal)
- [x] **No cross-project write.** PROJ-450's Phase 0 inspects current code state directly (`Projects/active_projects/PROJ-450/phase_0_checklist.md` Task 0.1) — it does not depend on a SHA-signal in its own plan.md. See PROJ-450 decisions.md row 2026-05-19 "Cross-project gate mechanism = direct code inspection."

**Notes (2026-05-19 codex audit fix):** The earlier draft of this task wrote PROJ-450's plan.md to post a commit-SHA signal. That mechanism is removed; PROJ-450 Phase 0 already gates on the deletion being present in `planet.py`, which is more robust to sequencing errors than a sibling-plan SHA pinning. See PROJ-449 decisions.md row 2026-05-19 "Codex audit fixes applied."

---

## Phase Completion Checklist
- [x] Static guard `test_no_planet_legacy_kwarg_wrapper.py` exists and is green
- [x] `_planet_init_with_legacy_kwargs` deleted from `planet.py`
- [x] 3 @property/@setter blocks deleted from `planet.py`
- [x] `planet_serde.planet_to_dict` reads `_stockpile` / `_max_stockpile` / `_staging_yard` directly
- [x] Save-load round-trip green
- [x] Sharded suite green at same pre-phase count
- [x] PROJ-450 Phase 0 precondition observable in `planet.py` (no cross-project write needed; PROJ-450 inspects directly)
- [x] Plan.md Quick Status → Complete; Current State updated

## Notes / Risks / Coordination Touchpoints
- **PROJ-450 unblocks after this phase.** Codex r4 explicitly sequenced PROJ-450 after PROJ-449 for this reason: "Depends on: 1 (shared planet.py / serde surface)."
- **Risk: missed audit site.** If Phase 2's audit + sweep missed a caller, Phase 3 surfaces it as a hard failure (no wrapper to translate). The recovery path is identical to Phase 2 Task 2.2 (single-token rename, focused commit).
- **`planet_to_dict` save key names DO NOT change.** Old saves still load; new saves still write the same key names. Only the SOURCE of those values changes (private field instead of property read).
- **Sibling: AST guards.** `tests/static_guards/test_no_legacy_storage_fields.py` should remain green after this phase — it pins the absence of the dataclass FIELD names; the property cluster being deleted does not affect it. Verify in Task 3.6.
- **LOC budget.** `planet.py` is currently 420 LOC. After this phase, it drops by ~50 (wrapper block + 3 property pairs). Plenty of headroom for PROJ-450's substrate changes.
