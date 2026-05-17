# PROJ-429 File Manifest

> Generated at project scaffold. Used for conflict detection and phase planning. Coordinator updates if implementation discovers additional files.

## Files

### Phase 0: Scope-bounding read + design decision

| File | Type | Notes |
|------|------|-------|
| `docs/01_ARCHITECTURE.md` | Doc (read-only) | Re-read for ability-related conventions. |
| `docs/02_PATTERNS.md` | Doc (read-only) | Re-read for registry/view patterns. |
| `docs/03_CONVENTIONS.md` | Doc (read-only) | Re-read. |
| `docs/systems/strategy_layer.md` | Doc (read-only) | Re-read; modified in Phase 7. |
| `docs/guides/adding_abilities.md` | Doc (read-only) | Confirm live successor status. |

### Phase 1: Unified registry skeleton

| File | Type | Notes |
|------|------|-------|
| `game/strategy/services/ability_metadata.py` | Code (NEW) | `AbilityMetadata`, `EffectFacet`, `EnergyFacet`, `RoleTag`, `StrategicKind` + public API (`get_ability_metadata`, `ability_has_role_tag`, `ability_has_kind_tag`, `abilities_with_role_tag`, `abilities_with_kind_tag`, `ability_action_time_field`, `ability_drains_energy`). Built from a single tuple literal mirroring `EFFECT_ABILITY_METADATA` plus the new axes. |
| `game/strategy/services/effect_ability_metadata.py` | Code (modify) | Becomes a thin shim. Preserves `EFFECT_ABILITY_METADATA`, `find_metadata`, `is_known_effect_ability`, `all_owner_aware_scopes`, `EffectAbilityMetadata` (re-export). |
| `tests/unit/strategy/services/test_ability_metadata_registry.py` | Test (NEW) | Parity test: every currently-hardcoded name has at least one tag. Public-API contract tests for the seven exported functions. |
| `tests/unit/strategy/services/test_ability_metadata_contracts.py` | Test (NEW) | Cross-registry contract tests (extended in Phases 4 and 6). Empty-ish stub created in Phase 1. |
| `tests/unit/strategy/services/test_effect_ability_metadata.py` | Test (read-only) | Must remain green after shim conversion. |
| `tests/unit/strategy/services/test_effect_ability_display.py` | Test (read-only) | Must remain green after shim conversion. |

### Phase 2: `design_role` migration

| File | Type | Notes |
|------|------|-------|
| `game/strategy/data/design_role.py` | Code (modify) | Delete `_WEAPON_ABILITIES`, `_SEEKER_ABILITIES`, `_BEAM_PROJECTILE_ABILITIES`, `_SENSOR_ABILITIES`, `_SUPPORT_ABILITIES`, `_CARRIER_ABILITIES`, `_COMMAND_ABILITIES` constants (lines 56-70). Replace with `abilities_with_role_tag(...)` calls. Replace inline `"CommandAndControl"` literal at :105 with a tag query. |
| `tests/unit/strategy/data/test_design_role.py` | Test (modify) | Add new-ability classification test: `FooLaunchAbility` tagged `RoleTag.CARRIER` classifies as `CARRIER` without touching `design_role.py`. Existing fixtures keep passing. |

### Phase 3: `planet_energy_engine` migration

| File | Type | Notes |
|------|------|-------|
| `game/strategy/engine/planet_energy_engine.py` | Code (modify) | Delete dead `_ACTIVATABLE_ABILITIES` (lines 80-89). Replace literal `"PlanetaryShield"` at line 48 with `abilities_with_kind_tag(StrategicKind.PLANETARY_SHIELD)`. Preserve `_is_ability_active`, `get_activatable_ability_info`, `get_shield_info` public surface. |
| `tests/unit/strategy/engine/test_planet_energy_engine.py` | Test (modify) | Assert module no longer exports `_ACTIVATABLE_ABILITIES`. Keep existing imports (`PlanetEnergyEngine`, `_is_ability_active`, `get_activatable_ability_info`, `get_shield_info`) green. |
| `tests/unit/strategy/services/test_planet_query_service.py` | Test (modify) | `is_ability_active` characterization at lines 59-65 keeps passing. |

### Phase 4: `action_time_resolver` migration (TD-03 coupling)

