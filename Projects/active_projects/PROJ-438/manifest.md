# PROJ-438 File Manifest

> Generated during charter creation from direct code review plus three Codex subagent audits. Updated if implementation discovers additional files.

## Files

### Production — modified (Phase 1)

| File | Type | Notes |
|------|------|-------|
| `game/strategy/engine/session/persistence_adapter.py` | Production | Shared graph-restoration steps currently duplicated with `TurnStateSnapshot.restore()`. |
| `game/strategy/engine/turn_state_snapshot.py` | Production | Rollback restore path; candidate to reuse the canonical restoration collaborator/path. |
| `game/strategy/engine/game_session.py` | Production | If graph-restoration helper/API needs to be threaded through the session shell. |

### Production — modified (Phase 2)

| File | Type | Notes |
|------|------|-------|
| `game/strategy/engine/game_session.py` | Production | Remaining mixed state concerns (`save_path`, `human_player_ids`, `active_empire`, `enemy_empire`, lazy race-registry ownership) after PROJ-423. |
| `game/strategy/facade/strategy_session_facade.py` | Production | Public façade surface and cache/projection boundary review. |
| `game/strategy/facade/grouped_namespaces.py` | Production | Only if public grouped command/read surfaces need a narrower contract after residual state cleanup. |
| `game/strategy/facade/slices/_facade_state.py` | Production | Shared cache/projection holder; likely touched if projection boundaries move. |
| `game/strategy/facade/slices/economy_slice.py` | Production | Race/economy fallback or projection behavior if it remains split from session-owned state. |

### Production — modified (Phase 3)

| File | Type | Notes |
|------|------|-------|
| `game/strategy/data/ship_instance.py` | Production | Remaining post-storage broad entity surface: design payload, bridge/serializer shims, cache state, public helper wall. |
| `game/strategy/data/ship_instance_serializer.py` | Production | If serialization shape narrows away from the current broad entity surface. |
| `game/strategy/data/ship_instance_bridge.py` | Production | If runtime/simulation bridge responsibilities shift. |
| `game/core/protocols/strategy_domain.py` | Production | `IShipInstance` still advertises legacy/broad fields (e.g. `cargo_contents` today). |
| `game/strategy/facade/dto/fleet_dto.py` | Production | DTO contract if ship-facing summaries change with a narrower public state surface. |
| `game/strategy/facade/dto/fleet_hierarchy_dto.py` | Production | Same, if hierarchy DTOs depend on broad ship entity reads. |

### Production — modified (Phase 4)

| File | Type | Notes |
|------|------|-------|
| `game/strategy/data/planet.py` | Production | Save-schema-shaped root with broad direct ownership outside storage concerns. |
| `game/strategy/data/planet_serde.py` | Production | Mirrors the broad planet shape; likely changes if `Planet` slims. |
| `game/strategy/data/fleet.py` | Production | Broad aggregate root and persistence surface after deployables/storage leave. |
| `game/strategy/data/empire.py` | Production | Broad aggregate root, serial counters, deployable-group collection, read aggregates. |
| `game/strategy/data/galaxy_protocols.py` | Production | If remaining broad state surfaces require narrower read contracts beyond the storage-side protocol cleanup from PROJ-436. |

### Production — modified (Phase 5)

| File | Type | Notes |
|------|------|-------|
| `game/strategy/engine/commands/__init__.py` | Production | Replace stringly `IssuePlanetOrderCommand` multiplexing with typed strategic planet intents. |
| `game/strategy/engine/planet_command_handlers.py` | Production | Current manual `order_type` string mapping to `ACTIVATE_ABILITY` / `DEACTIVATE_ABILITY`. |
| `game/strategy/engine/commands/registry.py` | Production | If new typed planet intents require registry shape changes. |
| `game/strategy/data/order_types.py` | Production | Only if the typed intent work changes how planet action order types are represented. |

### Production — modified (Phase 6)

| File | Type | Notes |
|------|------|-------|
| `game/strategy/engine/action_execution_engine.py` | Production | Planet FMS loop, private `_handler_registry` reach-in, `TypeError` fallback, issuer-aware execution split. |
| `game/strategy/engine/planet_action_engine.py` | Production | Planet action lifecycle and instant activation/deactivation path. |
| `game/strategy/engine/component_activation_engine.py` | Production | Activation timer path if contract changes between intent issue and timer execution. |
| `game/strategy/engine/order_processor.py` | Production | If issuer-aware execution becomes a first-class public contract. |
| `game/strategy/engine/order_handlers/base.py` | Production | Current order-handler protocol shape; likely extension point for a stable issuer-aware contract. |
| `game/strategy/engine/order_handlers/registry_factory.py` | Production | If registry creation must expose a better contract for issuer-aware execution. |

### Production — modified (Phase 7)

