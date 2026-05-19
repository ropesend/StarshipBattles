# PROJ-456 File Manifest

> Generated during charter creation 2026-05-19 from Codex r4 audit redesign (job 8) + bucket_c findings re-verified against repo HEAD.
> Updated during implementation as additional caller sites are discovered.

## Files

### Phase 1 — Smallest-shim cluster (5 independent fixes)

#### F-C-002 — broad-catch marker

| File | Type | Notes |
|------|------|-------|
| `game/ui/screens/transfer_dialog.py` | Production | Add `# Intentional broad catch: <reason>` marker on line 412 (or immediately above) describing the catastrophic-dispatch rationale. |

#### F-C-005 — `draw_grid` free function retirement

| File | Type | Notes |
|------|------|-------|
| `game/ui/screens/strategy_render/grid.py` | Production | Delete module-level `draw_grid(r, screen)` at lines 104-110. |
| `tests/unit/ui/screens/test_strategy_renderer.py` | Test | Migrate from `draw_grid(r, screen)` to `GridLayer().draw(...)`. |
| `tests/unit/ui/screens/strategy_render/test_grid_and_storms.py` | Test | Same migration. |

#### F-C-007 — `RaceSetupScreen._description_controller` shim retirement

| File | Type | Notes |
|------|------|-------|
| `game/ui/screens/race_setup/screen.py` | Production | Delete property + setter at lines 277-285. |
| `tests/unit/ui/screens/test_race_setup_screen.py` | Test | Migrate `_description_controller` callers (1 ref) to `screen._controller.description_controller`. |
| `tests/unit/ui/screens/race_setup/test_controller.py` | Test | Migrate (4 refs). |
| `tests/unit/ui/screens/race_setup/test_panel_factory.py` | Test | Migrate (7 refs). |

#### F-C-010 — `OrdersWindow._get_order_description` shim retirement

| File | Type | Notes |
|------|------|-------|
| `game/ui/screens/orders_window.py` | Production | Delete shim method at lines 464-475. |
| `tests/unit/ui/screens/test_orders_window.py` | Test | Migrate to instantiating `OrderDescriber()` and calling `.describe(order, entity)` directly. |
| `tests/unit/ui/screens/test_fleet_orders_refresh.py` | Test | Same migration. |
| `tests/integration/ui/test_fleet_build_button.py` | Test | Same migration. |

#### F-C-012 — `EventLogWindow.empire_name=None` fallback retirement

| File | Type | Notes |
|------|------|-------|
| `game/ui/screens/event_log_window.py` | Production | Audit lines 113-116 and the title-rendering branch; either remove the `None` fallback (recommended) or change the parameter to required. |
| `tests/unit/ui/screens/test_strategy_modal_hidden_input.py` | Test | Audit `EventLogWindow(...)` construction; supply explicit `empire_name`. |
| `tests/unit/ui/screens/test_event_log_no_copy.py` | Test | Same. |
| `tests/unit/ui/screens/test_event_log_replay_button.py` | Test | Same. |
| `tests/unit/ui/screens/test_event_log_row_pool_visibility.py` | Test | Same. |
| `tests/unit/ui/screens/test_event_log_window_reuse.py` | Test | Same. |
| `tests/performance/test_panel_full_open_benchmark.py` | Test | Same (perf test). |
| `tests/integration/ui/test_event_log_replay_e2e.py` | Test | Same. |
| `tests/integration/replay/test_event_log_graceful_degradation.py` | Test | Same. |

### Phase 2 — `BuildQueueScreen` `build_context` legacy-kwarg sweep

> **Scope:** `BuildQueueScreen` constructor only. `BuildQueueController(build_context=...)` callers are OUT OF SCOPE (the controller API legitimately accepts `build_context=`; see `game/ui/panels/build_queue_controller.py:66-85`).

