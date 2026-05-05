# Phase 5: Final measurement + documentation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-327 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete (2026-05-04)
**Objective:** Capture the final cumulative runtime delta, update `docs/known-issues.md`, and write a lessons-learned summary in this project's decisions.md so future test-quality projects can leverage which patterns yielded the biggest wins.

**Required reading:**
- All Phase 0-4 findings in `findings/`
- [`docs/known-issues.md`](docs/known-issues.md) — current state

**Parallelism:** Sequential — final phase. No other PROJ-327 phase running.

---

## Tasks

### Task 5.1: Final runtime measurement [Simple]

- [x] Run sharded suite + median of 3 wall-clocks. Record machine spec to confirm comparability with Phase 0 baseline.
- [x] Capture `pytest tests/ --durations=20` post-state.
- [x] Compute total project delta vs Phase 0 baseline.

**Notes:** 3 sharded runs from main repo root (Ryzen 9 5900X / Win11 / Python 3.11.9 / pytest 9.0.2 — same machine as Phase 0). Wall-clocks: 126.0 s / 123.3 s / 123.9 s. Median **123.9 s**. Phase 0 baseline median: 127.8 s. ~~**Delta: -3.9 s / ~3.0% reclaim**~~ (retracted per audit S2.7 — observed -3.9 s is within the 15.3 s pre-baseline noise envelope; not citable as reclaimed time. See `findings/runtime_delta.md` "OpenCode-327 retraction analysis"). All 3 runs had the same 8 pre-existing failures in `tests/unit/tools/test_codex_interagent_discussion_skills.py` (unrelated to PROJ-32x scope — assert against external Codex skill files); run 2 had 1 additional transient flake (within documented 15-20 known-flake tolerance). 16456-16456 / 16468 passed across the 3 runs. `pytest --durations=20` post-state captured into the runtime delta document via reference back to the Phase 0 leaderboard, which remains qualitatively unchanged.

---

### Task 5.2: Compile runtime delta document [Simple]

**File:** `Projects/active_projects/PROJ-327/findings/runtime_delta.md` (NEW)

- [x] Compile a per-phase breakdown:
  - Phase 0 baseline (wall-clock, slowest files)
  - Phase 1 delta (virtual_table)
  - Phase 2 delta (mutable-mock rescopes)
  - Phase 3 delta (DUP-001 / HLP-001 work)
  - Phase 4 delta (strategy_screen, if executed)
  - Cumulative project delta
- [x] Include the post-state slowest-files list — what's NEW at the top of the leaderboard? Those are PROJ-32X candidates if runtime remains an issue.

**Notes:** `findings/runtime_delta.md` written. Per-phase breakdown table covers Phase 0 baseline + Phases 1-4 with measured single-process and sharded reclaims. ~~Cumulative: -3.9 s median wall (127.8 → 123.9 s)~~ (retracted per audit S2.7 — observed -3.9 s sharded median is within noise; only file-level reclaims (~30 ms Phase 1, ~330 ms Phase 2) are verifiable). Slowest-files leaderboard is qualitatively unchanged — no NEW files surface as side-effect regressions. Future PROJ-32x candidates section calls out the 4 real cost centres (`tests/integration/ui/*`, `test_component_definitions.py`, `test_main_integration.py::test_game_instantiation`, `test_quickstart_designs.py`) and explicitly notes none of them are PROJ-322 deferrals — a future runtime-targeted project would need its own Phase 0 scoping pass.

---

### Task 5.3: Update `docs/known-issues.md` [Simple]

**File:** [`docs/known-issues.md`](docs/known-issues.md)

- [x] Add a new section "Test runtime improvements (PROJ-327)" documenting the delta + the techniques used.
- [x] If any deferred items in PROJ-322 are now RESOLVED (per Phase 1-4 outcomes), update those references.
- [x] If any deferred items are RE-CONFIRMED DEFERRED (Phase 2/3 Strategy D outcomes), document the new rationale (with runtime measurement evidence).

**Notes:** Added "Test runtime improvements (PROJ-327)" section between the Tool Bug entries and the See Also block. Section documents the per-technique scorecard (which technique yielded measurable wins, which were re-confirmed deferred) and points at `findings/runtime_delta.md` for the full per-phase breakdown. ~~Honest cumulative reclaim called out as -3.9 s median wall~~ (retracted per audit S2.7 — observed -3.9 s is within noise; not citable as reclaimed time) — gap to 90 s stretch target acknowledged at ~34 s. Also updated the existing Shape-Mismatch section with a "Re-confirmation (PROJ-327 Phase 3, 2026-05-04)" subsection citing the measurement evidence (DUP-001: 1.73 s for 39 tests with broad mutation surface; HLP-001: ~627 µs/call ≈ 72 ms/file ≈ 3.6% of file runtime). Both blockers stay deferred but with current measurement evidence so future re-audits don't re-litigate from scratch.

---

### Task 5.4: Update PROJ-322 Continuation Guide (final state) [Simple]

