# Phase 6: Codex consult follow-ups

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-422 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** phase_5
**Review Mode:** lightweight
**Files (planned):**
- `tests/unit/strategy/interfaces/test_engine_inheritance.py` (docstring fix)
- `tests/unit/strategy/interfaces/test_engines_leaf_path_discipline.py` (new guard)

**Objective:** Address two bounded findings raised by a Codex consult on the merged PROJ-422 surface — a stale docstring referencing the deleted monolith, and an unenforced architectural invariant (leaf-private import discipline).

---

## Tasks

### Task 6.1: Fix stale test docstring [Simple]
**File:** `tests/unit/strategy/interfaces/test_engine_inheritance.py`
**Tests:** focused run of the file (collection + 14 inheritance assertions)

- [x] Replace the reference to `game/strategy/interfaces/engines.py` (the deleted monolith) with the `game/strategy/interfaces/engines/` package path.
- [x] Restate the PROJ-422 leaf-private invariant so future readers know they must import via the package root.
- [x] Confirm the file still collects and all 14 parametrised inheritance assertions pass.

### Task 6.2: Add leaf-path import-discipline guard test [Medium]
**File:** `tests/unit/strategy/interfaces/test_engines_leaf_path_discipline.py` (new)
**Tests:** the new file itself — 1 repo-walk assertion + 5 walker self-tests

- [x] Walk `game/` and `tests/` for any `from game.strategy.interfaces.engines.<leaf> import ...` or `import game.strategy.interfaces.engines.<leaf>` (leaves: movement, orders, combat, production, logistics, population, planet_ops, terraforming, components).
- [x] Use `ast.parse` (matches the repo's preferred guard style; see `tests/unit/strategy/engine/test_no_specs_tuple_literal.py`).
- [x] Allowlist exactly two files: `game/strategy/interfaces/engines/__init__.py` and `tests/unit/strategy/interfaces/test_engines_package_layout.py`.
- [x] Emit a helpful failure message naming `<file>:<lineno>: imports <module>` for any offender, with the fix instruction (use package-root import).
- [x] Include walker self-tests proving the guard catches both `from`-leaf and bare-`import`-leaf forms, and does NOT flag the allowed package-root import, an unrelated import, or an unknown not-yet-real leaf name.
- [x] Confirm the file passes (no current violations).

### Task 6.3: Project state housekeeping [Simple]

- [x] Add `phase_6` entry to `phase_state.json` (status `complete`, `depends_on: ["phase_5"]`, `review_mode: lightweight`, both planned files listed).
- [x] Add Phase 6 row to `plan.md` Quick Status table.
- [x] Add Phase 6 paragraph to `plan.md` Phases section.
- [x] Update `plan.md` Current State (Last Updated, Last Action).
- [x] Append a row to `decisions.md` noting the Codex consult origin and what was added.

---

## Notes

- Strict TDD note: Task 6.2's guard test was written first and **passed on first run** — the architectural invariant was already being followed at the code level, just not enforced. The guard makes it permanent.
- Walker self-tests are included to satisfy the project convention used by `test_no_specs_tuple_literal.py`: prove the guard is not vacuous before relying on it.
- The 5 walker self-tests use synthetic AST strings only; no fixtures, no test files on disk.
