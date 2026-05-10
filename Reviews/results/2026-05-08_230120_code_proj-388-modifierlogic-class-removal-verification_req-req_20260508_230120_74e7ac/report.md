# Review Report: PROJ-388 — ModifierLogic class removal verification

**Request ID:** req_20260508_230120_74e7ac
**Review Type:** code
**Branch:** feat/03c-phase-aware-execution
**Completed:** 2026-05-08T23:30:00Z
**Recommendation:** APPROVE

---

## Summary

All 9 verification items pass. The `ModifierLogic` static-wrapper class has been completely removed from `game/ui/screens/builder/modifier_logic.py`. All 3 production consumers (`ModifierEditorPanel`, `ModifierControlRow`, `ComponentDetailPanel`) now receive `ModifierLogicService` via required constructor injection. No compat shims, fallbacks, or wrappers were introduced. Zero live code references to the deleted `ModifierLogic` class remain. Test files are correctly retargeted. PROJ-385's formula migration files are intact on the branch.

---

## Verification Matrix

| # | Item | Status | Severity | Details |
|---|---|---|---|---|
| 1 | Completeness of removal | PASS | — | Zero live-code references to `ModifierLogic` class |
| 2 | Constructor injection correctness | PASS | — | All 3 panels wired with required keyword args |
| 3 | `ComponentDetailPanel.__init__` signature | PASS | — | Both `modifier_logic` and `event_bus` are keyword-only; all call sites use kwargs |
| 4 | Test migration soundness | PASS | — | Tests retargeted correctly; no tests weakened |
| 5 | Compat-shim hygiene | PASS | — | Clean deletion; no new wrappers/fallbacks/shim introduced |
| 6 | Scope discipline | PASS | — | `ModifierLogicService` internals untouched |
| 7 | PROJ-385 changes preserved | PASS | — | `formula_evaluator.py` intact; `formula_engine.py` absent per PROJ-385 |
| 8 | Filename appropriateness | INFO | — | `modifier_logic.py` now contains only `ModifierLogicService`; filename slightly misleading but no rename required per instructions |
| 9 | Pre-existing failures | PASS | — | Plan.md confirms 3 pre-existing failures, 0 new failures |

---

## Detailed Findings

### 1. Completeness of Removal (PASS)

`grep -rn "\bModifierLogic\b" .` across the entire repo finds zero live production or test code that imports, references, or instantiates `ModifierLogic` (the deleted class). All hits fall into three categories:
- **PROJ-388 tracking docs** (`Projects/active_projects/PROJ-388/`) — expected
- **Archived/historical docs** (`Projects/deep_archive/`, `Reviews/results/_archive_*`) — expected
- **Review results** (`Reviews/results/`) — expected, pre-date this change
- **This request file** — expected

Specifically verified:
- `grep -rn "from game.ui.screens.builder.modifier_logic import ModifierLogic\b" .` → **zero hits**
- `grep -rn "ModifierLogic.init_service\|ModifierLogic.set_service\|ModifierLogic._get_service" . --include="*.py"` → **zero hits**
- `game/ui/screens/builder/modifier_logic.py` — only `ModifierLogicService` class remains (173 lines, lines 34-173)
- `game/ui/screens/builder/__init__.py:7` — re-exports `ModifierLogicService`, not `ModifierLogic`

### 2. Constructor Injection Correctness (PASS)

The wiring chain is clean with no `or` fallback defaults:

| Panel | Constructor signature | Production wiring |
|---|---|---|
| `ModifierEditorPanel` | `modifier_logic: ModifierLogicService` (builder_widgets.py:34) | `workshop_screen.py:260-267` — `modifier_logic=self._modifier_logic` |
| `ModifierControlRow` | `modifier_logic: ModifierLogicService` (modifier_row.py:42) | Created internally by `ModifierEditorPanel`, which passes its `_modifier_logic` through |
| `ComponentDetailPanel` | `modifier_logic: ModifierLogicService` (detail_panel.py:27) | `workshop_screen.py:296-301` — `modifier_logic=self._modifier_logic` |

The composition root at `workshop_screen.py:72`:
```python
self._modifier_logic = ModifierLogicService(context.registries)
```
No `init_service()` bootstrap pattern anywhere. The old `ModifierLogic.init_service(context.registries)` call that previously lived in `workshop_screen.py` is fully removed.

All 3 keyword args have **no default value** — constructing any of these panels without `modifier_logic=` will raise `TypeError`, preventing silent dependency swallowing.

### 3. `ComponentDetailPanel.__init__` Signature Change (PASS)

Signature at `detail_panel.py:27`:
```python
def __init__(self, manager, rect, *, modifier_logic: ModifierLogicService, event_bus=None):
```
Both `modifier_logic` and `event_bus` are keyword-only (after `*`).

Call site verification:
- **Production** (`workshop_screen.py:296-301`): passes `event_bus=self.event_bus, modifier_logic=self._modifier_logic` as kwargs
- **Test** (`test_detail_panel_rendering.py:72-76`): passes `modifier_logic=self.mock_modifier_logic` as kwargs
- No positional passing exists anywhere in the repo.

### 4. Test Migration Soundness (PASS)

