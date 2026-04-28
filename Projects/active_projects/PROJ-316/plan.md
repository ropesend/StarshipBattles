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
| 1. Paperwork sweep — checklists + docs | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Tighten `window_manager` to required on strategy-screen-only windows | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Replace Phase 7 click-blocking regression test | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Final verification + audit script green | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-04-28
**Active Phase:** Planning complete — ready for kick-off
**Last Action:** Project scaffolded from PROJ-313 audit findings. Four phases scoped covering: docs/checklist hygiene; constructor-default tightening on 13 windows; rewrite of the Phase 7 regression test that didn't actually exercise the migrated editor classes; final audit-script verification.
**Next Action:** Begin Phase 1 — paperwork sweep. Update PROJ-313 phase checklists from "Not Started" → "Complete" (with `Deferred:` notes for the genuinely-deferred Phase 8 demolition tasks), fix the doc inaccuracies in Pattern #31 (adopter count, "one-liner" claim, contract-test claim), and bump `Last verified:` blockquotes. Re-run `python Projects/scripts/validate_audit_ready.py PROJ-313` until exit code 0.
**Blockers:** None.
**Test baseline:** Per the audit, the reviewer observed 8 failing tests in `tests/unit/strategy/test_ship_instance_damage.py` (`iter_all_components_by_layer`). These are PROJ-315 in-progress, not PROJ-313 / PROJ-316 — see `findings/proj_313_audit_findings.md` §"Verification". Establish baseline at PROJ-316 kick-off by running `python Tools/test_sharded/test_sharded.py` and recording the pass/fail count + identifying any failures that are not from PROJ-315.

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
4. **Bypass risk via `window_manager=None` default.** The base class defaults to `None`. 13 of 14 strategy-screen-only windows also default to `None`. A future strategy-screen call site can omit the keyword and silently break the structural guarantee.
5. **Pattern #31 doc accuracy.** Claims "21 adopters" (actually 20), "Both methods are one-liners" (`has_modal_open` retains menu_panel + build_queue_screen checks), and "Replaces the source-string cleanup test" (the test still exists).

## Goals
- Make `Projects/active_projects/PROJ-313/` audit-ready —
  `validate_audit_ready.py PROJ-313` exits 0.
- Fix the documentation inaccuracies in Pattern #31 to match actual
  code state.
- Restore the structural guarantee that forgotten `window_manager=` at
  a strategy-screen call site is impossible (compile-time/construct-time
  failure) for the 13 windows that should never be opened off-strategy.
- Replace the Phase 7 click-blocking test with one that actually
  imports and exercises the 5 migrated editor classes, plus a
  spawn-site assertion test.

## Scope

**In scope:**
- All 5 audit findings.
- Doc updates (`docs/02_PATTERNS.md`, `docs/06_UI_STYLE_GUIDE.md`).
- Test rewrites (`tests/integration/ui/test_editor_click_blocking.py`).
- Constructor-signature changes on 13 windows.
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
| Strategy modal base class | `game/ui/screens/strategy_modal_window.py` | Tighten `window_manager` to required (no `None` default) |
| 13 migrated windows | `game/ui/screens/{planet_list,star_list,build_queue_list,empire_build_queue,event_log,empire_panel,fleet_report,planet_abilities}_window.py`, `game/ui/screens/strategy_windows/move_choice_dialog.py`, `game/ui/screens/{food_allocation,atmosphere_target,gravity_target,water_target,radiation_shield}_editor.py` | Remove `= None` default from `window_manager` parameter |
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
- [ ] Run `python Tools/test_sharded/test_sharded.py` — record baseline (expect 8 PROJ-315 failures, ignore those)
- [ ] Run `python Projects/scripts/validate_audit_ready.py PROJ-313` — record current 16 errors

### After Each Phase
- [ ] Run `pytest tests/unit/ui/screens/ tests/integration/ui/` (incremental)
- [ ] Targeted regression for changed windows

### Final Verification
- [ ] `python Projects/scripts/validate_audit_ready.py PROJ-313` exits 0
- [ ] `python Tools/test_sharded/test_sharded.py` — same baseline preserved (PROJ-315 failures still the only ones)
- [ ] All 13 windows reject construction without `window_manager=` (TypeError raised)
- [ ] Phase 7 regression test fails if you (a) un-subclass FoodAllocationEditor from StrategyModalWindow, (b) omit `window_manager=` at any of the 5 editor spawn sites, (c) remove `register_modal` from base class — verified by manual mutation test

## Phase Breakdown

### Phase 1 — Paperwork sweep
**Objective:** make PROJ-313 audit-ready and bring docs into agreement
with code. No production code changes in this phase.

#### Task 1.1 — Update PROJ-313 phase checklists to reflect actual state
**File:** `Projects/active_projects/PROJ-313/phase_1_checklist.md` … `phase_8_checklist.md`
- [ ] For each of phases 1–7: change `**Status:** Not Started` → `**Status:** Complete`. Walk the task list and check off the boxes that were done.
- [ ] For Phase 8: leave the demolition tasks unchecked, add `**Deferred:**` notes to each, and at the bottom of the file add a "Scope Deviation" section pointing to plan.md Current State.

