# Phase 2: MAJOR — 6 follow-up findings

**Status:** Not Started
**Objective:** Close the 6 MAJOR findings from the PROJ-393 review.

---

## Tasks

### Task 2.1: Read source review
**File:** `Reviews/results/2026-05-09_002247_code_proj-393-test-injection-legacy-fallbacks-comment-c_req-req_20260509_002246_bca19e/report.md` (MAJOR section)

- [ ] Read all 6 MAJOR items. Likely themes: Phase 2 test-side audit gaps; partial Task 3.2 (`fleet_id` tag-only removal — production confusion); audit-correction policy shortfalls.

### Task 2.2: Address each finding

- [ ] One commit per finding (or batched 2-3 if related). Apply the review's per-finding `Recommendation:`.

### Task 2.3: Verify
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Full sharded suite passes

---

## Phase Completion Checklist
- [ ] All 6 MAJOR items closed
- [ ] Update plan.md phase table row to `Complete`

_Source review: `Reviews/results/2026-05-09_002247_code_proj-393-test-injection-legacy-fallbacks-comment-c_req-req_20260509_002246_bca19e/`_
