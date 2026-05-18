# PROJ-438: Strategy State Surface and Intent Lifecycle Consolidation

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-438` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-438 [phase]` before stopping
> - Update Current State with specific handoff context

**Execution Protocol:** 03c-phase-aware-execution

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 0. Post-436/437 audit freeze + verification gate decision | Not Started | [phase_0_checklist.md](phase_0_checklist.md) |
| 1. Canonical graph restoration path | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Session / facade projection boundary cleanup | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. ShipInstance residual state-surface consolidation | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Planet / Fleet / Empire state-surface slimming | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Typed planet strategic intents | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Issuer-aware execution contract cleanup | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |
| 7. Order persistence + metadata-driven serialization convergence | Not Started | [phase_7_checklist.md](phase_7_checklist.md) |
| 8. DTO / protocol / doc sync + Codex consult remediation | Not Started | [phase_8_checklist.md](phase_8_checklist.md) |

## Current State
**Last Updated:** 2026-05-18
**Active Phase:** Planning
**Last Action:** Project scaffold created, then replaced with a full charter after direct code review plus three subagent audits. Charter assumes PROJ-436 and PROJ-437 land as designed and explicitly leaves the temporal scheduler concern (#2) out.
**Next Action:** User review and approval of the charter. Once approved, implementation should wait until PROJ-436 and PROJ-437 are complete and merged.
**Blockers:** Hard predecessor assumption: PROJ-436 and PROJ-437 must land as expected before this project begins implementation. By user instruction, this charter does not carry alternate partial-predecessor paths.
**Context for Next Agent:** This project is intentionally **post-container**. Do not reopen storage/container/transfer-UI scope here. Focus on the remaining persistence-shaped state surfaces and the residual strategic intent/order lifecycle seams.

## Overview
Assuming PROJ-436 and PROJ-437 land as planned, the biggest remaining blank-sheet debt is no longer storage. It is the persistence-shaped runtime object graph and the still-split strategic intent lifecycle. `GameSession`, `Planet`, `Fleet`, `Empire`, and `ShipInstance` remain broad mutable roots; save/load and rollback still require graph-repair passes; the read side still compensates with façade caches and DTO rebuilds. On the intent side, metadata convergence mostly landed in PROJ-424/429, but planet ability orders still flow through a stringly command path, planet FMS execution still reaches into a private handler registry with a `TypeError` fallback, and order persistence still lives partly outside the executable metadata surface.

## Goals
- Reduce the remaining persistence-shaped runtime state surface after PROJ-436/437, without reopening storage/container work.
- Eliminate duplicated graph-restoration logic between save-load and rollback restore paths.
- Narrow `GameSession` / façade / projection responsibilities further so runtime state, derivable projections, and public read surfaces are cleaner and easier to reason about.
- Consolidate the remaining strategic intent lifecycle seams: typed planet intents, issuer-aware execution, and order persistence/serialization alignment with live metadata.
- Reconcile DTO/protocol/doc surfaces with the post-436/437 world and preserve strong anti-drift guards.

## Scope
**In:** canonical graph restoration for `SessionPersistenceAdapter.rehydrate_state()` and `TurnStateSnapshot.restore()`; remaining `GameSession` / façade projection cleanup; `ShipInstance` residual state-surface cleanup after storage migration; remaining broad state-surface cleanup on `Planet`, `Fleet`, and `Empire`; typed planet strategic intent path replacing the current stringly `IssuePlanetOrderCommand` flow; issuer-aware execution contract cleanup in `ActionExecutionEngine` / `PlanetActionEngine`; order serialization/persistence convergence around executable metadata; DTO/protocol/doc/test updates required by those changes; verification-gate decision if the current sharded suite still misses high-signal `tests/unit/strategy/data/` ratchets.

**Out:** storage/container unification, `_fleet_resource_pool` deletion, `TransferValidator.VALID_CARGO_TYPES` removal, `RESOURCE_TYPES` removal, transfer UI rewrite, or any other PROJ-436/437 scope; temporal scheduler / 100-tick model changes (`#2`); battle-boundary work already covered by PROJ-426; broad 910-caller removal of the high-value `ShipInstance` entry-point shims unless a narrower state-surface cleanup naturally reduces them; product semantics such as `Empire.is_eliminated()` behavior when only `MineGroup`s remain.

## Dependencies
**Hard predecessors:** PROJ-436 and PROJ-437 complete and merged. This charter assumes their intended end states are real, not hypothetical.

**Soft back-links:** PROJ-423 (GameSession lifecycle extraction), PROJ-424 (order metadata convergence), PROJ-425 (ShipInstance slimming), and PROJ-429 (ability metadata unification). PROJ-438 should build on those seams, not recreate them.

**No worktrees** per user standing preference. Serial execution in the main checkout.

## Key Files
| Component | File Path |
|-----------|-----------|
| Game session shell | `game/strategy/engine/game_session.py` |
| Canonical bootstrap | `game/strategy/engine/session/bootstrap.py` |
| Persistence rehydrate path | `game/strategy/engine/session/persistence_adapter.py` |
| Turn rollback restore path | `game/strategy/engine/turn_state_snapshot.py` |
| Facade / grouped namespaces | `game/strategy/facade/strategy_session_facade.py`, `game/strategy/facade/grouped_namespaces.py`, `game/strategy/facade/slices/_facade_state.py` |
| State-heavy entities | `game/strategy/data/planet.py`, `game/strategy/data/planet_serde.py`, `game/strategy/data/fleet.py`, `game/strategy/data/empire.py`, `game/strategy/data/ship_instance.py`, `game/strategy/data/ship_instance_serializer.py`, `game/strategy/data/ship_instance_bridge.py` |
| Strategic intent command catalog | `game/strategy/engine/commands/__init__.py`, `game/strategy/engine/commands/registry.py`, `game/strategy/engine/commands/order_metadata_view.py` |
| Planet command path | `game/strategy/engine/planet_command_handlers.py`, `game/strategy/engine/planet_action_engine.py`, `game/strategy/engine/component_activation_engine.py` |
| Fleet/planet action execution | `game/strategy/engine/action_execution_engine.py`, `game/strategy/engine/order_processor.py`, `game/strategy/engine/order_handlers/base.py`, `game/strategy/engine/order_handlers/registry_factory.py` |
| Order persistence | `game/strategy/data/order_types.py`, `game/strategy/data/order_serializer.py` |
| Public seams / protocols | `game/core/protocols/strategy_domain.py`, `game/core/protocols/strategy_mutators.py`, `game/strategy/data/galaxy_protocols.py` |
| High-signal docs | `docs/systems/strategy_layer.md`, `docs/systems/orders_system.md`, `docs/04_SERVICES.md`, `docs/systems/ability_reference.md`, `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md` |

Full enumeration in [manifest.md](manifest.md).

## Phases

### Phase 0: Post-436/437 audit freeze + verification gate decision
Re-read the completed PROJ-436/437 artifacts and confirm the exact remaining contact surfaces for `#1` and `#3`. Default to fixing the current full-suite visibility gap for `tests/unit/strategy/data/` so the canonical sharded runner actually covers the highest-signal ratchets in this area; only fall back to a documented supplemental verification matrix if the collection fix proves materially riskier than expected. Record the resolved decision in `decisions.md` and the detailed contact map in `findings/`.

### Phase 1: Canonical graph restoration path
Consolidate the shared graph-repair steps between `SessionPersistenceAdapter.rehydrate_state()` and `TurnStateSnapshot.restore()`: galaxy backrefs, fleet registration, order-target rebinding, pursuer-tracker rebuild, and any remaining runtime-wiring repairs. The outcome should be one canonical restoration path or one shared restoration collaborator rather than duplicated knowledge.

### Phase 2: Session / facade projection boundary cleanup
Further narrow `GameSession` and the façade read side after PROJ-423. This phase is specifically about the remaining mixed session concerns: `save_path`, `human_player_ids`, derived `active_empire` / `enemy_empire`, lazy race-registry/config ownership, and the shared façade cache/projection holder. The goal is clearer separation between owned runtime state and derivable read projections, not a new façade API redesign.

### Phase 3: ShipInstance residual state-surface consolidation
After PROJ-436 storage work, revisit `ShipInstance` as a state root. Reduce remaining serializer/bridge/cache/design-template coupling where feasible without forcing the 910-caller shim sweep. Update the public protocol/DTO/serializer surfaces that still assume the old broad entity shape.

### Phase 4: Planet / Fleet / Empire state-surface slimming
Address only the bounded aggregate-root residue that remains after storage moves out: `Planet`'s save-schema breadth and directly-owned adjunct state, `Fleet`/`Empire` persistence-facing aggregate behavior, and the matching read contracts in `galaxy_protocols.py`. This phase is about narrowing the proven residual surface, not about inventing reducers/repositories from scratch. If the Phase 0 audit finds no high-value extractions beyond this bounded list, Phase 4 may collapse to a smaller protocol/doc sync instead of forcing a cosmetic entity rewrite.

### Phase 5: Typed planet strategic intents
Replace the current stringly `IssuePlanetOrderCommand(order_type: str, target: dict)` path with a typed strategic-intent contract for planet ability activation/deactivation. The goal is to remove the ad hoc command-string mapping and make planet strategic intents look like first-class commands rather than a multiplexed escape hatch.

### Phase 6: Issuer-aware execution contract cleanup
Clean up the remaining fleet/planet execution grafts. Replace `ActionExecutionEngine`’s private `_handler_registry` reach-in and `TypeError` fallback with one explicit issuer-aware execution contract. Reconcile `PlanetActionEngine`, `ActionExecutionEngine`, and the order-handler interface so the remaining planet/FMS splits are intentional, typed, and guard-tested.

### Phase 7: Order persistence + metadata-driven serialization convergence
Make order persistence derive more directly from live executable metadata. Revisit `CommandSpec.serializer_codec`, `Order.to_dict()`, `OrderSerializer`, and the post-load rebinding/removal of dead references. Default stance from D3: treat `IMPLICIT_ACTION_ORDER_TYPES`, mission decomposition, and the `JOIN_FLEET` instant path as acceptable specialized behavior unless the implementation audit proves they still leak across contracts in a way that blocks the main cleanup.

### Phase 8: DTO / protocol / doc sync + Codex consult remediation
Update affected protocols, DTO builders, façade surfaces, and docs to the post-438 state. Then run the required Codex consult; any verified findings become added phases per the end-of-project workflow.

## Related Documents
- [blank_sheet_remediation_r003.md](../../../AgentCoordination/Scratchpad/Discussion/20260517T150720Z_strategy-layer-blank-sheet/plans/blank_sheet_remediation_r003.md) — original post-435 remediation consensus
- [PROJ-436 plan](../PROJ-436/plan.md) — assumed-complete storage/container substrate project
- [PROJ-437 plan](../PROJ-437/plan.md) — assumed-complete transfer UI project
- [design.md](design.md) — detailed audit synthesis and project rationale
- [decisions.md](decisions.md) — design decisions and deferred questions
- [manifest.md](manifest.md) — phase-by-phase file touch map

## Verification
- [ ] All phase checklists complete
- [ ] All phase-specific focused tests passing
- [ ] Sharded suite green plus any explicit supplemental direct-run tests if the `tests/unit/strategy/data/` visibility gap remains
- [ ] Docs and public seams updated consistently
- [ ] Codex consult completed; verified findings remediated
- [ ] User verified
