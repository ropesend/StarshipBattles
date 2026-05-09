# Phase 2: MAJOR — 9 follow-up findings

**Status:** Complete
**Objective:** Close the 9 MAJOR findings from the PROJ-382 review.

---

## Tasks

### Task 2.1: Read source review
**File:** `Reviews/results/2026-05-08_235750_code_proj-382-pattern-conformance-facade-integrity-even_req-req_20260508_235748_8c0ea0/report.md` (MAJOR section)

- [x] Read all 9 MAJOR findings + agent context. Major themes:
  - `BuildQueuePortraitLoader` `portrait_session=` kwarg may be a re-introduced shim under a new name (Pattern #36 watch)
  - Phase 5 file-split fitness (genuine decomposition vs cosmetic line moves)
  - PROJ-381 cross-impact double-check on `game_session.py`
  - `_session` writable property setter creates a hole — verify static-guard catches it (after Phase 1)
  - Pattern #36 'when not to use' may be too weak

### Task 2.2: Address each MAJOR per the review

- [x] Each finding ships its own fix. Consult the review's per-finding `Recommendation:` line. Typical patterns: rename a kwarg to a narrower type; tighten a Pattern #36 doc constraint; verify a Phase 5 split is semantic, not cosmetic.

### Task 2.3: Final regression
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Run full sharded suite — confirm baseline preserved

---

## Phase Completion Checklist
- [x] All 9 MAJOR items closed
- [x] Update plan.md phase table row to `Complete`

_Source review: `Reviews/results/2026-05-08_235750_code_proj-382-pattern-conformance-facade-integrity-even_req-req_20260508_235748_8c0ea0/`_
