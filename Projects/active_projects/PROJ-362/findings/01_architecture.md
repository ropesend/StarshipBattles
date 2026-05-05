# PROJ-352 Architecture Analysis

## 1. Hardcoded special cases in system_effects_collector.py
- **Line 62-76:** `SYSTEM_EFFECT_ABILITIES` dict — 12 ability names with display name overrides.
- **Line 81:** `_RATE_ABILITIES` frozenset — `{EnvironmentalDamage, FuelDrain}` for kind discrimination.
- **Line 86-90:** `_OWNER_AWARE_SCOPES` frozenset — 6 scope strings requiring owner_id.
- **Line 93-94:** `_ability_kind()` — membership check against `_RATE_ABILITIES`.
- **Line 128-148:** `make_group_key()` — special-case branches for `ResourceHarvestBooster`, `QualityImprovement`, `EnvironmentalDamage` (per resource_type / damage_type).
- **Line 151-166:** `make_display_name()` — mirrors `make_group_key` branches.
- **Line 364-367:** `_aggregate` value extraction — hardcoded `rate` vs `multiplier` field selection with `improvement_rate` fallback.

## 2. Ability families currently treated specially
- **Rate-style:** `EnvironmentalDamage`, `FuelDrain` (additive aggregation).
- **Multiplier-style:** all others (multiplicative; intra-group MAX, inter-group MULTIPLY).
- **Per-resource grouping:** `ResourceHarvestBooster`, `QualityImprovement` (key = `resource_type`).
- **Per-damage-type grouping:** `EnvironmentalDamage` (key = `damage_type`).
- **Activatable:** stabilizers + shield-related (have `activation_time`).
- **Always-on:** harvest/build boosters, environmental hazards.

## 3. Metadata available in component_data
Yes — every ability entry already carries the fields needed to drive these decisions: `resource_type`, `damage_type`, `rate`, `multiplier`, `improvement_rate`, `activation_time`, `scope`. Default scope per ability class is exposed via `get_ability_default_scope()` at `abilities/__init__.py:191-221`. **No data migration needed for the metadata registry.**

## 4. Proposed `EffectAbilityMetadata` shape
```python
@dataclass(frozen=True)
class EffectAbilityMetadata:
    ability_name: str
    display_name: str | None             # None = derive from ability_data (resource_type / damage_type)
    kind: Literal['rate', 'multiplier']
    is_activatable: bool                 # Has activation_time field
    grouping_key_field: str | None       # 'resource_type' | 'damage_type' | None
    owner_aware_scopes: frozenset[str]   # Scopes that require owner_id
    value_field_primary: str             # 'rate' | 'multiplier'
    value_field_fallback: str            # 'improvement_rate'
```
Replaces SYSTEM_EFFECT_ABILITIES + _RATE_ABILITIES + grouping branches. The collector's `_aggregate` becomes a pure walk over (source, ability) pairs with metadata-driven dispatch.

## 5. `_legacy_provider_fields` (lines 476-503)
Emits: `planet_name`, `planet_id`, `facility_name`, `facility_id`, `component_key` (None for non-facility sources).
**Consumers:**
- `system_tree_panel.py:9-20` (`_legacy_provider_label`)
- `planet_abilities_window.py:109`
- `planet_abilities_controller.py:129`
- `planet_report_panel.py:474+`
- `strategy_detail_fmt.py:435-436`

These are the blocking consumers for legacy field deletion (PROJ-352 Phase 5).

## 6. Existing test coverage
`tests/unit/strategy/services/test_system_effects_collector.py` already covers:
- Activation lifecycle (lines 102-123)
- D17 owner-aware-scope-on-ownerless (lines 527-576)
- D16 mixed-kind validation (lines 579-613)
- Group key + display name helpers (lines 681-759)
- BUG-119 storm coordinate frame (lines 638-672)

Coverage is mature; characterization additions needed for: (a) per-source error tolerance branches at lines 308-320, (b) multi-ability rolup ordering. The decomposition target is well-supported by existing tests.
