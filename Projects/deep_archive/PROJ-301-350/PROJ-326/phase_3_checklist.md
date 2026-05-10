# Phase 3: Audit zero-game-import test files; finalize allowlist; install hook

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-326 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Run the linter from Phase 1 against the existing tree, audit each flagged file, build the final allowlist, surface SUSPECT files to the user. Once the allowlist is comprehensive, install the hook.

**Required reading:**
- [`design.md`](design.md) — Phase 3 Audit section
- The Phase 1 Task 1.5 baseline output in `findings/`

**Parallelism:** Requires Phase 1 complete. Once started, parallel-safe with PROJ-324, PROJ-325 (all phases), and Phase 2 of this project.

---

## Tasks

### Task 3.1: Run linter against the tree, capture full violation list [Simple]

**Tests:** None for this audit task.

- [x] Run `python Tools/lint_test_files.py --strict` (strict mode bypasses allowlist for full enumeration).
- [x] Save output to `Projects/active_projects/PROJ-326/findings/zero_import_audit_baseline.txt`.
- [x] Count violations. Compare to OpenCode 321-review's "~41 files" estimate.

**Notes:** Strict baseline: 58 files (vs OpenCode's "~41" estimate — actual is ~40% higher). Saved to ``Projects/active_projects/PROJ-326/findings/zero_import_audit_baseline.txt``. After the seeded allowlist (tools/, combat_lab/, data/, test_test_infrastructure.py) the survivor count is 32 — those 32 are the ones audited in Task 3.2.

---

### Task 3.2: Per-file categorization audit [Complex]

**File:** [`Projects/active_projects/PROJ-326/findings/zero_import_audit.md`](Projects/active_projects/PROJ-326/findings/zero_import_audit.md) (NEW)

For each violation from Task 3.1:

- [x] Read the file's top docstring + first 50 lines.
- [x] Categorize into one of:
  - **A — TOOLS_TEST** (test of repo-level tooling, not game internals): allowlist
  - **B — INFRASTRUCTURE_TEST** (tests of test infrastructure itself, fixtures, conftest): allowlist
  - **C — DATA_FIXTURE** (test data / fixtures, not actual tests): allowlist
  - **D — STDLIB_OR_THIRDPARTY_ONLY** (legitimately tests stdlib/third-party only — rare): allowlist with comment
  - **E — CANDIDATE_FOR_DELETION** (zero game imports, reimplements production logic — the `test_modifier_logic.py` pattern): SUSPECT — surface to user
  - **F — REWRITE_NEEDED** (zero game imports but should test something real): SUSPECT — surface to user
- [x] Pay particular attention to [`tests/unit/tools/test_validate_agent_surfaces.py`](tests/unit/tools/test_validate_agent_surfaces.py) (1102 LOC — explicitly flagged by OpenCode 321-review).
- [x] Document each file with category + 1-line rationale.

**Notes:** Done — full per-file table at ``Projects/active_projects/PROJ-326/findings/zero_import_audit.md``. 32 files categorized; 0 SUSPECT. Includes verification of ``tests/unit/tools/test_validate_agent_surfaces.py`` (1102 LOC, OpenCode flagged) — confirmed legitimate.

---

### Task 3.3: Update allowlist with category A/B/C/D files [Simple]

**File:** [`Tools/lint_test_files_allowlist.txt`](Tools/lint_test_files_allowlist.txt)

- [x] Add allowlist entries for every category A/B/C/D file from Task 3.2. Prefer glob patterns over individual file entries where the entire directory is allowlisted.
- [x] Add comments explaining each glob (one-line per addition).
- [x] Run `python Tools/lint_test_files.py` (without `--strict`). Should now exit 0 (modulo SUSPECT files in categories E/F).
- [x] If category E/F files exist, the linter still reports them — that is intentional. They are addressed in Task 3.4.

**Notes:** Done — full per-file table at ``Projects/active_projects/PROJ-326/findings/zero_import_audit.md``. 32 files categorized; 0 SUSPECT. Includes verification of ``tests/unit/tools/test_validate_agent_surfaces.py`` (1102 LOC, OpenCode flagged) — confirmed legitimate.

---

### Task 3.4: Surface SUSPECT files to user [Simple]

- [x] For each category E/F file from Task 3.2, write a 2-3 line summary in this task's Notes describing: file path, LOC, why it's SUSPECT (zero game imports + what the file appears to be doing), recommendation (delete / rewrite / allowlist with rationale).
- [x] **Do NOT delete or rewrite unilaterally.** Surface the list to the user for triage.
- [x] If the user approves deletion / rewrite for any, those become a follow-up ticket (or fold into PROJ-327's general cleanup).
- [x] Add allowlist entries for any user-approved exceptions.

**Notes:** Audit found **0 SUSPECT (E/F) files** — every flagged survivor is either (A) tooling test, (B) infrastructure / indirect-conftest test, (C) shared fixture/factory, or (D) stdlib-only validation. No ``test_modifier_logic.py``-pattern candidates surfaced. Nothing for the user to triage.

---

### Task 3.5: Install pre-commit / CI hook [Simple]

After Task 3.3 + 3.4: `python Tools/lint_test_files.py` should exit 0 cleanly.

- [x] Per `docs/guides/pre_commit_hooks.md` (created in Phase 1 Task 1.6), wire the linter into pre-commit and/or CI per the user's preference.
- [x] Smoke test the hook: make a test file with zero game imports in a tmpdir, attempt commit, confirm hook fires.
- [x] Verify: the existing tree commits without issue (no false positives).

**Notes:** **Both integrations installed.**

- **CI:** Added a ``Lint test files (zero-game-import detector)`` step to ``.github/workflows/agent_coordination.yml`` after the existing ``Full validator`` step. Also extended the workflow's ``paths`` trigger to include ``Tools/lint_test_files.py``, ``Tools/lint_test_files_allowlist.txt``, and ``tests/**/*.py`` so CI re-runs whenever a test file is added.
- **Local pre-commit:** Installed ``.git/hooks/pre-commit`` per the bash recipe in ``docs/guides/pre_commit_hooks.md`` (skips on merge / rebase / cherry-pick). Verified: hook exits 0 against the current tree, exits 1 with the file path when a synthetic zero-game-import test is staged in a tmp tree (verified the linter --root + --allowlist flags work for arbitrary trees, including outside PROJECT_ROOT — added a relative_to fallback for that case).

Note: ``.git/hooks/pre-commit`` is per-checkout (each developer installs it from the documented recipe); CI is the centralized backstop.

---

## Phase Completion Checklist

When all tasks above are done:

- [x] All task checkboxes above are checked
- [x] `python Tools/lint_test_files.py` exits 0 against the current tree
- [x] SUSPECT files surfaced to user with documented disposition
- [x] Pre-commit and/or CI hook installed per user preference
- [~] Sharded test suite passes: `python Tools/test_sharded/test_sharded.py` — not run from this worktree per agent-instruction (known `\a` escape bug in worktree paths). Targeted suites passed: `pytest tests/unit/tools/test_lint_test_files.py tests/unit/strategy/facade/test_strategy_session_facade_contract.py tests/integration/ui/test_system_tree_panel_smoke.py tests/unit/data/test_test_infrastructure.py` (27 new + pre-existing tests, 3 unrelated pre-existing failures in TestUtilityScriptNaming/TestFormationScriptNaming about file-rename targets that don't exist in this branch).
- [x] Update status at top of this file to `Complete`
- [x] Update `plan.md` phase table row to `Complete`
- [x] Update `plan.md` Current State to "All phases Complete"
- [x] Update `plan.md` Verification section checkboxes
