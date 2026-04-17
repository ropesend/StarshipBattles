# Phase 1: Fix `_extract_scope()` default (CRITICAL — C-1)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-272 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Risk:** LOW (targeted fix; no existing tests rely on the broken default)
**Depends On:** None
**Objective:** Battle Setup compiler's `_extract_scope()` returns `"self"` when JSON omits `scope`, but runtime `Ability` base class falls back to class-level `default_scope` (e.g., `ShieldModifierAbility.default_scope = ALLIED_SYSTEM`). Compiler/runtime disagreement silently no-ops the complex at compile but DOES apply at runtime. Same bug in `combat_modifier_collector.py:88`. All production JSONs specify scope today — latent but will bite on first author omission.

## Tasks

### Task 1.1: Failing tests for scope-default resolution [Medium]
**Files:** `tests/unit/ui/screens/battle_setup/test_spec_compiler.py` + `tests/unit/strategy/services/test_combat_modifier_collector.py`

- [x] Added `TestExtractScopeResolvesClassDefault` (6 tests) in `tests/unit/ui/screens/battle_setup/test_spec_compiler.py`: ShieldModifier/DamageModifier/ShieldProjection missing-scope resolution, explicit scope wins, primitive → self, unknown ability → self fallback.
- [x] Ran — 6/6 failed with TypeError (signature mismatch — test expects 2 args, old code had 1).

**Notes:** Chose to test `_extract_scope` helper directly rather than end-to-end because: (a) helper is exported and stable-enough for direct testing, (b) end-to-end requires fabricating a missing-scope complex design JSON on disk which is noisier. Collector test coverage landed via regression guard (Task 1.3).

---

### Task 1.2: Implement scope-default resolution [Medium]
**Files:** `game/ui/screens/battle_setup/spec_compiler.py` (`_extract_scope`) + `game/strategy/services/combat_modifier_collector.py:88`

- [x] Extracted shared helper `get_ability_default_scope(ability_name: str) -> str` in `game/simulation/components/abilities/__init__.py`. Returns class-level `default_scope.value` from `ABILITY_REGISTRY`; falls back to "self" with a once-logged WARNING for unknown names.
- [x] Updated `_extract_scope(ability_name, ability_data)` in Battle Setup compiler: primitive → "self"; explicit dict scope wins; missing scope → `get_ability_default_scope(ability_name)`.
- [x] Same fix applied at all 3 scope read sites in `combat_modifier_collector.py` (lines 88, 97, 120) via an inner helper `_entry_scope(ability_key, entry)`.
- [x] Run — 29/29 tests green (6 new + 23 pre-existing in battle_setup tests and collector tests).

**Notes:** Shared helper keeps DRY and gives future compilers/collectors a clean API. Placed in simulation layer since both UI and strategy callers need it.

---

### Task 1.3: Regression guard + production JSON audit [Simple]
**File:** `tests/unit/simulation/test_unified_entry_guard.py`

- [x] Added `TestScopeDefaultResolutionIsWired` to `test_unified_entry_guard.py` — 2 tests (compiler uses registry; collector uses registry).
- [x] Audited `data/components.json`: 2 components use ShieldProjection as primitive (`shield_generator`, `mini_shield_generator`) — correct behavior (primitive → "self" preserved). Zero components have ShieldModifier/DamageModifier/ShieldProjection dict WITHOUT scope — the bug is latent today, fixed before it can surface.

**Notes:** Fix is preventive — no current production JSON triggered the bug, but the disagreement would have silently dropped a complex the moment an author forgot `scope`.

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Unit tests green (9826 passed in narrow regression; 1 pre-existing build-queue failure + 1 pre-existing AI import error unrelated)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