| File | Type | Notes |
|------|------|-------|
| `game/strategy/services/action_time_resolver.py` | Code (modify) | `_extract_time` reads time-field name from the unified `EnergyFacet`. Delete the empty `ORDER_TO_TIME_FIELD` at lines 54-55. Replace inline `'activation_time' if ... else 'deactivation_time'` at lines 89-93 with a facet-driven resolution. |
| `tests/unit/strategy/services/test_action_time_resolver.py` | Test (modify) | Add `ability_action_time_field('PlanetaryShield') == 'activation_time'` (or whichever fields the ability declares). Verify derived `ORDER_TO_ABILITY_MAP` still matches `CommandRegistry`. |
| `tests/unit/strategy/services/test_ability_metadata_contracts.py` | Test (modify) | Add: every `CommandSpec.action_ability_name` exists in the unified registry. |
| `game/strategy/engine/commands/registry.py` | Code (read-only) | Source of `CommandSpec.action_ability_name`. Re-confirm API shape per TD-07 Execution Precondition 2. |

### Phase 5: `combat_modifier_collector` + `spec_compiler` migration

| File | Type | Notes |
|------|------|-------|
| `game/strategy/combat/spec_compiler.py` | Code (modify) | Replace `combat_ability_names = {"ShieldModifier","DamageModifier","ThrustModifier"}` at line 827 with `abilities_with_kind_tag(StrategicKind.COMBAT_MODIFIER)`. |
| `game/strategy/services/combat_modifier_collector.py` | Code (modify) | Replace iterated tuple `("ShieldModifier","DamageModifier")` at lines 96, 127. Replace literal `"ShieldProjection"` at lines 109, 113 with a `StrategicKind.COMBAT_FLAT_BONUS` query. |
| `game/strategy/services/ability_metadata.py` | Code (modify) | Add `ShieldProjection` entry with `kind_tag=COMBAT_FLAT_BONUS`, no `EffectFacet` (or one explicitly excluded from multiplier aggregation). |
| `tests/unit/strategy/services/test_combat_modifier_collector.py` | Test (modify) | Iteration matches `abilities_with_kind_tag(StrategicKind.COMBAT_MODIFIER)` exactly; no name divergence between `combat_modifier_collector` and `spec_compiler`. |
| `tests/integration/test_combat_modifier_*` (if present) | Test (read-only) | Must stay green; gate Phase 5 exit. |

### Phase 6: `build_queue_source` migration + stabilizer/superweapon parity

| File | Type | Notes |
|------|------|-------|
| `game/strategy/data/build_queue_source.py` | Code (modify) | Replace literal `"BuildRateBooster"` at line 114 with `abilities_with_kind_tag(StrategicKind.BUILD_RATE_BOOSTER)`. Scope-sweep array `["planet","sector","system","empire"]` left as-is (out of scope). |
| `game/strategy/services/stabilizer_registry.py` | Code (read-only) | No changes; contract test added. |
| `game/strategy/services/superweapon_registry.py` | Code (read-only) | No changes; contract test added. |
| `tests/unit/strategy/services/test_ability_metadata_contracts.py` | Test (modify) | Add: every `STABILIZERS[*].ability_name` has `kind_tag=STABILIZER`. Add: every `SUPERWEAPONS[*].ability_name` has `kind_tag=SUPERWEAPON`. |

### Phase 7: Documentation + final validation

| File | Type | Notes |
|------|------|-------|
| `docs/systems/strategy_layer.md` | Doc (modify) | Describe `AbilityMetadataRegistry` as the canonical strategy-facing source of truth for ability metadata. Remove prose referencing `_ACTIVATABLE_ABILITIES`, the design-role frozensets, or `ORDER_TO_TIME_FIELD`. |
| `docs/guides/adding_abilities.md` (if it has a live successor) | Doc (modify) | Point at the unified registry as the **first** edit when adding a new ability. Skip if doc is archived / under `_marked_for_deletion_*/`. |

## Out-of-manifest (read-only references)

| File | Type | Why read-only |
|------|------|---------------|
| `game/simulation/components/abilities/**` | Code | Out of scope. Mechanical behavior stays with ability implementations. |
| `data/**` | Data | Out of scope. |
| `Reviews/results/2026-05-16_strategy-layer-tech-debt-review/**` | Doc | Source plan and execution-order doc. Do not edit during execution. |
| `Projects/active_projects/PROJ-424/**` | Doc/Code | Hard predecessor. Read for context; not modified by this project. |
