# Phase 4: Documentation pass — promote `make_ui_widget` + close blockers

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-324 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Lock in the test-infra gains by documenting the `make_ui_widget` factory + `bypass_init` pattern in `docs/02_PATTERNS.md`, marking the UIWindow + LLM blockers resolved in `docs/known-issues.md`, and updating PROJ-322's Continuation Guide.

**Required reading:**
- [`docs/02_PATTERNS.md`](docs/02_PATTERNS.md) — see existing pattern entries to match style
- [`docs/known-issues.md`](docs/known-issues.md) — current blocker entries
- [`Projects/active_projects/PROJ-322/plan.md`](Projects/active_projects/PROJ-322/plan.md) — Continuation Guide section

**Parallelism:** This phase is documentation-only and does not touch any test or production file. Safe to run in parallel with anything (PROJ-325, PROJ-326).

---

## Tasks

### Task 4.1: Add Pattern 15b "UI Widget Test Factory" to `docs/02_PATTERNS.md` [Simple]

**File:** [`docs/02_PATTERNS.md`](docs/02_PATTERNS.md)

- [ ] Locate the existing Pattern 15 entry (Factory pattern). Add a 15b sub-entry titled "UI Widget Test Factory (PROJ-322 / PROJ-324)".
- [ ] Use the suggested content from [`design.md`](design.md) "Patterns to Promote" section as the template.
- [ ] Cross-reference: `tests/fixtures/ui_widget_factory.py`, `tests/fixtures/test_ui_widget_factory.py`, and the `bypass_init` context manager.
- [ ] Verify: `docs/02_PATTERNS.md` parses cleanly (no markdown formatting errors). Open the docs README index — does the new entry need a pointer there?

**Notes:** [Filled during implementation]

---

### Task 4.2: Mark blockers resolved in `docs/known-issues.md` [Simple]

**File:** [`docs/known-issues.md`](docs/known-issues.md)

- [ ] Update the "UIWindow super-init chain blocker" section header to "**[RESOLVED in PROJ-324]** UIWindow super-init chain blocker (historical)". Preserve the original content for historical context.
- [ ] Add a "Resolution" subsection at the end of the entry pointing at PROJ-324 commit SHA(s) and the `bypass_init` pattern.
- [ ] Same treatment for "LLMBackgroundCall real-thread polling blocker" — mark `**[RESOLVED in PROJ-324]**` and add resolution pointer.
- [ ] Leave the Shape-Mismatch and Tool Bug sections unchanged (those are PROJ-327 owners, not yet resolved).

**Notes:** [Filled during implementation]

---

### Task 4.3: Update PROJ-322 Continuation Guide [Simple]

**File:** [`Projects/active_projects/PROJ-322/plan.md`](Projects/active_projects/PROJ-322/plan.md) — Continuation Guide section

- [ ] Update the Continuation Guide to reflect: 14 deferrals closed by PROJ-324; remaining items queued to PROJ-325 (RaceSetupScreen if NO-GO + Tasks 3.34/3.37) and PROJ-327 (Tasks 3.14, 3.25, 6.1, 6.4, 2.6, 2.11, 2.15, 2.19, 3.15).
- [ ] Add a new line at the top of the Current State noting the project is "Continuation in progress: PROJ-324, PROJ-325, PROJ-326, PROJ-327".
- [ ] Do NOT remove the original deferral analysis — it's a useful audit trail.

**Notes:** [Filled during implementation]

---

### Task 4.4: Final cross-project audit [Simple]

- [ ] Run `python Projects/scripts/check_project_status.py PROJ-324` — confirm all phases marked Complete.
- [ ] Run `python Projects/scripts/check_project_status.py PROJ-322` — verify the Continuation Guide update is reflected.
- [ ] Verify `docs/known-issues.md` no longer lists UIWindow / LLM as active blockers.
- [ ] Verify `docs/02_PATTERNS.md` lists the factory pattern with a working cross-reference.
- [ ] Run the full sharded test suite one more time: `python Tools/test_sharded/test_sharded.py`.

**Notes:** [Filled during implementation. Note any cross-project discrepancies for follow-up.]

---

## Phase Completion Checklist

When all tasks above are done:

- [ ] All task checkboxes above are checked
- [ ] Sharded test suite passes
- [ ] `docs/known-issues.md` updated; `docs/02_PATTERNS.md` updated
- [ ] PROJ-322 Continuation Guide updated
- [ ] Update status at top of this file to `Complete`
- [ ] Update `plan.md` phase table row to `Complete`
- [ ] Update `plan.md` Current State to "All phases Complete"
- [ ] Update `plan.md` Verification section checkboxes
