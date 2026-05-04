# Review Report: PROJ-330 + PROJ-329A Phase 2

**Review Mode:** code (deep, single-pass)
**Scope:** 14 production + fixture + test files
**Branch:** feat/03c-phase-aware-execution
**Request ID:** req_20260504_222600_cac643

---

## Verification Matrix

No parent request — this is an independent review.

---

## CRITICAL

### C1: Concurrent-commit contamination — FoodAllocationEditor refactor in PROJ-337 commit

**File:** commit `cd7f84b59`
**Severity:** CRITICAL

The commit labeled `test(research): characterize ResearchRenderer drawing behavior (PROJ-337)` bundles the entire PROJ-329A Phase 2 Task 2.1 refactor (FoodAllocationEditor two-stage construction):

| File | Delta | Belongs to |
|---|---|---|
| `game/ui/screens/food_allocation_editor.py` | +89/-55 | PROJ-329A Phase 2 Task 2.1 |
| `tests/fixtures/food_allocation_editor_ui_builder.py` | +80 (NEW) | PROJ-329A Phase 2 Task 2.1 |
| `tests/unit/ui/screens/test_food_allocation_editor.py` | +176/-? | PROJ-329A Phase 2 Task 2.1 |
| `tests/unit/research/test_research_renderer_drawing.py` | +667 (NEW) | PROJ-337 |

The commit message, Co-Authored-By metadata, and summary describe only PROJ-337 ResearchRenderer characterization tests. The PROJ-329A work (3 files, ~344 LOC delta) is unmentioned. A bisect landing on this commit would incorrectly implicate the FoodAllocationEditor when investigating a PROJ-337 regression, and reverting for a PROJ-337 bug would also revert the PROJ-329A work.

### C2: Concurrent-commit contamination — PROJ-330 assets + selection extractions in PROJ-329A commit

**File:** commit `2bbb260f6`
**Severity:** CRITICAL

The commit labeled `feat(329A): retrofit PlanetSelectionWindow to two-stage construction (TDD-first)` also creates PROJ-330 modules and their test files:

| File | Delta | Belongs to |
|---|---|---|
| `game/ui/screens/planet_selection_window.py` | +163/-? | PROJ-329A Phase 2 Task 2.3 |
| `tests/fixtures/planet_selection_window_ui_builder.py` | +72 (NEW) | PROJ-329A Phase 2 Task 2.3 |
| `tests/unit/ui/screens/test_planet_selection_window.py` | +209 (NEW) | PROJ-329A Phase 2 Task 2.3 |
| `game/ui/screens/strategy_screen_assets.py` | +88 (NEW) | PROJ-330 Phase 1 |
| `game/ui/screens/strategy_screen_selection.py` | +99 (NEW) | PROJ-330 Phase 4 |
| `tests/unit/ui/screens/test_strategy_screen_assets.py` | +170 (NEW) | PROJ-330 |
| `tests/unit/ui/screens/test_strategy_screen_selection.py` | +184 (NEW) | PROJ-330 |
| `game/ui/screens/strategy_screen.py` | +?/-145 | PROJ-330 |
| `game/ui/screens/strategy_screen_lifecycle.py` | +14/-? | PROJ-330 |
| `tests/unit/ui/screens/test_strategy_screen.py` | +20/-? | PROJ-330 |
| `tests/unit/ui/screens/test_strategy_screen_lifecycle.py` | +21/-? | PROJ-330 |

PROJ-330 has no independent Phase 1 (assets extraction) or Phase 4 (selection extraction) commit. The `strategy_screen_assets.py` (88 LOC) and `strategy_screen_selection.py` (99 LOC) modules — plus their combined 354 LOC of test files — were created inside a commit whose message, metadata, and summary describe only the PlanetSelectionWindow retrofit. A git blame on those files points to a PROJ-329A commit, which is semantically wrong.

---

## MAJOR

### M1: Per-class commit discipline (D-007) violated

**File:** PROJ-329A `decisions.md` § D-007, commits cd7f84b59, 2bbb260f6
**Severity:** MAJOR

PROJ-329A Decision D-007 requires: "Each retrofitted class lands in its own commit so bisect/revert is per-class." Two of the three Phase 2 classes violate this:

- **FoodAllocationEditor** (Task 2.1) — its production refactor, fixture, and test migration are co-resident with PROJ-337 research tests in commit cd7f84b59. The commit message does not mention FoodAllocationEditor or PROJ-329A.
- **PlanetSelectionWindow** (Task 2.3) — its production refactor, fixture, and tests are co-resident with ~664 LOC of PROJ-330 extraction work in commit 2bbb260f6.

Only FleetSelectionWindow (Task 2.2) landed in its own commit (5a3acb260).

---

## MINOR

### M2: PROJ-330 has no Phase 1 or Phase 4 commit

**File:** git history for `strategy_screen_assets.py`, `strategy_screen_selection.py`
**Severity:** MINOR

PROJ-330 Phase 2 (lifecycle, commit fef98c756) and Phase 3 (order-editing, commit f0b71d8ee) each have dedicated commits. Phases 1 and 4 have no independent commits — their modules were created in commit 2bbb260f6 alongside PROJ-329A work. The project's per-phase tracking and per-class commit discipline are incomplete.

---

## OBSERVATIONS

### O1: PROJ-330 patch targets verified correct

**File:** `tests/unit/ui/screens/test_strategy_screen.py:168, 181, 193, 205, 606`
**Severity:** OBSERVATION

