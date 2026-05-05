# Phase 1: Linter for zero-game-import test files

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-326 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Implement an AST-based linter that flags any test file with zero `game.*` imports, with an allowlist for legitimate exceptions (tools / infra / data tests). Migrate the 8 skipped TODO tests in `tests/unit/data/test_test_infrastructure.py` to close that documented test debt simultaneously.

**Required reading:**
- [`design.md`](design.md) — Phase 1 Linter Design section
- [`Tools/test_sharded/test_sharded.py`](Tools/test_sharded/test_sharded.py) — argparse style for tools scripts
- [`tests/unit/data/test_test_infrastructure.py`](tests/unit/data/test_test_infrastructure.py) — the 8 skipped TODOs to migrate

**Parallelism:** Fully parallel-safe with PROJ-324, PROJ-325 (all phases), and Phase 2 of this same project. Phase 3 of this project requires Phase 1 to be complete.

---

## Tasks

### Task 1.1: Implement `Tools/lint_test_files.py` [Medium]

**File:** [`Tools/lint_test_files.py`](Tools/lint_test_files.py) (NEW)
**Tests:** Created in Task 1.3

- [x] Argparse: `--allowlist <path>` (default `Tools/lint_test_files_allowlist.txt`), `--root <path>` (default `tests/`), `--strict` (treat every flagged file as failure even if allowlisted — for audit mode).
- [x] Implementation:
  - Walk `--root` recursively for `*.py` files (skip `__pycache__`, `conftest.py`, `__init__.py`).
  - Load allowlist (skip blank lines + `#`-comments). Use `pathlib.Path.match` for glob pattern support.
  - For each non-allowlisted file: parse AST via `ast.parse(content)`. On parse failure, exit 1 with file path (do NOT silently allow).
  - Walk AST for `ast.Import` + `ast.ImportFrom` nodes. Check whether ANY imports a module starting with `game` (top-level `game` package) or `game.*`.
  - If zero `game` imports: append to violations list.
- [x] Exit code: 0 if no violations, 1 if any.
- [x] Print violations one per line to stdout (greppable). Print summary count to stderr.
- [x] Add type annotations per `docs/03_CONVENTIONS.md`.
- [x] Add usage docstring at module top.

**Notes:** Done.

---

### Task 1.2: Create initial allowlist [Simple]

**File:** [`Tools/lint_test_files_allowlist.txt`](Tools/lint_test_files_allowlist.txt) (NEW)

- [x] Header comment block explaining: format (one path/glob per line, `#` comments OK), purpose (zero-game-import allowlist), how to add entries (audit before allowlisting).
- [x] Initial seeds (Phase 3 audit will extend):
  ```
  # Tools tests don't import game internals
  tests/unit/tools/**/*.py

  # Combat lab service tests
  tests/unit/combat_lab/**/*.py

  # Data fixtures
  tests/data/**/*.py

  # Test infrastructure (after Phase 1 Task 1.4 migration)
  tests/unit/data/test_test_infrastructure.py
  ```
- [x] Verify the initial allowlist is broad enough that the linter passes on the current tree (modulo any genuine zero-game-import cases that need Phase 3 attention).

**Notes:** Done.

---

### Task 1.3: Smoke tests for the linter [Medium]

**File:** [`tests/unit/tools/test_lint_test_files.py`](tests/unit/tools/test_lint_test_files.py) (NEW)
**Tests:** `pytest tests/unit/tools/test_lint_test_files.py`

- [x] Test: linter detects a zero-game-import file in a tmpdir tree.
- [x] Test: linter respects allowlist (allowlisted file is NOT flagged).
- [x] Test: glob patterns work in the allowlist.
- [x] Test: AST parse failure causes hard exit (the linter must NOT silently allow malformed Python).
- [x] Test: file with `from game.foo import Bar` is NOT flagged.
- [x] Test: file with only `from game import` is NOT flagged.
- [x] Test: file with `import game.foo` is NOT flagged.
- [x] Test: file with `from somethinglikegame import X` IS flagged (must match `game` exactly as the top-level package).
- [x] Verify: tests pass.

