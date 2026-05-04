# Phase 3: RaceSetupScreen testable construction — PROOF OF CONCEPT for two-stage UIWindow refactor

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-325 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Ready (no longer blocked — PROJ-324 Phase 3 Task 3.4 reported NO-GO; PoC scope is now active).

**Objective:** Land the **canonical proof-of-concept** for the two-stage UIWindow construction pattern (Codex–Claude consensus, see Required reading). RaceSetupScreen is the highest-touch case; if the pattern works here, PROJ-328A/B/C apply it to the other 6 UIWindow subclasses.

## Required reading before starting

1. **CONSENSUS REFACTOR PLAN** — [`findings/consensus_discussion/uiwindow_mvvm_refactor_plan_r002.md`](findings/consensus_discussion/uiwindow_mvvm_refactor_plan_r002.md) — the source of truth. Read all of it.
2. **Discussion outcome** — [`findings/consensus_discussion/outcome.md`](findings/consensus_discussion/outcome.md)
   (Full transcript at `findings/consensus_discussion/arc01_*.md` if more context needed.)
3. PROJ-325 [`design.md`](design.md) — the NO-GO path section + headline pattern
4. PROJ-324 [`phase_3_checklist.md`](../PROJ-324/phase_3_checklist.md) Task 3.4 Notes — the NO-GO probe data
5. **Structural target** — [`game/ui/screens/battle_setup/screen.py`](../../../game/ui/screens/battle_setup/screen.py) — read its `__init__` carefully; this is what we want RaceSetup to resemble structurally
6. [`docs/02_PATTERNS.md`](../../../docs/02_PATTERNS.md) Pattern #8 — local MVVM precedent
7. [`docs/03_CONVENTIONS.md`](../../../docs/03_CONVENTIONS.md) section 2.4
8. [`game/ui/screens/race_setup/screen.py`](../../../game/ui/screens/race_setup/screen.py) — full file before editing
9. [`tests/unit/ui/screens/test_race_setup_screen.py`](../../../tests/unit/ui/screens/test_race_setup_screen.py) — especially the `_make_race_setup_screen` helper at lines 31-148

