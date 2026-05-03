# Phase 5: Remediation — manifest, hygiene, false claims

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-319 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Resolve documentation, manifest, and __future__ import gaps surfaced by the OpenCode independent review (`req_20260503_042208_1f0252`). Self-verification of the report identified more gaps than the report itself flagged (see Notes per task). All work in this phase is project-records / hygiene; no production behavior changes.

---

## Tasks

### Task 5.1: Manifest — add 10 missing files [Simple]
**File:** `Projects/active_projects/PROJ-319/manifest.md`
**Tests:** None (project-records change)
**Audit IDs:** OpenCode H1 (under-counted)

The OpenCode review (H1) flagged 9 missing manifest entries. Self-verification against `git diff HEAD~1 HEAD --name-only` found **10 missing**. Add all 10:

- [x] Add `game/ui/widgets/column_toggle_section.py` as Production (NEW), Phase 4 / DUP-X-08 — note: hosts `build_column_toggle_section`. (OpenCode missed this one.)
- [x] Add `game/strategy/engine/handlers/base.py` as Production, Phase 4 / DUP-X-02 — note: added `_emit_validated_order(fleet, order_type, target, result, log_label)` helper.
- [x] Add `game/ui/screens/workshop_viewmodel.py` as Production, Phase 4 / DUP-X-10 — note: added `_with_ship(op_name, service_call, on_success, on_failure)` helper.
- [x] Add `game/ui/screens/planet_target_editor_base.py` as Production (NEW), Phase 4 / DUP-X-05.
- [x] Add `game/ui/screens/list_data_source_base.py` as Production (NEW), Phase 4 / DUP-X-14.
- [x] Add `game/ui/screens/data_list_window_mixin.py` as Production (NEW), Phase 4 / DUP-X-03.
- [x] Add `tests/unit/ui/screens/test_event_log_sidebar.py` as Test, Phase 4 follow-up (DUP-X-08) — patched `UILabel`/`UIButton` mocks to point at `game.ui.widgets.column_toggle_section` after the helper extraction moved the symbols.
- [x] Add `tests/unit/ui/screens/test_fleet_report_sidebar.py` as Test, Phase 4 follow-up (DUP-X-08) — same patch update.
- [x] Add `tests/unit/ui/screens/test_fleet_report_window_multi_select.py` as Test, Phase 4 follow-up (DUP-X-08) — same patch update for the `TestRemoveButtonState` fixture.
- [x] Add `tests/unit/ui/screens/test_planet_list_components.py` as Test, Phase 4 follow-up (DUP-X-07) — added patches for `game.ui.widgets.range_slider_builder.{UILabel, UIHorizontalSlider, UITextEntryLine}` after slider widgets moved.
- [x] Verify: every file in `git diff HEAD~1 HEAD --name-only | grep -E '^(game|tests)/'` is in `manifest.md`. Run the cross-check and report 0 omissions.

---

### Task 5.2: Manifest — fix inaccurate entry for `strategy_superweapons.py` [Simple]
**File:** `Projects/active_projects/PROJ-319/manifest.md`
**Tests:** None
**Audit IDs:** Self-verification finding (NOT flagged by OpenCode)

Current `manifest.md:30` reads:
> `game/ui/screens/strategy_superweapons.py | Production | Phase 4 — extract `_resolve_superweapon_target` helper from designation handlers (lines 119-310) (DUP-X-02)`

But `git diff HEAD~1 HEAD -- game/ui/screens/strategy_superweapons.py` shows **no changes** — the `_resolve_superweapon_target` extraction was deferred (decisions.md row 4 documents this). The manifest entry is a false claim.

- [x] Either remove the row entirely OR rewrite it to accurately describe the actual state: "Phase 4 — UNCHANGED. `_resolve_superweapon_target` helper extraction was DEFERRED (see decisions.md). Listed here for traceability only."
- [x] Verify: `git diff HEAD~1 HEAD -- game/ui/screens/strategy_superweapons.py` shows no actual diff.

---

### Task 5.3: Manifest — fix `_compute_circular_position` naming inconsistency [Simple]
**File:** `Projects/active_projects/PROJ-319/manifest.md`
**Tests:** None
**Audit IDs:** OpenCode M2

