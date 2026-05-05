# PROJ-300 File Manifest

> Generated during /claude-proj-start. Used by /claude-proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| `game/core/protocols.py` | Production | Add `IAbilitySource` Protocol + `is_ability_source` TypeGuard. Update `IStorm` to expose `abilities` instead of `effects`. |
| `game/strategy/services/strategic_ability_scanner.py` | Production | Add `aggregate_rates`. Add ValidationException for mixed-kind groups. |
| `game/strategy/services/system_effects_collector.py` | Production | Refactor onto iterator. Extend `SYSTEM_EFFECT_ABILITIES` for 4 new abilities. Add `kind` discriminator. Add `find_sector_effect`/`aggregate_value_or` helpers. New provider entry shape (universal source_label/source_kind). |
| `game/strategy/services/ability_iterator.py` | Production | NEW. `iter_ability_sources_at_hex` / `iter_ability_sources_in_system` + `register_source_provider` API. |
| `game/strategy/services/ability_sources/__init__.py` | Production | NEW. Adapter package init/re-exports. |
| `game/strategy/services/ability_sources/facility.py` | Production | NEW. `FacilityAbilitySource` adapter. |
| `game/strategy/services/ability_sources/storm.py` | Production | NEW. `StormAbilitySource` adapter. |
| `game/strategy/data/storm.py` | Production | Replace `StormEffect` with `abilities: Dict[str, Any]` on `Storm`. Delete `StormEffect` class. |
| `game/strategy/generation/storm_generator.py` | Production | Read `data/storm_types.json`. Populate `Storm.abilities`. Drop `StormEffect` construction. |
| `game/strategy/combat/spec_compiler.py` | Production | Replace `_entries_from_environmental_effects` with `_entries_from_sector_effects`. Parameter `environmental_effects` → `sector_effects`. |
| `game/strategy/engine/conflict_resolution_engine.py` | Production | Rename `_lookup_environmental_effects` → `_lookup_sector_effects`. Call collector. |
| `game/strategy/engine/fleet_movement_engine.py` | Production | Use `collect_sector_effects` + `aggregate_value_or('StrategicSpeedModifier', 1.0)`. Drop `area_effect_manager` constructor arg. |
| `game/strategy/engine/environmental_hazard_engine.py` | Production | Use `collect_sector_effects`. Sum across `EnvironmentalDamage` and `FuelDrain` effects. Drop `area_effect_manager` arg. |
| `game/strategy/adapters/simulation_adapter.py` | Production | Parameter `environmental_effects` → `sector_effects`. |
| `game/simulation/combat/ability_stat_registry.py` | Production | Register `ThrustModifier` → `thrust_mult`. |
| `game/ui/panels/system_tree_panel.py` | Production | Render with `provider['source_label']` (universal). Add rate-style value formatter for `EnvironmentalDamage`/`FuelDrain`/`ThrustModifier`/`StrategicSpeedModifier`. |
| `game/ui/screens/strategy_detail_formatter.py` | Production | `_format_storm` strips per-effect breakdown; keeps lore (name + description + size). |
| `game/context.py` | Production | Remove `AreaEffectManager` from DI wiring. |
| `game/core/paths.py` | Production | Rename `STORMS_FILE` → `STORM_TYPES_FILE`; point to new location. |
| `data/storm_types.json` | Data | NEW (renamed from `data/storms.json`). v2.0 schema with abilities-shaped storm types. |
| `data/storms.json` | Data | DELETE after generator migrated. |
| `game/strategy/services/area_effect_manager.py` | Production | **DELETE** — file removed entirely. |
| `tests/unit/strategy/services/test_area_effect_manager.py` | Test | **DELETE** — file removed entirely. |
| `tests/unit/strategy/services/test_strategic_ability_scanner.py` | Test | Add `TestAggregateRates` cases (intra-MAX, inter-SUM, mixed-kind rejection). |
| `tests/unit/strategy/services/test_system_effects_collector.py` | Test | New cases for storm sources, kind discriminator, new ability names, helpers. Existing tests updated to new provider shape. |
| `tests/unit/strategy/services/ability_sources/test_facility.py` | Test | NEW. `FacilityAbilitySource` cases. |
| `tests/unit/strategy/services/ability_sources/test_storm.py` | Test | NEW. `StormAbilitySource` cases. |
| `tests/unit/strategy/services/test_ability_iterator.py` | Test | NEW. Iterator cases. |
| `tests/unit/strategy/data/test_storm.py` | Test | Rewrite roundtrip tests for `abilities` shape. |
| `tests/unit/strategy/generation/test_storm_generator.py` | Test | Update assertions to `abilities` shape; reads `data/storm_types.json`. |
| `tests/unit/strategy/combat/test_spec_compiler_sector_effects.py` | Test | NEW (or extend existing). `_entries_from_sector_effects` cases including multi-storm multiply. |
| `tests/unit/strategy/conflict_resolution/test_storm_integration.py` | Test | Update to new effect dict path. |
| `tests/unit/strategy/adapters/test_simulation_adapter_storms.py` | Test | Update parameter name and effect shape. |
| `tests/unit/strategy/engine/test_environmental_hazard_engine.py` | Test | Rewrite to construct galaxy with storms (no AreaEffectManager). |
| `tests/unit/strategy/engine/test_fleet_movement_engine.py` | Test | Confirm storm-modified speed via collector. |
| `tests/unit/ui/panels/test_system_tree_panel.py` | Test | Add storm-source-label and rate-formatter cases. |
| `tests/unit/ui/screens/test_strategy_detail_formatter.py` | Test | Confirm storm detail panel is lore-only. |
| `tests/integration/strategy/test_turn_storms.py` | Test | Update assertions to new path. |
| `tests/integration/strategy/test_galaxy_generation_storms.py` | Test | Update assertions to `abilities` shape. |
| `tests/integration/strategy/combat/test_storm_shield_interference.py` | Test | Update assertions; add multi-storm multiply test. |
| `tests/integration/save_load/test_roundtrip_storms.py` | Test | New abilities-shape fixtures. |
| `tests/unit/core/test_protocols.py` | Test | Add `IAbilitySource` / `is_ability_source` cases. |
| `tests/unit/simulation/combat/test_ability_stat_registry.py` | Test | Confirm `ThrustModifier` registered. |
| `docs/02_PATTERNS.md` | Docs | Add "Universal Ability Source" pattern. |
| `docs/systems/strategy_layer.md` | Docs | Replace AreaEffectManager / EnvironmentalEffects / StormEffect references; describe new pipeline. |
| `docs/systems/ability_reference.md` | Docs | Add 4 new abilities + rate-style section. |
| `docs/01_ARCHITECTURE.md` | Docs | Update `IStorm` protocol description; add `IAbilitySource` to protocols table; remove `AreaEffectManager`. |
| `docs/guides/adding_abilities.md` | Docs | Add sector-scope/system-scope section. |