**Parallelism:** Parallel-safe with PROJ-327 (file-disjoint: PROJ-327 touches `tests/unit/ui/components/test_virtual_table.py` + mutable-mock fixtures + later strategy_screen; PROJ-325 Phase 3 touches `game/ui/screens/race_setup/` + `tests/unit/ui/screens/test_race_setup_screen.py` + `tests/fixtures/`). Coordinate before launching to avoid simultaneous edits to `tests/fixtures/ui_widget_factory.py` (PROJ-325 Phase 3 may add a `RaceSetupUiBuilder` reference; PROJ-327 doesn't touch the factory).

**Hard time budget:** 3 LLM-paced sessions (per consensus plan stop condition). If estimate balloons past that, STOP and surface to user — spin out the remainder rather than ballooning this project.

---

## Acceptance Criteria (from consensus plan, verbatim)

These are the success criteria for the PoC. Mirror to checkboxes on completion:

- [ ] **AC-1.** `RaceSetupScreen.__init__` follows the two-stage pattern: cheap state/delegates before the bypass point, UIWindow shell behind `bypass_init`, widget construction behind a builder.
- [ ] **AC-2.** `RaceSetupScreen` constructed with `with bypass_init(RaceSetupScreen): make_ui_widget(..., ui_builder=MockRaceSetupUiBuilder())` has `race_config`, `is_editing`, `race_library`, `race_registry`, `_asset_loader`, `_view_model`, `_renderer`, `_controller`, `_input_handler`, and `_llm_service` populated.
- [ ] **AC-3.** The old `_make_race_setup_screen` helper in `tests/unit/ui/screens/test_race_setup_screen.py` no longer patches `RaceSetupScreen.__init__` or manually assigns the delegate graph. The helper LOC delta is measured in the project notes (not asserted inside pytest).
- [ ] **AC-4.** Widget slots needed by existing tests are supplied by `MockRaceSetupUiBuilder`, not repeated per test.
- [ ] **AC-5.** All existing `tests/unit/ui/screens/test_race_setup_screen.py` tests pass after migration.
- [ ] **AC-6.** The resulting constructor structurally resembles `BattleSetupScreen.__init__`: delegate wiring is compact, behavior lives on delegates, and legacy property shims remain only where needed for compatibility with current tests/callers.
- [ ] **AC-7.** Do NOT document the new pattern in `docs/02_PATTERNS.md` until the PoC has landed and survived targeted tests. (Doc work owned by PROJ-324 Phase 4 + PROJ-328 close.)
- [ ] **AC-8.** If the PoC grows beyond the stop condition (3 sessions), stop and spin out the remaining work rather than ballooning the project.

---

## Tasks

### Task 3.1: Read the consensus plan + structural target [Simple]

- [ ] Read all of `uiwindow_mvvm_refactor_plan_r002.md` and `outcome.md`.
- [ ] Read `game/ui/screens/battle_setup/screen.py` end to end. Note its `__init__` shape, where delegates are constructed, what stays inline vs what's extracted.
- [ ] Read `game/ui/screens/race_setup/screen.py` end to end. Identify: cheap state assignments, delegate constructions, widget-touching code (`_create_ui()` + sub-methods).

**Notes:** [Filled during implementation. Brief structural diff: BattleSetup vs current RaceSetup.]

---

### Task 3.2: Failing test first — useful instance under bypass + null builder [Medium]

**File:** [`tests/unit/ui/screens/test_race_setup_screen.py`](../../../tests/unit/ui/screens/test_race_setup_screen.py)

- [ ] Add a NEW test (will fail at first):
  ```python
  def test_bypass_init_with_null_builder_yields_useful_instance():
      with bypass_init(RaceSetupScreen):
          screen = make_ui_widget(
              RaceSetupScreen,
              rect=pygame.Rect(0, 0, 800, 600),
              manager=Mock(),
              on_complete_callback=Mock(),
              on_cancel_callback=Mock(),
              ui_builder=NullRaceSetupUiBuilder(),
          )
      # Cheap state populated:
      assert screen.race_config is not None
      assert screen.is_editing is False
      assert screen.race_library is not None
      assert screen.race_registry is not None
      assert screen._asset_loader is not None
      # Delegates populated:
      assert screen._view_model is not None
      assert screen._renderer is not None
      assert screen._controller is not None
      assert screen._input_handler is not None
      assert screen._llm_service is not None
      # Widget slots are placeholders (None / empty):
      assert screen.btn_save is None
      assert screen.step_panels == {} or screen.step_panels == []
  ```
- [ ] Run it: confirm FAIL (currently `bypass_init` returns bare object).
- [ ] Commit the failing test alone for the audit trail (or hold for Task 3.3 commit, agent's call).

**Notes:** [Filled during implementation]

---

### Task 3.3: Production refactor — two-stage `__init__` + delegate factory + UI builder [Complex]

**File:** [`game/ui/screens/race_setup/screen.py`](../../../game/ui/screens/race_setup/screen.py) (refactor)
**File:** `game/ui/screens/race_setup/delegate_factory.py` (NEW — `DefaultRaceSetupDelegateFactory` + `RaceSetupDelegates` bundle)
**File:** `game/ui/screens/race_setup/ui_builder.py` (NEW — `RaceSetupUiBuilder` wrapping current `_create_ui()` flow)

- [ ] Create `RaceSetupDelegates` dataclass / NamedTuple with: `view_model`, `renderer`, `controller`, `input_handler`, `llm_service`.
- [ ] Create `DefaultRaceSetupDelegateFactory` with a `build(screen) -> RaceSetupDelegates` method. Construction logic moved verbatim from current inline code in `__init__`.
- [ ] Create `RaceSetupUiBuilder` with a `build(screen) -> None` method that wraps current `_create_ui()` (which itself calls `_create_tab_buttons` + `_create_step_panels` + `_create_navigation_buttons` + `error_label` setup).
- [ ] Refactor `RaceSetupScreen.__init__` to the two-stage pattern from consensus plan:
  ```python
  def __init__(self, rect, manager, on_complete_callback, on_cancel_callback,
               race_to_edit=None, race_registry=None,
               *, ui_builder=None, delegate_factory=None):
      self._init_state(rect, manager, on_complete_callback, on_cancel_callback,
                       race_to_edit, race_registry)
      self._init_widget_refs()
      self._delegates = (delegate_factory or DefaultRaceSetupDelegateFactory()).build(self)
      # Mirror delegate refs to legacy attribute names for back-compat with callers:
      self._view_model = self._delegates.view_model
      self._renderer = self._delegates.renderer
      self._controller = self._delegates.controller
      self._input_handler = self._delegates.input_handler
      self._llm_service = self._delegates.llm_service

      if getattr(type(self), 'bypass_init', False):
          self.ui_manager = manager
          self.rect = rect
          self._window_init_bypassed = True
          return

      super().__init__(rect, manager, ...)
      (ui_builder or RaceSetupUiBuilder()).build(self)
  ```
- [ ] Add `_init_state(...)` and `_init_widget_refs()` private methods. `_init_widget_refs()` assigns ALL widget slots to `None` / empty containers explicitly.
- [ ] Verify the failing test from Task 3.2 now PASSES.
- [ ] Verify production behavior unchanged: run any non-test callers (e.g., game launch path) confirm RaceSetup screen renders correctly. (If no easy way: defer to AC-5 full test pass.)

**Notes:** [Filled during implementation]

---

### Task 3.4: Add `NullRaceSetupUiBuilder` + `MockRaceSetupUiBuilder` [Medium]

**File:** [`tests/fixtures/race_setup_ui_builders.py`](../../../tests/fixtures/race_setup_ui_builders.py) (NEW — or wherever it fits)

- [ ] `NullRaceSetupUiBuilder.build(screen) -> None`: no-op.
- [ ] `MockRaceSetupUiBuilder.build(screen) -> None`: fills `screen.step_panels`, `screen.tab_buttons`, `screen.btn_save`, `screen.btn_cancel`, `screen.btn_load`, `screen.btn_randomize`, `screen.btn_randomize_all`, `screen.error_label`, plus the panel/gallery slots, with MagicMocks matching the old helper's expectations.
- [ ] Inspect the old `_make_race_setup_screen` helper in `test_race_setup_screen.py:31-148` to enumerate exactly which attributes need mocking. The MockBuilder should reproduce that wiring centrally.
- [ ] Add a smoke test for both builders.

**Notes:** [Filled during implementation. List exact widget refs the MockBuilder fills.]

---

### Task 3.5: Migrate `_make_race_setup_screen` helper + dependent fixtures [Complex]

**File:** [`tests/unit/ui/screens/test_race_setup_screen.py`](../../../tests/unit/ui/screens/test_race_setup_screen.py)

- [ ] Replace the `_make_race_setup_screen` helper body (currently ~118 LOC of `__new__` bypass + manual attribute assignment) with direct construction:
  ```python
  def _make_race_setup_screen(*, ui_builder=None, **overrides):
      with bypass_init(RaceSetupScreen):
          screen = make_ui_widget(
              RaceSetupScreen,
              rect=overrides.pop('rect', pygame.Rect(0, 0, 800, 600)),
              manager=overrides.pop('manager', Mock()),
              on_complete_callback=overrides.pop('on_complete_callback', Mock()),
              on_cancel_callback=overrides.pop('on_cancel_callback', Mock()),
              race_to_edit=overrides.pop('race_to_edit', None),
              race_registry=overrides.pop('race_registry', None),
              ui_builder=ui_builder or MockRaceSetupUiBuilder(),
          )
      # Apply any remaining overrides as attribute injection:
      for k, v in overrides.items():
          setattr(screen, k, v)
      return screen
  ```
- [ ] Run `pytest tests/unit/ui/screens/test_race_setup_screen.py -v --tb=short` — verify all 62 (or however many) tests still pass.
- [ ] Measure helper LOC delta — record in this Notes section.
- [ ] If any tests fail, diagnose: are they relying on widget refs the MockBuilder didn't fill? Adjust the MockBuilder, NOT the per-test wiring.

**Notes:** [Filled during implementation. Record helper LOC before/after + test pass count.]

---

### Task 3.6: Update PROJ-322 deferral annotations [Simple]

**Files:**
- [`Projects/active_projects/PROJ-322/phase_5_checklist.md`](../PROJ-322/phase_5_checklist.md)
- [`Projects/active_projects/PROJ-322/phase_3_checklist.md`](../PROJ-322/phase_3_checklist.md)
- [`Projects/active_projects/PROJ-322/phase_2_checklist.md`](../PROJ-322/phase_2_checklist.md)

- [ ] PROJ-322 Task 5.11 (RaceSetupScreen APC-001): change annotation from `**RE-DEFERRED IN PROJ-324 Phase 3 ...` to `**RESOLVED IN PROJ-325 Phase 3 (commit <SHA>) — two-stage construction pattern, see consensus plan**`. Same for Tasks 2.17 + 3.21 (RaceSetup-related).
- [ ] Other UIWindow subclass annotations (Tasks 5.6, 5.7, 5.10/5.10a, 5.12, 5.16, 5.29, 3.19, 3.20, 3.24, 3.26): leave pointing at PROJ-328A/B/C (already updated by Pass 2 housekeeping).

**Notes:** [Filled during implementation]

---

### Task 3.7: Stop-condition check + handoff to PROJ-328 [Simple]

- [ ] Verify session count: did the PoC fit within the 3-session budget?
- [ ] Update `plan.md` Current State to "PoC complete; pattern validated; PROJ-328 unblocked".
- [ ] Notify PROJ-328 owner that the canonical pattern is now in production at `game/ui/screens/race_setup/` (delegate_factory.py + ui_builder.py + refactored screen.py).
- [ ] PROJ-324 Phase 4 docs: signal that the pattern is ready to be documented in `docs/02_PATTERNS.md` (PROJ-324 Phase 4 owns that work; this Task just unblocks it).

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist

When all tasks above are done:

- [ ] All AC-1 through AC-8 satisfied
- [ ] All task checkboxes above are checked
- [ ] All `tests/unit/ui/screens/test_race_setup_screen.py` tests pass
- [ ] Sharded test suite passes: `python Tools/test_sharded/test_sharded.py` (run from main repo, NOT a worktree — known `\a` escape bug)
- [ ] Helper LOC delta measured + documented in Task 3.5 Notes
- [ ] PROJ-322 RaceSetup annotations updated
- [ ] PROJ-328 unblocked signal sent
- [ ] Update status at top of this file to `Complete`
- [ ] Update `plan.md` phase table row to `Complete`
- [ ] Update `plan.md` Current State to "All phases Complete"
- [ ] Update `plan.md` Verification section checkboxes
