# PROJ-435 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| game/ui/screens/builder/stat_rows_dynamic.py | Production | Migrate `_ACTIVATABLE_ABILITIES` and `modifier_abilities` literals to registry-driven iteration |
| game/strategy/services/ability_metadata.py | Production (conditional) | May extend with display_name field and/or register `GravityModifier`/`RadiationShield` depending on Phase 1 decision |
| tests/unit/ui/screens/builder/test_stat_rows_dynamic.py | Test | Regression guards against new hardcoded ability-name literals |
| docs/systems/strategy_layer.md | Docs (conditional) | If registry shape changes |
