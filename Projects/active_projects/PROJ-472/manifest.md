# PROJ-472 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| `game/ui/screens/strategy_screen.py` | Production | FAC-003: route `.session` read-path consumers through facade accessors |
| `game/ui/panels/build_queue_controller.py` | Production | FAC-002: reconcile TYPE_CHECKING strategy imports with read-path policy |
| `game/ui/screens/build_queue_screen.py` | Production | FAC-002: route `BuildQueueSource`/`collect_build_queues_at_hex` runtime import via facade |
| `game/ui/screens/fleet_data_source.py` | Production | FAC-002: route `FleetCapabilityCalculator` late-import via facade |
| `game/ui/screens/strategy_detail_formatter.py` | Production | FAC-003: migrate `.session.registries`/`.session.turn_engine` reads |
| `game/ui/screens/strategy_windows/list_windows.py` | Production | FAC-003: migrate `.session.empires` read |
| `game/ui/screens/hex_outlines.py` | Production | FAC-003: migrate `.session.active_empire.id` read |
| `tests/static_guards/test_facade_bypass_guard.py` | Test | Existing write-path guard; mirrored by the new read-path guard (read, not edited) |
| `tests/static_guards/test_facade_read_path_guard.py` | Test | New read-path static guard |
| `docs/02_PATTERNS.md` | Doc | Pattern #5 read-path policy |
