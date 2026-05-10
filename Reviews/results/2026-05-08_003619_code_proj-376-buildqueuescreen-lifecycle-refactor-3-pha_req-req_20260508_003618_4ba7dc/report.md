# PROJ-376 BuildQueueScreen Lifecycle Refactor Review — Phases 1-3

**Review type:** code
**Request ID:** req_20260508_003618_4ba7dc
**Review date:** 2026-05-08
**Scope:** 3 commits on `feat/03c-phase-aware-execution` (56bbe4c54, a93330bb9, 4ef34e87b)
**Review mode:** normal
**Files reviewed:** 19 (7 production + 6 test + 6 doc/plan)

---

## Executive Summary

- **Total Findings:** 6
- **Critical:** 0 | **Major:** 1 | **Minor:** 3 | **Info:** 2
- **Overall Assessment:** PROJ-376 is well-executed. All 11 focus areas pass verification. The lifecycle seam is clean, the instance-reuse contract is correctly implemented, all three `is_visible()` migration sites are correct, `_request_close()` is the single close path, `_rebuild_panels` handles cross-context-type transitions, plan-vs-implementation drift is documented, and PROJ-373 review hygiene items are addressed. One MAJ finding: build_queue_screen.py at 822 LOC exceeds the 500 soft target — acknowledged in design, acceptable given the lifecycle methods are cohesive.

---

## Verification Matrix (per instruction focus areas)

### 1. Lifecycle correctness — PASS

`test_open_for_yard_initial_yard_kwarg_matches_post_open_state` (`test_build_queue_screen_lifecycle.py:252-299`) compares 11 yard-specific attributes between eager construction (`initial_yard=planet_a`) and shell-then-open (`initial_yard=None` + `open_for_yard`):
- `build_context`, `hex_coord`, `queue_sources` (len), `selected_queue_indices`, `active_queue_source`, `selected_queue_index`, `planet_selection_window`
- `controller.build_context`, `controller.hex_coord`, `controller.selected_category`, `controller.selected_role`

`test_open_for_yard_populates_state_for_planet` (line 211-249) additionally asserts `controller.active_queue_source` identity, covering the full catalog of 12 fields. The shell-only constructor (`test_init_with_no_yard_constructs_ui_shell_only`, line 180-208) correctly leaves all yard state empty and panels/collaborators at None.

### 2. Instance-reuse contract — PASS

(a) All 3 construction sites (`on_build_yard_click`, `on_fleet_build_click`, `on_navigate_to_hex_build`) route through the single `_open_build_queue` helper (`strategy_build_queue_manager.py:77-130`). No bypass exists.

(b) The `else` branch in `_open_build_queue` (lines 110-126) rebinds `design_library`, `design_loader`, and `portrait_loader` on the cached instance. The portrait_loader is freshly constructed because it holds a reference to the per-click `design_library`. Correct.

(c) `BuildQueueScreen.open_for_yard` line 302 rebinds `self.drag_handler.design_library = self.design_library`. The drag handler is already constructed (we only reach this path after first construction), so the rebind chains naturally.

(d) `_on_build_queue_close` (lines 160-199) does NOT null `self._screen.build_queue_screen` (line 186 comment confirms intent). The test `test_close_callback_does_not_null_screen_slot` (line 159-171) verifies the slot survives.

### 3. `is_visible()` contract — PASS

All three sites migrated with defense-in-depth (`is not None and is_visible()`):
- `strategy_event_router.py:61-64` — modal-block check returns True only when visible.
- `strategy_input_handler.py:58-62` — events only route to visible screen; early return prevents hidden-screen event processing.
- `strategy_screen.py:248-251` — draw gate prevents drawing a hidden screen.

### 4. `_request_close()` contract — PASS

(a) Close-button handler at `build_queue_screen.py:593-594` routes through `self._request_close()`.
(b) Esc handler at `build_queue_screen.py:720-721` routes through `self._request_close()` (via `InputAction.BUILD_QUEUE_CLOSE`).
(c) `hide()` (lines 317-338) kills `planet_selection_window` if open, then calls `self.panels.background.hide()` + `manager.update(0)`. Does NOT invoke `on_close`.
(d) `_close()` is removed: `grep -n "def _close"` returns 0 matches.
(e) `test_close_method_is_removed` (line 545-550) asserts `not hasattr(BuildQueueScreen, '_close')` and `hasattr(BuildQueueScreen, '_request_close')`.

### 5. `_rebuild_panels` correctness — PASS

`test_open_for_yard_planet_to_fleet_rebuilds_panels` (line 302-336):
- Line 332: `assert screen.panels is not old_panels` — identity change confirmed
- Line 334: `assert not old_background.alive()` — old panels killed
- Line 336: `assert not isinstance(screen.panels.context_report, PlanetReportPanel)` — fleet panel layout used

