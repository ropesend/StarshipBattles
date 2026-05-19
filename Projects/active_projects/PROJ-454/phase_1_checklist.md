# PROJ-454 Phase 1: Retire `effect_ability_metadata.py` (F-B-004)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-454 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Close F-B-004 by migrating the 3 caller sites of `effect_ability_metadata.py` to import from `ability_metadata.py`, then deleting the shim module. 131 LOC of pure delegation goes away.

**Cross-bucket file-ownership rule:** This phase touches only `game/strategy/services/effect_ability_metadata.py` (delete), `effect_ability_display.py` (import migration), `system_effects_collector.py` (import migration), and the matching test file. Do NOT touch any file PROJ-452 / PROJ-453 / PROJ-455 owns.

**Source-of-truth findings:** [`findings/PROJ-454_findings.md`](findings/PROJ-454_findings.md) — read F-B-004's full text and the "F-B-004 caller list" subsection.

---

## Tasks

### Task 1.1: Verify symbol parity between `effect_ability_metadata.py` and `ability_metadata.py` [Simple]
**File:** Read-only — `game/strategy/services/effect_ability_metadata.py` + `game/strategy/services/ability_metadata.py`

- [ ] Read `effect_ability_metadata.py` end-to-end. Confirm the 5 public symbols: `EffectAbilityMetadata` (dataclass), `EFFECT_ABILITY_METADATA` (tuple), `find_metadata`, `is_known_effect_ability`, `all_owner_aware_scopes`.
- [ ] Read `ability_metadata.py`. Locate each of the 5 symbols (or the equivalent canonical name). Per the shim header at `effect_ability_metadata.py:1-26`, the canonical names should already exist on `ability_metadata.py` — verify by inspection.
- [ ] **Per-symbol decision**: for any symbol whose name on `ability_metadata.py` differs, document the rename in `decisions.md`. The Phase 1 migration uses the canonical names; the shim's name aliases die when the shim does.
- [ ] If any symbol has NO equivalent on `ability_metadata.py`, the migration is blocked — pause and surface for user decision. (Pre-audit per 2026-05-19 grep: all symbols are present; this is a defensive check.)

**Notes:** [Empty until implementation.]

---

### Task 1.2: Migrate the 2 production callers to `ability_metadata.py` [Simple]
**Files:**
- `game/strategy/services/effect_ability_display.py:20`
- `game/strategy/services/system_effects_collector.py:42-45`

**Tests:** `pytest tests/unit/strategy/services/ -q -k "system_effects or effect_ability"`

- [ ] Open `game/strategy/services/effect_ability_display.py`. Line 20: change `from game.strategy.services.effect_ability_metadata import find_metadata` to `from game.strategy.services.ability_metadata import find_metadata` (or the canonical name per Task 1.1).
- [ ] Open `game/strategy/services/system_effects_collector.py`. Lines 42-45: change the multi-symbol import. The current shape is likely:
  ```python
  from game.strategy.services.effect_ability_metadata import (
      find_metadata,
      is_known_effect_ability,
  )
  ```
  Migrate to:
  ```python
  from game.strategy.services.ability_metadata import (
      find_metadata,
      is_known_effect_ability,
  )
  ```
- [ ] Run targeted tests; confirm green.
- [ ] **Sanity check**: `git grep -n "from game.strategy.services.effect_ability_metadata" game/` should return zero matches (production-side only).

**Notes:**

---

### Task 1.3: Decide test file fate — delete or rewrite [Simple-Medium]
**File:** `tests/unit/strategy/services/test_effect_ability_metadata.py`
**Tests:** `pytest tests/unit/strategy/services/test_effect_ability_metadata.py -v` (current) + `pytest tests/unit/strategy/services/test_ability_metadata.py -v` (canonical, if exists)

- [ ] Read `tests/unit/strategy/services/test_effect_ability_metadata.py` end-to-end. Identify what behaviour it locks:
  - Pure structural tests (assert `EFFECT_ABILITY_METADATA` is a tuple, `find_metadata` returns the right shape, etc.) — these are likely duplicated in `ability_metadata.py`'s own test file. **Delete after parity check.**
  - Behaviour tests specific to the effect-ability narrowing (only effect-facet entries surface, owner-aware scope rules, etc.) — these are unique value if `ability_metadata.py`'s own tests don't cover them. **Migrate by rewriting against `ability_metadata.py` and renaming the file** (e.g., `test_ability_metadata_effects.py`).
- [ ] Check `tests/unit/strategy/services/test_ability_metadata.py` (if it exists) for coverage overlap. The 2026-05-19 audit didn't confirm whether `ability_metadata.py` has its own test file; verify.
- [ ] Apply the decision (delete or rewrite-and-rename). Document the choice in `decisions.md`: `2026-XX-XX | F-B-004 test file decision | <delete | rewrite-and-rename> | <reason>`.
- [ ] Run the surviving test (if any) to confirm green.

**Notes:**

---

### Task 1.4: Delete `effect_ability_metadata.py` [Simple]
**File:** `game/strategy/services/effect_ability_metadata.py` (delete)
**Tests:** Full sharded suite

- [ ] **Pre-delete sanity check**: `git grep -n "effect_ability_metadata" game/ tests/` should return:
  - Zero matches under `game/` after Tasks 1.2 lands
  - Zero matches under `tests/` after Task 1.3 lands
  - Possibly matches in archived projects (`Projects/archived_projects/`) or docs — these stay; they're historical narration
- [ ] If the sanity check passes, delete the file: `git rm game/strategy/services/effect_ability_metadata.py`.
- [ ] **Post-delete sanity check**: `python -c "from game.strategy.services import effect_ability_metadata"` should fail with `ModuleNotFoundError`.
- [ ] Run `pytest tests/unit/strategy/services/ -q` — confirm no test file fails on the module deletion.
- [ ] Run `python Tools/test_sharded/test_sharded.py` — full sharded suite green.

**Notes:** If the post-delete sharded run fails because a missed caller still imports `effect_ability_metadata`, restore the file (`git restore`), find the caller, migrate it, and try again. The 2026-05-19 audit identified 3 callers; if a 4th surfaces during the sharded run, it's a discovered miss — fix and document in `decisions.md`.

---

### Task 1.5: Verify F-B-004 closure [Simple]

- [ ] `git grep -n "effect_ability_metadata" game/ tests/` returns zero matches (excluding archived projects + docs/comments).
- [ ] `game/strategy/services/effect_ability_metadata.py` no longer exists.
- [ ] Document closure in `decisions.md`: `2026-XX-XX | F-B-004 closed | Migrated 2 production + 1 test caller to ability_metadata.py; deleted shim (131 LOC). | PROJ-454 Phase 1.`

**Notes:**

---

## Phase Completion Checklist

When all tasks above are checked off:

- [ ] F-B-004 closed (documented in `decisions.md`)
- [ ] `effect_ability_metadata.py` deleted
- [ ] All caller migrations green
- [ ] `pytest tests/unit/strategy/services/ -q` green
- [ ] Full sharded suite green (`python Tools/test_sharded/test_sharded.py`)
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-454 1` — PASSED
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2

## Notes / Deferrals

- **`_OWNER_AWARE_SCOPES` constant** — per F-B-004's suggested action, this constant should move inline at its single use-site or to `ability_metadata.py`. If it's already on `ability_metadata.py`, no action; otherwise migrate during Task 1.2.
- **F-B-005 (component_inspector)** — separate phase. Do NOT mix the two migrations in one PR; F-B-004 is a 3-site close, F-B-005 is a 45-site sweep.