#### Task 1.2 — Update PROJ-313 plan.md goals section
**File:** `Projects/active_projects/PROJ-313/plan.md`
- [ ] In the Goals section, mark the goals that were downscoped with `[deferred — see Current State scope deviation]`. Specifically: "Delete `_handle_window_close`" and "Replace the false-negative-prone `TestModalSlotCleanupContract` test".

#### Task 1.3 — Fix Pattern #31 doc accuracy
**File:** `docs/02_PATTERNS.md`
- [ ] Adopter count: "21 windows" → "20 windows" (count the listed names: 20).
- [ ] "Both methods are one-liners" → "Both methods walk `iter_live_modals()` for modal-tracking; `has_modal_open()` additionally checks `menu_panel` and `build_queue_screen` (pre-modal-tracking concerns retained from before PROJ-313)."
- [ ] "Replaces the source-string-matching test" → "Augments the legacy `TestModalSlotCleanupContract` (kept as a regression for the slot-cleanup pathway that still operates for caller-convenience pointers; see Migration notes). The new structural invariant test is at `tests/unit/ui/screens/test_strategy_modal_window.py`."
- [ ] Bump `Last verified:` blockquote.

#### Task 1.4 — Pattern #30 SUPERSEDED banner clarification
**File:** `docs/02_PATTERNS.md`
- [ ] Confirm Pattern #30's SUPERSEDED banner accurately states: the registrar `on_close_callback` mechanism remains active for slot-cleanup of caller-convenience pointers; what was superseded is the use of these slots as the *modal-tracking contract* (now done structurally via Pattern #31).

#### Task 1.5 — Re-run audit script until green
**Command:** `python Projects/scripts/validate_audit_ready.py PROJ-313`
- [ ] Run the script. Capture errors.
- [ ] Address each error (most should be resolved by Task 1.1). Iterate.
- [ ] Acceptance: exit code 0.

**Tests:** `python Projects/scripts/validate_audit_ready.py PROJ-313` exits 0; `pytest tests/` no regression.

---

### Phase 2 — Tighten `window_manager` to required on strategy-screen-only windows
**Objective:** Restore the structural guarantee — make forgotten
registration impossible at strategy-screen spawn sites by removing the
`= None` default on the 13 windows that are only opened from the
strategy screen.

#### Task 2.1 — Inventory call sites
**Goal:** confirm each of the 13 windows is opened ONLY from
strategy-screen contexts (`game/ui/screens/strategy_event_router.py`,
`game/ui/screens/strategy_windows/*.py`, or `strategy_screen.py`).
- [ ] For each of the 14 candidate windows, grep the codebase for `<ClassName>(` constructor calls (excluding test files and the class definition itself).
- [ ] Categorise: STRATEGY-ONLY (safe to require `window_manager=`) vs DUAL-CALLER (needs to keep `None` default). Per PROJ-313 implementation, only `PlanetSelectionWindow` is dual-caller (also opened from `BuildQueueScreen`).
- [ ] Document the inventory in `decisions.md`.

#### Task 2.2 — Tighten the base class signature
**File:** `game/ui/screens/strategy_modal_window.py`
- [ ] Change `window_manager: "StrategyWindowManager | None" = None` → `window_manager: "StrategyWindowManager | None"` (keyword-only, no default). The type stays `Optional` so `PlanetSelectionWindow` can still pass `None` from `BuildQueueScreen`.
- [ ] Update the docstring to say "Pass `None` only when the window is being opened outside the strategy screen".
- [ ] Run `pytest tests/unit/ui/screens/test_strategy_modal_window.py` — should still pass (tests pass `window_manager=` explicitly).

#### Task 2.3 — Tighten each of the 13 strategy-screen-only windows
**Files:** the 13 window class files listed in Key Files.
- [ ] For each, remove the `= None` default from `window_manager` parameter. Keep the type `"StrategyWindowManager | None"` or change to `"StrategyWindowManager"` (decide per-window based on whether `None` is ever a sensible value; for strategy-screen-only the answer is no, so use `"StrategyWindowManager"`).
- [ ] Verify the spawn site already passes `window_manager=` (per PROJ-313 it does). If not, fix.
- [ ] Run `pytest tests/unit/ui/screens/` — find tests that constructed the window without `window_manager=`, add `window_manager=None` (acceptable in test contexts) or a real fixture.

#### Task 2.4 — Update `docs/06_UI_STYLE_GUIDE.md` Window Management section
**File:** `docs/06_UI_STYLE_GUIDE.md`
- [ ] Update the example code template to show `window_manager: "StrategyWindowManager"` (required) for strategy-screen-only adopters. Add a separate "Cross-screen reuse" subsection covering the `Optional[...]` + explicit `None` pattern for windows like `PlanetSelectionWindow`.
- [ ] Bump `Last verified:` blockquote.

#### Task 2.5 — Verification
- [ ] Construct each of the 13 windows in a Python REPL without `window_manager=` and confirm `TypeError: missing required keyword-only argument` is raised.
- [ ] `pytest tests/unit/ui/ tests/integration/ui/` clean.

