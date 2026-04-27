# PROJ-303 File Manifest

| File | Type | Notes |
|------|------|-------|
| `data/warp_point_types.json` | Data | NEW. Warp point type templates. |
| `game/core/paths.py` | Production | Add `Paths.WARP_POINT_TYPES_FILE`. |
| `game/strategy/data/galaxy.py` (`WarpPoint` dataclass) | Production | Add `type: str` field AND `intrinsic_abilities: Dict[str, Any]` field. *(2026-04-27: WarpPoint has no type field today — PROJ-303 introduces it.)* |
| `game/strategy/generation/` (warp_point generator) | Production | Assign `type` at generation; load registry; populate `intrinsic_abilities` via `roll_intrinsic_abilities` (imported from PROJ-300). |
| `game/strategy/services/ability_sources/warp_point.py` | Production | NEW. Adapter. |
| `game/strategy/services/ability_sources/__init__.py` | Production | Re-export `WarpPointAbilitySource`. |
| `game/strategy/services/ability_iterator.py` | Production | Register `_warp_point_provider`. |
| `tests/unit/strategy/services/ability_sources/test_warp_point.py` | Test | NEW. Adapter cases. |
| `tests/unit/strategy/services/test_ability_iterator.py` | Test | Add warp_point provider cases. |
| `tests/unit/strategy/data/test_warp_point.py` | Test | Field cases. |
| `tests/unit/strategy/generation/test_warp_point_generator.py` | Test | Intrinsic-rolling cases. |
| `tests/integration/data/test_warp_point_types_registry.py` | Test | NEW. Registry coverage. |
| `tests/integration/save_load/test_roundtrip_warp_points.py` | Test | Roundtrip with rolled values. |
| `tests/integration/strategy/test_fleet_through_unstable_warp_point.py` | Test | NEW. Damage application. |
| `docs/systems/strategy_layer.md` | Docs | Warp point subsection. |
| `docs/systems/ability_reference.md` | Docs | Warp point entries + `"warp"` damage_type. |
| `docs/01_ARCHITECTURE.md` | Docs | List `WarpPointAbilitySource`. |
