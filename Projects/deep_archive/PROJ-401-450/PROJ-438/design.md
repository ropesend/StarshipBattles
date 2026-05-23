# PROJ-438: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

This project is explicitly **post-436/437**.

Assumption set:
- PROJ-436 lands and removes storage/container fragmentation, `_fleet_resource_pool`, `VALID_CARGO_TYPES`, `RESOURCE_TYPES`, `context_type` storage branching, and `_CarriedItemsProxy`.
- PROJ-437 lands and rebuilds the transfer UI on the unified container API.
- The remaining target is the residue of original blank-sheet concerns `#1` and `#3`, while `#2` (temporal scheduler / 100-tick rethink) stays out of scope.

## Swarm Findings Summary

Combined from direct code review plus three focused Codex subagent audits.

### Architecture

#### Remaining `#1` (persistence-shaped mutable runtime state)

- **Graph restoration is still duplicated knowledge.** Save/load replays backrefs, fleet registration, order-target rebinding, and pursuer-tracker rebuild in [persistence_adapter.py](../../../game/strategy/engine/session/persistence_adapter.py#L62), while rollback restore repeats that shape in [turn_state_snapshot.py](../../../game/strategy/engine/turn_state_snapshot.py#L73). Even after storage cleanup, that is still evidence of a live mutable graph that must be repaired after deserialization rather than a naturally reconstructible state model.

- **GameSession is still a mixed runtime/persistence/UI root.** It still carries `save_path`, `human_player_ids`, and derived `active_empire` / `enemy_empire` in [game_session.py](../../../game/strategy/engine/game_session.py#L279), while the services bag also owns turn execution, command dispatch, and persistence-adjacent runtime services in [runtime_services.py](../../../game/strategy/engine/session/runtime_services.py#L34) and [bootstrap.py](../../../game/strategy/engine/session/bootstrap.py#L88). The façade still compensates with a shared cache holder in [strategy_session_facade.py](../../../game/strategy/facade/strategy_session_facade.py#L181) and [_facade_state.py](../../../game/strategy/facade/slices/_facade_state.py#L34).

- **Broad entity roots remain after storage leaves.**
  - `Planet` still declares “47 dataclass fields preserved verbatim” and owns facilities, populations, orders, environmental targets, and cache state in [planet.py](../../../game/strategy/data/planet.py#L44) and [planet.py](../../../game/strategy/data/planet.py#L166).
  - `Fleet` still owns ships, hierarchy overlay, policy, orders, path, and build queue in [fleet.py](../../../game/strategy/data/fleet.py#L67) and serializes the entire bundle in [fleet.py](../../../game/strategy/data/fleet.py#L466).
  - `Empire` still owns colonies, fleets, deployed groups, serial counters, and broad serialization in [empire.py](../../../game/strategy/data/empire.py#L37) and [empire.py](../../../game/strategy/data/empire.py#L343).
  - `ShipInstance` is still the highest-signal post-container seam: it combines durable fields, cache state, delegate slots, projection helpers, and bridge/serializer shims in [ship_instance.py](../../../game/strategy/data/ship_instance.py#L47), [ship_instance.py](../../../game/strategy/data/ship_instance.py#L189), [ship_instance.py](../../../game/strategy/data/ship_instance.py#L357), and [ship_instance.py](../../../game/strategy/data/ship_instance.py#L578).

- **The read side still compensates instead of replacing the graph.** Heavy reads are rebuilt from live entities on demand in façade slices and DTO factories like [economy_slice.py](../../../game/strategy/facade/slices/economy_slice.py#L85), [fleet_dto.py](../../../game/strategy/facade/dto/fleet_dto.py#L113), and [planet_dto.py](../../../game/strategy/facade/dto/planet_dto.py#L93). That is a safer boundary than raw entities, but it is still a compensation layer on top of the mutable graph, not a first-class query model.

#### Remaining `#3` (strategic intent / order lifecycle)

- **Planet ability orders are still a separate lifecycle.** `IssuePlanetOrderCommand` still carries `order_type: str`; the handler manually maps that string to `ACTIVATE_ABILITY` / `DEACTIVATE_ABILITY`, queues a dict payload, `PlanetActionEngine` instantly pops the order and writes `ComponentActivationState`, and `ComponentActivationEngine` advances the timer later in a separate phase ([commands/__init__.py](../../../game/strategy/engine/commands/__init__.py#L558), [planet_command_handlers.py](../../../game/strategy/engine/planet_command_handlers.py#L63), [planet_action_engine.py](../../../game/strategy/engine/planet_action_engine.py#L132), [component_activation_engine.py](../../../game/strategy/engine/component_activation_engine.py#L48)).

- **Planet FMS reuse is still a graft.** `ActionExecutionEngine` has a second planet tick loop, filters with `planet_fms_action_order_types`, reaches into `OrderProcessor._handler_registry`, and uses a `TypeError` fallback because issuer handlers do not share one stable signature ([action_execution_engine.py](../../../game/strategy/engine/action_execution_engine.py#L119), [action_execution_engine.py](../../../game/strategy/engine/action_execution_engine.py#L252), [action_execution_engine.py](../../../game/strategy/engine/action_execution_engine.py#L311), [order_handlers/base.py](../../../game/strategy/engine/order_handlers/base.py#L58)).

- **Order persistence still sits partly outside the executable metadata surface.** `CommandSpec.serializer_codec` exists, but `Order.to_dict()` still hardcodes target-shape branching and `OrderSerializer` still separately does marker-dict deserialization plus post-load rebinding/removal of dead references ([commands/registry.py](../../../game/strategy/engine/commands/registry.py#L90), [order_types.py](../../../game/strategy/data/order_types.py#L80), [order_serializer.py](../../../game/strategy/data/order_serializer.py#L99), [order_serializer.py](../../../game/strategy/data/order_serializer.py#L155)).

- **A few lifecycle families still depend on explicit special cases.** `IMPLICIT_ACTION_ORDER_TYPES`, mission decomposition, and the `JOIN_FLEET` instant path are likely still the highest-value residual special cases once metadata convergence from PROJ-424/429 is assumed landed.

### Key Patterns to Reuse

- **Bootstrap-State Single Assignment Path**: already landed in PROJ-423 and should be reused rather than reopened. See [docs/02_PATTERNS.md](../../../docs/02_PATTERNS.md#L1081).
- **CQRS-lite + grouped façade namespaces**: keep the UI write/read boundary intact; this project should narrow it further, not bypass it. See [strategy_session_facade.py](../../../game/strategy/facade/strategy_session_facade.py#L63) and [docs/02_PATTERNS.md](../../../docs/02_PATTERNS.md#L167).
- **Metadata-driven command/order surfaces**: `OrderMetadataView` and `AbilityMetadataRegistry` are already the right source-of-truth direction. This project should extend them where needed, not replace them.
- **Substrate-then-sweep checkpointing** from PROJ-431 and PROJ-436 remains the migration model: new seams first, then caller sweeps, then final cutover.

### Dependencies & Risks

1. **Hard dependency on PROJ-436/437 completion.** This charter assumes the storage/UI layer is already stable. If those projects drift materially, phase ordering here will need review.
2. **Verification gap risk.** `pytest.ini` currently excludes any directory named `data`, which may hide some of the best `tests/unit/strategy/data/` ratchets from the default suite. This project should make an explicit decision in Phase 0 rather than assuming the sharded runner is sufficient.
3. **910-caller trap.** A broad forced sweep to remove all remaining `ShipInstance` thin shims would balloon this project and distract it from the higher-value state/intent seams. Keep that explicitly bounded.
4. **Public seam churn.** Protocols, DTOs, façade namespaces, and save/load tests are all touchpoints. If they are not treated together, the project could improve internals while leaving a fragmented public contract.

### Opportunities Discovered

- A canonical restore-path collaborator could simultaneously reduce `#1` state debt and simplify high-signal rollback/save-load verification.
- Typed planet strategic intents can likely absorb both the planet-ability string path and the brittle planet-FMS private-dispatch seam.
- The already-landed anti-drift tests from PROJ-423/424/425/429 are strong enough that PROJ-438 can be narrower and more assertive than the original blank-sheet framing suggested.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
