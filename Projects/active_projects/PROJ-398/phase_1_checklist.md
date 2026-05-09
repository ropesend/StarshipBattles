# Phase 1: MAJOR follow-ups

**Status:** Not Started
**Objective:** Close the 5 MAJOR findings from the PROJ-380 OpenCode review.

---

## Tasks

### Task 1.1: Read source review
**File:** `Reviews/results/2026-05-09_015904_code_proj-380-audit-shrink-cleanup-3-phases-11-verified_req-req_20260509_015902_916201/report.md`

- [ ] Read all 5 MAJOR items + agent context. Likely themes (per orchestrator's review-instruction-prompt):
  - DUP-X-07 narrowing call — were 3-4 left-click handlers consolidatable that the agent rejected?
  - DUP-X-12 narrowing call — were 4-5 ability providers consolidatable that the agent rejected at 3?
  - `Camera.hex_at_screen` semantic delta vs inline `pixel_to_hex`
  - `MissionCommandHandler` template fitness across 5 mission handlers
  - ProviderFactory base — captures behavior or just types?

### Task 1.2: Address each MAJOR per the review

- [ ] One commit per finding (or batched 2-3 if related). Apply the review's per-finding `Recommendation:` line.
- [ ] If a narrowing call (DUP-X-07 or DUP-X-12) WAS over-conservative per the review, widen the consolidation to cover the additional sites the review identified.
- [ ] If `Camera.hex_at_screen` has subtle semantic drift, fix the migration sites.

### Task 1.3: Verify
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run full sharded suite — confirm baseline preserved

---

## Phase Completion Checklist
- [ ] All 5 MAJOR items closed
- [ ] Update plan.md phase table row to `Complete`

_Source review: `Reviews/results/2026-05-09_015904_code_proj-380-audit-shrink-cleanup-3-phases-11-verified_req-req_20260509_015902_916201/`_
