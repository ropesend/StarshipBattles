# Validation Report: Validator 2

## Summary
- **Findings Reviewed:** 13
- **Confirmed:** 8
- **Downgraded:** 3
- **Rejected:** 2
- **Rejection Rate:** 15%

## Verdicts

#### Finding: CP-001
**Original Severity:** Critical
**Verdict:** DOWNGRADED(Major)
**Reason:** The bypass is real -- `handle_global_event` on line 386 of `fleet_orders_window.py` calls `self.fleet.clear_orders()` directly instead of dispatching a `ClearFleetOrdersCommand` through the facade. However, Critical severity is excessive for a single-player game where the `ClearOrdersCommandHandler` only clears orders and logs (no validation, audit, or security logic). The practical impact is limited to a missed log message. Major is more appropriate.

#### Finding: CP-002
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified at `strategy_build_queue_manager.py` lines 128-142. The `_handle_fleet_build_queue_close` method directly constructs `FleetOrder(OrderType.BUILD)` and inserts into `fleet.orders`, and also removes BUILD orders via list comprehension. No `IssueBuildCommand` class or handler exists in the registry. The inconsistency with the pipeline pattern is accurately described.

#### Finding: CP-003
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified identical auto-load population blocks at `command_handlers.py` lines 235-246 (`ColonizeCommandHandler`) and lines 430-441 (`ColonizeMissionCommandHandler`). The code is nearly verbatim, including the redundant inner guard `if origin_colony.populations` inside a block already guarded by the same condition. Extracting to a shared helper is straightforward.

#### Finding: CP-004
**Original Severity:** Major
**Verdict:** REJECTED
**Reason:** The finding claims `ColonizeCommandHandler` does NOT check colony pod availability or chain limits. This is incorrect. The handler calls `session.turn_engine.validate_colonize_order()` which delegates to `ColonizeValidator.validate()` with `component_registry=self._registries.components`. That validator performs both `find_ship_with_colony_pod` checks (line 162) and chain limit checks via `get_available_colony_pods`/`get_committed_colony_pods` (lines 172-185). Both handlers get pod validation; they simply take different code paths to achieve it.

#### Finding: CP-005
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified in `superweapon_command_handlers.py`. All five mission handlers (lines 223-344) only resolve fleet/planet and call `_setup_mission_move()`. None of them invoke any `SuperweaponValidator.validate_*()` method, while all six direct handlers (lines 30-178) do call the validator. The validation gap is real -- queued missions skip capability checks that direct commands enforce.

#### Finding: CP-006
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Confirmed 9 `logger.info("DIAG ...")` calls in `TransferCommandHandler` at lines 488-549 of `command_handlers.py`. All are at `info` level and prefixed with "DIAG", indicating temporary debugging instrumentation that was not cleaned up.

#### Finding: CP-007
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified in `commands.py`. All 20 command subclasses define explicit `__init__` methods that set `self.type = CommandType.ISSUE_ORDER` and assign fields, defeating the `@dataclass` auto-generated constructor. The boilerplate is real and the recommendation to use `__post_init__` or a `field(init=False, default=...)` pattern is sound.

#### Finding: CP-008
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified at `fleet_orders_window.py` lines 271-318. The `move_order()`, `delete_order()`, and `undo_delete()` methods directly manipulate `self.fleet.orders` (list swap, pop, insert) and `self.fleet.path`. No corresponding command classes exist for reorder or delete operations. The finding accurately describes a pipeline bypass for these operations.

#### Finding: CP-009
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified that `BaseCommandHandler._resolve_fleet()` accepts an optional `empire_id` parameter (line 91), but a grep of all `_resolve_fleet(session, cmd.` calls across `command_handlers.py` shows none pass the `empire_id` argument. The observation is accurate, and the severity is appropriate for a single-player game.

#### Finding: CP-010
**Original Severity:** Minor
**Verdict:** DOWNGRADED(Info)
**Reason:** The finding itself acknowledges "Accept current state" with effort "N/A (accepted)" and explains why full unification is impractical. This is an architectural observation, not an actionable issue. Info severity is more appropriate since the finding recommends no action.

#### Finding: CP-011
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Confirmed via grep: no references to `IssueWarpCommand` exist in the `game/ui/` directory. The command and handler are fully implemented but have no UI entry point. The finding correctly notes this may not be a bug if warp traversal is handled via MOVE orders.

#### Finding: CP-012
**Original Severity:** Info
**Verdict:** DOWNGRADED(Info)
**Reason:** The finding claims the handler iterates all empires with O(E*F) complexity, but the actual code (line 497-501) uses `fleet.owner_id` as a direct index into `session.empires` -- this is O(1), not O(E*F). A PROJ-204 comment on line 497 confirms this was already refactored. However, the dead code observation is valid: `owning_empire` is assigned on line 501 but never referenced again in the method. Downgraded because the primary claim (O(E*F) loop) is already fixed; only the dead variable assignment remains.

#### Finding: CP-013
**Original Severity:** Info
**Verdict:** REJECTED
**Reason:** This is a positive observation ("the architectural pattern is well-adopted"), not a finding about an issue. It has no action item and no impact. Positive observations should not be tracked as findings in a code review.
