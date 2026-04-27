# PROJ-302 File Manifest

| File | Type | Notes |
|------|------|-------|
| `data/star_types.json` | Data | NEW. Star type intrinsic ability templates. |
| `game/core/paths.py` | Production | Add `Paths.STAR_TYPES_FILE`. |
| `game/strategy/data/stars.py` | Production | Add `intrinsic_abilities` field to Star. |
| `game/strategy/generation/` (star generator file — confirm during Phase A) | Production | Load star_types.json; populate intrinsic_abilities via `roll_intrinsic_abilities`. |
| `game/strategy/services/ability_sources/star.py` | Production | NEW. `StarAbilitySource` adapter. |
| `game/strategy/services/ability_sources/intrinsic_roll.py` | Production | Created by PROJ-301; used here. |
| `game/strategy/services/ability_sources/__init__.py` | Production | Re-export `StarAbilitySource`. |
| `game/strategy/services/ability_iterator.py` | Production | Register star at-hex and in-system providers. |
| `tests/unit/strategy/services/ability_sources/test_star.py` | Test | NEW. Adapter cases. |
| `tests/unit/strategy/services/test_ability_iterator.py` | Test | Add star provider cases. |
| `tests/unit/strategy/data/test_stars.py` | Test | Add `intrinsic_abilities` field cases. |
| `tests/unit/strategy/generation/test_star_generator.py` | Test | Add intrinsic-ability rolling cases (or appropriate test file). |
| `tests/integration/data/test_star_types_registry.py` | Test | NEW. Registry coverage validation. |
| `tests/integration/save_load/test_roundtrip_stars.py` | Test | Roundtrip with rolled values. |
| `tests/integration/strategy/test_system_effects_neutron_star.py` | Test | NEW. System-scope effect propagation. |
| `docs/systems/strategy_layer.md` | Docs | Star-intrinsic subsection. |
| `docs/systems/ability_reference.md` | Docs | Stellar effects entries. |
| `docs/01_ARCHITECTURE.md` | Docs | List `StarAbilitySource`. |
