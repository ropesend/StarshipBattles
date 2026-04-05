# PROJ-240 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| game/simulation/entities/ship.py | Production | Decompose into facade; delegate to new managers; add set_event_bus() |
| game/simulation/entities/ship_component_manager.py | Production | New — component lifecycle delegate (~250 lines) |
| game/simulation/entities/ship_combat_manager.py | Production | New — combat orchestration delegate (~200 lines) |
| docs/01_ARCHITECTURE.md | Production | Update Ship entity architecture if documented |
| docs/02_PATTERNS.md | Production | Add ShipComponentManager/ShipCombatManager to delegate list |
| docs/03_CONVENTIONS.md | Production | Verify naming conventions match new files |
| tests/unit/simulation/entities/test_ship_component_manager.py | Test | New — comprehensive component manager tests |
| tests/unit/simulation/entities/test_ship_combat_manager.py | Test | New — comprehensive combat manager tests |
