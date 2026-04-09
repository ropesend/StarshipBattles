# PROJ-236 File Manifest

> Generated during Protocol 01. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| `game/strategy/data/stars.py` | Production | Extract magic numbers, SB group helper, name physics constants, fix while-True |
| `game/strategy/data/planet_gen.py` | Production | Wire to OrbitalGenerationConfig, wire chthonian to ClassificationConfig, wire ramp_c |
| `game/strategy/data/star_generation_config.py` | Production | NEW — StarGenerationConfig class |
| `game/strategy/data/orbital_generation_config.py` | Production | NEW — OrbitalGenerationConfig class |
| `game/strategy/data/classification_config.py` | Production | Add DEFAULT_CHTHONIAN, 4 new attributes |
| `game/strategy/data/resource_generation_config.py` | Production | Add ramp_c to DEFAULT_QUANTITY |
| `data/astrophysics.json` | Data | Add star_generation, orbital_generation sections + chthonian_stripping + ramp_c |
| `game/strategy/generation/loaders/astrophysics_loader.py` | Production | Add star_generation, orbital_generation to required_sections |
| `tests/unit/strategy/data/test_star_generation_config.py` | Test | NEW — StarGenerationConfig unit tests |
| `tests/unit/strategy/data/test_orbital_generation_config.py` | Test | NEW — OrbitalGenerationConfig unit tests |
| `tests/unit/strategy/data/test_stars.py` | Test | Add characterization/golden-output tests |
| `tests/unit/strategy/data/test_planet_gen.py` | Test | Add characterization tests for moon/mass/surface |
| `tests/unit/strategy/data/test_classification_config.py` | Test | Add chthonian stripping tests |
| `tests/unit/strategy/data/test_resource_generation_config.py` | Test | Add ramp_c test |
