# PROJ-470 File Manifest

> Generated from pattern-audit `2026-05-20_075227_pattern-audit`. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| `game/ui/screens/strategy_screen.py` | Production | FAC-003: route `.session` read-path consumers through facade accessors (Phase 2) |
| `game/ui/panels/build_queue_controller.py` | Production | FAC-002: reconcile TYPE_CHECKING strategy imports with read-path policy (Phase 1) |
| `game/ui/screens/build_queue_screen.py` | Production | FAC-002: route `BuildQueueSource`/`collect_build_queues_at_hex` runtime import via facade (Phase 1) |
| `game/ui/screens/fleet_data_source.py` | Production | FAC-002: route `FleetCapabilityCalculator` late-import via facade (Phase 1) |
| `game/ui/screens/strategy_detail_formatter.py` | Production | FAC-003: migrate `.session.registries`/`.turn_engine` reads (Phase 2) |
| `game/ui/screens/strategy_windows/list_windows.py` | Production | FAC-003: migrate `.session.empires` read (Phase 2) |
| `game/ui/screens/hex_outlines.py` | Production | FAC-003: migrate `.session.active_empire.id` read (Phase 2) |
| `game/ui/screens/settings_window.py` | Production | MOD-001: subclass `StrategyModalWindow`, add `window_manager`, drop manual close-callback (Phase 2) |
| `game/ui/screens/strategy_windows/empire_panel_ctrl.py` | Production | MOD-001: update `SettingsRegistrar.open()` to pass `window_manager` (Phase 2) |
| `game/ui/screens/builder/event_bus.py` | Production | EVT-001: fix stale docstring path to `game/core/event_logging.py` (Phase 2) |
| `game/strategy/data/order_types.py` | Production | TG-001: replace `isinstance(Planet/Fleet)` with `is_planet`/`is_fleet` (Phase 3) |
| `game/strategy/facade/dto/fleet_dto.py` | Production | TG-002: replace `isinstance(Planet/Fleet)` arms with TypeGuards (Phase 3) |
| `game/strategy/facade/slices/system_slice.py` | Production | TG-003: replace `isinstance(Storm)` with `is_storm` (Phase 3) |
| `game/strategy/data/build_queue_source.py` | Production | TG-004: replace `isinstance(Fleet)` with `is_fleet` (Phase 3) |
| `game/core/protocols/strategy_entities.py` | Production | ENUM-001: add typed enum for `source_kind` (Phase 3) |
| `game/strategy/services/ability_sources/facility.py` | Production | ENUM-001: adapter returns typed `source_kind` (Phase 3; representative of 7 adapters) |
| `game/simulation/battle_state.py` | Production | LOC-001: top-10 LOC split target (832 LOC) (Phase 3) |
| `game/simulation/battle_controller.py` | Production | LOC-001: top-10 LOC split target (831 LOC) (Phase 3) |
| `game/strategy/engine/turn_engine.py` | Production | LOC-001: top-10 LOC split target (830 LOC) (Phase 3) |
| `game/strategy/engine/production_engine.py` | Production | LOC-001: top-10 LOC split target (830 LOC) (Phase 3) |
| `game/strategy/data/ship_instance.py` | Production | LOC-001: top-10 LOC split target (789 LOC) (Phase 3) |
| `game/simulation/systems/battle_engine.py` | Production | LOC-001: top-10 LOC split target (758 LOC) (Phase 3) |
| `game/ui/screens/event_log_window.py` | Production | LOC-001: top-10 LOC split target (735 LOC) (Phase 3) |
| `game/simulation/battle_runner.py` | Production | LOC-001: top-10 LOC split target (735 LOC) (Phase 3) |
| `game/ui/screens/empire_build_queue_window.py` | Production | LOC-001: top-10 LOC split target (734 LOC) (Phase 3) |
| `game/ui/panels/race_summary_panel.py` | Production | LOC-001: top-10 LOC split target (732 LOC) (Phase 3) |
| `game/strategy/data/habitability_factors.py` | Production | UP-001: source for the HabitabilityFactor Registry doc entry (Phase 4; doc-only — file read, not edited) |
| `game/strategy/services/ability_metadata.py` | Production | UP-002: source for the AbilityMetadataRegistry doc entry (Phase 4; doc-only — file read, not edited) |
| `game/core/roles.py` | Production | UP-006: source for the RoleRegistry doc entry (Phase 4; doc-only — file read, not edited) |
| `game/strategy/data/design_role_registry.py` | Production | UP-006: source for the RoleRegistry doc entry (Phase 4; doc-only — file read, not edited) |
| `tests/static_guards/test_facade_bypass_guard.py` | Test | FAC-001: existing write-path guard mirrored by the new read-path guard (Phase 1; read, not edited) |
| `tests/static_guards/test_facade_read_path_guard.py` | Test | FAC-001/FAC-003: new read-path static guard (Phase 1, extended Phase 2) |
| `docs/02_PATTERNS.md` | Doc | Pattern #5 read-path policy (Phase 1); #10 class name (Phase 2); #32/#36 doc-drift (Phase 3); UP-001/UP-002/UP-006 new entries (Phase 4) |
