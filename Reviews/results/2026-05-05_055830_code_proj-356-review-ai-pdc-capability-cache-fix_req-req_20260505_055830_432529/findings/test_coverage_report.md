# Test Coverage Report — PROJ-356: AI PDC Capability Cache Fix

**Reviewed:** `test_capability_cache_pdc.py`, `test_ai_capabilities_cache.py`, `controller.py:184-240`, `decisions.md`
**Reviewer:** OpenCode Test Coverage Analyst
**Date:** 2026-05-04

---

## Summary

- **Total issues found:** 5
- **Critical:** 0, **Major:** 0, **Minor:** 2, **Info:** 3

---

## TDD Verification

### Did the regression test genuinely test the broken path?

Yes. The `_make_weapon` helper (`test_capability_cache_pdc.py:70-83`) is deliberately constructed with asymmetric mocks:

| Mocked method | Return value | Mirrors |
|---|---|---|
| `has_pdc_ability()` | `is_pdc` (True for PDC) | Canonical tag-based surface (real components implement this) |
| `has_ability(...)` | Always `False` | Pre-fix dead path: no `PDCAbility` class exists, so real components return False |

### Would it have failed on unfixed code?

Three of four tests would **fail** on unfixed code, one is neutral:

| Test | Old code behavior | Fails? |
|---|---|---|
| `test_pdc_weapon_appears_in_pdc_components` | `has_ability('PDCAbility')` returns False → `pdc_weapons` empty → `has_pdc` is False, `pdc_components` is [] | **YES** — asserts `has_pdc is True` and weapon in list |
| `test_non_pdc_weapon_excluded_from_pdc_components` | `has_ability('PDCAbility')` returns False → `pdc_weapons` empty → same result as new code | No — neutral (both paths produce empty lists for non-PDC) |
| `test_mixed_weapons_only_pdc_in_pdc_components` | `has_ability('PDCAbility')` returns False → `pdc_weapons` empty → `has_pdc` is False | **YES** — asserts `has_pdc is True` and PDC weapon in list |
| `test_does_not_call_legacy_string_ability_path` | `has_ability('PDCAbility')` IS called (that's the broken path) | **YES** — asserts `'PDCAbility' not in args` |

**Forward-recall trace for `test_pdc_weapon_appears_in_pdc_components`:**

```
Unfixed _build_capabilities_cache:
  weapons = entity.get_components_by_ability('WeaponAbility')  → [pdc_weapon_mock]
  pdc_weapons = [w for w in weapons if w.has_ability('PDCAbility')]  → []  (has_ability → False)
  cache[pdc_ship] = {'has_pdc': False, 'pdc_components': []}

Test assertions:
  assert cache['pdc_ship']['has_pdc'] is True   → FAIL (got False)
  assert pdc_weapon in cache['pdc_ship']['pdc_components']  → FAIL (empty list)
```

---

## Findings

#### MINOR: Neutral test provides no regression signal
**ID:** TC-001
**Location:** `tests/unit/ai/test_capability_cache_pdc.py:101-112`
**Issue:** `test_non_pdc_weapon_excluded_from_pdc_components` passes identically under both old (`has_ability('PDCAbility')`) and new (`has_pdc_ability()`) code paths because both paths correctly classify a non-PDC weapon as not being PDC. It is not a regression detector for the specific bug.
**Impact:** Low. The test still validates correct behavior for non-PDC weapons and rounds out the behavioral spec. It just won't catch a re-introduction of the string-based bug.
**Recommendation:** No action required. The test is correct and useful as a behavioral specification. Its presence alongside the three true regression tests is a reasonable completeness goal. Optionally, add a docstring note: "This test passes under both old and new code; it validates correct non-PDC behavior, not the fix itself."
**Effort:** Simple

#### MINOR: `create_mock_enemy` fix drops `has_ability` mock silently
**ID:** TC-002
**Location:** `tests/unit/ai/test_ai_capabilities_cache.py:62-70`
**Issue:** The PROJ-356 fix replaced `weapon.has_ability = MagicMock(return_value=has_pdc)` (which locked in the bug) with `weapon.has_pdc_ability = MagicMock(return_value=has_pdc)`. The old `has_ability` mock was removed entirely rather than being explicitly set to `False`, meaning the existing cache tests no longer assert anything about `has_ability('PDCAbility')` not being called.
**Impact:** Low-moderate. The PDC-specific test file (`test_capability_cache_pdc.py`) now owns the regression guard against the string-based path. The existing tests in `test_ai_capabilities_cache.py` focus on cache structure and integration, not PDC specifically. This separation of concerns is defensible.
**Recommendation:** Acceptable as-is. The PDC-specific tests explicitly verify the legacy path is dead. The old helper was actively harmful (it made the bug pass green). The fix correctly routes PDC testing to the new dedicated test file.
**Effort:** Simple

#### INFO: `has_pdc` / `pdc_components` cache keys are dead at read time
**ID:** TC-003
**Location:** `game/ai/controller.py:231-237` (write), `game/ai/target_evaluator.py:241-263` (read path)
**Issue:** The `_build_capabilities_cache` method computes `has_pdc` and `pdc_components` but no consumer reads them. `_eval_capability_rule` routes `pdc_arc` / `missiles_in_pdc_arc` rules to `_eval_pdc_arc_rule`, which calls `is_in_pdc_arc(ship, candidate)` directly — never consulting the cache's PDC keys. Only `has_weapons` and `weapon_components` are consumed.
**Impact:** Low (correctness only). The bug fix is still correct — leaving these keys with wrong values (always empty/False) is a latent data-quality problem. The docstring at `target_evaluator.py:285-287` documents the cache shape including `has_pdc`/`pdc_components`, implying they were intended for future use. Decisions.md already acknowledges this as a known state.
**Recommendation:** No immediate action. Either: (a) mark `has_pdc`/`pdc_components` as reserve keys in the docstring with a note they are currently unused at consumption, or (b) file a follow-up task to consume them in `_eval_capability_rule` for the `pdc_arc` path, which would reduce per-target `is_in_pdc_arc` calls from O(n) to O(1) lookups. Option (b) would be a legitimate performance optimization.
**Effort:** Medium (for consumption path)

#### INFO: `test_controllable_adapter_edge_cases.py:231` `'PDCAbility'` usage is benign
**ID:** TC-004
**Location:** `tests/unit/ai/test_controllable_adapter_edge_cases.py:231`
**Issue:** The test `test_get_components_by_ability_with_operational_flag` calls `adapter.get_components_by_ability('PDCAbility', operational_only=False)` and asserts the call is forwarded to the underlying ship. The string `'PDCAbility'` is a passthrough probe value to verify the adapter delegates verbatim — it is not a contract about controller PDC discovery.
**Impact:** None. Decisions.md correctly identifies this as benign. Changing the probe string would merely shift the test without gaining coverage.
**Recommendation:** No action required.
**Effort:** N/A

#### INFO: `_make_weapon` mock for `has_ability` is broadly blunt
**ID:** TC-005
**Location:** `tests/unit/ai/test_capability_cache_pdc.py:78-82`
**Issue:** The mock `weapon.has_ability = MagicMock(return_value=False)` causes any `has_ability(...)` call to return False regardless of the argument. This means if a future code change accidentally calls `has_ability('WeaponAbility')` (a real ability class) instead of `has_pdc_ability()`, the mock would silently return False and the tests might pass spuriously.
**Impact:** Low. The production code at `controller.py:226` calls `entity.get_components_by_ability('WeaponAbility', ...)` on the entity (ship), not on individual weapon components. The weapon-level `has_ability` is only ever called at `controller.py:231` (the legacy path for individual weapons), which is the exact dead path these tests guard against. The blunt mock is therefore well-scoped.
**Recommendation:** Optionally, use `wraps` or a `side_effect` that raises `AssertionError` for unexpected arguments to make the mock stricter. Example: `weapon.has_ability = MagicMock(side_effect=lambda arg: pytest.fail(f"Unexpected has_ability({arg})") if arg != 'PDCAbility' else False)`. This would catch accidental non-PDC-string calls. Low priority.
**Effort:** Simple

---

## Test Quality Assessment

### Assertion Quality
**Strong.** Assertions use exact-value comparisons (`is True`, `is False`), containment checks (`in`, `not in`), and structural validation (`len() == 1`, `== []`). No weak `assertTrue`/`assertFalse` calls.

### Edge Case Coverage
**Comprehensive.** Covered: PDC-only ships, non-PDC-only ships, mixed-weapon ships, projectile entities (in existing cache tests), unarmed ships. The only edge case not explicitly tested is a ship with zero weapons but present in cache — this is implicitly covered by `test_build_capabilities_cache_has_weapons_false` in the existing file.

### Test Isolation
**Pure unit tests.** Both test files use `MagicMock` fixtures for ship, grid, and weapon components. No dependency on `pygame.init()`, no database, no filesystem, no global registry state. The `pygame.math.Vector2` imports are used only for positional stubs and do not require a display surface.

### Test Organization
**Follows project conventions.** Test classes are named `Test...` with descriptive names. Methods use `test_*` prefix. Docstrings are present and informative. Fixtures are at module level. The regression test file is cleanly separated from the existing cache tests.

---

## Top 5 Priority Issues

1. **TC-003 (INFO):** `has_pdc` / `pdc_components` cache keys are computed but never read — low-impact correctness-only; performance optimization opportunity
2. **TC-002 (MINOR):** `create_mock_enemy` fix drops `has_ability` mock — acceptable, PDC-specific tests now own regression guard
3. **TC-001 (MINOR):** One test is neutral for regression — acceptable for behavioral completeness
4. **TC-005 (INFO):** Blunt `has_ability` mock could be stricter — low priority
5. **TC-004 (INFO):** `'PDCAbility'` passthrough probe is benign — no action needed

---

## Overall Assessment

**The regression test suite is well-designed.** The asymmetric mock pattern (tag-based `has_pdc_ability` returns correct value while string-based `has_ability` always returns False) is an elegant technique that exposes the exact bug it targets. Three of four tests would have failed on unfixed code, providing strong confidence the fix works.

The existing cache test helper (`create_mock_enemy`) was correctly patched to use the tag-based surface, breaking the cycle where the test itself masked the bug. The separation of concerns between the existing structural tests and the new PDC-specific regression tests is appropriate.
