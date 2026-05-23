# Phase 6: Migrate `build_queue_source` and confirm stabilizer/superweapon parity

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-429 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** phase_5
**Review Mode:** lightweight

**Files (planned):**
- `game/strategy/data/build_queue_source.py` (modify — line 114 `"BuildRateBooster"` literal)
- `game/strategy/services/stabilizer_registry.py` (read-only — contract test only)
- `game/strategy/services/superweapon_registry.py` (read-only — contract test only)
- `tests/unit/strategy/services/test_ability_metadata_contracts.py` (modify — add stabilizer/superweapon contracts FIRST)

**Objective:** Eliminate the last hardcoded ability-name literal in the strategy layer (`"BuildRateBooster"` at `build_queue_source.py:114`) and pin `STABILIZERS` / `SUPERWEAPONS` to the unified registry via contract tests. Do not collapse the spec tables themselves — that is a follow-up.

---

## Reading

- [ ] Re-read `design.md` "Per-Consumer Migration Order" Phase 6 row.
- [ ] Re-read `decisions.md` row 6 (no collapse of `StabilizerSpec` / `SuperweaponSpec`).
- [ ] Read `game/strategy/data/build_queue_source.py` lines 100-130.
- [ ] Read `game/strategy/services/stabilizer_registry.py` lines 54-70 (the `STABILIZERS` tuple).
- [ ] Read `game/strategy/services/superweapon_registry.py` lines 70-111 (the `SUPERWEAPONS` tuple).

---

## Tasks

### Task 6.1: Add the failing stabilizer/superweapon contract tests (TDD red) [Simple]

**File:** `tests/unit/strategy/services/test_ability_metadata_contracts.py`

- [ ] Add `test_every_stabilizer_ability_name_has_stabilizer_kind_tag`:
      `for spec in STABILIZERS: assert ability_has_kind_tag(spec.ability_name, StrategicKind.STABILIZER)`
- [ ] Add `test_every_superweapon_ability_name_has_superweapon_kind_tag`:
      `for spec in SUPERWEAPONS: assert ability_has_kind_tag(spec.ability_name, StrategicKind.SUPERWEAPON)`
- [ ] Confirm: if Phase 1 properly tagged these entries, the tests pass on first run; if not, they fail and reveal the gap.

**Notes:** [Filled during implementation]

### Task 6.2: Add the failing build-queue parity test (TDD red) [Simple]

**File:** `tests/unit/strategy/services/test_ability_metadata_contracts.py` (or `tests/unit/strategy/data/test_build_queue_source.py` if it exists)

- [ ] Add `test_build_rate_booster_aggregation_uses_registry`:
      Assert that the function calling `"BuildRateBooster"` at `build_queue_source.py:114` produces identical output after the swap (characterization test against current behavior).
- [ ] Add a separate `test_build_rate_booster_has_kind_tag`:
      `assert ability_has_kind_tag('BuildRateBooster', StrategicKind.BUILD_RATE_BOOSTER)`

**Notes:** [Filled during implementation]

### Task 6.3: Replace `"BuildRateBooster"` literal (TDD green) [Simple]

**File:** `game/strategy/data/build_queue_source.py`

- [ ] Line 114: replace literal `"BuildRateBooster"` with `next(iter(abilities_with_kind_tag(StrategicKind.BUILD_RATE_BOOSTER)))` if a single ability is expected, or iterate the set if multiple are.
- [ ] Leave the scope sweep array `["planet","sector","system","empire"]` untouched — out of scope for this project.
- [ ] Verify: focused tests green.

**Notes:** [Filled during implementation]

### Task 6.4: Backfill missing entries if contract tests fail [Simple]

- [ ] If any `STABILIZERS[*].ability_name` or `SUPERWEAPONS[*].ability_name` is missing the matching `kind_tag` in the registry, add it in `ability_metadata.py`.
- [ ] Re-run contract tests; confirm green.

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist

When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] No literal `"BuildRateBooster"` string in `build_queue_source.py`
- [ ] Stabilizer/superweapon contract tests are green and pinned
- [ ] `STABILIZERS` and `SUPERWEAPONS` tables themselves are unchanged (per decisions.md row 6)
- [ ] **Sanity grep:** the TD-07 inventory regex returns no hits in `game/strategy/` outside `ability_metadata.py` itself (and outside `data/` / `game/simulation/`)
- [ ] `pytest tests/unit/strategy/services/test_ability_metadata_contracts.py` is fully green
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 7