| File | Type | Notes |
|------|------|-------|
| `game/ui/screens/build_queue_screen.py` | Production | Remove `build_context` parameter from `__init__` signature; drop the `effective_initial_yard = initial_yard if initial_yard is not None else build_context` resolution at line 90; update docstring at lines 84-90. |
| `game/ui/screens/strategy_build_queue_manager.py` | Production | Migrate the `BuildQueueScreen(..., build_context=None, ...)` caller at line 128 to `initial_yard=`. |
| `tests/unit/ui/screens/test_build_queue_screen_lifecycle.py` | Test | Sweep ~25 `BuildQueueScreen(..., build_context=...)` sites to `initial_yard=`. |

**Out of scope (do NOT touch in Phase 2 — controller API is legitimate):**

| File | Reason |
|------|--------|
| `tests/unit/ui/panels/test_build_queue_controller.py:57-87` | Calls `BuildQueueController(build_context=...)` (controller API). |
| `tests/unit/ui/panels/test_build_queue_catalog_threading.py:20-30` | Same. |
| `tests/unit/strategy/engine/test_production_repro.py:150-157,201-206` | Same. |
| `tests/integration/ui/build_queue_screen/test_controller_multi_queue.py:77-116` | Same. |

### Phase 3 — BattleSetupState `side_0` / `side_1` cluster

| File | Type | Notes |
|------|------|-------|
| `game/ui/screens/battle_setup_state.py` | Production | Delete property/setter pair at lines 172-192 (and the comment block at 172-176). |
| `game/ui/screens/battle_setup/controller.py` | Production | Migrate `state.side_0` / `state.side_1` reads to `state.sides[0]` / `state.sides[1]` (or `state.get_side(team_id)` where the team-id index is the natural read). |
| `tests/unit/ui/screens/test_battle_setup_state.py` | Test | 13 refs migrate to `state.sides[i]` (re-counted 2026-05-19; was 12). |
| `tests/unit/ui/screens/battle_setup/test_controller.py` | Test | 37 refs migrate. |
| `tests/unit/ui/screens/battle_setup/test_spec_compiler.py` | Test | 22 refs migrate (re-counted 2026-05-19; was 19). |
| `tests/unit/ui/screens/battle_setup/test_spec_compiler_formation.py` | Test | 5 refs migrate. |
| `tests/integration/strategy/combat/test_suppressor_effects.py` | Test | 4 refs migrate. |

### Phase 4 — transfer_dialog cluster + characterization sweep

#### F-C-003 — Three method shims

| File | Type | Notes |
|------|------|-------|
| `game/ui/screens/transfer_dialog.py` | Production | Delete `_extract_dropdown_value` / `_format_pending` / `_discover_pod_designs` at lines 279-286. |
| `tests/unit/ui/screens/test_transfer_dialog_characterization.py` | Test | Migrate 2-3 sites to call `TransferGridRenderer.extract_dropdown_value`, `dialog.view_model.format_pending`, `dialog._controller.discover_pod_designs` directly. |

#### F-C-011 — Sentinel + layout-constant class re-exports

| File | Type | Notes |
|------|------|-------|
| `game/ui/screens/transfer_dialog.py` | Production | Delete sentinel re-exports (`MAX_LOAD`, `MAX_DROP`) + 18 layout-constant re-exports at lines 58-86. |
| `game/ui/screens/transfer_grid_renderer.py` | Production | Confirm `ROW_HEIGHT` / `NAME_X` / `NAME_W` / `SOURCE_AMT_X` / etc. live here (canonical home). |
| `game/ui/screens/transfer_view_model.py` | Production | Confirm `MAX_LOAD` / `MAX_DROP` live here (canonical home). |
| (any importer of the dialog-class constants) | Test/Production | Audit (PowerShell-safe) `rg -n "TransferDialog\.(MAX_LOAD\|MAX_DROP\|ROW_HEIGHT\|NAME_X\|NAME_W\|SOURCE_AMT_X\|MAX_LOAD_X\|LOAD_ARROWS_X\|PENDING_X\|ZERO_BTN_X\|DROP_ARROWS_X\|MAX_DROP_X\|TARGET_AMT_X)"`; migrate to canonical-home class. |

