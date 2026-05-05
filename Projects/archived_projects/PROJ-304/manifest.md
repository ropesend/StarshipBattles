# PROJ-304 File Manifest

| File | Type | Notes |
|------|------|-------|
| `data/system_archetypes.json` | Data | NEW. System archetype templates. |
| `data/galaxy_generation_config.json` (or equivalent) | Data | Add `archetype_chance` knob. |
| `game/core/paths.py` | Production | Add `Paths.SYSTEM_ARCHETYPES_FILE`. |
| `game/strategy/data/galaxy.py` | Production | Add `archetype` and `intrinsic_abilities` fields to `StarSystem`. |
| `game/strategy/generation/` (galaxy generator) | Production | Roll archetypes per `archetype_chance`; populate intrinsic_abilities. |
| `game/strategy/services/ability_sources/system.py` | Production | NEW. `SystemAbilitySource` adapter. |
| `game/strategy/services/ability_sources/__init__.py` | Production | Re-export. |
| `game/strategy/services/ability_iterator.py` | Production | Register providers. |
| `tests/unit/strategy/services/ability_sources/test_system.py` | Test | NEW. Adapter cases. |
| `tests/unit/strategy/services/test_ability_iterator.py` | Test | Add system-archetype provider cases. |
| `tests/unit/strategy/data/test_galaxy.py` | Test | StarSystem field cases. |
| `tests/unit/strategy/generation/test_galaxy_generator.py` | Test | Archetype rolling cases. |
| `tests/integration/save_load/test_roundtrip_galaxy.py` | Test | Roundtrip with archetype + rolled values. |
| `tests/integration/strategy/test_system_archetype_effects.py` | Test | NEW. System-scope effect propagation. |
| `docs/systems/strategy_layer.md` | Docs | System archetype subsection. |
| `docs/systems/ability_reference.md` | Docs | Archetype entries. |
| `docs/01_ARCHITECTURE.md` | Docs | List `SystemAbilitySource`. |
