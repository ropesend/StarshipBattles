# Phase 1: Pattern §33 + Stage-1 purity (T4.1 .. T4.7)

**Status:** Not Started
**Objective:** Mechanical extension of MAJ-001 fix to sibling classes; restore Stage-1 purity in `EmpirePanelWindow`; fix doc self-contradiction; resolve T4.7 with user before committing.

---

## Tasks

### Task 1.1: T4.1 — `virtual_table` placeholder in `star_list_window.py` [Simple]
**File:** `game/ui/screens/star_list_window.py:467-478`
**Tests:** `pytest tests/unit/ui/screens/test_star_list_window* -x`

- [ ] Read the existing class. Find where `virtual_table` is set in the live (non-bypass) path.
- [ ] Add `self.virtual_table = None` (or appropriate placeholder) BEFORE the bypass guard, matching the MAJ-001 fix shape used for `EmpireBuildQueueWindow`.
- [ ] Add a characterization test that constructs via `bypass_init` and asserts the placeholder is set (not AttributeError).
- [ ] Commit: `fix(star-list-window): add virtual_table placeholder for Pattern §33 bypass safety (PROJ-347 T4.1a)`

**Notes:**

### Task 1.2: T4.1 — same in `planet_list_window.py` [Simple]
**File:** `game/ui/screens/planet_list_window.py:720-739`

- [ ] Same fix shape as 1.1.
- [ ] Same test pattern.
- [ ] Commit: `fix(planet-list-window): add virtual_table placeholder for Pattern §33 bypass safety (PROJ-347 T4.1b)`

**Notes:**

### Task 1.3: T4.2 — `btn_confirm`/`btn_cancel` in `system_selection_window.py` [Simple]
**File:** `game/ui/screens/system_selection_window.py:143,153`

- [ ] Read lines 143, 153 to see how `btn_confirm` and `btn_cancel` are accessed in `update()`.
- [ ] Add placeholders before the bypass guard.
- [ ] Test + commit `fix(system-selection-window): add btn placeholders for Pattern §33 (PROJ-347 T4.2)`.

**Notes:**

### Task 1.4: T4.3 — `process_event` placeholders [Simple x3]
**Files:** `save_selection_window.py`, `race_browser_dialog.py`, `design_selector_window.py`

- [ ] For each: read `process_event` signature and any state it mutates. Add placeholders.
- [ ] Test + per-class commit (3 commits total).

**Notes:**

### Task 1.5: T4.4 — Stage-1 purity in `empire_panel_window.py` [Medium]
**File:** `game/ui/screens/empire_panel_window.py:114-116`
**Tests:** new + existing — `pytest tests/unit/ui/screens/test_empire_panel_window* -x`

- [ ] Read lines 114-116 — `load_resource_icons()` call.
- [ ] Read `game/ui/panels/empire_treasury_panel.py:311-333` to see what `load_resource_icons` does (`pygame.image.load(...).convert_alpha()` per Codex).
- [ ] Move the call AFTER the bypass guard so Stage 1 stays cheap/pure.
- [ ] Add a characterization test that constructs via `bypass_init` and asserts NO `pygame.image.load` is called (mock or spy).
- [ ] Commit: `fix(empire-panel-window): keep Stage 1 pure under bypass — defer icon loading (PROJ-347 T4.4)`

**Notes:**

### Task 1.6: T4.6 — `_window_init_bypassed = False` in production paths [Simple]
**Files:** `race_setup/screen.py`, `new_game_setup_screen.py`

- [ ] For each: locate the production-path `__init__` exit (the non-bypass branch). Set `self._window_init_bypassed = False` to match `StrategyModalWindow` base.
- [ ] Per-class commit (2 commits).

**Notes:**

### Task 1.7: T4.5 — fix `docs/02_PATTERNS.md` self-contradiction [Simple]
**File:** `docs/02_PATTERNS.md:1765-1776, 1833`

- [ ] Read both spans. Lines 1765-1776 show the first-statement-guard sketch (PROJ-324 NO-GO shape). Line 1833 says PROJ-325/PROJ-328 superseded that.
- [ ] Either (a) delete the obsolete sketch with a note pointing to PROJ-325/PROJ-328, or (b) replace the obsolete sketch with the current canonical Pattern §33 example.
- [ ] Headline copy-pasta reproducing the bug must also go.
- [ ] Commit: `docs(02_PATTERNS): resolve §33 self-contradiction; show only PROJ-325/PROJ-328 superseded shape (PROJ-347 T4.5)`

**Notes:**

### Task 1.8: T4.7 — user confirmation + execution [Complex]
**File:** `game/ui/screens/new_game_setup_ui_builder.py:37-38`

- [ ] Read current state: `build()` is a one-line pass-through to `screen._create_ui()`. ~400 LOC of widget code on the screen.
- [ ] Surface to user: "Option (a) move ~400 LOC widget code into builder.build() — bigger refactor but matches the builder pattern. Option (b) remove the builder facade — simpler, accepts that this screen doesn't use the builder pattern. Which?"
- [ ] Wait for user direction. Document choice in [decisions.md](decisions.md).
- [ ] Execute the chosen option. If (a): characterization test for builder.build() asserts produced widget tree matches pre-refactor. If (b): remove builder, update `screen.py` to no longer reference it.
- [ ] Commit per direction: `refactor(new-game-setup): <option> per user direction (PROJ-347 T4.7)`.

**Notes:**

### Task 1.9: Verification + index update
- [ ] `pytest tests/unit/ui/screens/ -x -q` — all pass.
- [ ] `python Tools/lint_test_files.py` — 0 violations.
- [ ] Update `Projects/projects_index.md` PROJ-347 → `Awaiting Verification`. Commit: `chore(PROJ-347): mark Sprint 5 awaiting verification`.

**Notes:**

---

## Phase Completion Checklist
- [ ] All tasks checked
- [ ] ~10 commits landed (per-class for T4.1-4.6, plus T4.5 doc, T4.7 per-user)
- [ ] plan.md phase row → `Complete`
- [ ] Surface to user
