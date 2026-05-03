# Validation Report: Validator 1

## Summary
- **Findings Reviewed:** 22
- **Confirmed:** 10
- **Downgraded:** 7
- **Rejected:** 5
- **Rejection Rate:** 22.7%

## Verdicts

### Order Data Model Report

#### Finding: ODM-001
**Original Severity:** Critical
**Verdict:** CONFIRMED
**Reason:** Verified that `from_dict()` stores `{'_fleet_ref': id}` and `{'_planet_ref': id}` markers (lines 456, 462 of `fleet.py`), and a codebase-wide search confirms no resolution pass exists anywhere in the game or save_game_service load path. These markers would remain as dicts, causing AttributeError when order processors access `.location` or `.id` on them.

#### Finding: ODM-002
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** The `target` field is indeed untyped and accepts many runtime types. However, this is a code smell / design issue, not a Major functional bug. The existing code works correctly in production for all current order types. The polymorphism is managed through explicit dispatch in `to_dict`, `from_dict`, and consumers. Upgrading to typed unions would be beneficial but is an enhancement, not a bug fix.

#### Finding: ODM-003
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified that `to_dict()` serializes COLONIZE planet targets via `self.target.to_dict()` (line 99), which produces a dict with keys like `id`, `name`, `location` (nested), `planet_type`, etc. In `from_dict()`, this dict has no top-level `q`/`r` and no `type` key, so it falls through all conditions and `target` remains `None`. This is a confirmed save/load data loss bug for COLONIZE orders with specific planet targets.

#### Finding: ODM-004
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** The `to_dict()` method (lines 81-104) genuinely mixes `self.type` checks (e.g., `self.type in (OrderType.TRANSFER, ...)`) with `isinstance(self.target, ...)` checks, and some branches check both. This is a real maintainability concern, accurately described and appropriately severity-rated.

#### Finding: ODM-005
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified that `BUILD` is not in either `MOVEMENT_ORDER_TYPES` or `ACTION_ORDER_TYPES`, and the test at `test_action_execution_engine.py:506` only parametrizes `ACTION_ORDER_TYPES` members, not an exhaustive check that all OrderType values are categorized. The finding accurately describes the gap.

#### Finding: ODM-006
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Positive finding confirming consistent usage of the categorization sets. Verified that both `FleetMovementEngine.collect_movements()` and `ActionExecutionEngine._process_fleet_action_tick()` correctly filter using these sets. No action needed.

#### Finding: ODM-007
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** The silent drop of unrecognized target formats is real and verified (the `from_dict()` has no `else` branch logging a warning). However, Major overstates the severity. The only known case that triggers this is ODM-003 (COLONIZE planet target), which is already reported separately. In general, this is a defensive coding improvement (add a warning log), not a Major architectural issue.

#### Finding: ODM-008
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified that `CLOSE_WARP_POINT` targets are plain strings that serialize via the `raw` fallback at line 104. The round-trip works but relies on an undifferentiated fallback handler. Accurately described at appropriate severity.

#### Finding: ODM-009
**Original Severity:** Minor
**Verdict:** DOWNGRADED(Info)
**Reason:** The finding itself acknowledges this is an intentional design choice (Commands are input-layer, FleetOrders are execution-layer) and says "No immediate action needed beyond ODM-002." This is an architectural observation, not an actionable issue on its own.

#### Finding: ODM-010
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Positive finding. Verified that command handlers follow a consistent resolve-validate-create-add pattern with shared `BaseCommandHandler` helpers. No action needed.

#### Finding: ODM-011
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** Verified that `ClearOrdersCommandHandler.execute()` (line 473 of `command_handlers.py`) directly sets `fleet.orders = []` and `fleet.path = []` instead of calling `fleet.clear_orders()`. The inconsistency is real. However, `clear_orders()` (line 330-333 of `fleet.py`) does `self.orders.clear()` and `self.path = []`, which is functionally equivalent. The finding's concern about "future logic" is speculative. This is a Minor code hygiene issue, not a Major bug.

#### Finding: ODM-012
**Original Severity:** Minor
**Verdict:** DOWNGRADED(Info)
**Reason:** The `pop(0)` on line 344 of `fleet.py` is O(n), but the finding itself acknowledges that fleet order queues are typically 1-5 items, making this a non-issue in practice. This is an observation, not an actionable problem at current queue sizes.

