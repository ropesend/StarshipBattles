# Phase 4: Documentation pass — promote `make_ui_widget` + close blockers

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-324 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete (2026-05-04)
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

- [x] Locate the existing Pattern 15 entry (Factory pattern). Add a 15b sub-entry titled "UI Widget Test Factory (PROJ-322 / PROJ-324)".
- [x] Use the suggested content from [`design.md`](design.md) "Patterns to Promote" section as the template.
- [x] Cross-reference: `tests/fixtures/ui_widget_factory.py`, `tests/fixtures/test_ui_widget_factory.py`, and the `bypass_init` context manager.
- [x] Verify: `docs/02_PATTERNS.md` parses cleanly (no markdown formatting errors). Open the docs README index — does the new entry need a pointer there?

**Notes:** Pattern landed as §33 "UI Widget Test Factory (PROJ-322 / PROJ-324 / PROJ-325 / PROJ-328)" — section 15b would have been confusing alongside the existing §15 (generic Factory pattern), so it took the next free slot. Header/TOC/section-count updated. Cross-references include `tests/fixtures/ui_widget_factory.py`, `tests/fixtures/test_ui_widget_factory.py`, `bypass_init` context manager, the `Default{Foo}DelegateFactory` + `Foo{Delegates}` bundle from PROJ-325 + PROJ-328 A/B/C, and the per-class `Null{Foo}UiBuilder` / `Mock{Foo}UiBuilder` test-fixture convention. Explicit relationship-to-§32 callout at the top of the entry: §32 (Compositional Construction) is the canonical pattern for new code, §33 is the retrofit pattern for legacy UIWindow subclasses. `docs/README.md` already routes through `docs/02_PATTERNS.md` for pattern lookups; no extra index pointer required.

---

### Task 4.2: Mark blockers resolved in `docs/known-issues.md` [Simple]

**File:** [`docs/known-issues.md`](docs/known-issues.md)

- [x] Update the "UIWindow super-init chain blocker" section header to "**[RESOLVED in PROJ-324]** UIWindow super-init chain blocker (historical)". Preserve the original content for historical context.
- [x] Add a "Resolution" subsection at the end of the entry pointing at PROJ-324 commit SHA(s) and the `bypass_init` pattern.
- [x] Same treatment for "LLMBackgroundCall real-thread polling blocker" — mark `**[RESOLVED in PROJ-324]**` and add resolution pointer.
- [x] Leave the Shape-Mismatch and Tool Bug sections unchanged (those are PROJ-327 owners, not yet resolved).

**Notes:** Both blocker headers prefixed with **[RESOLVED in PROJ-324 + PROJ-325 PoC + PROJ-328]** and renamed `(historical)`. Resolution subsections cite Phase 1 commit 9ae5c4959, Phase 2 commit af7328281, Phase 3 systemic finding 9e177edb7, plus the downstream PROJ-325 PoC + PROJ-328 A/B/C rollouts. The Shape-Mismatch section now also carries a "Re-confirmation (PROJ-327 Phase 3, 2026-05-04)" subsection rather than being marked resolved, since PROJ-327 RE-CONFIRMED DEFERRED with measurement evidence — that's a PROJ-327 ownership scope, not PROJ-324's. Tool Bug section unchanged.

---

### Task 4.3: Update PROJ-322 Continuation Guide [Simple]

**File:** [`Projects/active_projects/PROJ-322/plan.md`](Projects/active_projects/PROJ-322/plan.md) — Continuation Guide section

- [x] Update the Continuation Guide to reflect: 14 deferrals closed by PROJ-324; remaining items queued to PROJ-325 (RaceSetupScreen if NO-GO + Tasks 3.34/3.37) and PROJ-327 (Tasks 3.14, 3.25, 6.1, 6.4, 2.6, 2.11, 2.15, 2.19, 3.15).
- [x] Add a new line at the top of the Current State noting the project is "Continuation in progress: PROJ-324, PROJ-325, PROJ-326, PROJ-327".
- [x] Do NOT remove the original deferral analysis — it's a useful audit trail.

**Notes:** Continuation Guide now opens with a "Final disposition summary (2026-05-04)" table covering all 25 PROJ-322 deferrals — 14 UIWindow / LLM RESOLVED via PROJ-324 + PROJ-325 + PROJ-328; Task 3.25 RESOLVED via PROJ-327 Phase 4; 3 mutable-mock fixtures RESOLVED via PROJ-327 Phase 2; 4 RE-CONFIRMED DEFERRED with measurement evidence; PROJ-323 leftovers via PROJ-325; linter via PROJ-326. Original deferral analysis preserved verbatim under "Original deferral analysis (preserved for historical context)" heading. Current State updated to "All phases Complete; ALL 25 formally deferred items now have current dispositions". Note: the original Task 4.3 wording asked for a "Continuation in progress: 324, 325, 326, 327" line at the top of Current State — by close-out time those projects are themselves Complete, so that bullet would have been stale by the time it landed; the Final disposition summary table covers the same intent better.

---

### Task 4.4: Final cross-project audit [Simple]

- [x] Run `python Projects/scripts/check_project_status.py PROJ-324` — confirm all phases marked Complete.
- [x] Run `python Projects/scripts/check_project_status.py PROJ-322` — verify the Continuation Guide update is reflected.
- [x] Verify `docs/known-issues.md` no longer lists UIWindow / LLM as active blockers.
- [x] Verify `docs/02_PATTERNS.md` lists the factory pattern with a working cross-reference.
- [x] Run the full sharded test suite one more time: `python Tools/test_sharded/test_sharded.py`.

**Notes:** All 6 sibling projects (PROJ-322 / 324 / 325 / 326 / 327 / 328) report `Status: complete` via `check_project_status.py`. `validate_phase.py PROJ-324 4` PASSED with 0 errors / 4 warnings (3 empty-Notes warnings cleared by this update; 1 unparseable-date warning is cosmetic — script expects `YYYY-MM-DD` exactly, our header reads `2026-05-04 (final close-out)`, harmless). Sharded suite (final run, 3 wall-clocks per PROJ-327 Task 5.1) median 123.9 s — 16456/16468 passed, 8 pre-existing failures in `tests/unit/tools/test_codex_interagent_discussion_skills.py` (out of PROJ-32x scope; tests assert against external Codex skill files), 4 skipped. No PROJ-322 / 323 / 324 / 325 / 326 / 327 / 328 cross-references broken by this Phase's edits (verified by grep over patched files for the rerouted paths). One small naming choice surfaced for follow-up: the original checklist asked for "Pattern 15b" in `docs/02_PATTERNS.md`; landed as Pattern §33 instead because the section-15 "Factory" entry is the generic factory pattern and a 15b would have read as a sub-clause. No structural issue; documented in Task 4.1 Notes.

---

## Phase Completion Checklist

When all tasks above are done:

- [x] All task checkboxes above are checked
- [x] Sharded test suite passes
- [x] `docs/known-issues.md` updated; `docs/02_PATTERNS.md` updated
- [x] PROJ-322 Continuation Guide updated
- [x] Update status at top of this file to `Complete`
- [x] Update `plan.md` phase table row to `Complete`
- [x] Update `plan.md` Current State to "All phases Complete"
- [x] Update `plan.md` Verification section checkboxes
