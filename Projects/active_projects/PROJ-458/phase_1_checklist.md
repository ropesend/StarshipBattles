# PROJ-458 Phase 1: SettingsWindow (109 LOC, smallest) — characterization tests + two-stage retrofit + F-C-016 docs touch

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-458 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** None — PROJ-458 has no hard predecessors.
**Review Mode:** standard
**Objective:** Apply Pattern #33 two-stage `bypass_init` retrofit to `SettingsWindow` (109 LOC, simplest of the 5). Write dedicated behavior-locking characterization tests first (RED), then apply the retrofit (GREEN), then verify both production and bypass-init paths. F-C-016 closure is limited to deleting the stale-doc warning at `docs/known-issues.md:37`; `tests/fixtures/README.md` is already current at HEAD as of 2026-05-19 — see Task 1.4. Do NOT re-edit the README.

**Source-of-truth findings:** F-C-017 (SettingsWindow row) + F-C-016 in [`findings/PROJ-458_findings.md`](findings/PROJ-458_findings.md).

**Pattern reference:** `docs/02_PATTERNS.md` §33 (UI Widget Test Factory + two-stage UIWindow bypass-init).

**Existing structure (verified 2026-05-19 by reading `game/ui/screens/settings_window.py`):**
- Inherits directly from `UIWindow` (not from `StrategyModalWindow` or `PlanetTargetEditor`).
- Constructor: `__init__(self, rect, manager, on_close_callback=None)`.
- State assignments: `self.on_close_callback`, `self._settings = GameSettings()`.
- Widget construction: title, brightness slider + label + value display, Reset button, Close button (~80 LOC of widget setup).
- Methods: `process_event`, `update`, `kill`.

---

## Tasks

### Task 1.1: Read Pattern #33 + 5 retrofitted templates [Medium]
**Files (read-only):**
- `docs/02_PATTERNS.md` §33 (UI Widget Test Factory)
- `tests/fixtures/ui_widget_factory.py` (the `make_ui_widget` + `bypass_init` helpers)
- `game/ui/screens/race_setup/screen.py` (line 149 — the canonical two-stage shape)
- `game/ui/screens/new_game_setup_screen.py` (similar pattern)
- `game/ui/screens/strategy_modal_window.py` (the base-class-level guard for `StrategyModalWindow` subclasses)

- [ ] Read Pattern #33 in full. Note the exact Stage 1 / guard / Stage 2 boundaries and the bypass-init context manager.
- [ ] Read `race_setup/screen.py:144-161` for the canonical two-stage `__init__` shape (Stage 1 pure-Python state + delegate factory + ui_builder seam; bypass guard at line 149; Stage 2 `super().__init__(...)` + widget tree below).
- [ ] Read `tests/fixtures/ui_widget_factory.py` to confirm the `make_ui_widget(SettingsWindow, **kwargs)` invocation pattern with `bypass_init(SettingsWindow)` context manager.
- [ ] Decide whether to introduce a `SettingsWindowUiBuilder` Protocol + `DefaultSettingsWindowUiBuilder` (full Stage-2 widget construction wrapped in a swappable builder) or to inline the Stage-2 work (simpler; less testable). Record the decision in `decisions.md`. Default recommendation: introduce the builder for consistency with the 5 already-retrofitted windows.

### Task 1.2: Write dedicated characterization tests (RED) [Medium]
**File:** `tests/unit/ui/screens/test_settings_window.py` (new)
**Tests:** `pytest tests/unit/ui/screens/test_settings_window.py -q`

- [ ] Create the test file. Mirror the existing pattern in `tests/unit/ui/screens/test_race_setup_screen.py` for header / imports / class organization.
- [ ] **Test class: TestConstruction**
  - `test_bypass_init_yields_instance_without_widgets`: with `bypass_init(SettingsWindow)`, `make_ui_widget(SettingsWindow, ...)` returns an instance where `_settings` is initialized but the widget handles (`_brightness_slider`, etc.) are absent (or stubs).
  - `test_production_init_constructs_widget_tree`: without bypass, `SettingsWindow(rect, manager)` constructs the full widget tree (assert widget handles exist).
