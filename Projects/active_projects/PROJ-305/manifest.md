# PROJ-305 File Manifest

| File | Type | Notes |
|------|------|-------|
| `game/simulation/components/abilities/<various>.py` | Production | Expand `allowed_scopes` per Phase 1 audit (e.g. `defense.py`, `sensor.py` if it exists). |
| `data/components.json` | Data | Add Flagship Sensor Array (or similar) component using new strategic scope. |
| `data/designs/qs_battleship.json` (or appropriate) | Data | Mount the new flagship component on an existing or new test design. |
| `game/strategy/services/ability_sources/fleet.py` | Production | NEW. `FleetAbilitySource` adapter. |
| `game/strategy/services/ability_sources/__init__.py` | Production | Re-export `FleetAbilitySource`. |
| `game/strategy/services/ability_iterator.py` | Production | Register `_fleet_provider`. May require API change to plumb `registries`. |
| `game/strategy/services/system_effects_collector.py` | Production | If profiling demands: add per-turn cache; export `_STRATEGIC_SCOPES` constant for `FleetAbilitySource`. |
| `game/strategy/engine/turn_engine.py` | Production | If caching added: invalidate at turn start. |
| `tests/unit/simulation/components/abilities/` (multiple files) | Test | Validate expanded scope acceptance. |
| `tests/unit/strategy/services/ability_sources/test_fleet.py` | Test | NEW. `FleetAbilitySource` cases. |
| `tests/unit/strategy/services/test_ability_iterator.py` | Test | Add fleet provider cases. |
| `tests/integration/strategy/test_fleet_sector_effects_owner_filtering.py` | Test | NEW. Allied/enemy scope filtering. |
| `tests/integration/strategy/test_fleet_sector_effects_end_to_end.py` | Test | NEW. End-to-end with new component. |
| `tests/integration/strategy/test_unified_ability_framework_complete.py` | Test | NEW. Canonical "all 7 source kinds" smoke test. Regression baseline for the entire framework. |
| `docs/systems/strategy_layer.md` | Docs | Final framework section listing all 7 source kinds. |
| `docs/systems/ability_reference.md` | Docs | New abilities; strategic-vs-combat scope dichotomy. |
| `docs/02_PATTERNS.md` | Docs | Update "Universal Ability Source" pattern. |
| `docs/01_ARCHITECTURE.md` | Docs | Final adapter list. |