Current `manifest.md:53` says `_compute_circular_position` (with leading underscore, the audit's recommended name). Actual exported symbol in `game/ai/spatial_behaviors/_formation_utils.py` is `compute_circular_position` (without underscore — deliberate deviation noted in `phase_4_checklist.md` Task 4.7 but not propagated to the manifest).

- [x] Update the manifest entry to use `compute_circular_position` (no leading underscore).
- [x] Verify: `grep -n 'def compute' game/ai/spatial_behaviors/_formation_utils.py` shows `compute_circular_position` (no underscore prefix).

---

### Task 5.4: Add `from __future__ import annotations` to 6 new modules [Simple]
**File:** `game/ai/spatial_behaviors/_formation_utils.py`, `game/ui/widgets/range_slider_builder.py`, `game/ui/widgets/column_toggle_section.py`, `game/ui/screens/list_data_source_base.py`, `game/ui/screens/planet_target_editor_base.py`, `game/ui/screens/data_list_window_mixin.py`
**Tests:** `pytest tests/ --testmon` (smoke check after edits)
**Audit IDs:** OpenCode M1 (under-counted)

OpenCode said 3 files; self-verification found **6 of 7 new files** missing the import (only `race_resolver.py` has it). Per project convention (visible in 90%+ of touched files), all new modules should declare `from __future__ import annotations` at the top.

- [x] Add `from __future__ import annotations` immediately after the module docstring in `game/ai/spatial_behaviors/_formation_utils.py`.
- [x] Same for `game/ui/widgets/range_slider_builder.py`.
- [x] Same for `game/ui/widgets/column_toggle_section.py`.
- [x] Same for `game/ui/screens/list_data_source_base.py`.
- [x] Same for `game/ui/screens/planet_target_editor_base.py`.
- [x] Same for `game/ui/screens/data_list_window_mixin.py`.
- [x] Smoke-test: `python -c "import <module>"` for all 6.
- [x] Run targeted tests: `pytest tests/unit/ai/ tests/unit/ui/screens/ tests/integration/strategy/` — confirm 0 failures.

---

### Task 5.5: Decisions log — capture review verdict and Phase 5+6 scope [Simple]
**File:** `Projects/active_projects/PROJ-319/decisions.md`
**Tests:** None
**Audit IDs:** None (durability)

- [x] Add a row capturing the OpenCode review verdict: READY-TO-ARCHIVE with 0 CRITICAL / 3 HIGH / 5 MEDIUM / 5 LOW; report path; the under-counts in H1 and M1 found during self-verification.
- [x] Add a row explaining why Phase 5 and Phase 6 were added rather than amending Phase 4's checklist (decision rationale: phase boundaries should reflect when work was done, not what category it belongs to; the OpenCode review surfaced post-completion remediation work that warrants its own phase).

---

### Task 5.6: Document deferred items as out-of-scope follow-ups [Simple]
**File:** `Projects/active_projects/PROJ-319/decisions.md` and/or a new `findings/deferred_items.md`
**Tests:** None
**Audit IDs:** OpenCode H2, L1, L2, M3, M4

Surface the items the OpenCode review flagged that are intentionally NOT being addressed in PROJ-319, so a future agent has the same context:

- [x] H2 (`planet_list_window.py` 698 LOC, exceeds 500 ceiling) — pre-existing, NOT caused by PROJ-319 (was 735 before; PROJ-319 reduced by 37). Splitting would be a separate project (call it PROJ-320 candidate).
- [x] L1 (`get_shield_info` in `planet_energy_engine.py:40` is now genuinely dead — confirmed zero callers anywhere). Worthy of a tiny follow-up project, OR the next audit-shrink will pick it up. Note: would be a Phase 7 candidate if scope expands.
- [x] L2 (`_ccm_module` monkey-patching pattern in `context.py:137-138`) — pre-existing anti-pattern, out of PROJ-319 scope.
- [x] M3 (`==` vs `is` change in `PlanetTargetEditor` close-callback guard) — accept as deliberate stylistic improvement; `is` is correct for identity-on-self.
- [x] M4 (`_with_ship` placement on `WorkshopViewModel` rather than `WorkshopShipOps`) — accept as cohesive choice; moving would not change behavior.

---

## Phase Completion Checklist

When all tasks above are done:

- [x] All task checkboxes above are checked
- [x] Manifest cross-check (`git diff HEAD~1 HEAD --name-only | grep -E '^(game|tests)/'` vs manifest.md rows) shows 0 omissions
- [x] All 7 new modules have `from __future__ import annotations`
- [x] Targeted pytest still passes (no regression from Task 5.4)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 6

_Source review: `Reviews/results/2026-05-03_042208_code_proj-319-audit-shrink-cleanup-independent-review-o_req-req_20260503_042208_1f0252/report.md`. See [findings/source_audit.md](findings/source_audit.md) for the original audit-shrink source._
