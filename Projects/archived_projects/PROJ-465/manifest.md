# PROJ-465 File Manifest

> Generated during project creation from audit `2026-05-20_060020_audit_shrink`.
> Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| `game/strategy/engine/handlers/base.py` | Production | Add `_find_ship` (DUP-X-1) and `_handle_vehicle_order` template (DUP-X-3) |
| `game/strategy/engine/handlers/launch_fighters.py` | Production | Reduce to template calls; replace inline ship loop (DUP-X-3, DUP-X-7) |
| `game/strategy/engine/handlers/launch_satellites.py` | Production | Reduce to template calls; replace inline ship loop (DUP-X-3, DUP-X-7) |
| `game/strategy/engine/handlers/lay_mines.py` | Production | Reduce to template calls; replace inline ship loop (DUP-X-3, DUP-X-7) |
| `game/strategy/engine/handlers/recover_fighters.py` | Production | Reduce to template calls; replace inline ship loop (DUP-X-3, DUP-X-7) |
| `game/strategy/engine/handlers/recover_satellites.py` | Production | Reduce to template calls; replace inline ship loop (DUP-X-3, DUP-X-7) |
| `game/strategy/engine/handlers/movement.py` | Production | Route warp check through `Fleet.can_use_warp()` (DUP-X-6) |
| `game/strategy/engine/order_handlers/launch_fighters.py` | Production | Remove `_find_ship`; share `_run_with_issuer` (DUP-X-1, Cluster 21) |
| `game/strategy/engine/order_handlers/launch_satellites.py` | Production | Remove `_find_ship`; share `_run_with_issuer` (DUP-X-1, Cluster 21) |
| `game/strategy/engine/order_handlers/lay_mines.py` | Production | Remove `_find_ship` (DUP-X-1) |
| `game/strategy/engine/order_handlers/recover_fighters.py` | Production | Remove `_find_ship`; share `_run_with_issuer`/`execute_for_issuer`/converter (DUP-X-1, DUP-X-9, Cluster 11/12) |
| `game/strategy/engine/order_handlers/recover_satellites.py` | Production | Remove `_find_ship`; share `_run_with_issuer`/`execute_for_issuer`/converter (DUP-X-1, DUP-X-9, Cluster 11/12) |
| `game/strategy/engine/fleet_movement_engine.py` | Production | Route warp check through `Fleet.can_use_warp()` (DUP-X-6) |
| `game/strategy/services/fleet_navigation_service.py` | Production | Route warp check through `Fleet.can_use_warp()` (DUP-X-6) |
| `game/strategy/services/galaxy_pathfinding_service.py` | Production | Route warp check through `Fleet.can_use_warp()` (DUP-X-6) |
| `game/strategy/data/fleet_consumable_aggregator.py` | Production | Route warp check through `Fleet.can_use_warp()` (DUP-X-6) |
| `game/strategy/facade/dto/fleet_dto.py` | Production | Route warp check through `Fleet.can_use_warp()` (DUP-X-6) |
| `game/strategy/data/fleet.py` | Production | Add `Fleet.can_use_warp()` wrapper (DUP-X-6) — confirm exact module during impl |
| `game/strategy/services/component_abilities.py` | Production | Add canonical `facility_has_ability` (DUP-X-2) |
| `game/strategy/validation/planet_order_validator.py` | Production | Route `_facility_has_ability` through canonical (DUP-X-2) |
| `game/ui/screens/planet_menu_items.py` | Production | Route `_facility_has_ability` through canonical (DUP-X-2) |
| `game/ui/screens/strategy_detail_formatter.py` | Production | Route `_planet_has_ability` through canonical (DUP-X-2) |
| `game/strategy/data/deployed_group.py` | Production | Template `_from_dict_payload` (DUP-X-5) |
| `game/simulation/components/abilities/planetary/stat_modifiers.py` | Production | Inherit `SimpleMultiplierAbility` (Cluster 2) |
| `game/simulation/systems/battle_engine.py` | Production | Merge `launch_*_in_battle` (Cluster 8) |
| `game/services/llm/background.py` | Production | Shared `BackgroundCall.cancel()` (Cluster 9) |
| `game/ui/services/image/background.py` | Production | Shared `BackgroundCall.cancel()` (Cluster 9) |
| `game/ui/effects/hit_effects.py` | Production | Unify `_draw_radial_hit` (Cluster 10) |
| `game/simulation/entities/stat_contributors/launch.py` | Production | Parameterize `_contribute_launch` (Cluster 19) |
| `game/ui/screens/strategy_superweapons.py` | Production | Parameterize `_handle_designation` (Cluster 3) |
| `game/ui/screens/strategy_windows/selection_prompts.py` | Production | Generic `_open_selection_modal` (Cluster 6) |
| `game/ui/screens/defeat_dialog.py` | Production | Shared `DismissableDialog` (Cluster 7) |
| `game/ui/screens/turn_failed_dialog.py` | Production | Shared `DismissableDialog` (Cluster 7) |
