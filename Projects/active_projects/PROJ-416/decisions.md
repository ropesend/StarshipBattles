# PROJ-416: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-13 | Project initialized | Starting point for Legacy removal — race_setup_screen.py shim + Game.running (PROJ-309 vestige) (2026-05-13) |
| 2026-05-13 | Bundled findings from `2026-05-13_194106_legacy-audit` by removal cluster `proj309_vestige` per user direction | Bundling driven by removal cluster (one project per system being eradicated) rather than severity to maximize deletion-PR coherence; full bundling discussion in findings/bundling_decisions.md |
| 2026-05-14 | Codex consult confirmed: shard 04 claim that `game/app.py` imports from the shim is false | `app.py` has zero matches for `race_setup_screen`; the shim docstring's `game/app.py:522` reference is stale (import moved to `screen_router.py` in a prior refactor). No plan change required for caller count — production callers are `screen_router.py` and `new_game_setup_controller.py`. |
| 2026-05-14 | Codex consult: `test_race_setup_screen_public_api.py` must be DELETED not migrated | The file is a shim contract test (3 tests that assert the shim still works). Migrating it to canonical imports would produce redundant smoke tests with no behavior coverage. Delete with the shim. |
| 2026-05-14 | Codex consult: Phase 2 scope is materially larger than the plan stated | `Game.running` has 3 production write/read sites beyond `__init__`: `_request_shutdown` (line 266 writes `self.running = False`), `_handle_strategy_action("quit_game")` (line 452 writes `self.running = False`), and `run()` (lines 502-507 bridges `self.running` ↔ `_loop.running`). All must be removed/migrated; plan and checklist updated accordingly. |
| 2026-05-14 | Codex consult: do NOT introduce `Game.is_running()` for test migration | The canonical state owner is `RunLoop.running` with an existing `request_shutdown()` method. Tests should be rewritten to assert behavior (shutdown delegation) rather than read `game.running`. Adding a new public method solely to satisfy tests is the wrong trade-off. |
| 2026-05-14 | Codex consult: `sys.modules` injection in `test_screen_router.py:283-287` is in scope for Phase 1 | Even though it uses `sys.modules` not `mock.patch`, it targets the shim module path and must be updated to `game.ui.screens.race_setup.screen` when the shim is deleted. |
| 2026-05-14 | Codex consult: docs cleanup required alongside Phase 1 | `docs/02_PATTERNS.md` lists `race_setup_screen.py` as a current re-export shim. Must be updated when the file is deleted per conventions (`docs/03_CONVENTIONS.md:392-394`). Stale source docstrings in `race_setup/__init__.py` and `race_setup/screen.py` also need updating. |