The 5 patch sites correctly target `game.ui.screens.strategy_screen_selection.is_fleet` and `game.ui.screens.strategy_screen_selection.is_star_system`. These names are bound via `from game.core.protocols import is_fleet, is_star_system` inside `strategy_screen_selection.py`, so patching at the importing module's namespace is correct. The original patches (pre-refactor) targeted `strategy_screen.is_fleet`; post-refactor, the function's binding site moved to `strategy_screen_selection`. The test behavior is unchanged.

### O2: Pattern §33 conformance — all 3 classes pass

**Severity:** OBSERVATION

All three PROJ-329A Phase 2 classes implement the two-stage construction pattern correctly:

| Check | FoodAllocationEditor | FleetSelectionWindow | PlanetSelectionWindow |
|---|---|---|---|
| Cheap state before bypass guard | ✓ (line 279-290) | ✓ (line 117-121) | ✓ (line 124-142) |
| Explicit `ui_builder` parameter | ✓ (line 277) | ✓ (line 103) | ✓ (line 109) |
| Default builder in production path | ✓ (line 310) | ✓ (line 135) | ✓ (line 156) |
| Null fixture | ✓ (`NullFoodAllocationEditorUiBuilder`) | ✓ (`NullFleetSelectionWindowUiBuilder`) | ✓ (`NullPlanetSelectionWindowUiBuilder`) |
| Mock fixture | ✓ (`MockFoodAllocationEditorUiBuilder`) | ✓ (`MockFleetSelectionWindowUiBuilder`) | ✓ (`MockPlanetSelectionWindowUiBuilder`) |
| Bypass guard type-checks `type(self)` (per Pattern §33 migration note) | ✓ (`getattr(self, '_window_init_bypassed', False)`) | ✓ | ✓ |

### O3: LOC ceilings verified

**Severity:** OBSERVATION

| File | LOC | Under 500? |
|---|---|---|
| `strategy_screen.py` | 458 | ✓ |
| `strategy_screen_lifecycle.py` | 148 | ✓ |
| `strategy_screen_order_editing.py` | 91 | ✓ |
| `strategy_screen_assets.py` | 88 | ✓ |
| `strategy_screen_selection.py` | 99 | ✓ |
| `food_allocation_editor.py` | 394 | ✓ |
| `fleet_selection_window.py` | 152 | ✓ |
| `planet_selection_window.py` | 232 | ✓ |

### O4: No new MVVM seam in PROJ-330

**Severity:** OBSERVATION

Each PROJ-330 helper module passes the `StrategyScreen` instance as a parameter and mutates it directly. No new Protocol classes, factories, or abstractions beyond PROJ-327 Phase 4's `StrategyScreenComposition` were added. The decomposition is purely mechanical — function extraction with lazy imports.

### O5: Test quality — characterization tests are meaningful

**Severity:** OBSERVATION

- **FleetSelectionWindow** (11 tests): Covers Stage-1 cheap state (fleets reference, callback storage, display label generation, label-to-fleet lookup), bypass flag, Null/Mock builder interaction, `_fleet_display_label` formatting, and update() button dispatch (confirm-with-selection invokes callback and kills, confirm-without-selection no-ops, cancel kills without callback). Tests cross the public update() boundary rather than patching private methods.
- **PlanetSelectionWindow** (18 tests): Covers Stage-1 state initialization (planets, callback, 3 selection-tracking attributes), list_label and show_any_button storage, minimum-rect clamping (3 sub-cases), conditional Any-Planet button (2 sub-cases), Null builder widget-slot emptiness, and update() button dispatch (3 sub-cases). Tests verify the rect clamping happens in Stage 1 before the shell is constructed.
- **FoodAllocationEditor** (31 tests): Retains all existing business-logic tests (gather_rows, resolve_food_resource_name, compute_consumption_preview, apply_allocations, editor preview text) plus new two-stage construction smoke tests (bypass flag, Null builder, collect_allocations branches, apply/cancel button behavior).

None are vacuous — every test pins a specific behavior or invariant.

### O6: Bypass safety — kill() known limitation

**Severity:** OBSERVATION

Under `bypass_init`, `StrategyModalWindow.__init__` returns before calling `UIWindow.__init__`. Consequently, `kill()` → `StrategyModalWindow.kill()` → `super().kill()` → `UIWindow.kill()` reaches pygame_gui cleanup code that depends on `__init__`-time initialization. This is a documented limitation of Pattern #33 (PROJ-325 PoC finding 1). The test files correctly handle this by patching `window.kill` when they need to assert it was called, avoiding a real kill() call on bypass-mode instances. Production code is unaffected — the production path always calls `super().__init__()` fully.

### O7: Test counts match claims

**Severity:** OBSERVATION

| Claim | Actual |
|---|---|
| test_strategy_screen.py: 62 tests | 62 ✓ |
| test_fleet_selection_window.py: 11 tests | 11 ✓ |
| test_planet_selection_window.py: 18 tests | 18 ✓ |
| test_food_allocation_editor.py: ~31 tests | 31 ✓ |
| strategy_screen_lifecycle.py: 148 LOC | 148 ✓ |

---

## Summary

| Severity | Count | Key Issue |
|---|---|---|
| CRITICAL | 2 | Cross-project commit contamination |
| MAJOR | 1 | Per-class commit discipline violated |
| MINOR | 1 | Incomplete per-phase commit history |
| OBSERVATION | 7 | Pattern conformance, LOC, test quality all pass |

The production code is correct and the pattern implementation is clean. The sole substantive issue is commit hygiene: two commits (`cd7f84b59`, `2bbb260f6`) bundle work across multiple projects, making bisect/revert unsafe and violating D-007. The FoodAllocationEditor refactor is particularly problematic — its entire production + test change is invisible from the commit message.
