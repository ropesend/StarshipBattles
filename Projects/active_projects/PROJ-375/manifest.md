# PROJ-375 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

### Phase 1 — Dead method removal
| File | Type | Notes |
|------|------|-------|
| `game/strategy/engine/planet_action_engine.py` | Production | Delete `_find_shield_component_id` (lines 385-387) |

### Phase 2 — Strategy-layer duplication consolidation
| File | Type | Notes |
|------|------|-------|
| `game/strategy/services/component_inspector.py` | Production | Add `get_ability_field_from_facility` (Task 2.1) |
| `tests/unit/strategy/services/test_component_inspector.py` | Test | Coverage for new helper (Task 2.1) |
| `game/strategy/engine/planet_action_engine.py` | Production | Migrate 4 ability-extraction variants (Task 2.1, DUP-X-06) |
| `game/strategy/engine/water_engine.py` | Production | Migrate to `get_ability_field_from_facility` (Task 2.1) |
| `game/strategy/engine/quality_engine.py` | Production | Migrate to `get_ability_field_from_facility` (Task 2.1) |
| `game/strategy/engine/atmosphere_engine.py` | Production | Migrate to `get_ability_field_from_facility` (Task 2.1) |
| `game/strategy/engine/planet_energy_engine.py` | Production | Migrate to `get_ability_field_from_facility` (Task 2.1) |
| `game/strategy/engine/harvesting_engine.py` | Production | Migrate to `get_ability_field_from_facility` (Task 2.1) AND consolidate harvester/storage info pairs (Task 2.6) |
| `game/strategy/engine/empire_economy_calculator.py` | Production | Migrate to `get_ability_field_from_facility` after re-confirming pattern (Task 2.1) |
| `game/ui/screens/strategy_detail_formatter.py` | Production | Migrate to `get_ability_field_from_facility` (Task 2.1) |
| `game/strategy/engine/handlers/base.py` | Production | Add `_resolve_player_planet` (Task 2.2) |
| `tests/unit/strategy/engine/handlers/test_base.py` | Test | Coverage for `_resolve_player_planet` (Task 2.2) |
| `game/strategy/engine/planet_command_handlers.py` | Production | Refactor 7 handlers to use `_resolve_player_planet` (Task 2.2); merge 3 SetXTarget handlers (Task 2.3) |
| `tests/unit/strategy/engine/test_planet_command_handlers.py` | Test | Update for refactored handlers (Tasks 2.2, 2.3) |
| `game/strategy/engine/superweapon_command_handlers.py` | Production | Refactor 4 handlers to use `_emit_validated_order` (Task 2.4) |
| `tests/unit/strategy/engine/test_superweapon_command_handlers.py` | Test | Update for refactored handlers (Task 2.4) |
| `game/strategy/services/race_description_llm_controller.py` | Production | Replace mirrored bio/socio attributes with field dict; PRESERVE 6 public `@property` accessors (Task 2.5) |
| `tests/unit/strategy/services/test_race_description_llm_controller.py` | Test | Update for unified field handling (Task 2.5) |
| `tests/unit/ui/panels/test_race_description_panel.py` | Test | Regression check — external readers of bio/socio properties (Task 2.5) |
| `tests/unit/ui/screens/race_setup/test_llm_dialog_service.py` | Test | Regression check — external readers of bio/socio properties (Task 2.5) |
| `tests/unit/strategy/engine/test_harvesting_engine.py` | Test | Update for generic ability-info helpers (Task 2.6) |

### Phase 3 — UI-layer duplication consolidation
| File | Type | Notes |
|------|------|-------|
| `game/ui/screens/workshop_event_router.py` | Production | Replace 5 dropdown handlers with config-driven dispatcher (Task 3.1) |
| `tests/unit/ui/screens/test_workshop_event_router.py` | Test | Update for unified dispatcher (Task 3.1) |
| `game/ui/screens/planet_list_window.py` | Production | Migrate `update()` + filter helpers to shared template (Task 3.2) |
| `game/ui/screens/star_list_window.py` | Production | Migrate `update()` + filter helpers to shared template (Task 3.2) |
| `tests/unit/ui/screens/test_planet_list_window.py` | Test | Update for shared template path (Task 3.2) |
| `tests/unit/ui/screens/test_star_list_window.py` | Test | Update for shared template path (Task 3.2) |
| `game/ui/screens/builder/structure_list_items.py` | Production | Extract shared `_rebuild_modifier_icons` (Task 3.3) |
| `tests/unit/ui/screens/builder/test_structure_list_items.py` | Test | Update for extracted helper (Task 3.3) |
