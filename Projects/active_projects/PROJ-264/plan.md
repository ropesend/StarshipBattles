# PROJ-264: Strategy Engine Test Coverage

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-264` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-264 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Planet Command Handlers + Order Validator | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Order Processor Fleet Transfer + Staging Yard | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Facade Dispatch Helpers | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-04-09
**Active Phase:** 1
**Last Action:** Plan written
**Next Action:** Read source files, write failing tests for `IssuePlanetOrderCommandHandler`
**Blockers:** None

## Overview
This project closes the worst coverage gaps in the strategy engine layer by writing new tests against existing production code. The three target areas are planet command handlers (17.9% covered), planet order validator (15.0% covered), and order processor fleet-transfer/staging-yard paths (0% covered on multiple methods), plus the 26 facade dispatch helpers that have zero coverage. All work follows TDD: write a failing test, verify it fails for the right reason, then confirm it passes against existing production code. No production code changes are expected.

## Goals
- Raise `planet_command_handlers.py` coverage from 17.9% to 90%+
- Raise `planet_order_validator.py` coverage from 15.0% to 90%+
- Cover the 5 zero-coverage methods in `order_processor.py` (fleet transfer, resource load/unload, staging yard load/unload)
- Cover BUG-70 auto-resolve colony path in `order_processor.py`
- Cover all 26 `dispatch_*` methods and 2 build queue query methods in `strategy_session_facade.py`

## Scope
**In:**
- New test files for the 4 source files listed in Key Files
- Mock-based unit tests (no integration tests, no production code changes)
- Coverage verification after each phase

**Out:**
- Production code changes (these are coverage gaps in working code)
- Integration or end-to-end tests
- Other strategy engine files not listed below
- Changes to the Combat Lab / simulation test framework

## Design Approach

All tests use `unittest.mock` (Mock/MagicMock) to isolate the unit under test from its dependencies. Each test class targets a single handler/validator/method and follows the Arrange-Act-Assert pattern:

1. **Arrange:** Build mocks for GameSession, Planet, PlanetaryFacility, Fleet, Empire, Galaxy as needed
2. **Act:** Call the production method under test
3. **Assert:** Verify the returned `ValidationResult` (success/error) and any side effects (order queued, cargo moved, etc.)

**Key mock patterns established in the codebase:**
- `tests/unit/strategy/facade/test_strategy_session_facade.py` -- mock session/empire/fleet construction
- `tests/unit/strategy/engine/test_fleet_order_transfer.py` -- mock fleet/empire/galaxy for OrderProcessor

## Key Files
| Component | File Path |
|-----------|-----------|
| Planet Command Handlers (source) | `game/strategy/engine/planet_command_handlers.py` |
| Planet Order Validator (source) | `game/strategy/validation/planet_order_validator.py` |
| Order Processor (source) | `game/strategy/engine/order_processor.py` |
| Strategy Session Facade (source) | `game/strategy/facade/strategy_session_facade.py` |
| Command definitions | `game/strategy/engine/commands.py` |
| Order types | `game/strategy/data/order_types.py` |
| PlanetaryFacility | `game/strategy/data/planetary_facility.py` |
| ActivationPhase | `game/strategy/data/component_activation_state.py` |
| BaseCommandHandler._resolve_planet | `game/strategy/engine/command_handlers.py` |
| **New test: planet command handlers** | `tests/unit/strategy/engine/test_planet_command_handlers.py` |
| **New test: planet order validator** | `tests/unit/strategy/validation/test_planet_order_validator.py` |
| **New test: fleet transfer extended** | `tests/unit/strategy/engine/test_fleet_transfer_extended.py` |
| **New test: staging yard operations** | `tests/unit/strategy/engine/test_staging_yard_operations.py` |
| **New test: facade dispatch** | `tests/unit/strategy/facade/test_facade_dispatch.py` |

## Phase Details

### Phase 1: Planet Command Handlers + Order Validator (17.9% / 15.0% coverage)

These two files handle planet order issuance and validation. They are tightly coupled -- the handlers call the validator -- so testing them together ensures full path coverage.

**Test file 1: `test_planet_command_handlers.py`**

Target: 4 handler classes (IssuePlanetOrderCommandHandler, ClearPlanetOrdersCommandHandler, DeletePlanetOrderCommandHandler, SetAtmosphereTargetCommandHandler)

Test cases for `IssuePlanetOrderCommandHandler.execute()`:
- Planet not found (via _resolve_planet returning error)
- Planet owned by different empire (ownership check)
- Unknown order type string (KeyError on OrderType)
- ACTIVATE_ABILITY without ability_name
- DEACTIVATE_ABILITY without ability_name
- ACTIVATE_ABILITY with validation failure (validator returns error)
- ACTIVATE_ABILITY success -- verify order queued with correct target dict
- ACTIVATE_ABILITY with component_key and component_id -- verify target dict includes both
- DEACTIVATE_ABILITY success path
- Unsupported order type (not ACTIVATE/DEACTIVATE)

Test cases for `ClearPlanetOrdersCommandHandler.execute()`:
- Planet not found
- Wrong owner
- Success -- verify `planet.clear_orders()` called

Test cases for `DeletePlanetOrderCommandHandler.execute()`:
- Planet not found
- Wrong owner
- Index out of range (negative)
- Index out of range (>= len)
- Success -- verify correct order popped

Test cases for `SetAtmosphereTargetCommandHandler.execute()`:
- Planet not found
- Wrong owner
- Success with atmosphere target dict
- Success with empty dict (clear target)

**Test file 2: `test_planet_order_validator.py`**

Target: 3 static methods (validate_activate_ability, validate_deactivate_ability, _facility_has_ability)

Test cases for `validate_activate_ability()`:
- Facility not found on planet
- Facility not operational
- Facility lacks the named ability
- Component-key path: component already ACTIVE
- Component-key path: component already ACTIVATING
- Component-key path: conflicting activation order already queued
- Component-key path: success (INACTIVE component, no conflicts)
- Legacy path (no component_key): ability already active via active_abilities
- Legacy path: activation already queued in orders
- Legacy path: success

Test cases for `validate_deactivate_ability()`:
- Facility not found
- Facility not operational
- Facility lacks ability
- Component-key path: component not active or activating (INACTIVE)
- Component-key path: success (component is ACTIVE)
- Component-key path: success (component is ACTIVATING)
- Legacy path: ability not active and no pending activation order
- Legacy path: success when ability is active
- Legacy path: success when activation order pending (deactivate before it completes)

Test cases for `_facility_has_ability()`:
- Component is dict with ability in abilities dict
- Component is dict without ability, but component_registry has it
- Component is string reference, registry has ability
- Component is string reference, registry lacks ability
- No components match

**Estimated new tests:** ~35-40

### Phase 2: Order Processor Fleet Transfer + Staging Yard (0% on 5 methods)

These are the uncovered execution paths in `order_processor.py`. Each method is independent and testable in isolation with mocks.

**Test file 3: `test_fleet_transfer_extended.py`**

Target: `_execute_fleet_transfer()`, resource-cargo paths in `_execute_load()` / `_execute_unload()`, BUG-70 auto-resolve

Test cases for `_execute_fleet_transfer()`:
- Unload direction: transfers from fleet to target_fleet
- Load direction: transfers from target_fleet to fleet
- Caps by source cargo available
- Caps by destination space available
- Amount=0 means transfer all available
- Zero available space returns 0
- Zero source cargo returns 0

Test cases for `_execute_load()` resource cargo path (non-passenger, non-drop_pod):
- Loads from planet stockpile to fleet cargo
- Caps by fleet available space
- Caps by planet stockpile amount
- Amount=0 loads maximum possible
- Zero stockpile returns 0
- Verify `planet.consume_from_stockpile` and `fleet.resources.load_cargo_to_fleet` called

Test cases for `_execute_unload()` resource cargo path:
- Unloads from fleet cargo to planet stockpile
- Caps by fleet current cargo
- Amount=0 unloads all
- Zero cargo returns 0
- Verify `fleet.resources.unload_cargo_from_fleet` and `planet.add_to_stockpile` called

Test cases for BUG-70 auto-resolve colony:
- LOAD_POPULATION with no planet_id and no target_fleet_id: finds owned colony at fleet hex
- No owned colony at fleet hex: returns success with skip message
- Colony found: uses it as transfer target

**Estimated new tests:** ~20-25

**Test file 4: `test_staging_yard_operations.py`**

Target: `_load_pod_from_staging_yard()`, `_unload_pod_to_staging_yard()`

Test cases for `_load_pod_from_staging_yard()`:
- Loads pod from staging yard to ship carried_items
- Filters by pod_name when provided
- Skips pods that don't match pod_name
- Caps by amount parameter
- Amount=0 loads all that fit
- No ship has capacity: pod stays in staging yard
- Multiple ships: fills first with capacity
- Multiple pods: loads in reverse order

Test cases for `_unload_pod_to_staging_yard()`:
- Unloads pod from ship to staging yard
- Filters by pod_name when provided
- Amount=0 unloads all
- Caps by amount parameter
- Multiple ships: iterates through all
- `add_to_staging_yard` returns False: pod stays on ship

**Estimated new tests:** ~15-18

### Phase 3: Facade Dispatch Helpers (zero coverage, 26 methods)

All 26 `dispatch_*` methods follow an identical pattern: import a command class, instantiate it with `**kwargs`, pass it to `self.handle_command()`, return the result. Testing is mechanical but provides regression safety that ensures the correct command class is wired to each dispatch method.

**Test file 5: `test_facade_dispatch.py`**

Strategy: For each dispatch method, verify:
1. The correct Command subclass is instantiated
2. `handle_command()` is called with that command
3. The return value from `handle_command()` is propagated

Implementation approach: Use `unittest.mock.patch` to mock the command class import inside each dispatch method, then verify the command was constructed with the expected kwargs and passed to `handle_command`.

Alternative (simpler): Mock `self.handle_command` on the facade, call each dispatch method with test kwargs, and verify `handle_command` was called once with a command of the correct type and the kwargs forwarded.

The 26 dispatch methods and their command classes:
1. `dispatch_issue_colonize` -> `IssueColonizeCommand`
2. `dispatch_issue_move` -> `IssueMoveCommand`
3. `dispatch_issue_intercept` -> `IssueInterceptCommand`
4. `dispatch_issue_join_fleet` -> `IssueJoinFleetCommand`
5. `dispatch_queue_colonize_mission` -> `QueueColonizeMissionCommand`
6. `dispatch_clear_orders` -> `ClearOrdersCommand`
7. `dispatch_issue_transfer` -> `IssueTransferCommand`
8. `dispatch_issue_implode_planet` -> `IssueImplodePlanetCommand`
9. `dispatch_issue_stellerate_star` -> `IssueStellerateStarCommand`
10. `dispatch_issue_open_warp_point` -> `IssueOpenWarpPointCommand`
11. `dispatch_issue_close_warp_point` -> `IssueCloseWarpPointCommand`
12. `dispatch_issue_create_dyson_sphere` -> `IssueCreateDysonSphereCommand`
13. `dispatch_issue_self_destruct` -> `IssueSelfDestructCommand`
14. `dispatch_queue_implode_planet_mission` -> `QueueImplodePlanetMissionCommand`
15. `dispatch_queue_stellerate_star_mission` -> `QueueStellerateStarMissionCommand`
16. `dispatch_queue_open_warp_point_mission` -> `QueueOpenWarpPointMissionCommand`
17. `dispatch_queue_close_warp_point_mission` -> `QueueCloseWarpPointMissionCommand`
18. `dispatch_queue_create_dyson_sphere_mission` -> `QueueCreateDysonSphereMissionCommand`
19. `dispatch_issue_warp` -> `IssueWarpCommand`
20. `dispatch_issue_build_order` -> `IssueBuildOrderCommand`
21. `dispatch_remove_build_order` -> `RemoveBuildOrderCommand`
22. `dispatch_split_fleet` -> `SplitFleetCommand`
23. `dispatch_delete_order` -> `DeleteOrderCommand`
24. `dispatch_reorder_order` -> `ReorderOrderCommand`
25. `dispatch_add_to_construction_queue` -> `AddToConstructionQueueCommand`
26. `dispatch_remove_from_construction_queue` -> `RemoveFromConstructionQueueCommand`
27. `dispatch_reorder_construction_queue` -> `ReorderConstructionQueueCommand`
28. `dispatch_issue_planet_order` -> `IssuePlanetOrderCommand`
29. `dispatch_clear_planet_orders` -> `ClearPlanetOrdersCommand`
30. `dispatch_delete_planet_order` -> `DeletePlanetOrderCommand`
31. `dispatch_set_atmosphere_target` -> `SetAtmosphereTargetCommand`

Additional test cases for build queue queries:
- `get_empire_build_queues` with valid empire_id
- `get_empire_build_queues` with unknown empire_id returns []
- `get_hex_build_queues` with valid empire_id and hex
- `get_hex_build_queues` with unknown empire_id returns []

**Estimated new tests:** ~35 (31 dispatch + 4 query)

## Total Estimated Tests
~90-100 new tests across 5 test files

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [manifest.md](manifest.md) - File manifest for conflict detection
- [Test Review Report](../../Reviews/results/2026-04-08_test-review/final_report.md) - Source of coverage data

## Verification
- [ ] Phase 1 checklist complete (planet command handlers + validator)
- [ ] Phase 2 checklist complete (fleet transfer + staging yard)
- [ ] Phase 3 checklist complete (facade dispatch)
- [ ] All new tests passing
- [ ] Full test suite green (`python Tools/test_sharded/test_sharded.py`)
- [ ] Coverage improved on target files (spot-check with `pytest --cov`)
