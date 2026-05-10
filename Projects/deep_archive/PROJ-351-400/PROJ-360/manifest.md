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
| `game/simulation/entities/stat_contributors/registry.py` | Production (new, Phase 3) | `CREW_PRIORITY_REGISTRY`, `STAT_CONTRIBUTOR_REGISTRY`, register/unregister + `apply_registered_contributors`. |
| `game/simulation/combat/ability_stat_registry.py` | Production | Untouched — sibling registry for modifier emission, NOT extended. (Decision: separate concerns.) |
| `tests/unit/simulation/entities/test_ship_stats_golden.py` | Test (new) | Phase 1: bit-identical `calculate()` output for representative ship designs. |
| `tests/unit/simulation/entities/test_ship_stats_golden_snapshot.json` | Test fixture (new) | Phase 1: locked-in stats baseline. |
| `tests/unit/simulation/entities/stat_contributors/test_movement.py` | Test (new) | Phase 2: movement contributor unit tests. |
| `tests/unit/simulation/entities/stat_contributors/test_defense.py` | Test (new) | Phase 2: defense contributor unit tests. |
| `tests/unit/simulation/entities/stat_contributors/test_weapons.py` | Test (new) | Phase 2: targeting score unit tests. |
| `tests/unit/simulation/entities/stat_contributors/test_command.py` | Test (new) | Phase 2: priority + crew allocation unit tests. |
| `tests/unit/simulation/entities/stat_contributors/test_launch.py` | Test (new) | Phase 2: hangar contributor unit tests. |
| `tests/unit/simulation/entities/stat_contributors/test_registry.py` | Test (new) | Phase 3: registry register/unregister/apply round-trips. |
| `tests/unit/simulation/entities/test_stat_contributor_extension.py` | Test (new) | Phase 3: end-to-end "no central edits" acceptance test. |
| `docs/02_PATTERNS.md` | Doc (extend) | Phase 3: §35 "Stat Contributor Registry". |
