# PROJ-316: PROJ-313 Remediation — Audit-Readiness and Structural Tightening

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-316` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-316 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Paperwork sweep — checklists + docs | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Tighten `window_manager` to required on strategy-screen-only windows | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Replace Phase 7 click-blocking regression test | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Final verification + audit script green | Complete | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-04-28
**Active Phase:** All 4 phases complete — ready for user verification.
**Last Action:** Closed PROJ-313 audit-readiness gaps, corrected Pattern #31 and UI style-guide guidance, tightened strategy-screen modal constructor signatures, replaced the Phase 7 editor regression test, ran mutation checks, and completed final verification.
**Next Action:** User review/smoke verification of PROJ-313/316 remediation.
**Blockers:** None
**Test baseline:** Kickoff full shard was clean: 15998 passed, 0 failed, 0 errors. Final full shard is clean: 16008 passed, 0 failed, 0 errors.

## Overview
PROJ-313 ("Strategy Modal Window Base Class Refactor") merged on
2026-04-28 with all 8 phases marked Complete in `plan.md`. An
independent reviewer audit identified five legitimate gaps between the
project's stated state and the actual code/docs. PROJ-316 is the
focused follow-up to close those gaps without re-litigating the
underlying architecture.

The five audit findings (full detail in [findings/proj_313_audit_findings.md](findings/proj_313_audit_findings.md)):

1. **Audit-readiness gap.** `plan.md` says all 8 phases complete; the 8 phase checklist files still say "Status: Not Started" with unchecked tasks; `python Projects/scripts/validate_audit_ready.py PROJ-313` exits FAILED with 16 errors.
2. **Phase 8 demolition not executed.** `_handle_window_close`, the 16 slot fields on `StrategyWindowManager`, and `TestModalSlotCleanupContract` are all still present. This was a knowing scope deviation documented in plan.md, but the deviation was not propagated into the docs (Pattern #31 still claims "Both methods are one-liners" and "Replaces the source-string-matching test"), and the deferred tasks are not flagged as such on the checklists.
3. **Phase 7 regression test does not exercise the editor classes.** `tests/integration/ui/test_editor_click_blocking.py` parametrises by class-name string only and uses `MagicMock`. It would still pass if `FoodAllocationEditor` (etc.) stopped subclassing `StrategyModalWindow` or if a spawn site omitted `window_manager=`. This is a real regression-coverage gap.
4. **Bypass risk via `window_manager=None` default.** At audit time, the base class and 13 strategy-screen-only constructors defaulted to `None`. A future strategy-screen call site could omit the keyword and silently break the structural guarantee.
5. **Pattern #31 doc accuracy.** Claims "21 adopters" (actually 20), "Both methods are one-liners" (`has_modal_open` retains menu_panel + build_queue_screen checks), and "Replaces the source-string cleanup test" (the test still exists).

## Goals
- Make `Projects/active_projects/PROJ-313/` audit-ready —
  `validate_audit_ready.py PROJ-313` exits 0.
- Fix the documentation inaccuracies in Pattern #31 to match actual
  code state.
- Restore the structural guarantee that forgotten `window_manager=` at
  a strategy-screen call site is impossible (compile-time/construct-time
  failure) for the strategy-only windows that should never be opened off-strategy.
- Replace the Phase 7 click-blocking test with one that actually
  imports and exercises the 5 migrated editor classes, plus a
  spawn-site assertion test.

## Scope

**In scope:**
- All 5 audit findings.
- Doc updates (`docs/02_PATTERNS.md`, `docs/06_UI_STYLE_GUIDE.md`).
- Test rewrites (`tests/integration/ui/test_editor_click_blocking.py`).
- Constructor-signature changes on strategy-only windows.
- PROJ-313 phase checklist updates and audit-script remediation.

**Out of scope (explicitly):**
- Full Phase 8 demolition of `_handle_window_close` + slot fields. The
  PROJ-313 scope deviation is accepted; this project codifies the
  deviation rather than reversing it. If full demolition is desired,
  file a separate follow-up project.
- The 8 failing tests in `tests/unit/strategy/test_ship_instance_damage.py`
  — those are PROJ-315 in-progress.
- The `_pending_confirmation_dialog` asymmetry — pre-existing latent
  bug, was explicitly out of scope for PROJ-313 too.

## Key Files
| Component | File Path | Notes |
|-----------|-----------|-------|
| Audit findings | [findings/proj_313_audit_findings.md](findings/proj_313_audit_findings.md) | Source of all remediation items |
| PROJ-313 plan | `Projects/active_projects/PROJ-313/plan.md` | Goals section to mark deferred items; Quick Status to keep |
| PROJ-313 phase checklists | `Projects/active_projects/PROJ-313/phase_1_checklist.md` … `phase_8_checklist.md` | Update statuses; mark Phase 8 deferred tasks |
| Strategy modal base class | `game/ui/screens/strategy_modal_window.py` | Already required `window_manager`; docstring corrected for retained slot-cleanup tests |
| Strategy-only migrated windows | `game/ui/screens/{planet_list,star_list,build_queue_list,empire_build_queue,event_log,empire_panel,fleet_report,planet_abilities}_window.py`, `game/ui/screens/strategy_windows/move_choice_dialog.py`, `game/ui/screens/{food_allocation,atmosphere_target,gravity_target,water_target,radiation_shield}_editor.py` | Remove `= None` default from `window_manager` parameter where defined; `MoveChoiceWindow` inherits required base signature |
| Spawn sites | `game/ui/screens/strategy_event_router.py`, `game/ui/screens/strategy_windows/*.py` | Verify already pass `window_manager=` (they do per PROJ-313); add explicit assertion tests |
| Phase 7 regression test | `tests/integration/ui/test_editor_click_blocking.py` | Rewrite to import editor classes + assert subclassing + assert spawn site passes `window_manager=` |
| Pattern doc | `docs/02_PATTERNS.md` | Pattern #31: adopter count, "one-liner" claim, contract-test claim. Pattern #30 status note clarification |
| UI style guide | `docs/06_UI_STYLE_GUIDE.md` | Window Management section: example signature should show `window_manager` required (after Phase 2) |

## Related Documents
- [design.md](design.md) — Per-item design rationale and trade-offs
- [decisions.md](decisions.md) — Decisions log
- [manifest.md](manifest.md) — Per-file change inventory
- [findings/proj_313_audit_findings.md](findings/proj_313_audit_findings.md) — Source audit + verification

## Verification

### Project Start
- [x] Run `python Tools/test_sharded/test_sharded.py` — kickoff baseline: 15998 passed, 0 failed, 0 errors
- [x] Run `python Projects/scripts/validate_audit_ready.py PROJ-313` — initial failure recorded: 16 errors

### After Each Phase
- [x] Run `pytest tests/unit/ui/screens/ tests/integration/ui/` (incremental)
- [x] Targeted regression for changed windows

### Final Verification
- [x] `python Projects/scripts/validate_audit_ready.py PROJ-313` exits 0
- [x] `python Tools/test_sharded/test_sharded.py` — final: 16008 passed, 0 failed, 0 errors
- [x] Strategy-only windows reject omitted `window_manager=` by signature guard
- [x] Phase 7 regression test fails if you (a) un-subclass FoodAllocationEditor from StrategyModalWindow, (b) omit `window_manager=` at any of the 5 editor spawn sites, (c) remove `register_modal` from base class — verified by manual mutation test

## Phase Breakdown

### Phase 1 — Paperwork sweep
**Objective:** make PROJ-313 audit-ready and bring docs into agreement
with code. No production code changes in this phase.

#### Task 1.1 — Update PROJ-313 phase checklists to reflect actual state
**File:** `Projects/active_projects/PROJ-313/phase_1_checklist.md` … `phase_8_checklist.md`
- [x] For each of phases 1–7: change `**Status:** Not Started` → `**Status:** Complete`. Walk the task list and check off the boxes that were done.
- [x] For Phase 8: record demolition items as explicit `Deferred:` checklist entries and add a "Scope Deviation" section pointing to plan.md Current State.

#### Task 1.2 — Update PROJ-313 plan.md goals section
**File:** `Projects/active_projects/PROJ-313/plan.md`
- [x] In the Goals section, mark the goals that were downscoped with `[deferred — see Current State scope deviation]`. Specifically: "Delete `_handle_window_close`" and "Replace the false-negative-prone `TestModalSlotCleanupContract` test".

#### Task 1.3 — Fix Pattern #31 doc accuracy
**File:** `docs/02_PATTERNS.md`
- [x] Adopter count: "21 windows" → "20 windows" (count the listed names: 20).
- [x] "Both methods are one-liners" → "Both methods walk `iter_live_modals()` for modal-tracking; `has_modal_open()` additionally checks `menu_panel` and `build_queue_screen` (pre-modal-tracking concerns retained from before PROJ-313)."
- [x] "Replaces the source-string-matching test" → "Augments the legacy `TestModalSlotCleanupContract` (kept as a regression for the slot-cleanup pathway that still operates for caller-convenience pointers; see Migration notes). The new structural invariant test is at `tests/unit/ui/screens/test_strategy_modal_window.py`."
- [x] Bump `Last verified:` blockquote.

#### Task 1.4 — Pattern #30 SUPERSEDED banner clarification
**File:** `docs/02_PATTERNS.md`
- [x] Confirm Pattern #30's SUPERSEDED banner accurately states: the registrar `on_close_callback` mechanism remains active for slot-cleanup of caller-convenience pointers; what was superseded is the use of these slots as the *modal-tracking contract* (now done structurally via Pattern #31).

#### Task 1.5 — Re-run audit script until green
**Command:** `python Projects/scripts/validate_audit_ready.py PROJ-313`
- [x] Run the script. Capture errors.
- [x] Address each error (most should be resolved by Task 1.1). Iterate.
- [x] Acceptance: exit code 0.

**Tests:** `python Projects/scripts/validate_audit_ready.py PROJ-313` exits 0; `pytest tests/` no regression.

---

### Phase 2 — Tighten `window_manager` to required on strategy-screen-only windows
**Objective:** Restore the structural guarantee — make forgotten
registration impossible at strategy-screen spawn sites by removing the
`= None` default on strategy-screen-only windows that are opened from the
strategy screen.

#### Task 2.1 — Inventory call sites
**Goal:** confirm each candidate window's call sites before tightening
strategy-screen contexts (`game/ui/screens/strategy_event_router.py`,
`game/ui/screens/strategy_windows/*.py`, or `strategy_screen.py`).
- [x] For each of the 14 candidate windows, grep the codebase for `<ClassName>(` constructor calls (excluding test files and the class definition itself).
- [x] Categorise: STRATEGY-ONLY (safe to require `window_manager=`) vs DUAL-CALLER (must pass explicit `None` from non-strategy callers). Per PROJ-313 implementation, only `PlanetSelectionWindow` is dual-caller (also opened from `BuildQueueScreen`).
- [x] Document the inventory in `decisions.md`.

#### Task 2.2 — Tighten the base class signature
**File:** `game/ui/screens/strategy_modal_window.py`
- [x] Change `window_manager: "StrategyWindowManager | None" = None` → `window_manager: "StrategyWindowManager | None"` (keyword-only, no default). The type stays `Optional` so `PlanetSelectionWindow` can still pass `None` from `BuildQueueScreen`.
- [x] Update the docstring to say "Pass `None` only when the window is being opened outside the strategy screen".
- [x] Run `pytest tests/unit/ui/screens/test_strategy_modal_window.py` — should still pass (tests pass `window_manager=` explicitly).

#### Task 2.3 — Tighten each strategy-screen-only window
**Files:** the strategy-only window class files listed in Key Files.
- [x] For each, remove the `= None` default from `window_manager` parameter. Keep the type `"StrategyWindowManager | None"` or change to `"StrategyWindowManager"` (decide per-window based on whether `None` is ever a sensible value; for strategy-screen-only the answer is no, so use `"StrategyWindowManager"`).
- [x] Verify the spawn site already passes `window_manager=` (per PROJ-313 it does). If not, fix.
- [x] Run `pytest tests/unit/ui/screens/` — find tests that constructed the window without `window_manager=`, add `window_manager=None` (acceptable in test contexts) or a real fixture.

#### Task 2.4 — Update `docs/06_UI_STYLE_GUIDE.md` Window Management section
**File:** `docs/06_UI_STYLE_GUIDE.md`
- [x] Update the example code template to show `window_manager: "StrategyWindowManager"` (required) for strategy-screen-only adopters. Add a separate "Cross-screen reuse" subsection covering the `Optional[...]` + explicit `None` pattern for windows like `PlanetSelectionWindow`.
- [x] Bump `Last verified:` blockquote.

#### Task 2.5 — Verification
- [x] Confirm each strategy-only window has no `window_manager` default and would reject omitted `window_manager=`.
- [x] `pytest tests/unit/ui/ tests/integration/ui/` clean.

**Tests:** `pytest tests/unit/ui/ tests/integration/ui/` no regression.

---

### Phase 3 — Replace Phase 7 click-blocking regression test
**Objective:** the regression test must fail if any of the migration
steps are undone — subclass changed, spawn-site omits
`window_manager`, or base class skips registration.

#### Task 3.1 — Add structural-subclass test
**File:** `tests/integration/ui/test_editor_click_blocking.py`
- [x] At the top, import the 5 editor classes:
      `FoodAllocationEditor`, `AtmosphereTargetEditor`,
      `GravityTargetEditor`, `WaterTargetEditor`,
      `RadiationShieldEditor`.
- [x] Add a parametrised test over the imported class objects (not strings) that asserts `issubclass(cls, StrategyModalWindow)`. Failure mode: a future commit removing the subclass relationship causes a hard test failure.

#### Task 3.2 — Add registration-on-construct test
**File:** same.
- [x] For each editor, use the existing `__new__` + patched-`pygame_gui.elements.UIWindow.__init__` pattern (mirror `tests/unit/ui/screens/test_strategy_modal_window.py`'s `_make_modal_window` helper) to construct the editor with a stub `StrategyWindowManager`-shaped object.
- [x] Assert the constructed instance appears in the manager's modal list immediately after construction.
- [x] Construct each editor's `kill()` and assert it deregisters.

#### Task 3.3 — Add spawn-site assertion test
**File:** same (or split into a new file `test_editor_spawn_sites.py` if cleaner).
- [x] For each `StrategyEventRouter._open_*_editor()` method (5 methods):
      patch the editor class via `unittest.mock.patch`, call the spawn
      method, assert `mock_editor.call_args.kwargs["window_manager"]` is
      `ui.window_manager` and is not None.
- [x] Also assert it's NOT default-constructed without the keyword.

#### Task 3.4 — Rename or remove the existing click-blocking integration test
**File:** same.
- [x] The current test exercises the router OR-bridge with a mocked editor in `iter_live_modals` — this is still useful as router-level coverage. Either:
      a) Keep it under a clearer name like `test_router_blocks_clicks_inside_any_modal_in_iter_live_modals`, OR
      b) Delete it entirely now that the structural tests above provide stronger coverage.
- [x] Decide and update.

#### Task 3.5 — Manual mutation test (verification)
- [x] Temporarily un-subclass `FoodAllocationEditor` from `StrategyModalWindow` (change to `pygame_gui.elements.UIWindow`). Run the new tests. Confirm Task 3.1's test fails.
- [x] Temporarily comment out `window_manager=ui.window_manager` in `_open_food_allocation_editor`. Run tests. Confirm Task 3.3's test fails.
- [x] Temporarily comment out `window_manager.register_modal(self)` in `StrategyModalWindow.__init__`. Run tests. Confirm Task 3.2's test fails.
- [x] Revert all temporary changes. Confirm tests pass again.

**Tests:** new tests in `tests/integration/ui/test_editor_click_blocking.py` (or split file).

---

### Phase 4 — Final verification + audit-script green
**Objective:** confirm the remediation closed all 5 findings and the
project is genuinely audit-ready.

#### Task 4.1 — PROJ-313 audit script green
- [x] `python Projects/scripts/validate_audit_ready.py PROJ-313` exits 0.

#### Task 4.2 — Full sharded test suite
- [x] `python Tools/test_sharded/test_sharded.py` — record pass/fail count.
- [x] Failures should be limited to the 8 PROJ-315 `test_ship_instance_damage.py` cases recorded at PROJ-316 kick-off (or 0 if PROJ-315 is fixed by then). Anything else is a regression.

#### Task 4.3 — Doc cross-reference walk
- [x] Re-read `docs/02_PATTERNS.md` Pattern #31. Cross-reference every claim against the live code (count adopters, look at `has_modal_open` shape, confirm the new structural test exists, confirm the legacy test still exists). All claims must be accurate.
- [x] Re-read `docs/06_UI_STYLE_GUIDE.md` Window Management section. The example must reflect Phase 2 changes.

#### Task 4.4 — Update PROJ-316 plan.md and close out
- [x] Mark all 4 PROJ-316 phases Complete in the Quick Status table.
- [x] Update Current State.
- [x] Update `Tracking/active_projects` index if present (or `Projects/projects_index.md`).
- [x] Hand off to user for verification.

**Tests:** None new; verification is sweep + audit-script + manual.

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 0 | 2026-04-28 | Initial audit (reviewer) — 5 findings: P1.1 audit-readiness, P1.2 Phase 8 demolition, P1.3 Phase 7 test, P2.4 bypass risk, P2.5 doc accuracy | This project. Phases 1-4 above. |

## Completion Checklist
- [x] All Phase 1 tasks checked off
- [x] All Phase 2 tasks checked off
- [x] All Phase 3 tasks checked off
- [x] All Phase 4 tasks checked off
- [x] `validate_audit_ready.py PROJ-313` exits 0
- [x] All 5 audit findings closed
- [ ] User verified