`test_open_for_yard_planet_to_planet_does_not_rebuild_panels` (line 339-368):
- Line 366: `assert id(screen.panels) == panels_id` — same object identity
- Line 367: `assert screen.panels.background.alive()` — panels alive
- Line 368: `assert screen.build_context is planet_b` — yard updated without rebuild

### 6. Plan-vs-implementation drift — PASS

All three logged deviations in decisions.md match implementation:
- **decisions.md:27**: `panel.hide()`/`panel.show()` used (not `set_visible`). Implementation at `build_queue_screen.py:336,343` uses `self.panels.background.hide()`/`.show()`.
- **decisions.md:25**: Inline dependency rebinding. Implementation at `strategy_build_queue_manager.py:110-126`.
- **decisions.md:26**: `_close()` removed entirely. Confirmed by grep.

### 7. PROJ-373 review hygiene — PASS

- **MIN-001** (reset_filters docstring): `build_queue_controller.py:264-270` — updated to "PROJ-376... called from BuildQueueScreen.open_for_yard... Live as of PROJ-376 Phase 1."
- **MIN-002** (HFS+ mtime comment): `build_queue_controller.py:213-216` — comment added.
- **MIN-003** (layout-pass dependency): `virtual_table.py:548-551` — public `rebuild_row_pool` docstring documents the requirement.
- **MIN-005** (column-config test): `test_virtual_table.py:1377` — `test_column_config_change_triggers_rebuild` exists and verifies pool invalidation.
- **MAJ-003** (Phase 1 cross-open caveat): PROJ-373 plan.md line 16 updated with "cross-open value live since PROJ-376 Phase 2".
- **MAJ-004** (Phase 2 status update): PROJ-373 plan.md line 17 — "Completed in PROJ-376". Detailed Phase 2 section updated. Old "Deferred... Do not implement" wording removed.

### 8. Tests — PASS

Spot-checked 3 tests for actual claim coverage:
- `test_open_for_yard_initial_yard_kwarg_matches_post_open_state` — 11 direct attribute comparisons + identity check.
- `test_open_for_yard_planet_to_fleet_rebuilds_panels` — object identity (`is not`), alive state, panel type change.
- `test_column_config_change_triggers_rebuild` — mutates column_manager, verifies old pool killed.

### 9. LOC ceiling — MAJ (acknowledged)

`build_queue_screen.py`: 822 LOC (was 659 pre-PROJ-376). Growth of 163 lines. The 500 LOC soft target is exceeded by 322 lines. The lifecycle methods (`hide`, `show`, `is_visible`, `open_for_yard`, `_request_close`, `_construct_collaborators`, `_rebuild_panels`, `_validate_params`) are cohesive and belong in this file. `_construct_collaborators` (lines 177-227, ~50 lines) was extracted to avoid duplicating construction logic. No further split is obvious — the remaining methods are each 10-30 lines of lifecycle-specific code. See finding LOC-01.

### 10. Manual smoke + re-profile — DOCUMENTED

Plan.md line 26: "Task 3.1 user-side re-profile deferred". Decisions.md row 20 documents the re-profile requirement. Phase 3 checklist Task 3.1 (lines 33-39) outlines the exact repro steps and acceptance criteria. This is correctly documented as a user-side gate.

### 11. Pre-existing failure — CONFIRMED UNRELATED

One pre-existing sharded failure (`test_pathfinder_attached_after_init` — references `galaxy._intercept` deleted in PROJ-372) is unrelated to PROJ-376. No PROJ-376 changes touch pathfinding or galaxy state.

---

## Findings

### MAJ

#### MAJ: build_queue_screen.py at 822 LOC exceeds 500-line soft target

**ID:** LOC-01
**Location:** `game/ui/screens/build_queue_screen.py` (822 lines)
**Issue:** File grew from 659 to 822 LOC (+163) across PROJ-376. The 500 LOC soft target per `docs/03_CONVENTIONS.md` §2.3 is exceeded by 322 lines.
**Impact:** Reduced navigability for future maintainers. The file has accreted lifecycle methods + the existing screen logic into one module.
**Recommendation:** Acknowledge as acceptable for PROJ-376 — the lifecycle methods are cohesive. Future work should consider extracting the event-handling block (lines 550-746, ~197 lines) or the command-dispatch block (lines 383-509, ~127 lines) into sibling delegates. No action required now.
**Effort:** Medium (future split; deferred)

---

### MIN

#### MIN: `open_for_yard` redundantly rebinds `controller.galaxy`/`controller.empire`

**ID:** LS-01
**Location:** `game/ui/screens/build_queue_screen.py:291-292`
**Issue:** `open_for_yard` writes `self.controller.galaxy = self.galaxy` and `self.controller.empire = self.empire` on every invocation. In `_construct_collaborators` (line 212-213), the controller is already constructed with the correct `galaxy` and `empire`. For same-context-type opens (the common case), these writes are redundant — the controller already holds the same values. For cross-type rebuilds, `_construct_collaborators` sets them correctly.
**Impact:** Negligible — two trivial attribute writes per open. No correctness bug. Code clarity: the writes suggest a contract that doesn't exist (the controller might not hold the right galaxy/empire on reuse).
**Recommendation:** Either remove lines 291-292 and rely on `_construct_collaborators` initial values, or keep as defense-in-depth with a comment noting they're idempotent in the common case. Either is fine.
**Effort:** Trivial

