# PROJ-492 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Canonical helpers (read-only references)

| File | Type | Notes |
|------|------|-------|
| tests/fixtures/colonization_fixtures.py | Test fixture | Canonical MockPlanetType (HLP-002 target) |
| tests/conftest.py | Test fixture | Canonical _make_mock_fleet (HLP-004 target) |
| tests/unit/strategy/save_game_service/conftest.py | Test fixture | Canonical setup_tmpdir at line 48 (Paths.SAVES_DIR variant — HLP-005 target) |
| game/strategy/systems/save_game_service.py | Production READ | Reference for HLP-005 contract decision |
| game/core/paths.py | Production READ | Reference for HLP-005 contract decision |

## Phase 1 — HLP-002 nested MockPlanetType consumers

Files identified via `grep -rln "class MockPlanetType" tests/` (8 files):

| File | Type | Notes |
|------|------|-------|
| tests/integration/ui/test_colonization_facade.py | Test | 9 nested copies (lines 71, 380, 441, 494, 583, 642, 697, 751, 819) — primary target |
| tests/integration/strategy/test_commands.py | Test | Verify and migrate |
| tests/integration/strategy/turn_engine/conftest.py | Test fixture | **OUT-OF-FAMILY** per audit Finding 9: this file defines `class MockPlanetType:` with a `name` attribute (plain class, line 125-128), NOT an `Enum`. Cannot mechanically migrate to canonical Enum. Skip in mechanical lane; triage separately in Phase 1 Task 1.10 (see phase_1_checklist.md). |
| tests/unit/strategy/test_engine_event_emission.py | Test | Verify and migrate |
| tests/unit/strategy/test_fleet_order_processor.py | Test | Verify and migrate |
| tests/unit/strategy/turn_engine/conftest.py | Test fixture | Verify and migrate |
| tests/unit/strategy/validation/test_colonize_validator.py | Test | Verify and migrate |
| tests/unit/ui/screens/test_strategy_colonization.py | Test | Verify and migrate |

Site count: ~21 non-canonical `class MockPlanetType` occurrences across 8 files (per audit Finding 9; earlier "~40 sites" estimate in plan was wrong).

## Phase 2 — HLP-004 _make_fleet consumers (exact-name match)

Files identified via `grep -rl "def _make_fleet\b\|def make_fleet\b\|def _make_mock_fleet\b" tests/` (37 consumer files, excluding canonical `tests/conftest.py`). Helpers with sibling names like `_make_fleet_pair`, `_make_fleet_at`, `_make_fleet_with_ship`, `_make_fleet_mock`, `_make_fleet_controller_with_galaxy` are EXCLUDED — they're different families (per audit Finding 3).

