# Phase 1: Failing Test + One-Line Fix

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-356 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** none
**Review Mode:** standard
**Files (planned):** game/ai/controller.py, tests/unit/ai/test_capability_cache_pdc.py, tests/unit/ai/test_controllable_adapter_edge_cases.py
**Objective:** Replace the dead `has_ability('PDCAbility')` filter in the AI capability cache with a tag-based `has_pdc_ability()` check. Lock in correct behavior with a regression test that fails on current main.

---

## Tasks

### Task 1.1: Audit consumers of `pdc_components` / `'has_pdc'` cache entries [Simple]
**File:** Read-only audit across `game/ai/` and `game/simulation/combat/`
**Tests:** None (research)

- [x] Grep for `pdc_components` and `'has_pdc'` (and `"has_pdc"`) across `game/`
- [x] List every consumer in [decisions.md](decisions.md) under a "Consumer audit" row
- [x] For each consumer: note whether the silently-empty cache changes observable AI behavior today
- [x] If a consumer was relying on `'has_pdc' == True` and getting `False`, surface to user before fixing — fixing the cache may flip targeting behavior

**Notes:** Only writer is `controller._build_capabilities_cache`. The readers in `target_evaluator` (`_eval_capability_rule`, `_eval_pdc_arc_rule`) bypass the `has_pdc`/`pdc_components` keys entirely and call `is_in_pdc_arc(ship, candidate)` directly. Cache keys exist for future consumers but are dead at read time today. No behavior flip expected from the fix.

---

### Task 1.2: Write failing regression test [Simple]
**File:** `tests/unit/ai/test_capability_cache_pdc.py` (new)
**Tests:** `pytest tests/unit/ai/test_capability_cache_pdc.py -v`

- [x] Test 1: ship with a weapon component carrying a `pdc`-tagged ability appears in `cache[entity_id]['pdc_components']` and `'has_pdc'` is True
- [x] Test 2: ship with a non-PDC `WeaponAbility` is in `weapon_components` but NOT in `pdc_components` and `'has_pdc'` is False
- [x] Test 3: ship with no weapons does not appear in cache  → Implemented as test 4: assert dead `has_ability('PDCAbility')` path is not consulted (stronger lock-in than the no-weapons case, which is already covered by `test_build_capabilities_cache_has_weapons_false` in the existing fixture). Mixed-weapons case (test 3) added for additional coverage.
- [x] Run on current main — verify tests 1 and 2 FAIL (test 1's `pdc_components` is empty; test 2's `'has_pdc'` happens to pass but verify both tests are red on main first)
- [x] Use the existing `is_combat_ship` / `get_capability_cache_key` plumbing; mirror fixture style from `test_controllable_adapter_edge_cases.py`

**Notes:** RED on unfixed code: 3 of 4 new tests failed (`test_pdc_weapon_appears_in_pdc_components`, `test_mixed_weapons_only_pdc_in_pdc_components`, `test_does_not_call_legacy_string_ability_path`). Test 2 (`test_non_pdc_weapon_excluded_from_pdc_components`) passed coincidentally on main because the buggy code returned False either way for a non-PDC weapon — kept as a coverage anchor.

---

### Task 1.3: Apply one-line fix [Simple]
**File:** `game/ai/controller.py:229`
**Tests:** `pytest tests/unit/ai/test_capability_cache_pdc.py -v`

- [x] Replace `pdc_weapons = [w for w in weapons if w.has_ability('PDCAbility')]` with `pdc_weapons = [w for w in weapons if w.has_pdc_ability()]`
- [x] Verify regression tests now PASS
- [x] No other edits to `_build_capabilities_cache`

**Notes:** Added a 3-line comment above the replacement explaining PROJ-241/PROJ-356 rationale so the next reader sees why a tag-based query is canonical.

---

### Task 1.4: Update existing fixture assertion [Simple]
**File:** `tests/unit/ai/test_controllable_adapter_edge_cases.py:231`
**Tests:** `pytest tests/unit/ai/test_controllable_adapter_edge_cases.py -v`

- [x] Read lines 231 and 233 — these assert that `get_components_by_ability('PDCAbility', operational_only=False)` is the call shape
- [x] If the test is asserting the *adapter* delegates correctly, leave it (delegation contract unchanged); if it's verifying the controller's PDC discovery path, rewrite to assert `has_pdc_ability()` is consulted
- [x] Document the choice in [decisions.md](decisions.md)

**Notes:** Left as-is. The test verifies adapter delegation: it passes `'PDCAbility'` in and asserts that string flows verbatim to the wrapped ship. The test does not depend on `'PDCAbility'` being a real ability class — any string would do. Documented in decisions.md. **Additionally** (out-of-plan but in-scope): updated `tests/unit/ai/test_ai_capabilities_cache.py:65` where the shared `create_mock_enemy` helper was setting `weapon.has_ability = MagicMock(return_value=has_pdc)` — this was silently locking in the dead path. Switched to `weapon.has_pdc_ability`.

---

### Task 1.5: Sharded suite green [Medium]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Run full sharded suite
- [x] No regressions; new regression test is included in the count
- [x] If a test now fails because the cache started returning the right answer, treat that as a real bug surfaced by the fix — investigate before weakening any test

**Notes:** Sharded suite shows pre-existing failures in `tests/unit/simulation/combat/test_fleet_aura_register.py`, `test_planetary_fleet_components.py`, `test_post_battle_hook.py`, and `test_battle_outcome.py`. All trace to the in-flight `AuraProvider` signature change visible in `git status` (modified `fleet_aura_manager.py` etc.) — unrelated to PROJ-356. Confirmed via running `tests/unit/ai/` (386 passed) and `tests/unit/simulation/combat/` + `tests/unit/ai/` together (736 passed). PDC fix is clean. Per CLAUDE.md "do not revert unrelated user changes."

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to closure / awaiting user verification
- [x] Update [manifest.md](manifest.md) if files outside the planned set were touched
