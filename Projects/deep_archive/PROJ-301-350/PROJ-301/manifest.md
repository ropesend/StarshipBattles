# PROJ-301 File Manifest

> Generated during /claude-proj-start. Used by /claude-proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| `data/planet_types.json` | Data | NEW. Planet type intrinsic ability templates. |
| `game/core/paths.py` | Production | Add `Paths.PLANET_TYPES_FILE`. |
| `game/strategy/data/planet.py` | Production | Add `intrinsic_abilities: Dict[str, Any]` field. Update `to_dict`/`from_dict`. |
| `game/strategy/generation/planet_generator.py` | Production | Load planet_types.json; populate `intrinsic_abilities` via `roll_intrinsic_abilities` (imported from PROJ-300). |
| `game/strategy/services/ability_sources/planet_intrinsic.py` | Production | NEW. `PlanetIntrinsicAbilitySource` adapter. Uses `format_intrinsic_source_label` from PROJ-300. |
| ~~`game/strategy/services/ability_sources/intrinsic_roll.py`~~ | ~~Production~~ | **REMOVED 2026-04-27** — helper now ships in PROJ-300 per PROJ-300 D15. PROJ-301 is a pure consumer. |
| `game/strategy/services/ability_sources/__init__.py` | Production | Re-export `PlanetIntrinsicAbilitySource`. |
| `game/strategy/services/ability_iterator.py` | Production | Register `_planet_intrinsic_provider`. |
| ~~`tests/unit/strategy/services/ability_sources/test_intrinsic_roll.py`~~ | ~~Test~~ | **REMOVED 2026-04-27** — tests live in PROJ-300. |
| `tests/unit/strategy/services/ability_sources/test_planet_intrinsic.py` | Test | NEW. Adapter cases. |
| `tests/unit/strategy/services/test_ability_iterator.py` | Test | Add planet-intrinsic provider cases. |
| `tests/unit/strategy/data/test_planet.py` | Test | Add `intrinsic_abilities` field cases. |
| `tests/unit/strategy/generation/test_planet_generator.py` | Test | Add intrinsic-ability rolling cases. |
| `tests/integration/data/test_planet_types_registry.py` | Test | NEW. Registry coverage validation. |
| `tests/integration/save_load/test_roundtrip_planets.py` | Test | Roundtrip with rolled values. |
| `tests/integration/strategy/test_sector_effects_multi_source.py` | Test | NEW. Multi-source aggregation (planet + facility + storm). |
| `docs/systems/strategy_layer.md` | Docs | Add planet-intrinsic effects subsection. |
| `docs/systems/ability_reference.md` | Docs | Add planet intrinsic abilities section. |
| `docs/01_ARCHITECTURE.md` | Docs | List `PlanetIntrinsicAbilitySource` if applicable. |
