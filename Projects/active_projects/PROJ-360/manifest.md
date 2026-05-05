# PROJ-360 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| `game/simulation/entities/ship_stats.py` | Production | Reduce below 500 LOC by extracting domain contributors; replace hardcoded ability-name checks with registered contributors. |
| `game/simulation/entities/stat_contributors/__init__.py` | Production (new) | Package marker + contributor registry. |
| `game/simulation/entities/stat_contributors/movement.py` | Production (new) | Thrust, turn speed, strategic movement, drag. |
| `game/simulation/entities/stat_contributors/defense.py` | Production (new) | Shields, regen, repair, armor (emissive, shield-regenerating). |
| `game/simulation/entities/stat_contributors/weapons.py` | Production (new) | Weapon-derived stats; may consume PROJ-359 typed contract. |
| `game/simulation/entities/stat_contributors/command.py` | Production (new) | Command priority, engine priority, multiplex. |
| `game/simulation/entities/stat_contributors/launch.py` | Production (new) | Hangar capacity, fighters_per_wave, launch_cycle, fighter_size_cap. |
| `game/simulation/combat/ability_stat_registry.py` | Production (audit / extend) | Existing registry may grow to cover the contributors' lookup table. |
| `tests/unit/simulation/entities/test_ship_stats_golden.py` | Test (new) | Phase 1: bit-identical `calculate()` output for representative ship designs. |
| `tests/unit/simulation/entities/stat_contributors/test_movement.py` | Test (new, one per contributor) | Phase 2/3: domain-level tests. |
| `tests/unit/simulation/entities/test_stat_contributor_extension.py` | Test (new) | Phase 3: a fake contributor can be added without editing other domains. |