| File | Type | Notes |
|------|------|-------|
| `game/strategy/engine/commands/registry.py` | Production | `serializer_codec` is currently more documentary than executable. |
| `game/strategy/engine/commands/order_metadata_view.py` | Production | Only if persistence/intent convergence needs additional live metadata views. |
| `game/strategy/data/order_types.py` | Production | `Order.to_dict()` currently hardcodes target-shape branching. |
| `game/strategy/data/order_serializer.py` | Production | Separate hardcoded deserialization / rebinding / dead-reference removal path. |
| `game/strategy/services/action_time_resolver.py` | Production | If action-time resolution and persistence metadata are consolidated further. |
| `game/strategy/engine/superweapon_command_handlers.py` | Production | Mission decomposition path if still treated as leaking lifecycle special case. |
| `game/strategy/engine/order_handlers/join_fleet.py` | Production | `JOIN_FLEET` instant-only path if the project decides it still leaks across contracts. |

### Production — modified (Phase 8)

| File | Type | Notes |
|------|------|-------|
| `game/core/protocols/strategy_domain.py` | Production | Public state protocol sync after phases 3–7. |
| `game/core/protocols/strategy_mutators.py` | Production | If ship/entity mutation contracts narrow with the remaining state-surface cleanup. |
| `game/strategy/facade/strategy_session_facade.py` | Production | Final public surface sync if needed. |
| `game/strategy/facade/grouped_namespaces.py` | Production | Same. |
| `docs/systems/strategy_layer.md` | Docs | Residual post-436/437 and post-438 state/intent lifecycle docs. |
| `docs/systems/orders_system.md` | Docs | Planet intent and persistence/serializer convergence changes. |
| `docs/04_SERVICES.md` | Docs | Current doc drift still points some contributors at old metadata surfaces. |
| `docs/systems/ability_reference.md` | Docs | Same, if order/ability metadata convergence requires it. |
| `docs/01_ARCHITECTURE.md` | Docs | If public state/protocol surfaces change materially. |
| `docs/02_PATTERNS.md` | Docs | If the project lands a named state/intent lifecycle pattern or retires another one. |

### Tests — added

| File | Type | Notes |
|------|------|-------|
| `tests/unit/strategy/engine/test_restore_path_parity.py` | Test (new) | Phase 1. Shared restore-path behavior between save-load and rollback. |
| `tests/unit/strategy/engine/test_game_session_projection_boundary.py` | Test (new) | Phase 2. Remaining GameSession/facade boundary contract. |
| `tests/unit/strategy/ship_instance/test_post_container_surface.py` | Test (new) | Phase 3. Post-storage ShipInstance state/serializer/bridge contract. |
| `tests/unit/strategy/engine/test_typed_planet_intents.py` | Test (new) | Phase 5. Typed planet strategic intents replace stringly `order_type`. |
| `tests/unit/strategy/engine/test_issuer_execution_contract.py` | Test (new) | Phase 6. Stable issuer-aware execution contract, no private-registry reach-in or `TypeError` probing. |
| `tests/unit/strategy/engine/test_order_persistence_from_metadata.py` | Test (new) | Phase 7. Persistence derives from live metadata rather than split hardcoded paths. |

### Tests — modified

| File | Type | Notes |
|------|------|-------|
| `tests/unit/strategy/engine/session/test_bootstrap.py` | Test | Existing anti-drift/session tests likely extended, not replaced. |
| `tests/unit/strategy/engine/test_game_session_shape.py` | Test | Existing GameSession boundary checks. |
| `tests/unit/strategy/ship_instance/test_ship_instance_serializer.py` | Test | ShipInstance residual surface changes. |
| `tests/integration/save_load/test_roundtrip_ships.py` | Test | Save/load expectations still pin broad ship state today. |
| `tests/unit/strategy/engine/commands/test_order_metadata_view.py` | Test | Metadata surface still relevant after persistence convergence. |
| `tests/unit/strategy/engine/test_command_specs_contract.py` | Test | Command/spec parity if typed planet intents are introduced. |
| `tests/unit/strategy/engine/order_handlers/test_handler_registry_completeness.py` | Test | Action/planet/FMS registry completeness after contract cleanup. |
| `tests/unit/strategy/services/test_action_time_resolver.py` | Test | If action-time and serialization metadata converge further. |
| `tests/unit/strategy/facade/test_strategy_session_facade_public_api.py` | Test | Public façade surface if it changes. |

### Verification / support files

| File | Type | Notes |
|------|------|-------|
| `pytest.ini` | Support (optional, Phase 0) | Only if the project chooses to fix the `tests/unit/strategy/data/` visibility gap rather than documenting direct-path test runs. |
| `Projects/active_projects/PROJ-438/findings/post_436_437_contact_audit.md` | Findings (new) | Combined direct-review + subagent contact map. |

