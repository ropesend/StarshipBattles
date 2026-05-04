# Phase 1: Linter for zero-game-import test files

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-326 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
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

- [ ] Argparse: `--allowlist <path>` (default `Tools/lint_test_files_allowlist.txt`), `--root <path>` (default `tests/`), `--strict` (treat every flagged file as failure even if allowlisted — for audit mode).
- [ ] Implementation:
  - Walk `--root` recursively for `*.py` files (skip `__pycache__`, `conftest.py`, `__init__.py`).
  - Load allowlist (skip blank lines + `#`-comments). Use `pathlib.Path.match` for glob pattern support.
  - For each non-allowlisted file: parse AST via `ast.parse(content)`. On parse failure, exit 1 with file path (do NOT silently allow).
  - Walk AST for `ast.Import` + `ast.ImportFrom` nodes. Check whether ANY imports a module starting with `game` (top-level `game` package) or `game.*`.
  - If zero `game` imports: append to violations list.
- [ ] Exit code: 0 if no violations, 1 if any.
- [ ] Print violations one per line to stdout (greppable). Print summary count to stderr.
- [ ] Add type annotations per `docs/03_CONVENTIONS.md`.
- [ ] Add usage docstring at module top.

**Notes:** [Filled during implementation]

---

### Task 1.2: Create initial allowlist [Simple]

**File:** [`Tools/lint_test_files_allowlist.txt`](Tools/lint_test_files_allowlist.txt) (NEW)

- [ ] Header comment block explaining: format (one path/glob per line, `#` comments OK), purpose (zero-game-import allowlist), how to add entries (audit before allowlisting).
- [ ] Initial seeds (Phase 3 audit will extend):
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
- [ ] Verify the initial allowlist is broad enough that the linter passes on the current tree (modulo any genuine zero-game-import cases that need Phase 3 attention).

**Notes:** [Filled during implementation]

---

### Task 1.3: Smoke tests for the linter [Medium]

**File:** [`tests/unit/tools/test_lint_test_files.py`](tests/unit/tools/test_lint_test_files.py) (NEW)
**Tests:** `pytest tests/unit/tools/test_lint_test_files.py`

- [ ] Test: linter detects a zero-game-import file in a tmpdir tree.
- [ ] Test: linter respects allowlist (allowlisted file is NOT flagged).
- [ ] Test: glob patterns work in the allowlist.
- [ ] Test: AST parse failure causes hard exit (the linter must NOT silently allow malformed Python).
- [ ] Test: file with `from game.foo import Bar` is NOT flagged.
- [ ] Test: file with only `from game import` is NOT flagged.
- [ ] Test: file with `import game.foo` is NOT flagged.
- [ ] Test: file with `from somethinglikegame import X` IS flagged (must match `game` exactly as the top-level package).
- [ ] Verify: tests pass.

**Notes:** [Filled during implementation]

---

### Task 1.4: Migrate `tests/unit/data/test_test_infrastructure.py` 8 TODOs [Medium]

**File:** [`tests/unit/data/test_test_infrastructure.py`](tests/unit/data/test_test_infrastructure.py)
**Tests:** `pytest tests/unit/data/test_test_infrastructure.py`

- [ ] Read the 8 `test_no_duplicate_*` tests + their TODO comments. Identify what each is meant to detect.
- [ ] Pick one of:
  - **Option A:** Verify the new linter (Task 1.1) covers each pattern; delete the 8 tests.
  - **Option B:** If the linter doesn't cover one of the patterns, extend Task 1.1's linter to cover it OR keep the test and remove the `pytest.skip` + TODO (make it a real test).
- [ ] Add a comment at the top of the file documenting the migration: `# 8 test_no_duplicate_* tests migrated to Tools/lint_test_files.py in PROJ-326.`
- [ ] Verify: file passes pytest.

**Notes:** [Filled during implementation. Document which option chosen for each pattern.]

---

### Task 1.5: Run linter against current tree, document baseline [Simple]

- [ ] Run `python Tools/lint_test_files.py`. Record output.
- [ ] If violations exist beyond the seeded allowlist, document them as Phase 3 input. Do NOT add to allowlist yet (Phase 3 audits each one).
- [ ] If the linter exits 0 with no violations, the seed allowlist is comprehensive. Phase 3 still runs for audit purposes but may be a quick confirm.

**Notes:** [Filled during implementation. Save baseline output to a file in `findings/`.]

---

### Task 1.6: Document hook integration [Simple]

**File:** [`docs/guides/pre_commit_hooks.md`](docs/guides/pre_commit_hooks.md) (NEW or modify existing)

- [ ] Document how to install the linter as a pre-commit hook (manual `.git/hooks/pre-commit` setup OR via `pre-commit` framework if the repo uses it).
- [ ] Document how to add it to CI (point at the existing CI workflow file).
- [ ] **DO NOT install the hook yet.** Phase 3 must complete the allowlist build first (Decision D-003).
- [ ] Mention: "After Phase 3 completes, install the hook via `cp <example>` or similar."

**Notes:** [Filled during implementation. Confirm whether `pre-commit` framework is used or raw hooks.]

---

## Phase Completion Checklist

When all tasks above are done:

- [ ] All task checkboxes above are checked
- [ ] Linter exists at `Tools/lint_test_files.py` with passing smoke tests
- [ ] `tests/unit/data/test_test_infrastructure.py` 8 TODO tests migrated
- [ ] Hook integration documented (but NOT installed — Phase 3 dependency)
- [ ] Sharded test suite passes: `python Tools/test_sharded/test_sharded.py`
- [ ] Update status at top of this file to `Complete`
- [ ] Update `plan.md` phase table row to `Complete`
- [ ] Update `plan.md` Current State to point to Phase 2 + Phase 3 (parallel)