#### MIN: shell-only `BuildQueueScreen.__init__` accepts `hex_coord=None` but `_validate_params` skips validation only when `build_context is None`

**ID:** LS-02
**Location:** `game/ui/screens/build_queue_screen.py:155-157`
**Issue:** When `initial_yard is None` and `build_context is None`, `effective_initial_yard` is None, and `_validate_params` skips `hex_coord` validation. This works correctly today because `initial_yard=None, build_context=None` is the only none-yes path. However, if a caller passes `initial_yard=None, build_context=planet, hex_coord=None`, the code would fail at `open_for_yard` with a confusing TypeError rather than the validation catching it.
**Impact:** Very low — the only shell-only call site (`_open_build_queue` line 95) correctly passes `hex_coord=None` and `build_context=None` together. No production callers combine None build_context with a non-None hex_coord.
**Recommendation:** Optional: add a guard in `_validate_params` that raises if `build_context is None and hex_coord is not None` (inconsistent: context-less hex implies unknown yard state).
**Effort:** Trivial

#### MIN: `_rebuild_panels` reseats controller/renderer/drag_handler but orphaned old instances may hold kill-callback registrations

**ID:** LS-03
**Location:** `game/ui/screens/build_queue_screen.py:237-240`
**Issue:** When `_rebuild_panels` kills the old panel tree and calls `_construct_collaborators`, the new controller/renderer/drag_handler replace the old ones. The old instances are orphaned and GC-eligible. If any pygame_gui internal callback (e.g., kill-completion hook) references the old controller through a lambda/closure, that reference would point to a stale controller. No such registration is visible in the code, but it's a latent risk of the kill-then-reconstruct pattern.
**Impact:** Low — no current callbacks observed; the risk is theoretical. The `manager.update(0)` after kill (line 239) flushes pygame_gui's deferred-kill queue before reconstruction, which should clear any pending callbacks.
**Recommendation:** No action required. Documented for awareness.
**Effort:** None

---

### INFO

#### INFO: `BuildQueueScreen.open_for_yard` sets `self.planet_selection_window = None` unconditionally

**ID:** LS-04
**Location:** `game/ui/screens/build_queue_screen.py:281`
**Issue:** `open_for_yard` sets `self.planet_selection_window = None` at line 281 without checking if one is currently open. If a PlanetSelectionWindow was open (user was mid-selection from a previous yard), it would be orphaned (not killed — its UIPanel tree still lives in the pygame_gui manager) while the slot is cleared. The earlier `hide()` code path (line 329-331) correctly kills the window first. But if `open_for_yard` is called while the screen is still visible (e.g., rapid yard switch without close), the window leaks.
**Impact:** Very low — `open_for_yard` is only called after `hide()` via the manager's close-then-reopen pattern. No production path calls `open_for_yard` while a PlanetSelectionWindow is open.
**Recommendation:** Add `if self.planet_selection_window is not None: self.planet_selection_window.kill()` before clearing the slot, matching hide()'s pattern. Defense-in-depth.
**Effort:** Trivial

#### INFO: Manual smoke and re-profile correctly documented as user-side deferred gate

**ID:** DOC-01
**Location:** `Projects/active_projects/PROJ-376/plan.md:26-27` and `phase_3_checklist.md:8`
**Issue:** Task 3.1 (re-profile) and Task 2.7 (manual smoke) are user-side acceptance gates. Both are correctly documented as deferred/not-blocking the code-side closeout. The re-profile instructions in `phase_3_checklist.md:33-39` are clear and match PROJ-373's original repro.
**Impact:** None — informational confirmation.
**Recommendation:** N/A.
**Effort:** None

---

## Findings by Category

| ID | Severity | Title | Location | Effort |
|----|----------|-------|----------|--------|
| LOC-01 | MAJ | File exceeds 500-line soft target | `build_queue_screen.py` (822 LOC) | Medium (future) |
| LS-01 | MIN | Redundant galaxy/empire rebind in open_for_yard | `build_queue_screen.py:291-292` | Trivial |
| LS-02 | MIN | Missing guard for inconsistent None hex_coord | `build_queue_screen.py:155-157` | Trivial |
| LS-03 | MIN | Orphaned controller on panel rebuild | `build_queue_screen.py:237-240` | None |
| LS-04 | INFO | PlanetSelectionWindow orphan risk on direct open_for_yard | `build_queue_screen.py:281` | Trivial |
| DOC-01 | INFO | Smoke/re-profile documented as user deferred | `plan.md:26-27` | None |

---

## Scope Details

Full scope definition in [scope.md](scope.md).

## Agent Reports

- Direct analysis by reviewer (no sub-agents used; all 11 focus areas verified against source code)