| File | Type | Notes |
|------|------|-------|
| tests/integration/strategy/test_fleet_registration_lifecycle.py | Test | Verify, migrate |
| tests/integration/strategy/test_replay_capture_e2e.py | Test | Verify, migrate |
| tests/integration/strategy/test_three_empire_battle.py | Test | Verify, migrate |
| tests/unit/strategy/adapters/test_simulation_adapter.py | Test | Verify, migrate |
| tests/unit/strategy/adapters/test_simulation_adapter_registry_threading.py | Test | Verify, migrate |
| tests/unit/strategy/combat/test_battle_assembly.py | Test | Verify, migrate |
| tests/unit/strategy/combat/test_battle_assembly_third_party_mines.py | Test | Verify, migrate |
| tests/unit/strategy/data/test_construction_queue_paused_persistence.py | Test | Verify, migrate |
| tests/unit/strategy/data/test_fleet_cargo_resources.py | Test | Verify, migrate |
| tests/unit/strategy/data/test_order_serializer.py | Test | Verify, migrate |
| tests/unit/strategy/engine/handlers/test_movement_handlers.py | Test | Verify, migrate |
| tests/unit/strategy/engine/handlers/test_order_queue_handlers.py | Test | Verify, migrate |
| tests/unit/strategy/engine/order_handlers/conftest.py | Test fixture | Triage, migrate |
| tests/unit/strategy/engine/test_action_execution_engine.py | Test | Verify, migrate (overlap with PROJ-491 Phase 3) |
| tests/unit/strategy/engine/test_action_execution_engine_gaps.py | Test | Verify, migrate |
| tests/unit/strategy/engine/test_conflict_round_budget.py | Test | Verify, migrate |
| tests/unit/strategy/engine/test_environmental_hazard_engine.py | Test | Verify, migrate |
| tests/unit/strategy/engine/test_fleet_transfer_extended.py | Test | Verify, migrate |
| tests/unit/strategy/engine/test_issuer_adapter.py | Test | Verify, migrate |
| tests/unit/strategy/engine/test_multi_pod_colonization.py | Test | Verify, migrate |
| tests/unit/strategy/engine/test_pod_transfer.py | Test | Verify, migrate |
| tests/unit/strategy/engine/test_resupply_engine.py | Test | Verify, migrate |
| tests/unit/strategy/engine/test_staging_yard_operations.py | Test | Verify, migrate |
| tests/unit/strategy/engine/test_superweapon_event_payloads.py | Test | Verify, migrate |
| tests/unit/strategy/engine/test_superweapon_order_pop_matrix.py | Test | Verify, migrate |
| tests/unit/strategy/engine/test_transfer_handler_fleet_to_fleet.py | Test | Verify, migrate (overlap with PROJ-491 Task 1.18) |
| tests/unit/strategy/facade/test_strategy_session_facade.py | Test | Verify, migrate |
| tests/unit/strategy/fleet/test_fleet_pursuer_tracker.py | Test | Verify, migrate |
| tests/unit/strategy/fleet_navigation/test_service_edge_cases.py | Test | Verify, migrate |
| tests/unit/strategy/services/test_fleet_cargo_projector.py | Test | Verify, migrate |
| tests/unit/strategy/services/test_fleet_navigation_mutual_pursuit.py | Test | Verify, migrate |
| tests/unit/strategy/test_fleet_speed_calculator.py | Test | Verify, migrate |
| tests/unit/strategy/validation/test_transfer_drop_pod.py | Test | Verify, migrate (also touched by PROJ-491 Task 1.19 for unrelated CAT-6 work) |
| tests/unit/ui/screens/battle_setup/test_fleet_hierarchy_editor.py | Test | Verify, migrate |
| tests/unit/ui/screens/test_build_queue_screen_lifecycle.py | Test | Verify, migrate |
| tests/unit/ui/screens/test_fleet_detail_fmt.py | Test | Verify, migrate |
| tests/unit/ui/screens/test_fleet_menu_items.py | Test | Verify, migrate |

### Excluded from Phase 2 (sibling helpers, different families)

Per audit Finding 3, these files match the broad pattern `_make_fleet.*` but their helpers are NOT `_make_fleet` / `make_fleet` / `_make_mock_fleet`:

| File | Local helper name | Reason excluded |
|------|-------------------|-----------------|
| tests/integration/strategy/test_economy_e2e.py | `_make_fleet_with_ship` | Builds fleet+ship pair — different shape |
| tests/unit/strategy/engine/test_conflict_resolution_event_replay.py | `_make_fleet_pair` | Builds pair of fleets — different shape |
| tests/unit/strategy/engine/test_minefield_resolver.py | `_make_fleet_at` | Builds fleet at specific location — different shape |
| tests/unit/strategy/engine/test_production_normalisation.py | (other variant — verify) | Audit-flagged adjacent; verify and re-include if exact match |
| tests/unit/strategy/engine/test_transfer_order.py | (other variant — verify) | Audit-flagged adjacent; verify and re-include if exact match |
| tests/unit/strategy/data/test_build_queue_source.py | (other variant — verify) | Audit-flagged adjacent; verify and re-include if exact match |
| tests/unit/strategy/data/test_fleet_consume_cargo_symmetry.py | (other variant — verify) | Audit-flagged adjacent; verify and re-include if exact match |
| tests/unit/strategy/production_engine/test_paused_queue.py | (other variant — verify) | Audit-flagged adjacent; verify and re-include if exact match |
| tests/unit/ui/panels/test_build_queue_controller.py | `_make_fleet_controller_with_galaxy` | Builds controller + galaxy — different shape |
| tests/unit/ui/screens/test_fleet_report_window.py | `_make_fleet_mock` | Builds mock fleet specifically for the report window — verify |
| tests/unit/ui/screens/test_strategy_screen.py | (other variant — verify) | Audit-flagged adjacent; verify and re-include if exact match |
| tests/fixtures/strategy_screen_composition.py | (variant — verify) | Audit-flagged adjacent; verify and re-include if exact match |

## Phase 3 — HLP-005 setup_tmpdir

| File | Type | Notes |
|------|------|-------|
| tests/unit/strategy/save_game_service/conftest.py | Test fixture | Canonical (line 48) — Paths.SAVES_DIR variant |
| tests/unit/strategy/test_auto_save.py | Test | chdir-based variant to rewrite (lines 26-33) |
| tests/unit/ui/test_save_selection.py | Test | Already follows production-like contract (lines 21-33) — reference for migration |
