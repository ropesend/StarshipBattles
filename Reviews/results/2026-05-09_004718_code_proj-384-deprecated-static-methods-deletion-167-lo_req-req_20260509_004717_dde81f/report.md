# Review Report: PROJ-384 — Deprecated *_static methods deletion

**Review Type:** code  
**Request ID:** req_20260509_004717_dde81f  
**Commit:** 6398bb1da  
**Review Mode:** normal  
**Scope:** `game/simulation/components/ability_manager.py`, `game/simulation/components/modifier_manager.py`, and associated test files  

---

## Findings

### INFO-001: PROJ-380 Phase 2 plan is stale — work already completed by PROJ-384

**Severity:** INFO  
**File:** `Projects/active_projects/PROJ-380/plan.md:32-33`  
**Status:** Open — requires orchestrator follow-up

PROJ-380 Phase 2 ("Dead functions (deprecated statics)") lists as its goal: *"Delete 5 deprecated `ModifierManager` static methods (~95 LOC) while preserving `remove_modifier_inplace` (still used internally)."* The plan also references scope-reduced `DUP-X-05` that "preserves the still-used `remove_modifier_inplace` helper."

PROJ-384 commit 6398bb1da has already:
1. Deleted all 6 `ModifierManager._*_static` methods (including the 5 PROJ-380 planned to delete)
2. Deleted `remove_modifier_inplace` (which PROJ-380 planned to preserve)
3. Verified `remove_modifier_inplace` had only one internal caller (`add_modifier_static`) which was deleted alongside it

PROJ-380 Phase 2 should be marked as **obsolete/superseded** by PROJ-384. The preservation note about `remove_modifier_inplace` was correct at the time of the audit review but became outdated once PROJ-241's instance API migration made the in-place mutation the default behavior of the instance-level `remove_modifier()`.

---

## Verification Summary

### 1. Zero remaining callers — PASS ✓

Grep searches across `game/`, `combat_lab/`, `Tools/`, and `tests/` for all 12 deleted method names:

| Method | Production callers | Test callers |
|---|---|---|
| `get_abilities_static` | 0 | 0 (removed from test) |
| `get_ability_static` | 0 | 0 |
| `has_ability_static` | 0 | 0 (removed from test) |
| `has_pdc_ability_static` | 0 | 0 |
| `get_ui_rows_static` | 0 | 0 (removed from test) |
| `instantiate_abilities_static` | 0 | 0 |
| `add_modifier_static` | 0 | 0 |
| `remove_modifier_static` | 0 | 0 |
| `get_modifier_static` | 0 | 0 |
| `get_all_effects_static` | 0 | 0 |
| `get_stat_summary_static` | 0 | 0 |
| `remove_modifier_inplace` | 0 | 0 |

The only references found anywhere in the repo are in `test_modifier_manager.py:140-142`, a comment block correctly noting the PROJ-384 deletion attribution.

### 2. Test migration correctness — PASS ✓

`tests/unit/simulation/components/test_ability_manager.py` class `TestAbilityManagerStandalone` (lines 130-164) was migrated from 3 static-method tests to 3 instance-method tests:

| Before | After | Same behavior? |
|---|---|---|
| `test_manager_get_abilities_static` → `AbilityManager.get_abilities_static(...)` | `test_manager_get_abilities` → `mgr.get_abilities(...)` via `railgun.ability_manager` | ✓ Same assertion (`len(weapons) >= 1`) |
| `test_manager_has_ability_static` → `AbilityManager.has_ability_static(...)` | `test_manager_has_ability` → `mgr.has_ability(...)` via `railgun.ability_manager` | ✓ Same assertion (`result is True`) |
| `test_manager_get_ui_rows_static` → `AbilityManager.get_ui_rows_static(...)` | `test_manager_get_ui_rows` → `mgr.get_ui_rows()` via `railgun.ability_manager` | ✓ Same assertion (`isinstance(rows, list)`) |

No semantic drift. Uses canonical instance access path (`railgun.ability_manager` → delegate methods). All 63 focused tests pass.

### 3. `remove_modifier_inplace` deletion — PASS ✓

Git diff of 6398bb1da confirms:
- The sole internal caller was `add_modifier_static` at line `ModifierManager.remove_modifier_inplace(modifiers_list, mod_id)`
- Both `add_modifier_static` and `remove_modifier_inplace` were deleted together
- The instance-level `remove_modifier()` (modifier_manager.py:126-137) now implements in-place mutation with the same list comprehension pattern
- Zero references to `remove_modifier_inplace` exist anywhere else in the repo

PROJ-384 is correct; PROJ-380's preservation note was outdated by the time PROJ-384 ran.

### 4. TYPE_CHECKING import cleanup — PASS ✓

- `GameRegistries` was removed from `modifier_manager.py`'s TYPE_CHECKING import block (confirmed in git diff)
- Zero remaining references to `GameRegistries` in `modifier_manager.py` (grep confirms)
- No `GameRegistries` references in `ability_manager.py` either (grep confirms)
- Instance methods now access registries via `self._component._registries` instead of requiring a separate `registries` parameter

### 5. Test results — PASS ✓

`pytest tests/unit/simulation/components/test_ability_manager.py tests/unit/simulation/components/test_modifier_manager.py`: **63 passed** in 1.69s.

### 6. Pre-existing issue (unrelated to PROJ-384)

`game/strategy/services/fleet_navigation_service.py` has merge-conflict state (`UU` in git status) causing a SyntaxError that blocks adjacent test collection. This is a pre-existing working-tree issue unrelated to this commit (the committed HEAD version is clean). Not introduced by PROJ-384.

---

## Summary

| Severity | Count |
|---|---|
| CRITICAL | 0 |
| MAJOR | 0 |
| MINOR | 0 |
| INFO | 1 |

**Verdict:** PROJ-384 is clean. All 12 deprecated static methods are fully removed with zero remaining callers. Test migration preserves original test intent. The `remove_modifier_inplace` deletion is correct — its sole internal caller was deleted with it. PROJ-380 Phase 2 should be marked obsolete by the orchestrator.
