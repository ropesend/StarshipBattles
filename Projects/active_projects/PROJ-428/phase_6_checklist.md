# Phase 6: Harden registry purity AST guard (Codex follow-up)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-428 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete

**Depends on:** phase_5
**Review Mode:** lightweight
**Files (planned):**
- `tests/unit/strategy/turn_engine/test_turn_phase_registry_purity.py`

**Objective:** harden the Phase 4 registry-purity AST guard so that it cannot
be bypassed by class-body imports of gameplay engines, or by dynamic
`importlib.import_module(...)` / `__import__(...)` calls at module load.
Mirrors PROJ-424 Phase 7's hardening of the lazy-import guard at
`tests/unit/strategy/engine/commands/test_order_metadata_view.py`.

**Codex consult finding:** the original `test_no_forbidden_engine_module_imports`
helper walked only `tree.body` and only `ast.Import` / `ast.ImportFrom`
nodes. That left two classes of bypasses unguarded:

1. **Class-body imports** — a top-level `class _RegistryShim:` whose
   body contains `from game.strategy.engine.planet_modifier_effect_engine
   import PlanetModifierEffectEngine`. Class bodies execute at module
   load, so this reintroduces a gameplay-engine import while satisfying
   the old guard.
2. **Dynamic imports at module scope** —
   `importlib.import_module("game.strategy.engine.minefield_resolver")`
   and `__import__("game.strategy.engine.planet_modifier_effect_engine")`
   evaluated at module top (or inside a top-level class body).

Function-body imports are NOT bypasses (they only execute when the
function is called) and the hardened guard correctly leaves them alone.

---

## Tasks

### Task 6.1: Write the failing negative tests first [Simple]
**File:** `tests/unit/strategy/turn_engine/test_turn_phase_registry_purity.py`
**Tests:**
- `TestGuardCatchesBypassVectors::test_guard_detects_class_body_import_of_planet_modifier_engine`
- `TestGuardCatchesBypassVectors::test_guard_detects_top_level_importlib_import_module_call`
- `TestGuardCatchesBypassVectors::test_guard_detects_top_level_dunder_import_call`
- `TestGuardCatchesBypassVectors::test_guard_ignores_function_body_import`

- [x] Add four synthetic-source-string tests covering each vector
- [x] Confirm conceptually that each "must detect" case would have
      returned an empty offenders list under the original implementation
      (the original walker only iterated `tree.body` for `Import` /
      `ImportFrom` — `ClassDef` and `Expr(Call)` nodes were ignored).

### Task 6.2: Harden the helper [Simple]
**File:** `tests/unit/strategy/turn_engine/test_turn_phase_registry_purity.py`
**Tests:** all 8 tests in the file

- [x] Add `_iter_module_load_evaluated_statements(tree)` that yields
      module-top statements plus top-level class-body statements.
- [x] Add `_collect_dynamic_import_target(call)` that recognizes
      `importlib.import_module("...")` and `__import__("...")` and
      returns the string-literal argument.
- [x] Add `_find_forbidden_engine_imports(tree)` that scans both static
      imports and dynamic-import calls in the module-load-evaluated
      statement list, matching against the existing
      `_FORBIDDEN_ENGINE_IMPORT_SUBSTRINGS` and
      `_FORBIDDEN_IMPORTED_NAMES`.
- [x] Collapse the old `test_no_forbidden_engine_module_imports` and
      `test_no_forbidden_imported_names` into a single delegating test
      that calls the hardened helper.
- [x] Update class docstring to reflect the wider guard.

### Task 6.3: Run focused tests [Simple]
**File:** n/a
**Tests:**
- `pytest tests/unit/strategy/turn_engine/test_turn_phase_registry_purity.py -v`

- [x] All 8 tests green (4 prior structural + 4 new synthetic regression)
- [x] Real-registry purity assertion still green against the production
      `game/strategy/engine/turn_phase_registry.py`

**Notes:** Local run: `8 passed in 1.68s`.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Hardened helper handles class-body imports and dynamic imports
- [x] Function-body imports still correctly ignored
- [x] Real-registry purity assertion green against production source
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State
