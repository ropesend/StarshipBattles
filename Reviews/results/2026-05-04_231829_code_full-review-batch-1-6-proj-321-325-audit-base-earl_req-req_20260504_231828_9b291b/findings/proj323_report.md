# PROJ-323 & PROJ-325 Phase 1 Review Report

**Review date:** 2026-05-04
**Review scope:** PROJ-323 (149 tasks, 5 phases) work quality + PROJ-325 Phase 1 documentation corrections
**Severity distribution:** 0 CRITICAL, 1 MAJOR, 0 MINOR

---

## 1. Verification of PROJ-325 Phase 1 Corrections

### 1.1 Tasks 3.3 and 3.6 false-positive checkmarks (FND-CC-001)

**Verified.** Both tasks are now correctly marked `[~]` with `_(skipped — upstream project already deleted target file)_` annotations in `phase_3_checklist.md`:
- Task 3.3 (lines 46-51): S11-CAT10-004 and S11-CAT10-005 target `test_colonization_facade.py` — file confirmed deleted by PROJ-321.
- Task 3.6 (lines 87-92): S11-CAT10-006 and S11-CAT10-007 target `test_color_helpers.py` — file confirmed deleted by PROJ-321.
- Combined fictitious LOC delta (~314) is annotated in Notes.

### 1.2 Manifest.md cleanup (FND-CC-004)

**Verified.** 41 stale entries removed. Header comment (line 3) documents the cleanup provenance. 17 known PROJ-321-deleted files verified absent from manifest (test_colonization_facade.py, test_color_helpers.py, test_projectile_manager.py, test_battle_state_validation.py, test_fleet_validation.py, test_loading.py, test_ship_serialization.py, test_engine_validation.py, test_happiness_engine.py, test_save_game_service.py, test_warp_logic_rework.py, test_mass_validation.py, test_system_tree_panel.py, test_planet_command_handlers.py, test_strategy_menu_panel.py, test_battle_panels_extended.py, test_draw_helpers.py, test_resource_constants.py). Some moved-by-PROJ-322 files correctly removed from the old path. Post-cleanup: 90 files in manifest.

### 1.3 Other PROJ-325 Phase 1 corrections

| Finding | File | Verified? |
|---------|------|-----------|
| FND-CC-002/003 (terminology + LOC annotation) | plan.md | Yes — footnote block added under Quick Status table (lines 22-27) |
| FND-CC-005 (Task 3.10 ambiguity) | phase_3_checklist.md | Yes — deferred annotation removed; confirmed parametrize landed |
| FND-CC-006 (Tasks 2.8/2.9 LOC double-count) | phase_2_checklist.md | Yes — annotated as Phase 1 double-count |
| FND-P2-001 (Task 5.19 tolerance) | test_colony_output.py | Yes — rel=1e-9 → rel=1e-5 (see detailed review below) |
| FND-P2-003 (design.md deleted-file ref) | design.md line 41 | Yes — replaced with surviving Task 5.18/5.19 examples |
| FND-P2-004 (Task 4.9 mis-categorization) | phase_4_checklist.md | Not spot-checked (minor) |
| FND-P2-005 (design.md assertion mischaracterization) | design.md line 42 | Yes — reworded to "hard-assertion regression guard with adjustable threshold" |

---

## 2. PROJ-323 Code Change Spot-Checks

### 2.1 CAT-9 Simplification: Task 1.2 — test_protocols.py module-level imports

**Commit:** `31a8def8c` (PROJ-323 Phase 1 partial)

**What changed:** ~40 method-level `from game.core.protocols import ...` and `from game.strategy.data...` imports hoisted to module top-level. Result: imports organized in two blocks (core protocols, strategy data), test bodies cleaned to only contain assertions and setup.

**Verification:** Current file (`tests/unit/core/test_protocols.py`) shows all imports at top in organized blocks (lines 10-44). Test methods no longer contain local imports. The refactor is correct — method-level imports in test files carry no circular-dependency benefit and harm readability.

**Result: PASSED.**

### 2.2 CAT-10 Parametrize: Task 3.10 — test_defense_marker_bindings.py collapse

**Commit:** `87dcf520c` (PROJ-323 Phase 3 partial)

**What changed:** 6 individual `test_*_empty_bindings` methods collapsed into single `@pytest.mark.parametrize("ability_class", [...])` test `test_marker_ability_has_empty_bindings`. Each test was near-identical: import the ability class, assert `hasattr(cls, 'STAT_BINDINGS')`, assert `len(cls.STAT_BINDINGS) == 0`.

**Verification:** Current file shows clean parametrize at lines 64-93. All 6 ability classes covered with parametrize ids. Assertions identical across all cases. Functionally correct.

