# PROJ-380 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| `game/ai/controller.py` | Production | Phase 1 — Remove dead `IControllableShip` import + update string annotation (DCV-01) |
| `game/simulation/components/modifier_manager.py` | Production | Phase 2 — Delete 5 deprecated `*_static` methods; possibly also `remove_modifier_inplace` if no surviving callers (DUP-X-05) |
| `game/services/llm/factory.py` | Production | Phase 3.1 — Delegate to shared `ProviderFactory` (DUP-X-02) |
| `game/ui/services/image/factory.py` | Production | Phase 3.1 — Delegate to shared `ProviderFactory` (DUP-X-02) |
| `game/services/provider_factory.py` (new — confirm path) | Production | Phase 3.1 — Shared base for LLM/Image factories (DUP-X-02) |
| `game/strategy/data/fleet_consumable_aggregator.py` | Production | Phase 3.2 — Extract `_distribute_cargo_to_fleet` helper (DUP-X-06) |
| `game/ui/screens/strategy_superweapons.py` | Production | Phase 3.3 — Replace 5 designation-handler coord-conversion sites + ability-check pattern (DUP-X-08) |
| `game/ui/screens/strategy_fleet_ops.py` | Production | Phase 3.3 + 3.5 — Replace 2 `pixel_to_hex` sites; extract `_format_result_error` for 3 result-handling sites (DUP-X-08, DUP-X-10) |
| `game/ui/screens/strategy_click_dispatcher.py` | Production | Phase 3.3 + 3.7 — Replace 2 `pixel_to_hex` sites; extract `_handle_input_mode_click` base for 9 click handlers (DUP-X-08, DUP-X-07) |
| `game/ui/screens/strategy_colonization.py` | Production | Phase 3.3 — Replace 1 `pixel_to_hex` site (DUP-X-08) |
| `game/ui/screens/strategy_input_handler.py` | Production | Phase 3.3 — Replace 1 `pixel_to_hex` site (DUP-X-08) |
| `game/ui/camera.py` (path TBC) | Production | Phase 3.3 — Add `Camera.hex_at_screen` convenience method (DUP-X-08) |
| `game/ui/screens/event_log_data_source.py` | Production | Phase 3.4 — Extract `_get_cell_detail` helper (DUP-X-09) |
| `game/strategy/engine/superweapon_command_handlers.py` | Production | Phase 3.6 — Consolidate 5 mission handlers behind `MissionCommandHandler` template (DUP-X-01) |
| `game/strategy/services/ability_iterator.py` | Production | Phase 3.8 — Extract `_iter_ability_sources` and refactor 7 providers (DUP-X-12) |
| `game/simulation/systems/battle_end_conditions.py` | Production | Phase 3.9 — Add base serialization for 9 condition subclasses (DUP-X-11) |
| `tests/unit/ai/` | Test | Phase 1 — Run focused tests to confirm import removal is safe |
| `tests/unit/simulation/components/test_modifier_manager.py` | Test | Phase 2 — Existing tests must still pass; no test changes expected |
| `tests/unit/services/llm/test_factory.py` | Test | Phase 3.1 — Existing tests must still pass post-refactor |
| `tests/unit/ui/services/image/test_factory.py` | Test | Phase 3.1 — Existing tests must still pass post-refactor |
| `tests/unit/strategy/data/test_fleet_consumable_aggregator.py` | Test | Phase 3.2 — Existing tests must still pass |
| `tests/unit/ui/screens/test_strategy_superweapons.py` | Test | Phase 3.3 / 3.6 — Existing tests must still pass |
| `tests/unit/ui/screens/test_strategy_fleet_ops.py` | Test | Phase 3.5 — Existing tests must still pass |
| `tests/unit/ui/screens/test_strategy_click_dispatcher.py` | Test | Phase 3.7 — Existing tests must still pass |
| `tests/unit/ui/screens/test_event_log_data_source.py` | Test | Phase 3.4 — Existing tests must still pass |
| `tests/unit/strategy/engine/test_superweapon_command_handlers.py` | Test | Phase 3.6 — Dispatch tests must still pass |
| `tests/unit/strategy/services/test_ability_iterator.py` | Test | Phase 3.8 — Iteration semantics unchanged |
| `tests/unit/simulation/systems/test_battle_end_conditions.py` | Test | Phase 3.9 — Round-trip serialization tests must pass |
