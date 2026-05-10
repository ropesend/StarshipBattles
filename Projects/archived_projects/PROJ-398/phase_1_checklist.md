# Phase 1: MAJOR follow-ups

**Status:** Complete
**Objective:** Close the 5 MAJOR findings from the PROJ-380 OpenCode review.

## Closed Findings
- **FND-012** (Camera.hex_at_screen integration test): closed by `c6e0113ec`. 3 new tests in `TestCameraHexAtScreen` exercise the real `screen_to_world -> pixel_to_hex` chain (origin, zoom+offset position, viewport offset propagation).
- **FND-017** (`handle_colonize_designation` no coverage): closed by `c6e0113ec`. 4 new tests in `TestHandleColonizeDesignation` covering fleet=None, no-system-at-hex, no-colonizable-planets, and unowned-planet prompt path.
- **FND-031** (DROP_CARGO/LOAD_CARGO identical bodies): closed by `e14d7f1ce`. Extracted `_handle_dialog_mode_click(mx, my, button, dialog_method_name, *extra_args)`.
- **FND-032** (TRANSFER same skeleton): closed by `e14d7f1ce`. Same parameterized helper covers all 3 modes; widened narrowing was the recommended action.
- **FND-041** (`_star_provider` over-conservatively excluded): closed by `6744b44e1`. Scope-aware fallback moved into `StarAbilitySource.affects_hex` (now also returns True for system-shaped scopes); `_star_provider` reduced to 5-line delegation to `_iter_hex_filtered_sources`. 4 of 7 providers now share the skeleton.

---

## Tasks

### Task 1.1: Read source review
**File:** `Reviews/results/2026-05-09_015904_code_proj-380-audit-shrink-cleanup-3-phases-11-verified_req-req_20260509_015902_916201/report.md`

- [x] Read all 5 MAJOR items + agent context. Likely themes (per orchestrator's review-instruction-prompt):
  - DUP-X-07 narrowing call — were 3-4 left-click handlers consolidatable that the agent rejected?
  - DUP-X-12 narrowing call — were 4-5 ability providers consolidatable that the agent rejected at 3?
  - `Camera.hex_at_screen` semantic delta vs inline `pixel_to_hex`
  - `MissionCommandHandler` template fitness across 5 mission handlers
  - ProviderFactory base — captures behavior or just types?

### Task 1.2: Address each MAJOR per the review

- [x] One commit per finding (or batched 2-3 if related). Apply the review's per-finding `Recommendation:` line.
- [x] If a narrowing call (DUP-X-07 or DUP-X-12) WAS over-conservative per the review, widen the consolidation to cover the additional sites the review identified.
- [x] If `Camera.hex_at_screen` has subtle semantic drift, fix the migration sites.

### Task 1.3: Verify
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Run full sharded suite — confirm baseline preserved

---

## Phase Completion Checklist
- [x] All 5 MAJOR items closed
- [x] Update plan.md phase table row to `Complete`

_Source review: `Reviews/results/2026-05-09_015904_code_proj-380-audit-shrink-cleanup-3-phases-11-verified_req-req_20260509_015902_916201/`_