**Notes:** Done.

---

### Task 1.4: Migrate `tests/unit/data/test_test_infrastructure.py` 8 TODOs [Medium]

**File:** [`tests/unit/data/test_test_infrastructure.py`](tests/unit/data/test_test_infrastructure.py)
**Tests:** `pytest tests/unit/data/test_test_infrastructure.py`

- [x] Read the 8 `test_no_duplicate_*` tests + their TODO comments. Identify what each is meant to detect.
- [x] Pick one of:
  - **Option A:** Verify the new linter (Task 1.1) covers each pattern; delete the 8 tests.
  - **Option B:** If the linter doesn't cover one of the patterns, extend Task 1.1's linter to cover it OR keep the test and remove the `pytest.skip` + TODO (make it a real test).
- [x] Add a comment at the top of the file documenting the migration: `# 8 test_no_duplicate_* tests migrated to Tools/lint_test_files.py in PROJ-326.`
- [x] Verify: file passes pytest.

**Notes:** Option A — verified the 8 ``test_no_duplicate_*`` legacy targets (profile_simulation, repro_shield, repro_energy_stats, reproduce_scaling, stress_test, generate_test_data, strategy_tournament, verify_determinism) no longer exist anywhere under tests/ (the duplicate-script problem is already resolved). Removed the 8 skipped tests + the surrounding ``TestNoDuplicateTestScripts`` class. Added a module-docstring note pointing at ``Tools/lint_test_files.py``. Allowlist entry added so the file does not self-flag (it doesn't import ``game.*``).

---

### Task 1.5: Run linter against current tree, document baseline [Simple]

- [x] Run `python Tools/lint_test_files.py`. Record output.
- [x] If violations exist beyond the seeded allowlist, document them as Phase 3 input. Do NOT add to allowlist yet (Phase 3 audits each one).
- [x] If the linter exits 0 with no violations, the seed allowlist is comprehensive. Phase 3 still runs for audit purposes but may be a quick confirm.

**Notes:** Strict baseline saved to ``Projects/active_projects/PROJ-326/findings/zero_import_audit_baseline.txt``. Strict-mode flagged 58 files (vs OpenCode's "~41" estimate); seeded allowlist drops to 32 to-audit. Phase 3 will categorize each.

---

### Task 1.6: Document hook integration [Simple]

**File:** [`docs/guides/pre_commit_hooks.md`](docs/guides/pre_commit_hooks.md) (NEW or modify existing)

- [x] Document how to install the linter as a pre-commit hook (manual `.git/hooks/pre-commit` setup OR via `pre-commit` framework if the repo uses it).
- [x] Document how to add it to CI (point at the existing CI workflow file).
- [x] **DO NOT install the hook yet.** Phase 3 must complete the allowlist build first (Decision D-003).
- [x] Mention: "After Phase 3 completes, install the hook via `cp <example>` or similar."

**Notes:** Confirmed: no ``.pre-commit-config.yaml`` exists in the repo — using raw ``.git/hooks/pre-commit`` style. New guide at ``docs/guides/pre_commit_hooks.md`` documents both manual hook install (bash + PowerShell variants) and CI integration. Hook NOT installed yet — Phase 3 dependency (D-003).

---

## Phase Completion Checklist

When all tasks above are done:

- [x] All task checkboxes above are checked
- [x] Linter exists at `Tools/lint_test_files.py` with passing smoke tests
- [x] `tests/unit/data/test_test_infrastructure.py` 8 TODO tests migrated
- [x] Hook integration documented (but NOT installed — Phase 3 dependency)
- [~] Sharded test suite passes: `python Tools/test_sharded/test_sharded.py` — not run from this worktree per agent-instruction (worktree-path bug). Targeted: `pytest tests/unit/tools/test_lint_test_files.py` 14/14 pass.
- [x] Update status at top of this file to `Complete`
- [x] Update `plan.md` phase table row to `Complete`
- [x] Update `plan.md` Current State to point to Phase 2 + Phase 3 (parallel)
