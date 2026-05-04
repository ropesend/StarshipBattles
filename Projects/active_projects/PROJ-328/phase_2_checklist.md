# Phase B: NewGameSetupScreen MVVM split (PROJ-322 Tasks 5.12 + 3.21)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-328 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete (2026-05-03) — full MVVM split landed; PROJ-322 Tasks 5.12 + 3.21 resolved.

**Objective:** Apply the two-stage UIWindow construction pattern (PROJ-325 PoC; PROJ-328 Phase A) to `NewGameSetupScreen`, but go deeper than the small modals — full MVVM split with `NewGameSetupViewModel` + `NewGameSetupController` + `NewGameSetupUiBuilder`. Migrate the corresponding test file and add coverage for the new VM + Controller pieces.

## Required reading (already done by the agent before kicking off)

1. `Projects/active_projects/PROJ-325/findings/consensus_discussion/uiwindow_mvvm_refactor_plan_r002.md`
2. PROJ-328 Phase A commits (esp. `495fa0f39` — FleetReportWindow refactor, the closest analog to NewGameSetup as an already-decomposed direct UIWindow subclass)
3. `game/ui/screens/race_setup/{screen,delegate_factory,ui_builder}.py` — PoC reference
4. `tests/fixtures/race_setup_ui_builders.py` — Null + Mock builder pair pattern
5. The 4 PoC findings (in `phase_1_checklist.md`) — applied here

---

## Tasks

### Task B.1: Create `NewGameSetupViewModel` [Medium]

**File:** `game/ui/screens/new_game_setup_view_model.py` (NEW)

- [x] Pure-Python state container — `player_count`, `galaxy_type`, `system_count`, `player_races: List[Optional[RaceConfig]]` (4 slots), modal-state tracking (`active_race_modal`, `race_modal_player_index`).
- [x] No pygame imports. No widget refs. No validation logic (lives on Controller).
- [x] Helpers: `is_player_visible(i)`, `set_player_count(count) -> hidden_indices`, `set_race`, `clear_race`, `get_race`, `active_player_races()`, `open_race_modal`, `close_race_modal`, plus static `system_count_min/max` accessors.
- [x] Constants: `MAX_PLAYER_SLOTS = 4`, `DEFAULT_PLAYER_COUNT = 2`, `DEFAULT_GALAXY_TYPE = "spiral"`.

**Notes:** 191 LOC. The view model is `from __future__ import annotations` so `RaceConfig` only resolves under `TYPE_CHECKING`.

---

### Task B.2: Create `NewGameSetupController` [Complex]

**File:** `game/ui/screens/new_game_setup_controller.py` (NEW)

- [x] Owns mutations + lifecycle: race-modal open/close callbacks (`on_load_race_clicked`, `on_setup_race_clicked`, `on_race_selected`, `on_race_created`, `on_race_dialog_cancelled`), start/cancel flow (`on_start_clicked`, `on_cancel_clicked`).
- [x] Static methods (canonical implementations): `validate_save_name`, `generate_default_save_name`, `build_game_config`. The screen exposes thin shim static methods that delegate here for back-compat with existing test patches like `NewGameSetupScreen.validate_save_name`.
- [x] Constructor takes `screen`, `view_model`, `race_library`, `on_start_callback`, `on_cancel_callback`. Cheap — no pygame_gui widgets created.
- [x] **Validation dispatch through screen class** — `on_start_clicked` calls `type(self._screen).validate_save_name(...)` so existing tests that patch `NewGameSetupScreen.validate_save_name` keep working.
- [x] Helpers: `_collect_empire_names`, `_centered_modal_rect`, `_screen_centered_rect`.

**Notes:** 364 LOC. The "open modal" callbacks instantiate live `pygame_gui` modal windows so they are exercised by the screen integration tests, not by the controller unit tests.

---

### Task B.3: Create `NewGameSetupUiBuilder` [Simple]

**File:** `game/ui/screens/new_game_setup_ui_builder.py` (NEW)

- [x] Production builder — thin wrapper that delegates to the screen's `_create_ui()`. Same shape as `RaceSetupUiBuilder`.

**Notes:** 41 LOC. Per the PoC pattern, the construction code lives on the screen because it reaches into `self.get_container()`; the builder is a swappable seam.

---

### Task B.4: Create test fixtures (Null + Mock UI builders) [Medium]

**File:** `tests/fixtures/new_game_setup_ui_builder.py` (NEW)

- [x] `NullNewGameSetupUiBuilder` — no-op builder for delegate-only tests.
- [x] `MockNewGameSetupUiBuilder` — populates the widget slots with `MagicMock` instances matching the legacy helper's expectations: top-level widgets (`save_name_input`, `player_count_dropdown`, `galaxy_type_dropdown`, `system_count_slider`, `system_count_label`, `btn_start`, `btn_cancel`, `error_label`) plus 4-element row arrays (`empire_name_inputs`, `theme_labels`, `num_labels`, `race_preview_labels`, `load_race_buttons`, `setup_race_buttons`).
- [x] PoC finding 4 audit: existing `test_new_game_setup_extended.py` does NOT reach into any controller- or view-model-internal widget refs — every widget access is on the screen itself. MockBuilder therefore only writes to the screen.