Sampled migrated test files — all correctly retargeted:

- **`test_mandatory_modifiers_ownership.py`** (`tests/unit/ui/screens/builder/`): Assertions retargeted from `ModifierLogic` to `ModifierLogicService.__dict__`. Checks that `ModifierLogicService` does not have its own `MANDATORY_MODIFIERS` constant. Comment block documents the PROJ-388 migration explicitly.
- **`test_modifier_logic_smart_floor.py`** (`tests/unit/ui/screens/builder/`): Uses `ModifierLogicService.calculate_snap_value(...)` as a class-level method call. Valid — `calculate_snap_value` is a `@staticmethod` on `ModifierLogicService`.
- **`test_modifier_control_row.py`** (`tests/unit/ui/screens/builder/`): Constructs `ModifierControlRow(modifier_logic=MagicMock(), ...)` with keyword arg.
- **`test_modifier_editor_panel.py`** (`tests/unit/ui/panels/`): Constructs `ModifierEditorPanel(modifier_logic=MagicMock(), ...)` with keyword arg.
- **`test_detail_panel_rendering.py`** (`tests/unit/ui/`): Constructs `ComponentDetailPanel(..., modifier_logic=self.mock_modifier_logic)` with keyword arg.
- **`test_modifier_row.py`** (`tests/unit/ui/screens/builder/`): Uses `ModifierControlRow` class; all constructor calls pass `modifier_logic=` kwarg.

No tests appear weakened — assertion counts match pre-migration levels. No `pytest.skip`, `pytest.xfail`, or conditionally-broadened assertions added.

### 5. Compat-Shim Hygiene (PASS)

Grep for `compat|shim|fallback|wrapper|deprecated` in all 6 production files returned only one false positive:
- `builder_widgets.py:5`: comment `"PROJ-50: Made registries mandatory, removed fallback pattern."` — pre-existing, unrelated to PROJ-388
- `workshop_screen.py:250`: comment `"We need a wrapper panel for the modifier editor..."` — refers to a pygame_gui `UIPanel` container element, not a code compat shim

No `warnings.warn`, `DeprecationWarning`, `__getattr__` fallbacks, or `try/except ImportError` compat paths introduced. The change is a clean delete + constructor injection migration.

### 6. Scope Discipline (PASS)

`ModifierLogicService` class body (`modifier_logic.py:34-173`) is untouched. Methods verified:
- `__init__`, `is_modifier_allowed`, `get_mandatory_modifiers`, `is_modifier_mandatory`, `get_initial_value`, `get_local_min_max`, `ensure_mandatory_modifiers`, `_get_base_firing_arc`, `calculate_snap_value` — all unchanged

No consolidation with `ModifierService` (simulation layer) attempted. The cross-system Pair 4 consolidation remains explicitly out of scope per the plan.

### 7. PROJ-385 Changes Preserved (PASS)

Key PROJ-385 artifacts verified intact on branch:
- `game/core/formula_evaluator.py` — 404 lines, last modified May 8 2026. Contains `FormulaEvaluator` class with PROJ-242 provenance. No recent modifications (`git diff` against parent commits shows no changes).
- `game/core/formula_engine.py` — correctly absent (removed by PROJ-385).
- `game/strategy/formulas/` directory — `__init__.py`, `colony_output.py`, `habitability.py` all present and intact.

### 8. Filename Appropriateness (INFO)

The file `game/ui/screens/builder/modifier_logic.py` now contains only `ModifierLogicService`. The filename `modifier_logic` previously encompassed both `ModifierLogic` (static wrapper) and `ModifierLogicService`. With the wrapper removed, the filename could be slightly misleading — a reader might expect a `ModifierLogic` class. However:

- The module was always the canonical home of `ModifierLogicService`
- Renaming would cascade to ~40 import sites across production and tests
- The request explicitly marks this as "informational — flag if misleading; no rename required"

**Severity:** INFO. No action required for this phase.

### 9. Pre-Existing Failures (PASS)

The PROJ-388 plan (`Projects/active_projects/PROJ-388/plan.md:21`) states:

> "Sharded suite: 19084 passed / 3 pre-existing failures (no new failures); `validate_phase.py PROJ-388 1` PASSED."

The 3 pre-existing failures match the same failures from PROJ-385:
1. `test_scalene_workflow_files_are_documented` (`tests/unit/tools/test_scalene_profiling_workflow.py:15`)
2. `test_skill_does_not_claim_coverage_json_is_supported` (`tests/unit/tools/test_testcoverage_audit.py:75`)
3. `test_pathfinder_attached_after_init` (`tests/integration/strategy/test_save_round_trip_phase4.py:31`)

These are known flakes documented in `AGENTS.md:58`. PROJ-388 introduced 0 new failures. (Note: `test_baseline.json` has a merge conflict on line 9 — unrelated to PROJ-388.)

---

## Recommendations

**APPROVE.** All 9 verification items pass. The change is a clean, well-executed legacy-class removal with proper constructor injection, correct test retargeting, no compat-shim regression, and preserved sibling-project changes.

One informational flag: `modifier_logic.py` filename is now slightly misleading (INFO, no action required).
