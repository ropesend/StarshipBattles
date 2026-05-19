---
protocol: consult/v1
from: codex
to: claude
mode: planning
created_at_utc: 2026-05-19T06:52:25.4393090Z
complete: true
exit_status: ok
---

# PROJ-456 audit response

## Findings

### Verdict table
| Finding | Status | Evidence |
|---|---|---|
| F-C-001 | closed | `BattleSetupState` now exposes `sides`/`get_side` at `game/ui/screens/battle_setup_state.py:162-176`; controller/tests read `self._state.get_side(...)` and `state.sides[...]` at `game/ui/screens/battle_setup/controller.py:186-235` and `tests/unit/ui/screens/test_battle_setup_state.py:109-118`. `side_0`/`side_1` hits in the current tree are comments/docstrings, not runtime accesses. |
| F-C-002 | closed | The broad catch is present at current HEAD line `game/ui/screens/transfer_dialog.py:307` (the file is shorter now, so it is no longer at line 412). I also scanned every Python file changed by PROJ-456 (`git diff --name-only 94dcf5108^..0c60b28e0`) for `except Exception` lines missing `# Intentional broad catch:` and found none. |
| F-C-003 | closed | `TransferDialog` now uses canonical surfaces: `TransferViewModel.build_row_data_from_containers(...)`, `self.view_model.pending_transfers`, and `self.view_model.toggle_filter_empty()` at `game/ui/screens/transfer_dialog.py:238-286`. Repo search found no remaining dialog-level `_extract_dropdown_value`, `_format_pending`, or `_discover_pod_designs` shim definitions/callers in the audited test files; formatting behavior is still covered through `dialog.view_model.format_pending(...)` at `tests/unit/ui/screens/test_transfer_dialog_characterization.py:184-205`. |
| F-C-004 | closed | `StrategyRenderer` now composes `BackgroundLayer` and `HexOutlineLayer` at `game/ui/screens/strategy_renderer.py:91-106`; the six retired shim names no longer exist on `StrategyRenderer`. Repo search for `_bg_image`, `_bg_scaled`, `_bg_scaled_size`, `_bg_brightness`, `_hex_outline_cache`, `_hex_outline_cache_turn` now lands only in the layer owners `game/ui/screens/strategy_render/background.py:21-58` and `game/ui/screens/strategy_render/hex_outlines.py:21-80`. |
| F-C-005 | closed | `game/ui/screens/strategy_render/grid.py:24-120` defines `_render_grid_to_surface(...)` plus `GridLayer`; there is no module-level `def draw_grid`. The former test surface now imports and exercises `GridLayer().draw(...)` at `tests/unit/ui/screens/strategy_render/test_grid_and_storms.py:11,53,71`. A repo search for free-function `draw_grid` callers found only unrelated `BattleUI.draw_grid` / `BattleScreen.ui.draw_grid` method calls. |
| F-C-006 | closed | `BuildQueueScreen.__init__` is now keyword-only on `initial_yard` and has no `build_context` parameter: `game/ui/screens/build_queue_screen.py:50-65`. The request-named constructor sites all use kwarg form with no positional-binding hazard: `tests/integration/ui/build_queue_screen/test_basics.py:337-348`, `tests/integration/ui/build_queue_screen/test_portrait_logging.py:132-143`, and `tests/integration/ui/build_queue_screen/test_queue_selector.py:163-172,298-307,356-365,435-444`. Search found no `BuildQueueScreen(... build_context=...)` callsites. |
| F-C-007 | closed | The screen-level shim is gone; current ownership is `RaceSetupController._description_controller` plus `description_controller` at `game/ui/screens/race_setup/controller.py:67-84`. `RaceSetupScreen` reads through `self._controller.description_controller` at `game/ui/screens/race_setup/screen.py:484-497`, and tests do the same at `tests/unit/ui/screens/test_race_setup_screen.py:1192-1202`. I found no remaining `screen._description_controller` access. The original 12-ref count was indeed inflated by controller internals and method names. |
| F-C-008 | closed | Search for `screen.player_count`, `screen.galaxy_type`, `screen.system_count`, `screen.player_races`, `screen.active_race_modal`, and `screen.race_modal_player_index` found only the stale module docstring in `game/ui/screens/new_game_setup_screen.py:34-37`. Canonical reads/writes now go through `_view_model`, e.g. `game/ui/screens/new_game_setup_screen.py:332,352,508,557,583,590` and `tests/unit/ui/screens/test_new_game_setup_extended.py:83-205`. |
| F-C-009 | closed | `FleetBattleSetupScreen` is now a thin shell exposing `state`, `view_model`, and `controller` only at `game/ui/screens/battle_setup/screen.py:43-95`; panels read canonical state through `screen.view_model.*` / `screen.state.*`, e.g. `game/ui/screens/battle_setup/panels/left_panel.py:46,79,86,113,120,133,140`, `game/ui/screens/battle_setup/panels/center_panel.py:28-31`, and `game/ui/screens/battle_setup/panels/right_panel.py:25`. Search for the old `screen.<shim>` access pattern found only stale screen docstring text, not live callers. |
| F-C-010 | closed | `OrdersWindow` owns an `OrderDescriber` at `game/ui/screens/orders_window.py:60-80,326-327`; the old `_get_order_description` shim is absent. Tests/integration now call the canonical describer directly at `tests/unit/ui/screens/test_orders_window.py:67-76` and `tests/integration/ui/test_fleet_build_button.py:224-226`. |
| F-C-011 | closed | `rg -n 'MAX_LOAD|MAX_DROP|ROW_HEIGHT|TARGET_AMT_W' game/ui/screens/transfer_dialog.py` returned no hits, so the sentinel/layout re-exports are gone from the dialog class. Tests now reference the canonical sentinel owner `TransferViewModel.MAX_LOAD/MAX_DROP` at `tests/unit/ui/screens/test_transfer_dialog_characterization.py:200-205,401-418`. |
| F-C-012 | partially-closed | Test-side explicitness improved, but the production optional path remains live. `EventLogWindow.__init__` still accepts `empire_name: Optional[str] = None` and falls back to `"Event Log"` at `game/ui/screens/event_log_window.py:132-179`; `update_events_only` / `open_for_events` still accept optional `empire_name` at `game/ui/screens/event_log_window.py:615-654`; upstream still passes `getattr(empire, "name", None)` at `game/ui/screens/strategy_game_state_manager.py:270-272,294-307`; and a unit test still asserts `empire_name=None` forwarding at `tests/unit/ui/screens/test_event_log_window.py:364-372`. I agree with the phase decision that making it required-str without the upstream audit would be premature, but that means the original fallback-retirement finding is only partially closed. |
| F-C-029 | closed | The old dialog shim-access patterns are gone from live test code; the remaining hits are comments/docstrings. Coverage still exists on the canonical surfaces: confirm dispatch count at `tests/unit/ui/screens/test_transfer_dialog.py:163-172`, fleet-to-fleet passenger unload at `tests/unit/ui/screens/test_transfer_dialog_enhanced.py:73-87`, formatting at `tests/unit/ui/screens/test_transfer_dialog_characterization.py:184-205`, source/target filtering at `tests/unit/ui/screens/test_transfer_dialog_characterization.py:252-267`, and confirm-direction/sentinel translation at `tests/unit/ui/screens/test_transfer_dialog_characterization.py:326-343,381-406`. |
| DI-2026-05-18-002 | closed | Current checkout measurement is 364 lines for `game/ui/screens/transfer_dialog.py` (`(Get-Content ... | Measure-Object -Line).Lines`), which is below both the 500-line ceiling and the request’s expected 418-line post-phase size. Combined with F-C-003/F-C-011/F-C-029 removal evidence above, the natural close is stronger than planned. |