#### F-C-029 — 69-ref characterization-test sweep

| File | Type | Notes |
|------|------|-------|
| `tests/unit/ui/screens/test_transfer_dialog_characterization.py` | Test | 61 refs. Sweep `dialog._current_source` → `dialog.view_model.current_source`, etc. |
| `tests/unit/ui/screens/test_transfer_dialog.py` | Test | 5 refs. Same sweep. |
| `tests/unit/ui/screens/test_transfer_dialog_enhanced.py` | Test | 3 refs. Same sweep. |
| `game/ui/screens/transfer_dialog.py` | Production | After the test sweep, delete the 6 dialog-level property shims (find via `rg -n "Back-compat property shims" game/ui/screens/transfer_dialog.py`). |

#### DI-2026-05-18-002 natural close

| File | Type | Notes |
|------|------|-------|
| `AgentCoordination/discovered_issues/log.jsonl` | Data | After F-C-003 + F-C-011 + F-C-029, run (PowerShell-safe) `(Get-Content game/ui/screens/transfer_dialog.py | Measure-Object -Line).Lines`. If under 500: append a `resolution_note` to DI-2026-05-18-002 (`status: resolved`). |

### Phase 5 — Big-three shim clusters

#### F-C-004 — StrategyRenderer 6 cache-attr shims

| File | Type | Notes |
|------|------|-------|
| `game/ui/screens/strategy_renderer.py` | Production | Delete property block at lines 107-130. No test reads of these names (verified 2026-05-19). |

#### F-C-008 — NewGameSetupScreen 6 VM property shims

| File | Type | Notes |
|------|------|-------|
| `game/ui/screens/new_game_setup_screen.py` | Production | Delete property block at lines 272-321 (and the 1 self-reference). |
| `tests/unit/ui/test_new_game_setup.py` | Test | 1 ref migrates. |
| `tests/unit/ui/screens/test_new_game_setup_extended.py` | Test | 29 refs migrate. |
| `tests/fixtures/new_game_setup_ui_builder.py` | Fixture | 4 refs migrate. |

#### F-C-009 — BattleSetupScreen 11 VM + controller property shims

| File | Type | Notes |
|------|------|-------|
| `game/ui/screens/battle_setup/screen.py` | Production | Delete property block at lines 93-205. |
| `game/ui/screens/battle_setup/panels/left_panel.py` | Production | 11 refs migrate `screen.<name>` → `screen.view_model.<name>` / `screen.controller.<name>`. |
| `game/ui/screens/battle_setup/panels/center_panel.py` | Production | 14 refs migrate. |
| `game/ui/screens/battle_setup/panels/right_panel.py` | Production | 1 ref migrates. |
| `tests/unit/ui/screens/test_battle_setup_state.py` | Test | 7 refs migrate. |

### Findings file updates (each phase)

| File | Type | Notes |
|------|------|-------|
| `Projects/active_projects/PROJ-456/findings/PROJ-456_findings.md` | Project | After each phase, flip the corresponding finding entries to `Status: resolved` with a one-line note (e.g. `Closed 2026-05-XX Phase N — property block deleted; N callers migrated`). |

### Decisions log updates

| File | Type | Notes |
|------|------|-------|
| `Projects/active_projects/PROJ-456/decisions.md` | Project | Record any deviation from the phase plan as it arises (e.g. additional caller files surfaced during a sweep; deferral of a sub-task; LOC-budget discoveries). |

### Plan + checklist updates

| File | Type | Notes |
|------|------|-------|
| `Projects/active_projects/PROJ-456/plan.md` | Project | Update Quick Status table + Current State after each phase. |
| `Projects/active_projects/PROJ-456/phase_<N>_checklist.md` | Project | Check off subtasks as the work progresses; final Phase Completion Checklist closed at phase end. |
| `Projects/projects_index.md` | Project | Update PROJ-456 row to `Complete` after Phase 5 lands (per `phase_5_checklist.md:101-103`). |