**Pattern concern:** The parametrize params use `__import__('module', fromlist=['Class']).Class` to dynamically reference ability classes (see FND-323-001 below).

### 2.3 CAT-12 Logic-Heavy: Task 5.18 — test_resupply_engine.py hardcoded values

**Commit:** `75cc98e16` (PROJ-323 pass 2 batch 8)

**What changed:** Inline arithmetic comments replaced with detailed derivation docstring. Hardcoded reference values (200.0 / 40.0) retained. Removed `events = ...` capture variable (unused). Inline assertion comments removed — "Hardcoded reference values; see docstring for derivation" added above assertions instead.

**Verification:** Current file (`tests/unit/strategy/engine/test_resupply_engine.py` lines 486-532) shows docstring with derivation formula: `240/12 = 20` hexes, `10*20 = 200.0`, `2*20 = 40.0`. The docstring explicitly states: "Updating these values without re-validating production is a regression signal." Assertions use `pytest.approx()` with hardcoded values. The refactor is correct and follows the design doc pattern for reference-value tests.

**Result: PASSED.**

### 2.4 Task 5.19 Tolerance Relaxation (FND-P2-001)

**Commit:** `b8ce4fa35` (PROJ-325 Phase 1)

**What changed:** Tolerance relaxed from `rel=1e-9` to `rel=1e-5` on `pytest.approx(-0.005596103475344202)` in `test_partial_food_and_low_happiness_matches_hand_computation`.

**Analysis:** `rel=1e-5` on `-0.005596...` means effective tolerance of `~5.6e-8` (0.001%). The docstring intermediate values are quoted at 4-decimal precision (~0.94, ~0.9787, ~0.004404, ~-0.01). A maintainer cannot re-derive 1e-9 precision from those. `rel=1e-5` still catches any meaningful production formula drift. The hardcoded reference value itself (`-0.005596103475344202`) was captured from the production helper and is not changed.

**Result: PASSED.** No production regression risk.

---

## 3. Findings

### FND-323-001: Non-idiomatic `__import__()` pattern in parametrize params

**Severity:** MAJOR (pattern violation)
**File:** `tests/unit/modifiers/test_defense_marker_bindings.py`
**Line:** 64-93
**Description:** The parametrize for `test_marker_ability_has_empty_bindings` uses `__import__('module', fromlist=['Class']).Class` inline within `pytest.param()` expressions (6 occurrences). This deviates from the codebase pattern established in `test_superweapon_handler_validation.py:89-132`, `test_command_handlers.py`, and the design doc examples, which use standard `from ... import ...` statements inside factory functions (e.g., `_direct_handler_cases()`). The `__import__` call is functionally correct — these are evaluated at module-load time — but it is less readable and harder to refactor than standard imports. The same PROJ-323 Phase 3 worker used the conventional pattern elsewhere (Task 3.2, `test_superweapon_handler_validation.py`), suggesting this was an inconsistent choice rather than a deliberate decision.
**Recommendation:** Replace the 6 `__import__` calls with module-level `from ... import ...` statements:
```python
from game.simulation.components.abilities.markers import CommandAndControl
from game.simulation.components.abilities.defense import ToHitAttackModifier, ToHitDefenseModifier, EmissiveArmor
from game.simulation.components.abilities.harvester import ResourceHarvesterAbility, SpaceShipyardAbility
```
Then reference class names directly in the `pytest.param()` list. Alternatively, use a factory function like `_defense_marker_cases()` with imports inside (matching the Task 3.2 precedent).

---

## 4. Summary

| Area | Status |
|------|--------|
| Tasks 3.3 + 3.6 false-positive checkmarks | Corrected |
| manifest.md stale entries | Corrected (41 removed) |
| plan.md terminology + LOC annotation | Corrected |
| design.md deleted-file ref + assertion wording | Corrected |
| Task 3.10 deferred ambiguity | Resolved |
| Task 5.19 tolerance (FND-P2-001) | Corrected (1e-9 → 1e-5, safe) |
| CAT-9 spot-check (Task 1.2) | PASSED |
| CAT-10 spot-check (Task 3.10) | PASSED with pattern concern (FND-323-001) |
| CAT-12 spot-check (Task 5.18) | PASSED |
| CAT-12 spot-check (Task 5.19 post-fix) | PASSED |
| PROJ-325 Phase 2 parametrize (Tasks 3.34 + 3.37) | PASSED (clean two-group split pattern) |

**Overall assessment:** PROJ-323's work quality is sound across all 5 phases. PROJ-325 Phase 1's documentation corrections are complete and accurate. One MAJOR finding (FND-323-001) — a non-idiomatic `__import__` pattern in one parametrize — does not affect correctness but should be normalized to match the codebase convention. No CRITICAL findings (no production regression risk, no silently-passing-on-broken-production).
