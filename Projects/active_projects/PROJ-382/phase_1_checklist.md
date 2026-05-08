# Phase 1: Critical — Facade bypass eradication (Pattern #5)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-382 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Eliminate the 4 verified Pattern #5 facade-bypass dispatch sites in `build_queue_screen.py` + `empire_build_queue_window.py` AND the public `self.session` propagation chain in `StrategyScreen` that enables them. Install an AST static-guard so the bypass cannot silently re-grow.

---

## Tasks

### Task 1.1: Remove session-fallback dispatch in `build_queue_screen.py`
**File:** `game/ui/screens/build_queue_screen.py`
**Pattern:** #5 (Facade / Delegate)
**Tests:** `pytest tests/ -k build_queue --testmon`

- [ ] Remove `self.session = session` at line 88; keep only `self.facade = facade`.
- [ ] Make `facade` constructor argument required (drop `Optional` / default).
- [ ] Replace `if self.facade: self.facade.handle_command(cmd) else: self.session.handle_command(cmd)` at lines 425-429 with unconditional `self.facade.handle_command(cmd)`.
- [ ] Replace the same fallback at lines 462-466 (remove command path) with unconditional facade dispatch.
- [ ] Replace the same fallback at lines 498-501 (toggle-pause path) with unconditional facade dispatch.
- [ ] Reroute `registries=self.session.registries` at line 507 — facade does not expose registries; route via the existing `galaxy` reference or pull through a new facade DTO method (decide in Phase 1 design discussion before editing).
- [ ] Verify: existing build-queue tests still pass; manual build-queue smoke (open screen, queue/remove/pause/unpause) functional.

### Task 1.2: Remove session-fallback dispatch in `empire_build_queue_window.py`
**File:** `game/ui/screens/empire_build_queue_window.py`
**Pattern:** #5 (Facade / Delegate)
**Tests:** `pytest tests/ -k empire_build_queue --testmon`

- [ ] Remove `self._session = session` at line 179; keep only `self._facade = facade`.
- [ ] Make `facade` constructor argument required (drop `None` default).
- [ ] Replace `if facade: facade.handle_command(cmd) else: session.handle_command(cmd)` at lines 422-426 with unconditional `facade.handle_command(cmd)`.
- [ ] Verify: existing empire-build-queue tests still pass; manual smoke (open window, queue/remove items) functional.

### Task 1.3: Privatize `self.session` on `StrategyScreen`; remove session= from child constructors
**File:** `game/ui/screens/strategy_screen.py`
**Pattern:** #5 (Facade / Delegate)
**Tests:** `pytest tests/ -k strategy_screen --testmon`

- [ ] Rename `self.session` → `self._session` at line 83 (private). Keep direct `GameSession` construction at line 81-82 — that is the legitimate composition-root action.
- [ ] Audit the public properties at lines 155-182 (`galaxy`, `empires`, `systems`, `active_empire`, `enemy_empire`, `human_player_ids`) — for each: leave it as a delegate to `self._session` if no facade DTO exists yet, or route through `self._facade` where the facade already exposes a DTO equivalent. Document any surviving direct `_session` reads with a `# Phase-1 audit: facade DTO not yet available — see PROJ-382 Phase 1 task 1.3` comment so the residue is visible.
- [ ] Audit every external read of `c.scene.session` / `screen.session` across the codebase. Each site either (a) needs to switch to `c.scene.facade` / `screen.facade`, or (b) is a legitimate intra-screen consumer that should be moved before privatization is enforced.

### Task 1.4: Stop passing `session=` to `BuildQueueScreen` and `EmpireBuildQueueWindow`
**File:** `game/ui/screens/strategy_build_queue_manager.py`, `game/ui/screens/strategy_windows/build_queue_windows.py`
**Pattern:** #5 (Facade / Delegate)
**Tests:** `pytest tests/ -k "build_queue or empire_build_queue" --testmon`

- [ ] In `strategy_build_queue_manager.py:98`: remove the `session=self._screen.session` kwarg from the `BuildQueueScreen(...)` call. Pass only `facade=self._screen.facade`.
- [ ] In `strategy_windows/build_queue_windows.py:73-74`: remove the `session=c.scene.session` kwarg from the `EmpireBuildQueueWindow(...)` call. Pass only `facade=c.scene.facade`.
- [ ] Verify: both child screens construct correctly; both render and accept input end-to-end.

### Task 1.5: AST static-guard test against re-introduced facade bypass
**File:** `tests/static_guards/test_facade_bypass_guard.py` (new)
**Pattern:** #5 (Facade / Delegate)
**Tests:** `pytest tests/static_guards/test_facade_bypass_guard.py`

- [ ] Author an AST scanner test that walks `game/ui/` and fails if it finds any `<expr>.session.handle_command(<args>)` calls — UI code may only call `<expr>.facade.handle_command(...)`.
- [ ] The test should also fail on construction calls passing `session=` to `BuildQueueScreen` or `EmpireBuildQueueWindow` from outside the existing composition root in `strategy_screen.py`.
- [ ] Use PROJ-306's `get_default_registry_provider` AST static-guard test as the canonical reference pattern to copy.
- [ ] Verify: test passes after Tasks 1.1-1.4; deliberately re-introduce a bypass call locally to confirm the test fails, then revert.

### Task 1.6: Phase verification
**File:** N/A
**Pattern:** #5
**Tests:** Full suite

- [ ] `pytest tests/ --testmon` passes.
- [ ] `python Tools/test_sharded/test_sharded.py` baseline matches the 15405-passing baseline (or higher).
- [ ] Re-run `Tools/pattern_audit/pattern_audit.py` (if present) — confirm Pattern #5 facade-bypass count for `build_queue_screen.py` + `empire_build_queue_window.py` drops from 4 sites to 0.
- [ ] No new bypass sites re-introduced in any UI file.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-07_220452_pattern-audit/`. See `findings/source_audit.md` for the link._
