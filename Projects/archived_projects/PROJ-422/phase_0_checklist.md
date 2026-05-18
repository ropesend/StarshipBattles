# Phase 0: Docs read + structural TDD anchor test

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-422 0`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** none
**Review Mode:** standard
**Files (planned):** tests/unit/strategy/interfaces/test_engines_package_layout.py
**Objective:** Establish the failing layout test (TDD anchor) and queue docs to update in Phase 4.

---

## Tasks

### Task 0.1: Read foundation docs and queue Phase 4 updates [Simple]
**Files:** `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`, `docs/03_CONVENTIONS.md`
**Tests:** none — discovery work

- [x] Read `docs/README.md` (documentation index)
- [x] Read `docs/01_ARCHITECTURE.md` (layers, APIs, protocols)
- [x] Read `docs/02_PATTERNS.md` (established design patterns)
- [x] Read `docs/03_CONVENTIONS.md` (naming, coding style)
- [x] Grep the `docs/` tree for any `engines.py` mention and queue findings for Phase 4:
  ```
  rg -n "engines\.py" docs/
  ```
  Skip any hit under `docs/_ignore/` per AGENTS.md. **Result: zero hits.**
- [x] Record discovered doc-update targets in `findings/phase_0_doc_targets.md`

**Notes:** docs/ tree had zero references to `engines.py`, `interfaces/engines`, or `interfaces.engines`. Phase 4 has no required updates; it will be a sanity-grep no-op.

### Task 0.2: Reconfirm baseline before editing [Simple]
**Files:** none (read-only verification)
**Tests:** none

- [x] Reconfirm the import-site inventory matches the TD plan:
  ```
  rg -n "from game\.strategy\.interfaces(\.engines)? import" game tests
  ```
  Expected: ~30 import sites. Mismatch → stop and reconcile with the TD plan before continuing.
- [x] Confirm the current single-file baseline still exists:
  ```
  python -c "from pathlib import Path; print(Path('game/strategy/interfaces/engines.py').exists())"
  ```
  Expected: `True`.
- [x] Confirm there is **no** pre-existing `game/strategy/interfaces/engines/` directory from parallel work. If one exists, stop and merge with that work instead of creating a second layout.

**Notes:** import-site sweep found 30 production+test consumers (matches the TD plan); `engines.py` exists; no `engines/` directory present.

### Task 0.3: Author the failing layout test (TDD anchor) [Medium]
**File:** `tests/unit/strategy/interfaces/test_engines_package_layout.py` (new)
**Tests:** `pytest tests/unit/strategy/interfaces/test_engines_package_layout.py -q` — MUST fail for the right reason

The test file declares the expected layout in code and asserts it. ~6 small tests:

- [x] `test_engines_is_a_package` — `game.strategy.interfaces.engines` has a `__path__` (package), not just a `__file__` (module).
- [x] `test_each_leaf_module_loads` — import each of the 9 leaf modules without error: `movement`, `orders`, `combat`, `production`, `logistics`, `population`, `planet_ops`, `terraforming`, `components`.
- [x] `test_each_abc_importable_from_package_root` — for every name in the expected 18-tuple, `getattr(engines, name)` resolves to a class that is a subclass of `abc.ABC`.
- [x] `test_each_leaf_exports_expected_abcs` — leaf module `__all__` matches the layout table verbatim (movement: `['IMovementEngine']`; orders: `['IOrderProcessor', 'IActionExecutionEngine']`; etc).
- [x] `test_top_level_interfaces_reexports_all_engines` — every name in `engines.__all__` is also in `game.strategy.interfaces.__all__`. (Will also fail today because of the 5-name drift; that's expected — Phase 2 fixes it.)
- [x] `test_no_dangling_engines_py_module` — `pathlib.Path('game/strategy/interfaces/engines.py')` does not exist. (Fails today because the monolith still exists; that's the TDD anchor — Phase 1 deletes it.)

- [x] Run the test, confirm it fails for the right reason: `engines` is still a module, not a package.

**Notes:** Layout test is RED with 5 failures and 1 pass — exactly the design contract:
- `test_engines_is_a_package` FAIL (engines is still a module)
- `test_each_leaf_module_loads` FAIL (no leaves yet)
- `test_each_leaf_exports_expected_abcs` FAIL (no leaves yet)
- `test_top_level_interfaces_reexports_all_engines` FAIL (5-name drift in `interfaces.__all__`)
- `test_no_dangling_engines_py_module` FAIL (`engines.py` still exists)
- `test_each_abc_importable_from_package_root` PASS (the 18 ABCs do live in the current monolith)

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Layout test is red for the documented reason (`engines` is still a module)
- [x] `python Projects/scripts/validate_phase.py PROJ-422 0` passes
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 1