**Tests:** `pytest tests/unit/ui/ tests/integration/ui/` no regression.

---

### Phase 3 — Replace Phase 7 click-blocking regression test
**Objective:** the regression test must fail if any of the migration
steps are undone — subclass changed, spawn-site omits
`window_manager`, or base class skips registration.

#### Task 3.1 — Add structural-subclass test
**File:** `tests/integration/ui/test_editor_click_blocking.py`
- [ ] At the top, import the 5 editor classes:
      `FoodAllocationEditor`, `AtmosphereTargetEditor`,
      `GravityTargetEditor`, `WaterTargetEditor`,
      `RadiationShieldEditor`.
- [ ] Add a parametrised test over the imported class objects (not strings) that asserts `issubclass(cls, StrategyModalWindow)`. Failure mode: a future commit removing the subclass relationship causes a hard test failure.

#### Task 3.2 — Add registration-on-construct test
**File:** same.
- [ ] For each editor, use the existing `__new__` + patched-`pygame_gui.elements.UIWindow.__init__` pattern (mirror `tests/unit/ui/screens/test_strategy_modal_window.py`'s `_make_modal_window` helper) to construct the editor with a stub `StrategyWindowManager`-shaped object.
- [ ] Assert the constructed instance appears in the manager's modal list immediately after construction.
- [ ] Construct each editor's `kill()` and assert it deregisters.

#### Task 3.3 — Add spawn-site assertion test
**File:** same (or split into a new file `test_editor_spawn_sites.py` if cleaner).
- [ ] For each `StrategyEventRouter._open_*_editor()` method (5 methods):
      patch the editor class via `unittest.mock.patch`, call the spawn
      method, assert `mock_editor.call_args.kwargs["window_manager"]` is
      `ui.window_manager` and is not None.
- [ ] Also assert it's NOT default-constructed without the keyword.

#### Task 3.4 — Rename or remove the existing click-blocking integration test
**File:** same.
- [ ] The current test exercises the router OR-bridge with a mocked editor in `iter_live_modals` — this is still useful as router-level coverage. Either:
      a) Keep it under a clearer name like `test_router_blocks_clicks_inside_any_modal_in_iter_live_modals`, OR
      b) Delete it entirely now that the structural tests above provide stronger coverage.
- [ ] Decide and update.

#### Task 3.5 — Manual mutation test (verification)
- [ ] Temporarily un-subclass `FoodAllocationEditor` from `StrategyModalWindow` (change to `pygame_gui.elements.UIWindow`). Run the new tests. Confirm Task 3.1's test fails.
- [ ] Temporarily comment out `window_manager=ui.window_manager` in `_open_food_allocation_editor`. Run tests. Confirm Task 3.3's test fails.
- [ ] Temporarily comment out `window_manager.register_modal(self)` in `StrategyModalWindow.__init__`. Run tests. Confirm Task 3.2's test fails.
- [ ] Revert all temporary changes. Confirm tests pass again.

**Tests:** new tests in `tests/integration/ui/test_editor_click_blocking.py` (or split file).

---

### Phase 4 — Final verification + audit-script green
**Objective:** confirm the remediation closed all 5 findings and the
project is genuinely audit-ready.

#### Task 4.1 — PROJ-313 audit script green
- [ ] `python Projects/scripts/validate_audit_ready.py PROJ-313` exits 0.

#### Task 4.2 — Full sharded test suite
- [ ] `python Tools/test_sharded/test_sharded.py` — record pass/fail count.
- [ ] Failures should be limited to the 8 PROJ-315 `test_ship_instance_damage.py` cases recorded at PROJ-316 kick-off (or 0 if PROJ-315 is fixed by then). Anything else is a regression.

#### Task 4.3 — Doc cross-reference walk
- [ ] Re-read `docs/02_PATTERNS.md` Pattern #31. Cross-reference every claim against the live code (count adopters, look at `has_modal_open` shape, confirm the new structural test exists, confirm the legacy test still exists). All claims must be accurate.
- [ ] Re-read `docs/06_UI_STYLE_GUIDE.md` Window Management section. The example must reflect Phase 2 changes.

#### Task 4.4 — Update PROJ-316 plan.md and close out
- [ ] Mark all 4 PROJ-316 phases Complete in the Quick Status table.
- [ ] Update Current State.
- [ ] Update `Tracking/active_projects` index if present (or `Projects/projects_index.md`).
- [ ] Hand off to user for verification.

**Tests:** None new; verification is sweep + audit-script + manual.

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 0 | 2026-04-28 | Initial audit (reviewer) — 5 findings: P1.1 audit-readiness, P1.2 Phase 8 demolition, P1.3 Phase 7 test, P2.4 bypass risk, P2.5 doc accuracy | This project. Phases 1-4 above. |

## Completion Checklist
- [ ] All Phase 1 tasks checked off
- [ ] All Phase 2 tasks checked off
- [ ] All Phase 3 tasks checked off
- [ ] All Phase 4 tasks checked off
- [ ] `validate_audit_ready.py PROJ-313` exits 0
- [ ] All 5 audit findings closed
- [ ] User verified
