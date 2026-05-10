# PROJ-343 File Manifest

> Generated during planning. Used by parallel-execution conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| `game/strategy/engine/handlers/transfer.py` | Production (refactor) | T1.1 — split planet-target vs fleet-target paths; carry `target_fleet_id` into queued `transfer_params` |
| `game/strategy/engine/commands.py` | Production (read-only verify) | T1.1 — confirm `IssueTransferCommand.target_fleet_id` field already exists (it does); no edit expected |
| `game/strategy/data/order_types.py` | Production (possible update) | T1.1 — only if `Order` for TRANSFER needs to learn about `target_fleet_id` (verify executor before deciding) |
| `game/strategy/engine/turn_engine.py` | Production (refactor) | T1.2 — narrow snapshot-capture except; wrap end-of-turn engines in `_time_phase` |
| `game/strategy/engine/environmental_hazard_engine.py` | Production (refactor) | T1.3 — pass `fleet.owner_id` to `collect_sector_effects` instead of `None` |
| `game/strategy/engine/conflict_resolution_engine.py` | Production (refactor) | T1.3 — same fix at lines 508-511 |
| `game/ui/screens/transfer_dialog.py` | Production (refactor) | T1.4 — selective-close on validation-abort returns |
| `game/ui/screens/transfer_controller.py` | Production (refactor) | T1.4 — `confirm_pending` returns `ConfirmResult(orders_issued, aborted_for_correction)` |
| `game/ui/screens/cargo_quick_dialog.py` | Production (refactor) | T1.5 — wrap `_issue_orders` body in `try/finally: self.kill()` |
| `tests/unit/strategy/engine/handlers/test_transfer_handler_fleet_to_fleet.py` | Test (NEW) | Phase 1 — failing API test for T1.1 |
| `tests/unit/strategy/turn_engine/test_turn_snapshot_capture_failure.py` | Test (NEW) | Phase 1 — failing API test for T1.2-snapshot |
| `tests/unit/strategy/turn_engine/test_turn_end_of_turn_engine_rollback.py` | Test (NEW) | Phase 1 — failing API test for T1.2-engines |
| `tests/unit/strategy/engine/test_owned_sector_effects_filter.py` | Test (NEW) | Phase 1 — failing API test for T1.3 |
| `tests/unit/ui/screens/test_transfer_dialog_keeps_open_on_abort.py` | Test (NEW) | Phase 1 — failing API test for T1.4 |
| `tests/unit/ui/screens/test_cargo_quick_dialog_kills_on_dispatch_failure.py` | Test (NEW) | Phase 1 — failing API test for T1.5 |
| `tests/unit/ui/screens/test_transfer_dialog_characterization.py` | Test (rewrite) | Phase 2 — replace lines 418-432 with handler-exercising assertions |
| `tests/unit/strategy/turn_engine/test_turn_engine_end_of_turn_order.py` | Test (rewrite) | Phase 4 — replace lines 168-172 raw-RuntimeError pins with `EnginePhaseError` contract |
| `tests/unit/strategy/turn_engine/test_turn_engine_snapshot_integration.py` | Test (rewrite) | Phase 3 — replace lines 130-160 silent-rollback-skip pins with surfacing contract |
| `tests/unit/ui/screens/test_transfer_dialog*.py` (4 tests with `patch.object(dialog, "kill")`) | Test (update) | Phase 6 — locate via grep; rewrite to assert selective-close behavior |
| `tests/unit/ui/screens/test_cargo_quick_dialog*.py` (no-finally pins) | Test (update) | Phase 7 — locate via grep; rewrite to assert teardown-on-exception |
| `tests/unit/strategy/engine/test_environmental_hazard_engine*.py` (cross-team leak pins) | Test (update) | Phase 5 — locate via grep; rewrite to assert owner-filter |
| `tests/unit/strategy/engine/test_conflict_resolution_engine*.py` (cross-team leak pins) | Test (update) | Phase 5 — locate via grep; rewrite to assert owner-filter |
| `Projects/active_projects/PROJ-328/phase_C_checklist.md` | Doc (update) | Phase 6 — fix Note 3 misdocumentation of always-kill |
| `Projects/active_projects/PROJ-343/plan.md` | Project artifact | Updated as phases progress |
| `Projects/active_projects/PROJ-343/phase_*_checklist.md` | Project artifact | Tasks checked off as completed |
| `Projects/projects_index.md` | Project index | Status update at end of Phase 8 |

## Verification commands

| Phase | Command |
|-------|---------|
| 1 | `pytest tests/unit/strategy/engine/handlers/test_transfer_handler_fleet_to_fleet.py tests/unit/strategy/turn_engine/test_turn_snapshot_capture_failure.py tests/unit/strategy/turn_engine/test_turn_end_of_turn_engine_rollback.py tests/unit/strategy/engine/test_owned_sector_effects_filter.py tests/unit/ui/screens/test_transfer_dialog_keeps_open_on_abort.py tests/unit/ui/screens/test_cargo_quick_dialog_kills_on_dispatch_failure.py -x` (must FAIL, every one, for the right reasons) |
| 2 | `pytest tests/unit/strategy/engine/handlers/ tests/unit/ui/screens/test_transfer_dialog_characterization.py -x` |
| 3 | `pytest tests/unit/strategy/turn_engine/test_turn_engine_snapshot_integration.py tests/unit/strategy/turn_engine/test_turn_snapshot_capture_failure.py -x` |
| 4 | `pytest tests/unit/strategy/turn_engine/ -x` |
| 5 | `pytest tests/unit/strategy/engine/test_environmental_hazard_engine* tests/unit/strategy/engine/test_conflict_resolution_engine* tests/unit/strategy/engine/test_owned_sector_effects_filter.py -x` |
| 6 | `pytest tests/unit/ui/screens/test_transfer_dialog* -x` |
| 7 | `pytest tests/unit/ui/screens/test_cargo_quick_dialog* -x` |
| 8 | `python -m pytest tests/unit/ -q` then `python Tools/lint_test_files.py` then dispatch `claude-delegate-review` for fresh OpenCode pass |

## Baseline reference

Pre-PROJ-343 unit suite: 15,708 pass / 0 fail / 2 skip on `feat/03c-phase-aware-execution` at HEAD `3dc703cb4`.
