# Phase 1: CRITICAL — static-guard blind spot + GameSession.from_dict mutators

**Status:** Complete
**Objective:** Close the 2 CRITICAL findings from the PROJ-382 OpenCode review.

---

## Tasks

### Task 1.1: Extend AST static-guard for `_session.handle_command(...)`
**File:** `tests/static_guards/test_facade_bypass_guard.py:58-68`
**Tests:** `pytest tests/static_guards/test_facade_bypass_guard.py -v`

- [x] Modify `_is_session_handle_command` (or equivalent function) to match BOTH `"session"` AND `"_session"` as the attribute name.
- [x] Add a positive-control test that intentionally introduces `screen._session.handle_command(...)` somewhere in test fixtures and confirms the guard fires.
- [x] Add a targeted check in the guard that specifically scans `game/ui/screens/strategy_screen.py` for any `self._session.handle_command(...)` call (defense in depth — the property setter still exists for test mocks).
- [x] Verify: focused test passes; guard fires on `_session` form.

### Task 1.2: Restore mutator services in `GameSession.from_dict()`
**File:** `game/strategy/engine/game_session.py:475-490`
**Tests:** `pytest tests/unit/strategy/test_game_session.py -k "from_dict" -v`

- [x] Read `__init__` lines 104-123 to get the canonical mutator-construction pattern.
- [x] In `from_dict()`, add the same mutator construction (`fleet_mutator`, `planet_mutator`, `empire_mutator`, `ship_mutator`) and pass them to `TurnEngineConfig.create_default()`.
- [x] Add a regression test: deserialize a session, call a command handler that uses `session.fleet_mutator.set_path(...)` (e.g., `add_move_order_if_needed`), confirm no `AttributeError`.
- [x] Verify: focused test passes; round-trip session-serialize-then-execute works.

### Task 1.3: Final regression
**Tests:** `pytest tests/ -k "game_session or static_guards or facade_bypass" --testmon`

- [x] Run focused regression — all relevant test paths pass

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2

_Source review: `Reviews/results/2026-05-08_235750_code_proj-382-pattern-conformance-facade-integrity-even_req-req_20260508_235748_8c0ea0/`_
