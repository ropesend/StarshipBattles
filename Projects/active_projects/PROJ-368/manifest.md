# PROJ-368 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files modified or created

| File | Type | Phase | Notes |
|------|------|-------|-------|
| `game/strategy/engine/order_processor.py` | Production (modify across all phases; net deletion) | 1, 2, 3, 4 | Phase 1: `process_join_fleet` + `process_instant_orders` become one-line delegates to `OrderHandlerRegistry`. Phase 2: `process_colonize` → delegate. Phase 3: `process_transfer` → delegate. Phase 4: delete every private helper (`_execute_*`, `_load/unload_pod_*`, `_deploy_drop_pod`, `_validate_tick_inputs`, `_elect_canonical_merges`, `_emit_join_cancelled`, `_execute_fleet_merge`); `execute_action_order` becomes a 5-line registry lookup. Final: ≤ 200 LOC facade. |
| `game/strategy/engine/order_handlers/__init__.py` | Production (new) | 1 | Re-exports + `__all__`. Phase 1 exports `IOrderHandler`, `BaseOrderHandler`, `OrderHandlerRegistry`, `JoinFleetHandler`, `OrderExecutionResult`, `create_default_order_handler_registry`. Phases 2-4 add new handlers. |
| `game/strategy/engine/order_handlers/base.py` | Production (new) | 1 | `IOrderHandler` Protocol; `BaseOrderHandler` mixin (with `_emit_event` helper); `OrderHandlerRegistry`; `OrderExecutionResult` dataclass. ≤ 200 LOC target. |
| `game/strategy/engine/order_handlers/registry_factory.py` | Production (new) | 1, 2, 3, 4 | `create_default_order_handler_registry(event_bus)` — composes the registry. Phase 1 registers `JoinFleetHandler`. Phase 2 adds Colonize + SelfDestruct. Phase 3 adds Transfer (under 3 OrderType keys). Phase 4 adds 5 superweapon adapters built from `SUPERWEAPON_SPECS`. |
| `game/strategy/engine/order_handlers/join_fleet.py` | Production (new) | 1 | `JoinFleetHandler` — owns `process_instant_orders` (BUG-122 3-phase), `execute_action_order` (single-fleet — see Open Question Q3), `_elect_canonical_merges`, `_emit_join_cancelled`, `_execute_fleet_merge`, `_validate_tick_inputs`. ≤ 250 LOC. |
| `game/strategy/engine/order_handlers/colonize.py` | Production (new) | 2 | `ColonizeHandler` — owns `execute_action_order` (was `process_colonize`) + `_deploy_drop_pod`. ≤ 200 LOC. |
| `game/strategy/engine/order_handlers/self_destruct.py` | Production (new) | 2 | `SelfDestructHandler` — lifted from `superweapon_order_processor.py:664-740`. ≤ 130 LOC. |
| `game/strategy/engine/order_handlers/transfer.py` | Production (new) | 3 | `TransferHandler` — owns `execute_action_order` (was `process_transfer`) + 7 explicit `_dispatch_*` methods + `_resolve_target_fleet_by_id`. Folds in `_execute_load`, `_execute_unload`, `_execute_fleet_transfer`, `_load_pod_from_staging_yard`, `_unload_pod_to_staging_yard`. ≤ 400 LOC. |
| `game/strategy/engine/order_handlers/superweapons.py` | Production (new) | 4 | `SuperweaponHandlerAdapter` — wraps existing `SuperweaponOrderProcessor.process_*` methods via `SUPERWEAPON_SPECS`. `_build_superweapon_handlers(processor)` factory. **5 adapters** (SELF_DESTRUCT was lifted in Phase 2). ≤ 100 LOC. |
| `game/strategy/engine/superweapon_order_processor.py` | Production (modify) | 2 | Phase 2: delete `process_self_destruct` (lifted into `order_handlers/self_destruct.py`). No other changes. |
| `game/strategy/interfaces/engines.py` | Production (modify) | 1 | Update `IOrderProcessor` docstring at lines 168-230 to reference the new handler-registry implementation. **Public method signatures unchanged.** |
| `tests/unit/strategy/engine/order_handlers/__init__.py` | Test (new) | 1 | Empty — Python package marker. |
| `tests/unit/strategy/engine/order_handlers/conftest.py` | Test (new) | 1 | Shared fixtures (`mock_fleet`, `mock_planet`, `mock_empire`, `captured_event_bus`). Lift from existing `tests/unit/strategy/engine/test_order_processor_*.py` helpers. |
| `tests/unit/strategy/engine/order_handlers/test_base.py` | Test (new) | 1 | Registry contract: `register`, `get`, `__contains__`, `all_registered`. Protocol conformance: `isinstance(handler, IOrderHandler)`. ~80 LOC, ~6 tests. |
| `tests/unit/strategy/engine/order_handlers/test_join_fleet_handler.py` | Test (new) | 1, 5 | Phase 1: focused unit tests for `JoinFleetHandler.process_instant_orders` (BUG-122 mutual-pair canonicalization, Phase C aliveness, both cancellation reasons), `execute_action_order` happy/unhappy. Phase 5: expand to ≥ 8 tests. |
| `tests/unit/strategy/engine/order_handlers/test_colonize_handler.py` | Test (new) | 2, 5 | Phase 2: focused unit tests for `ColonizeHandler.execute_action_order` (happy, validation failure, missing drop pod, "Any" planet sentinel, COLONY_FOUNDED event payload exact-match). |
| `tests/unit/strategy/engine/order_handlers/test_self_destruct_handler.py` | Test (new) | 2, 5 | Phase 2: focused unit tests for `SelfDestructHandler.execute_action_order` (happy with multi-ship, empty target, fleet-emptied detection, SHIPS_SELF_DESTRUCTED event payload). |
| `tests/unit/strategy/engine/order_handlers/test_transfer_handler.py` | Test (new) | 3, 5 | Phase 3: focused unit tests covering all 7 dispatch branches + BUG-70 auto-resolve. ≥ 12 tests. |
| `tests/unit/strategy/engine/order_handlers/test_superweapon_dispatch.py` | Test (new) | 4 | Adapter dispatch — assert each `OrderType` in `SUPERWEAPON_SPECS \ {SELF_DESTRUCT}` routes to the correct `SuperweaponOrderProcessor.process_*` method. Mock the processor; verify forwarding. |
| `tests/unit/strategy/engine/order_handlers/test_order_processor_facade.py` | Test (new) | 5 | AST static guard: < 200 LOC, no `if order.type == OrderType.X` branches, every `ACTION_ORDER_TYPES \ PLANET_ACTION_ORDER_TYPES + {JOIN_FLEET}` has a registered handler. |
| `tests/unit/strategy/engine/test_order_processor_colonize.py` | Test (preserve) | 2 | **Unchanged.** Continues to drive `OrderProcessor.process_colonize` (now a delegate). Acts as integration smoke for the facade-to-handler wiring. |
| `tests/unit/strategy/engine/test_order_processor_transfer.py` | Test (preserve) | 3 | **Unchanged.** Continues to drive `OrderProcessor.process_transfer`. |
| `tests/unit/strategy/engine/test_order_processor_instant.py` | Test (preserve) | 1 | **Unchanged.** Continues to drive `OrderProcessor.process_instant_orders`. |
| `tests/unit/strategy/engine/test_order_processor_fleet_merge.py` | Test (preserve OR delete pending Q3) | 1 | If `process_join_fleet` is dead production code (Open Question Q3), delete this 88-LOC file. Otherwise preserve unchanged. |
| `tests/unit/strategy/engine/test_action_execution_engine.py` | Test (verify) | 4 | Verify still passes — `ActionExecutionEngine._execute_action` calls `self._order_processor.execute_action_order(...)`; the facade delegate keeps this invariant. |
| `tests/unit/strategy/engine/test_action_execution_engine_gaps.py` | Test (verify) | 4 | Same as above. |
| `tests/unit/strategy/turn_engine/test_default_tick_phase_list.py` | Test (verify) | 1 | Verify still passes — references `e.order_processor.process_instant_orders`. |
| `tests/integration/strategy/test_mutual_join_rendezvous.py` | Test (verify) | 1 | End-to-end smoke for BUG-122. Must pass. |
| `tests/integration/strategy/test_pod_transfer.py` | Test (verify) | 3 | End-to-end smoke for drop-pod transfer. Must pass. |
| `tests/integration/strategy/test_fleet_order_transfer.py` | Test (verify) | 3 | End-to-end smoke for fleet-to-fleet transfer. Must pass. |
| `tests/integration/strategy/test_multi_pod_colonization.py` | Test (verify) | 2 | End-to-end smoke for COLONIZE + drop pod deploy. Must pass. |
| `docs/systems/strategy_layer.md` | Documentation (modify) | 5 | Add §"Order handlers (PROJ-368)" subsection mirroring the existing §"Command handlers" pattern (if present). Update `> **Last verified:**` blockquote per PROJ-307. |
| `docs/02_PATTERNS.md` | Documentation (modify) | 5 | Add cross-reference: the strategy layer has two registry-based dispatch systems — `engine/handlers/` (UI command → order creation) and `engine/order_handlers/` (action tick → state mutation). Note the parallel structure. Update `> **Last verified:**` blockquote. |
| `AgentCoordination/Scratchpad/reviews/strategy_layer_tech_debt_2026-05-05.md` | Project doc (modify) | 5 | Mark target #1 (OrderProcessor) as resolved by PROJ-368 commit `<sha>`. |
