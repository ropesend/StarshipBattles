# PROJ-265 File Manifest

> Generated during planning. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| `game/simulation/components/component_loader.py` | Production | NO CHANGES -- test target only (Phase 1) |
| `game/simulation/combat/damage_calculator.py` | Production | NO CHANGES -- test target only (Phase 2) |
| `game/simulation/combat/fleet_aura_manager.py` | Production | NO CHANGES -- test target only (Phase 3) |
| `game/simulation/combat/combat_events.py` | Production | NO CHANGES -- supporting types for Phase 2 |
| `game/core/combat_types.py` | Production | NO CHANGES -- DamageContext for Phase 2 |
| `tests/unit/simulation/components/test_component_loader.py` | Test | NEW -- Phase 1: component_loader error paths, cache, factory guards |
| `tests/unit/simulation/combat/test_damage_calculator_events.py` | Test | NEW -- Phase 2: all event emission paths in apply_damage() |
| `tests/unit/simulation/combat/test_fleet_aura_extended.py` | Test | NEW -- Phase 3: get_active_bonuses, external modifiers, operational checks, fingerprint |

## Conflict Notes

This project creates 3 new test files and modifies NO existing files. Conflict risk is minimal.

Existing test files in the same directories (not modified by this project):
- `tests/unit/simulation/combat/test_damage_calculator.py` -- existing DC tests (no event_bus coverage)
- `tests/unit/simulation/combat/test_fleet_aura_cache.py` -- existing FA cache tests
- `tests/unit/simulation/combat/test_fleet_aura_register.py` -- existing FA register tests
