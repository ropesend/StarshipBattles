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
| 0. Post-436/437 audit freeze + verification gate decision | Complete | [phase_0_checklist.md](phase_0_checklist.md) |
| 1. Canonical graph restoration path | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Session / facade projection boundary cleanup | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. ShipInstance residual state-surface consolidation | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Planet / Fleet / Empire state-surface slimming | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Typed planet strategic intents | Complete | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Issuer-aware execution contract cleanup | Complete | [phase_6_checklist.md](phase_6_checklist.md) |
| 7. Order persistence + metadata-driven serialization convergence | Complete | [phase_7_checklist.md](phase_7_checklist.md) |
| 8. DTO / protocol / doc sync + Codex consult remediation | Complete | [phase_8_checklist.md](phase_8_checklist.md) |
| 9. Bundled small follow-ups from Codex consult | Complete | [phase_9_checklist.md](phase_9_checklist.md) |
| 10. Behavioral E2E test for ActionExecutionEngine planet-FMS tick | Deferred | [phase_10_checklist.md](phase_10_checklist.md) |

## Current State
**Last Updated:** 2026-05-18
**Active Phase:** PROJ-438 COMPLETE through Phase 9. Phase 10 deferred as standalone follow-up.

**Status:**
- Phases 0–8 committed across 2 commits (`820d6d4b8` Phases 0–7, `fd6b456ab` Phase 8 doc sync).
- Codex consult run on `20260518T153829Z`. Response at `AgentCoordination/Scratchpad/Consult/20260518T153829Z_proj-438-end-of-project/response.md`. 6 verified findings; bundled small items into Phase 9, deferred medium engine-tick behavioral test as Phase 10.
- Phase 9 (bundled consult follow-ups): framing fix in decisions.md, duplicate-codec consistency ratchet, `MOVE_TO_FLEET` parity coverage, planet ability order save/load round-trip. 27 affected tests green.
- Phase 10 (deferred): behavioral E2E test through `ActionExecutionEngine._process_planet_action_tick` for planet FMS. Checklist created with full briefing for a future contributor; not blocking PROJ-438.
- Final sharded suite: see Phase 9 close-out artifacts (pending final commit's verification run).

**Next Action:** Final close-out commit + sharded suite verification + project-archive consideration.

**Blockers:** None. Phase 10 is intentionally deferred, not blocked.

**Context for Next Agent:** PROJ-438 is functionally done. The deferred Phase 10 has a self-contained briefing in `phase_10_checklist.md` and decisions.md. The strict-green canonical baseline is the post-PROJ-438 + PROJ-436 Phase 10/11 state.
**Last Action:** Phase 3 complete. Like Phase 2, collapsed to a documentation + invariant-pinning pass after audit. Added categorical class docstring on `ShipInstance` enumerating the post-Phase-9 attribute/method categories (Owned identity / Owned durable state / Owned runtime state / Status flags / Cached & DI / Delegate-manager slots / Protocol-alias properties / Retained-shim entry points). New test file `tests/unit/strategy/ship_instance/test_post_container_surface.py` (10 ratchets: categorical shape + legacy-shim docs contracts + `IShipInstance` protocol minimum surface + cargo_contents future-removal pointer). `IShipInstance.cargo_contents` removal ruled out (30+ caller files); DTO-side narrowing ruled out (DTOs already read concrete post-storage attributes). During close-out, the Phase 2 docstring tripped the `game_session.py` 500 LOC budget (529 LOC) — fixed by shrinking the docstring to a terse category list (now 498 LOC). All ratchets remain green.
**Next Action:** Start Phase 4. Re-audit the bounded scope (Planet save-schema breadth + Fleet/Empire persistence-facing aggregate behavior + `galaxy_protocols.py` read contracts). Per decisions.md, Phase 4 MAY collapse to a smaller protocol/doc sync if no high-value extractions are found — that is a valid outcome, not a failure.
**Blockers:** None for Phases 4–7. Phase 8 still hard-blocked on PROJ-436 Phase 10 (docs) landing on `main` — stop and surface before Phase 8 if not yet merged.
**Context for Next Agent:** This project is intentionally **post-container**. Phases 2 and 3 both collapsed to documentation + invariant passes because the named concerns' blast-radius made holder/sweep approaches a façade redesign in disguise. The same pragmatic test applies to Phase 4. Phases 5/6/7 are *real implementation* (typed planet intents, issuer-aware execution, order persistence) — they should be sized at ~40 changes (Phase 5), one signature alignment (Phase 6), and a metadata-driven sync (Phase 7) per the audit's blast-radius numbers. Per-phase verification gate is **strict green** sharded suite. Phase 1/2/3 working trees are uncommitted; user controls commit timing.

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

### Phase 9: Bundled small follow-ups from Codex consult
Added 2026-05-18 from the Phase 8 Codex consult. Four small verified findings bundled: framing fix in decisions.md (planet orders flow through `planet_serde._deserialize_planet_orders → Order.from_dict()` on the `'dict'` codec branch, not `OrderSerializer._deserialize_target`); duplicate-codec consistency ratchet so `serializer_codec_for(order_type)` becomes authoritative before any future `Order.to_dict()` flip; `MOVE_TO_FLEET` parity coverage in the restore-path parity tests; planet ability order save/load round-trip pin.

### Phase 10: Behavioral E2E test for ActionExecutionEngine planet-FMS tick (DEFERRED)
Added 2026-05-18 from the Phase 8 Codex consult. Behavioral end-to-end test that drives a planet FMS recovery / launch order through `ActionExecutionEngine._process_planet_action_tick()`. Today the engine-mediated dispatch path is protected by structural / inspect-based tests plus unit-level handler tests, but no behavioral test drives the full engine tick. **Deferred** rather than blocking PROJ-438 completion: the integration fixture work is ~100-200 LOC, didn't fit the "small bundled follow-up" shape of Phase 9, and the strict-green sharded suite + unit + structural coverage protects against the specific regressions Phase 6 was designed to prevent. Self-contained briefing in `phase_10_checklist.md` for a future contributor.

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