**Notes:** 109 LOC.

---

### Task B.5: Refactor `NewGameSetupScreen` to two-stage construction [Complex]

**File:** `game/ui/screens/new_game_setup_screen.py`

- [x] Refactor `__init__` to two-stage shape per refined headline pattern:
   - Stage 1: cheap state (`_init_state`) + widget-ref placeholders (`_init_widget_refs`) + delegates (VM + Controller).
   - Stage 2: bypass branch (sets `ui_manager`, `_window_init_bypassed = True`, invokes `ui_builder.build(self)` if supplied, returns) **without assigning `self.rect`** (PoC finding 1) OR `super().__init__(...)` shell.
   - Stage 3: production builder.
- [x] Property shims for back-compat — `player_count`, `galaxy_type`, `system_count`, `player_races`, `active_race_modal`, `race_modal_player_index` proxy to view-model state.
- [x] Thin `_on_*` wrappers delegate to controller methods.
- [x] Static methods `validate_save_name`, `generate_default_save_name`, `get_player_count_options`, `build_game_config` retained on the class — delegate to controller statics so test patches at the screen surface keep working.

**Notes:** Production LOC: 714 -> 733 (+19 net; the +19 is the property-shim block + the dual-import — the actual `__init__` body shrank substantially because the cheap state and validation/config-build code moved out). The new files account for the rest of the LOC.

---

### Task B.6: Migrate `test_new_game_setup_extended.py` to direct construction [Medium]

**File:** `tests/unit/ui/screens/test_new_game_setup_extended.py`

- [x] Replace legacy `_make_screen` (`__new__` + patched `__init__` + per-attribute wiring) with `bypass_init(NewGameSetupScreen)` + `make_ui_widget(...)` + `MockNewGameSetupUiBuilder()`.
- [x] All 15 existing tests pass unchanged (test bodies untouched; only `_make_screen` rewritten).

**Notes:** Helper LOC ~34 -> ~25 (-9 in helper plus elimination of per-test wiring like `screen.btn_cancel = MagicMock()` in the BUG-115 tests). Test count: 15 passing.

---

### Task B.7: Migrate `test_new_game_setup.py` BUG-92 cluster [Simple]

**File:** `tests/unit/ui/test_new_game_setup.py`

- [x] `TestSetupRacePassesLoadedData` — 2 tests used the legacy `__new__` pattern. Migrated to a class-level `_make_screen` helper using the same `bypass_init` + `MockNewGameSetupUiBuilder` shape.

**Notes:** Both tests pass. The pre-existing `validate_save_name` static-method tests (~30) needed no changes — they call the static method directly, no instance construction.

---

### Task B.8: Add tests for `NewGameSetupViewModel` + `NewGameSetupController` [Medium]

**Files:**
- `tests/unit/ui/screens/test_new_game_setup_view_model.py` (NEW)
- `tests/unit/ui/screens/test_new_game_setup_controller.py` (NEW)

- [x] VM tests cover defaults, visibility derivation, set_player_count return value, race set/clear/get + idempotency + out-of-range tolerance, modal state machine, system-count bound accessors. 26 tests.
- [x] Controller tests cover validate_save_name (empty, whitespace, invalid filesystem chars, uniqueness), build_game_config (invalid player count, defaults, race name override, race theme override, fallback empire name), race-modal state callbacks (selected/created/cancelled), on_start_clicked (invalid name blocks callback, ValueError surfaced to error label), on_cancel_clicked. 22 tests.

**Notes:** 48 new tests in 415 LOC across both files. All pure-Python; no pygame imports needed for the view-model file.

---

### Task B.9: Update PROJ-322 deferral annotations [Simple]

- [x] PROJ-322 Phase 3 Task 3.21 → RESOLVED IN PROJ-328 Phase B
- [x] PROJ-322 Phase 5 Task 5.12 → RESOLVED IN PROJ-328 Phase B

**Notes:** Per the original task instructions: confirmed via PROJ-322 phase_3_checklist.md line 195 that Task 3.21 ("Use real `__init__` for new-game-setup-extended screen") DOES target NewGame — Phase A agent's caveat resolved.

---

### Task B.10: Phase completion verification + handoff [Simple]

- [x] All targeted tests pass: `pytest tests/unit/ui/screens/test_new_game_setup_extended.py tests/unit/ui/screens/test_new_game_setup_view_model.py tests/unit/ui/screens/test_new_game_setup_controller.py tests/unit/ui/test_new_game_setup.py -q` — 100/100 passing.
- [x] Broader UI screens suite passes: `pytest tests/unit/ui/screens/ -q` — 2275 passed, 1 skipped.
- [x] Update `plan.md` Quick Status Phase B → Complete.
- [x] Update `plan.md` Current State.

**Notes:** Did NOT run the full sharded suite per task instructions (known `\a` bug from worktrees).

---

## Phase Completion Checklist

When all tasks above are done:

- [x] All task checkboxes above are checked
- [x] All migrated test files pass
- [x] PROJ-322 annotations updated (5.12 + 3.21)
- [x] Update status at top of this file to `Complete`
- [x] Update `plan.md` phase table row to `Complete`
- [x] Update `plan.md` Current State to point to next phase
