# PROJ-362: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

`_aggregate` (`system_effects_collector.py:281-430+`) has CC 47 and ~150+ LOC. It mixes seven concerns into one function. The supported ability set is hardcoded across:
- `SYSTEM_EFFECT_ABILITIES` (line 62-76) — 12 ability names with display name overrides
- `_RATE_ABILITIES` (line 81) — rate-vs-multiplier discrimination
- `_OWNER_AWARE_SCOPES` (line 86-90) — ownership-aware scope set
- `_ability_kind`, `make_group_key`, `make_display_name` — name-keyed branches

Per `findings/01_architecture.md`, every ability entry already carries the metadata fields needed (`resource_type`, `damage_type`, `rate`, `multiplier`, `improvement_rate`, `activation_time`, `scope`). **No data migration needed** — the registry is purely a code refactor.

## Swarm Findings Summary

### Architecture (findings/01_architecture.md)
Proposed `EffectAbilityMetadata`:
```python
@dataclass(frozen=True)
class EffectAbilityMetadata:
    ability_name: str
    display_name: str | None              # None = derive from ability_data field
    kind: Literal['rate', 'multiplier']
    is_activatable: bool                  # Has activation_time
    grouping_key_field: str | None        # 'resource_type' | 'damage_type' | None
    owner_aware_scopes: frozenset[str]    # Scopes requiring owner_id
    value_field_primary: str              # 'rate' | 'multiplier'
    value_field_fallback: str             # 'improvement_rate'
```

Decomposition target for `_aggregate`:
- `collect_providers(sources, allowed_scopes, empire_id, hex_coord, registries) -> dict[group_key, list[provider_dict]]`
- `aggregate_status(providers) -> str`
- `aggregate_value(providers, kind) -> float`
- `format_rows(group_data) -> list[dict]`

### Dependencies (findings/02_dependencies.md)
- 6 production callers (3 engines + UI tree panel + planet list helpers).
- `_legacy_provider_fields` consumed by 5 UI files (system_tree_panel, planet_abilities_window, planet_abilities_controller, planet_report_panel, strategy_detail_fmt). **These are blockers for legacy field deletion** — defer to Phase 4 after dedicated UI audit.
- `make_group_key` and `make_display_name` are public APIs (FEAT-16). Their **signatures stay**; bodies become metadata-driven.
- `combat_modifier_collector.py` is a **parallel consumer**, not a duplicator. Uses `find_abilities_in_scope` + `aggregate_multipliers` on its own. Do NOT try to unify in this project.

### Test Impact (findings/03_test_impact.md) — coverage gaps before refactoring
1. `get_abilities()` exception path not isolated.
2. `affects_hex` exception path not tested.
3. DEACTIVATING activation phase not exercised.
4. Mixed activation-state precedence (any_active / any_activating / any_deactivating) not pinned.
5. Owned source filtering with empire_id mismatch not tested.

These five gaps are **the Phase 1 deliverable** — characterization tests must land green BEFORE the refactor in Phases 2-3.

### Risks
- **Refactor of name-keyed branches without baseline coverage** would silently change behavior. Mitigated by Phase 1 characterization.
- **`_legacy_provider_fields` UI coupling**: 5 UI files read those fields directly. Deletion is out of scope for Phases 1-3. Phase 4 is documented but deferred until a separate UI audit.
- **Combat modifier collector divergence**: easy to be tempted to unify. Findings explicitly say no — keep parallel. Document why in decisions.md.

### Key Patterns to Reuse
- **Frozen dataclass + tuple registry** pattern (already used by `stabilizer_registry.py:54-70`).
- **Lookup-by-name function** (e.g. `find_metadata(ability_name)` returning `EffectAbilityMetadata | None`).

## Design Decisions
See [decisions.md](decisions.md) for full log with rationale.