---

### Execution Paths Report

#### Finding: EP-001
**Original Severity:** Critical
**Verdict:** DOWNGRADED(Major)
**Reason:** Verified that `JOIN_FLEET` is in `ACTION_ORDER_TYPES` (line 54 of `fleet.py`) and also handled by `process_instant_orders()` (line 691). The dual-processing path is real. However, the Critical severity is overstated because in normal gameplay, `JOIN_FLEET` is always preceded by `MOVE_TO_FLEET` (see `command_handlers.py:354-359`), so the JOIN_FLEET order only becomes current after arrival. The edge case of issuing JOIN_FLEET without MOVE_TO_FLEET is a non-standard usage path. Still a genuine design issue that should be cleaned up.

#### Finding: EP-002
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified that `complete_order()`, `cancel_order()`, and `cancel_all_orders()` are defined in `FleetOrderProcessor` (lines 76-127) but are never called from any production code -- only from test files. Meanwhile, there are 13 direct `fleet.pop_order()` calls in `fleet_order_processor.py`, 16 in `superweapon_order_processor.py`, 1 in `action_execution_engine.py`, and 3 in `fleet_navigation_service.py`. The centralized lifecycle design is indeed bypassed universally. The pop_order counts in the finding are slightly off (14/14 vs actual 13/16) but the core issue is accurate.

#### Finding: EP-003
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** Verified that `SuperweaponOrderProcessor()` is created fresh at line 647 of `fleet_order_processor.py`. However, as the finding itself notes, `__init__` is trivially `pass` (line 50-52 of `superweapon_order_processor.py`). The class is stateless. The DI pattern violation is a minor code hygiene issue, not a Major problem. Object construction cost is negligible.

#### Finding: EP-004
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** Verified that BUILD auto-pop exists in both `ActionExecutionEngine._process_fleet_action_tick()` (lines 140-144) and `FleetOrderProcessor.process_end_turn_orders()` (lines 606-614). The ActionExecutionEngine path fires first and returns `None` before delegating, so the `process_end_turn_orders` path is indeed unreachable for BUILD orders. This is dead code duplication, but since it's unreachable it cannot diverge in behavior. Minor cleanup, not Major.

#### Finding: EP-005
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified that `fleet_movement_engine.py` calls `fleet.clear_orders()` at lines 153, 165, and 170 (stranded/warp-blocked), destroying the entire order queue. Meanwhile, `fleet_order_processor.py` and `superweapon_order_processor.py` use `fleet.pop_order()`, preserving subsequent orders. The inconsistency is real and could surprise users: a MOVE order failing due to fuel destroys a queued COLONIZE, while a COLONIZE failing preserves a queued TRANSFER.

#### Finding: EP-006
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified that `process_end_turn_orders` is called by `ActionExecutionEngine._execute_action()` during tick processing, not at end-of-turn. The docstring at line 588-589 explicitly acknowledges: "Name retained for compatibility." The method name is misleading, and the interface `IOrderProcessor` (line 202 of `engines.py`) also preserves this name.

#### Finding: EP-007
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified that `ActionTimeResolver.resolve_action_time()` checks `movement_types` at lines 85-87 and returns 0, but `ActionExecutionEngine` filters movement orders at line 136-137 before ever calling `resolve_action_time`. The movement check in ActionTimeResolver is dead code.

#### Finding: EP-008
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified that `_get_movement_order_types()` at line 48 of `action_time_resolver.py` returns `{OrderType.MOVE, OrderType.MOVE_TO_FLEET}`, missing `OrderType.WARP` which is in the canonical `MOVEMENT_ORDER_TYPES` in `fleet.py` (line 41-45). Currently harmless due to the ActionExecutionEngine filter, but a maintenance risk from having two divergent definitions.

#### Finding: EP-009
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Positive finding. Verified that `turn_engine.py` has excellent phase documentation at lines 11-24 and 347-359, with clear phase numbering and labeled comments in the code. No action needed.

#### Finding: EP-010
**Original Severity:** Info
**Verdict:** REJECTED
**Reason:** This is a subjective architectural observation praising the separation of SuperweaponOrderProcessor, not a finding with an actionable issue. It doesn't describe a problem, a risk, or even an observation that could be tracked. It's editorial content rather than a code review finding.