- [ ] **Test class: TestBrightnessSlider**
  - `test_slider_initial_value_matches_settings`: the slider's `start_value` matches `GameSettings().background_brightness` at construction time.
  - `test_slider_update_writes_to_settings`: after `update(dt)` with `has_moved_recently=True` (mocked), `self._settings.background_brightness` is updated to the slider's current value.
  - `test_brightness_label_format`: the percentage label format `"{:.0%}"` is preserved (test exact text).
- [ ] **Test class: TestResetButton**
  - `test_reset_button_resets_settings_to_defaults`: with a non-default brightness, pressing the Reset button (UI_BUTTON_PRESSED event with `ui_element == self._btn_reset`) calls `self._settings.reset_to_defaults()`, updates slider to default, updates label.
- [ ] **Test class: TestCloseButton**
  - `test_close_button_calls_on_close_callback`: pressing Close (UI_BUTTON_PRESSED with `ui_element == self._btn_close`) calls `self.kill()` which calls `on_close_callback()`.
  - `test_close_without_callback_does_not_raise`: when `on_close_callback=None`, kill() still works.
- [ ] **Test class: TestCharacterization**
  - `test_constructor_positional_signature_preserved`: assert the public positional/keyword-able signature `__init__(self, rect, manager, on_close_callback=None, ...)` is preserved by the retrofit (regression catcher). Callers using `SettingsWindow(rect, manager)` or `SettingsWindow(rect, manager, on_close_callback=cb)` continue to work.
  - `test_constructor_accepts_keyword_only_ui_builder`: assert the retrofit ADDS a kw-only `ui_builder` parameter (defaults to `None`, falls back to `DefaultSettingsWindowUiBuilder()` inside `__init__`). This is the new injection seam introduced by Task 1.3 — Pattern #33 retrofit recipe.

  **Codex r5 audit decision (2026-05-19):** Codex flagged Task 1.2 vs Task 1.3 inconsistency: Task 1.2 was locking the pre-retrofit signature `(rect, manager, on_close_callback=None)`, but Task 1.3 introduces a new kw-only `ui_builder` parameter. The resolution is that the retrofit **adds** the kw-only `ui_builder` (per Pattern #33 recipe; see `game/ui/screens/race_setup/screen.py` for the template), and Task 1.2's regression catcher asserts the **positional/keyword-able** portion of the signature is unchanged — not the whole signature. The pre-retrofit `settings_window.py:17` has no `ui_builder`; the post-retrofit signature adds it as kw-only.
- [ ] Run the new test file. Expect all tests to FAIL initially because (a) the retrofit hasn't landed yet, (b) the bypass-init path isn't supported yet on this class, (c) the kw-only `ui_builder` parameter doesn't exist yet. Confirm failures match expectations.

### Task 1.3: Apply the two-stage retrofit (GREEN) [Medium]
**File:** `game/ui/screens/settings_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_settings_window.py tests/unit/ui/screens/strategy_windows/test_empire_panel_ctrl.py -q`

- [ ] Rewrite `SettingsWindow.__init__` to the two-stage shape. Sketch:
  ```python
  def __init__(
      self,
      rect,
      manager,
      on_close_callback=None,
      *,
      ui_builder: SettingsWindowUiBuilder | None = None,
  ):
      """Initialize the settings window.
      ...
      """
      # Stage 1 — pure-Python state + UI-builder seam.
      # No pygame_gui widgets, no self.get_container(), no asset I/O.
      self.on_close_callback = on_close_callback
      self._settings = GameSettings()
      self._ui_builder = ui_builder or DefaultSettingsWindowUiBuilder()

      # Bypass guard — type(self) so subclass flags win.
      if getattr(type(self), "bypass_init", False):
          return

      # Stage 2 — heavy widget tree.
      super().__init__(rect, manager, window_display_title="Settings")
      self._ui_builder.build(self)
  ```
- [ ] Extract Stage-2 widget construction (currently lines 30-76) into `DefaultSettingsWindowUiBuilder.build(window)`. Define the `SettingsWindowUiBuilder` Protocol + `DefaultSettingsWindowUiBuilder` class in the same module (small enough that a separate file is overkill).
- [ ] Verify `super().__init__(...)` is below the bypass guard.
- [ ] Run the new characterization tests; all should PASS.
- [ ] Run the incidental coverage tests at `tests/unit/ui/screens/strategy_windows/test_empire_panel_ctrl.py:100-127` (the `SettingsRegistrar` cluster). Confirm no regression.

### Task 1.4: F-C-016 docs touch — delete the stale `docs/known-issues.md:37` warning [Simple]
**Files:**
- `docs/known-issues.md` (single warning paragraph removal)

**Scope narrowed (codex r5 audit 2026-05-19):** The README half of F-C-016 is ALREADY resolved at HEAD. Verify before editing:
- `tests/fixtures/README.md:22` reads `ui_widget_factory.py    # pygame_gui widget factory + UIWindow bypass_init helper` (good — no rewrite needed).
- `tests/fixtures/README.md:310-336` documents the current two-stage Pattern #33 approach (good — no rewrite needed).

Only `docs/known-issues.md:37` still carries the stale "tests/fixtures/README.md still describes ui_widget_factory.py as 'non-UIWindow only'..." warning. Remove that warning paragraph; do NOT re-edit the README.

- [ ] Read `tests/fixtures/README.md:22, 310-336` first. Confirm the README is already updated (line 22 does NOT contain "Non-UIWindow"; lines 310-336 reference Pattern #33). If for some reason the README has drifted backward, scope grows back to its original "rewrite README" framing and update `findings/PROJ-458_findings.md` to match.
- [ ] Read `docs/known-issues.md:37`. Confirm it still says "Stale-doc warning: `tests/fixtures/README.md` still describes `ui_widget_factory.py` as 'non-UIWindow only' and points at the old blocker. The current authoritative guidance is the factory docstring plus `docs/02_PATTERNS.md` section 33."
- [ ] Delete that warning paragraph entirely (it's obsolete — the README is already correct).
- [ ] If `docs/known-issues.md` still has a known-issue anchor `#uiwindow-super-init-chain-blocker`, delete that anchor's section too (Pattern #33 solved the blocker).
- [ ] Bump the "Last verified" date on `docs/known-issues.md`.

### Task 1.5: Verify + commit [Simple]

- [ ] Run targeted tests: `pytest tests/unit/ui/screens/test_settings_window.py tests/unit/ui/screens/strategy_windows/test_empire_panel_ctrl.py tests/unit/ui/screens/test_strategy_modal_window.py -q`. All green.
- [ ] Run sharded suite: `python Tools/test_sharded/test_sharded.py`. Green at same count (Phase 1 adds new tests but no removals).
- [ ] Verify (PowerShell-safe): `(Get-Content game/ui/screens/settings_window.py | Measure-Object -Line).Lines` stays in a reasonable range (Stage 1 + bypass guard + Stage 2 + builder class likely ~140-160 LOC; still well under 500).
- [ ] Verify F-C-017 (SettingsWindow row) and F-C-016 are marked `Status: resolved` in `findings/PROJ-458_findings.md`.

---

## Phase Completion Checklist

When all 5 tasks are checked off:
- [ ] F-C-017 (SettingsWindow) + F-C-016 flipped to `Status: resolved` in `findings/PROJ-458_findings.md`.
- [ ] Run `python Tools/test_sharded/test_sharded.py` — full sharded suite green.
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-458 1` — PASSED.
- [ ] Update status at top of this file to `Complete`.
- [ ] Update plan.md phase table row to `Complete`.
- [ ] Update plan.md Current State to point to Phase 2.
- [ ] Commit message: `PROJ-458 Phase 1: retrofit SettingsWindow to two-stage bypass-init + dedicated characterization tests; close F-C-016 docs touch`.
- [ ] No new entries in `AgentCoordination/discovered_issues/log.jsonl` unless they are genuine out-of-scope discoveries.
