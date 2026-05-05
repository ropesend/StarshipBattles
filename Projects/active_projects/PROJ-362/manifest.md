# PROJ-362 File Manifest

## Files modified or created

| File | Type | Phase | Notes |
|------|------|-------|-------|
| `game/strategy/services/system_effects_collector.py` | Production (refactor) | 2, 3 | P2: replace `SYSTEM_EFFECT_ABILITIES`/`_RATE_ABILITIES`/`_OWNER_AWARE_SCOPES`/branches with metadata lookups. P3: split `_aggregate` into `_collect_providers`/`_aggregate_status`/`_aggregate_value`/`_format_rows`. |
| `game/strategy/services/effect_ability_metadata.py` | Production (new) | 2 | New module: `EffectAbilityMetadata` dataclass, `EFFECT_ABILITY_METADATA` registry tuple, `find_metadata`, `is_known_effect_ability`. |
| `tests/unit/strategy/services/test_system_effects_collector_aggregate_characterization.py` | Test (new) | 1 | 9 characterization tests for `_aggregate`: get_abilities exception, affects_hex exception, DEACTIVATING phase, mixed-state precedence (3 tests), owner mismatch, ownerless multi-empire, improvement_rate fallback. |
| `tests/unit/strategy/services/test_effect_ability_metadata.py` | Test (new) | 2 | Registry contract tests: every legacy ability name has a metadata entry; lookup helpers behave correctly. |
| `tests/unit/strategy/services/test_system_effects_collector.py` | Test (modify) | 2-3 | Existing tests must continue to pass; minor updates may be needed if any directly imported the deleted constants. |

## Files referenced for context (not modified)

| File | Purpose |
|------|---------|
| `game/strategy/services/stabilizer_registry.py:54-70` | Pattern: frozen dataclass + tuple registry |
| `game/strategy/services/combat_modifier_collector.py` | Parallel consumer (NOT unified per PROJ-272 separation) |
| `game/strategy/services/strategic_ability_scanner.py` | Used by combat_modifier_collector and others |
| `game/ui/panels/system_tree_panel.py` | Legacy field consumer (Phase 4 audit target) |
| `game/ui/screens/planet_abilities_window.py` | Legacy field consumer |
| `game/ui/screens/planet_abilities_controller.py` | Legacy field consumer |
| `game/ui/panels/planet_report_panel.py` | Legacy field consumer |
| `game/ui/screens/strategy_detail_fmt.py` | Legacy field consumer |
| `game/ui/screens/planet_list_window.py` | Public-API consumer (`make_group_key`, `make_display_name`); signatures preserved |
| `game/ui/screens/planet_list_sidebar.py` | Public-API consumer |
| `game/ui/screens/planet_list_filters.py` | Public-API consumer |
