# Phase 3: Audit zero-game-import test files; finalize allowlist; install hook

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-326 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started (BLOCKED on Phase 1)
**Objective:** Run the linter from Phase 1 against the existing tree, audit each flagged file, build the final allowlist, surface SUSPECT files to the user. Once the allowlist is comprehensive, install the hook.

**Required reading:**
- [`design.md`](design.md) — Phase 3 Audit section
- The Phase 1 Task 1.5 baseline output in `findings/`

**Parallelism:** Requires Phase 1 complete. Once started, parallel-safe with PROJ-324, PROJ-325 (all phases), and Phase 2 of this project.

---

## Tasks

### Task 3.1: Run linter against the tree, capture full violation list [Simple]

**Tests:** None for this audit task.

- [ ] Run `python Tools/lint_test_files.py --strict` (strict mode bypasses allowlist for full enumeration).
- [ ] Save output to `Projects/active_projects/PROJ-326/findings/zero_import_audit_baseline.txt`.
- [ ] Count violations. Compare to OpenCode 321-review's "~41 files" estimate.

**Notes:** [Filled during implementation. Record actual count.]

---

### Task 3.2: Per-file categorization audit [Complex]

**File:** [`Projects/active_projects/PROJ-326/findings/zero_import_audit.md`](Projects/active_projects/PROJ-326/findings/zero_import_audit.md) (NEW)

For each violation from Task 3.1:

- [ ] Read the file's top docstring + first 50 lines.
- [ ] Categorize into one of:
  - **A — TOOLS_TEST** (test of repo-level tooling, not game internals): allowlist
  - **B — INFRASTRUCTURE_TEST** (tests of test infrastructure itself, fixtures, conftest): allowlist
  - **C — DATA_FIXTURE** (test data / fixtures, not actual tests): allowlist
  - **D — STDLIB_OR_THIRDPARTY_ONLY** (legitimately tests stdlib/third-party only — rare): allowlist with comment
  - **E — CANDIDATE_FOR_DELETION** (zero game imports, reimplements production logic — the `test_modifier_logic.py` pattern): SUSPECT — surface to user
  - **F — REWRITE_NEEDED** (zero game imports but should test something real): SUSPECT — surface to user
- [ ] Pay particular attention to [`tests/unit/tools/test_validate_agent_surfaces.py`](tests/unit/tools/test_validate_agent_surfaces.py) (1102 LOC — explicitly flagged by OpenCode 321-review).
- [ ] Document each file with category + 1-line rationale.

**Notes:** [Filled during implementation]

---

### Task 3.3: Update allowlist with category A/B/C/D files [Simple]

**File:** [`Tools/lint_test_files_allowlist.txt`](Tools/lint_test_files_allowlist.txt)

- [ ] Add allowlist entries for every category A/B/C/D file from Task 3.2. Prefer glob patterns over individual file entries where the entire directory is allowlisted.
- [ ] Add comments explaining each glob (one-line per addition).
- [ ] Run `python Tools/lint_test_files.py` (without `--strict`). Should now exit 0 (modulo SUSPECT files in categories E/F).
- [ ] If category E/F files exist, the linter still reports them — that is intentional. They are addressed in Task 3.4.

**Notes:** [Filled during implementation]

---

### Task 3.4: Surface SUSPECT files to user [Simple]

- [ ] For each category E/F file from Task 3.2, write a 2-3 line summary in this task's Notes describing: file path, LOC, why it's SUSPECT (zero game imports + what the file appears to be doing), recommendation (delete / rewrite / allowlist with rationale).
- [ ] **Do NOT delete or rewrite unilaterally.** Surface the list to the user for triage.
- [ ] If the user approves deletion / rewrite for any, those become a follow-up ticket (or fold into PROJ-327's general cleanup).
- [ ] Add allowlist entries for any user-approved exceptions.

**Notes:** [Filled during implementation. Capture user decisions verbatim.]

---

### Task 3.5: Install pre-commit / CI hook [Simple]

After Task 3.3 + 3.4: `python Tools/lint_test_files.py` should exit 0 cleanly.

- [ ] Per `docs/guides/pre_commit_hooks.md` (created in Phase 1 Task 1.6), wire the linter into pre-commit and/or CI per the user's preference.
- [ ] Smoke test the hook: make a test file with zero game imports in a tmpdir, attempt commit, confirm hook fires.
- [ ] Verify: the existing tree commits without issue (no false positives).

**Notes:** [Filled during implementation. Record which integration(s) installed.]

---

## Phase Completion Checklist

When all tasks above are done:

- [ ] All task checkboxes above are checked
- [ ] `python Tools/lint_test_files.py` exits 0 against the current tree
- [ ] SUSPECT files surfaced to user with documented disposition
- [ ] Pre-commit and/or CI hook installed per user preference
- [ ] Sharded test suite passes: `python Tools/test_sharded/test_sharded.py`
- [ ] Update status at top of this file to `Complete`
- [ ] Update `plan.md` phase table row to `Complete`
- [ ] Update `plan.md` Current State to "All phases Complete"
- [ ] Update `plan.md` Verification section checkboxes
