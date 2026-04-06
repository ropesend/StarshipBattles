# PROJ-240 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| game/simulation/entities/ship.py | Production | Decomposed into facade, ~678 lines (from 850) |
| game/simulation/entities/ship_component_manager.py | Production | New, component lifecycle delegate (~295 lines) |
| game/simulation/entities/ship_combat_manager.py | Production | New, combat orchestration delegate (~179 lines) |
| game/simulation/systems/battle_engine.py | Production | Updated set_event_bus() call |
| tests/unit/simulation/entities/test_ship_component_manager.py | Test | New, 24 tests |
| tests/unit/simulation/entities/test_ship_combat_manager.py | Test | New, 19 tests |
| tests/unit/entities/test_ship.py | Test | Added change_class validation test |
| tests/unit/entities/ship_helpers/test_component_getters.py | Test | Updated defensive copy test |
| docs/01_ARCHITECTURE.md | Docs | Added ShipComponentManager, ShipCombatManager to entities table |
| docs/02_PATTERNS.md | Docs | Updated Facade/Delegate pattern section |