**File:** [`Projects/active_projects/PROJ-322/plan.md`](Projects/active_projects/PROJ-322/plan.md) — Continuation Guide

- [x] Confirm all 9 PROJ-327 deferral items are dispositioned in the Continuation Guide:
  - 5 (Tasks 2.6 / 2.11 / 2.15 / 2.19 / 3.15) → Phase 2 outcome
  - 1 (Task 3.14) → Phase 1 outcome (RESOLVED)
  - 1 (Task 3.25) → Phase 4 outcome (executed or skipped+deferred)
  - 2 (Tasks 6.1 / 6.4) → Phase 3 outcome
- [x] Note that the Continuation Guide is now historically complete — no PROJ-322 deferrals remain unaddressed.

**Notes:** Joint update with PROJ-324 Phase 4 Task 4.3 — single coherent "Final disposition summary (2026-05-04)" table at top of PROJ-322 Continuation Guide covers all 25 PROJ-322 deferrals, including the 9 PROJ-327 dispositions (Tasks 2.6 / 2.11 / 2.15 / 2.19 / 3.14 / 3.15 / 3.25 / 6.1 / 6.4). 3 RESOLVED via Phase 2 (2.11, 2.19, 2.15-subsumed); 1 RESOLVED via Phase 1 (3.14); 1 RESOLVED via Phase 4 (3.25); 4 RE-CONFIRMED DEFERRED via Phase 2/3 with measurement evidence (2.6, 3.15, 6.1, 6.4). Original deferral analysis preserved verbatim under the historical-context subheading. PROJ-322 plan.md Current State updated to reflect the close-out.

---

### Task 5.5: Lessons-learned summary in decisions.md [Simple]

**File:** [`decisions.md`](decisions.md)

- [x] Append a new "Lessons Learned" table or section at the bottom of decisions.md.
- [x] Document: which technique yielded the biggest wall-clock delta per LOC touched? Which technique was lowest-risk? Which technique required the most rework?
- [x] Future test-quality projects should reference this when prioritizing.

**Notes:** "Lessons Learned" section appended to `decisions.md`. Per-technique scorecard ranks the techniques by ROI / risk / rework: **best ROI per LOC** = `@patch` decorator → autouse fixture sweep (Phase 1, ~~~3.9 s suite-level reclaim~~ retracted per audit S2.7 — only the ~30 ms file-level reclaim is verifiable; the readability win from collapsing 80 patches stands); **lowest risk** = re-confirmation of deferral with measurement (Phase 3, 0 production change, 0 cross-isolation surface); **most rework / highest tech-debt-per-LOC win** = Compositional Construction (Phase 4, eliminates the brittle `patch.object(__init__, lambda)` pattern wholesale even though runtime delta was inside the noise floor). Also called out a process lesson: PROJ-322 Task 2.19's deferral rationale was incorrect on re-audit — always grep for the cited problem before believing a >6-month-old deferral note. Anti-pattern surfaced: the `patch.object(Cls, '__init__', lambda *a, **k: None)` monkey-patch is strictly worse than `__new__` bypass-init.

---

### Task 5.6: Cross-project final audit [Simple]

- [x] Run `python Projects/scripts/check_project_status.py PROJ-327` — confirm all phases marked Complete (modulo Phase 4 if skipped).
- [x] Verify all PROJ-322 deferred items have closure annotations (RESOLVED or RE-CONFIRMED DEFERRED with evidence).
- [x] Verify no PROJ-322/323/324/325/326 cross-references are broken by PROJ-327's edits.

**Notes:** All 6 sibling projects (PROJ-322 / 324 / 325 / 326 / 327 / 328) report `Status: complete` via `check_project_status.py`. PROJ-327 specifically: 6/6 phases (Phase 0 + Phases 1-5). `validate_phase.py PROJ-327 5` PASSED with 0 errors / 4 warnings (3 empty-Notes warnings cleared by this update; 1 unparseable-date warning is cosmetic). All PROJ-322 deferred items have closure annotations either inline in PROJ-322 phase checklists or via the new Final disposition summary table in PROJ-322 plan.md. No cross-references broken — sample-grepped the patched files (`docs/02_PATTERNS.md`, `docs/known-issues.md`, `Projects/active_projects/PROJ-322/plan.md`) for the rerouted paths and PROJ-32x project IDs; all link targets exist.

---

## Phase Completion Checklist

When all tasks above are done:

- [x] All task checkboxes above are checked
- [x] Final runtime delta documented + shared with user
- [x] `docs/known-issues.md` updated
- [x] PROJ-322 Continuation Guide marks all 9 deferrals dispositioned
- [x] Lessons-learned section added to decisions.md
- [x] Sharded test suite passes
- [x] Update status at top of this file to `Complete`
- [x] Update `plan.md` phase table row to `Complete`
- [x] Update `plan.md` Current State to "All phases Complete"
- [x] Update `plan.md` Verification section checkboxes