### Side-effects / regressions
- No additional behavioral regression is provable from inspection alone, but `allow_tests=false` meant I could not execute the named UI suites.
- `game/ui/screens/transfer_dialog.py` is 364 lines at the audited HEAD, not 418. That is extra shrinkage, not a reopen signal.

### Out-of-scope observations
- `game/ui/screens/new_game_setup_screen.py:34-37` still says property shims keep `screen.player_count` / `screen.player_races` working, but the live call surface is `_view_model`.
- `game/ui/screens/battle_setup/screen.py:8-9` still says panel builders read `screen.active_side` / `screen.tick_limit`, but panels now use `screen.view_model.*` and `screen.state.*`.
- `game/ui/screens/battle_setup_state.py:151-155` still says `side_0` / `side_1` properties remain, but live callers use `state.sides[...]` / `get_side(...)`.
- `game/ui/screens/strategy_render/grid.py:4-6` still says `draw_grid` is preserved for back-compat, but the module exports `GridLayer` only and tests call `GridLayer().draw(...)`.

### Summary
- Overall: 13 findings are closed by inspection; F-C-012 is partially closed because the optional `empire_name` API and upstream `getattr(..., None)` path are still live.

## Risks

- The only substantive reopen candidate is F-C-012. If the project wants that finding to be fully closed rather than intentionally narrowed, the follow-up scope must include `StrategyGameStateManager`/event-log caller auditing, not just `EventLogWindow`.
- I did not run tests because the consult request explicitly set `allow_tests: false`. The most relevant suites to run later are `tests/integration/ui/build_queue_screen/*`, `tests/unit/ui/screens/test_transfer_dialog*.py`, `tests/unit/ui/screens/strategy_render/test_grid_and_storms.py`, `tests/unit/ui/screens/test_strategy_renderer.py`, and `tests/unit/ui/screens/test_event_log_window.py`.

## Open questions

None.
