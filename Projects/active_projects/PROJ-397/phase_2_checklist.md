# Phase 2: MAJOR — 6 follow-up findings

**Status:** Complete
**Objective:** Close the 6 MAJOR findings from the PROJ-393 review.

---

## Tasks

### Task 2.1: Read source review
**File:** `Reviews/results/2026-05-09_002247_code_proj-393-test-injection-legacy-fallbacks-comment-c_req-req_20260509_002246_bca19e/report.md` (MAJOR section)

- [x] Read all 6 MAJOR items. Likely themes: Phase 2 test-side audit gaps; partial Task 3.2 (`fleet_id` tag-only removal — production confusion); audit-correction policy shortfalls.

### Task 2.2: Address each finding

- [x] One commit per finding (or batched 2-3 if related). Apply the review's per-finding `Recommendation:`. Closed in commit `6b8ee8c8f` (F-02 / F-03 / F-04 / F-05 / F-06 / F-07).

**PROJ-406 reconciliation Note on F-05:** F-05 originally asked for a real-constructor `TypeError` test on `EmpireBuildQueueWindow`. The implementation shipped an introspection-only signature test (`test_constructor_requires_facade`) which closes the core signature risk but does not literally exercise the constructor as the review recommended. The literal "instantiate-and-catch-TypeError" test is **deferred to PROJ-408 C-01** (Wave 4) per the implementation review.

### Task 2.3: Verify
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Full sharded suite passes

---

## Phase Completion Checklist
- [x] All 6 MAJOR items closed
- [x] Update plan.md phase table row to `Complete`

_Source review: `Reviews/results/2026-05-09_002247_code_proj-393-test-injection-legacy-fallbacks-comment-c_req-req_20260509_002246_bca19e/`_
