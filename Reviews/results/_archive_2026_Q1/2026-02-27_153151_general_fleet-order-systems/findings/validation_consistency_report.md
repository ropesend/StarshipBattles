# Validation Consistency Analysis: Fleet Order Validation Layer

## Summary
- Total issues found: 14
- Critical: 2, Major: 5, Minor: 5, Info: 2

## Architecture Overview

The fleet order validation system operates across four distinct layers:

1. **UI Layer** (`game/ui/screens/`) - Pre-command validation (e.g., `ColonizationSystem.on_colonize_click()` checks `facade.can_colonize()` before creating commands)
2. **Command Handler Layer** (`game/strategy/engine/command_handlers.py`, `superweapon_command_handlers.py`) - Validates before creating `FleetOrder` objects and adding them to queue
3. **Dedicated Validator Layer** (`game/strategy/validation/`) - Three validator classes: `ColonizeValidator`, `TransferValidator`, `SuperweaponValidator`
4. **Execution Layer** (`game/strategy/engine/fleet_order_processor.py`, `superweapon_order_processor.py`, `fleet_movement_engine.py`) - Runtime re-validation when orders actually execute

### Validator Coverage by OrderType

| OrderType | Dedicated Validator | Command Handler Validation | Execution-Time Validation |
|---|---|---|---|
| MOVE | No | Path check in `MoveCommandHandler` | Resource check in `FleetMovementEngine` |
| WARP | No | Warp capability + warp point check in `WarpCommandHandler` | Resource + capability check in `FleetMovementEngine` |
| MOVE_TO_FLEET | No | Fleet resolution only in `InterceptCommandHandler` | None (implicit - fleet tracks target) |
| JOIN_FLEET | No | Fleet resolution only in `JoinCommandHandler` | Location check in `FleetOrderProcessor.process_join_fleet()` |
| COLONIZE | **ColonizeValidator** | Via `TurnEngine.validate_colonize_order()` | Re-validates via `ColonizeValidator.validate()` with `skip_chain_check=True` |
| TRANSFER | **TransferValidator** | Full validation in `TransferCommandHandler` | Re-validates via `TransferValidator.validate()` |
| LOAD_POPULATION | **TransferValidator** (reused) | Created internally by colonize handlers, no command | Re-validates via `TransferValidator.validate()` |
| UNLOAD_POPULATION | **TransferValidator** (reused) | No dedicated command handler | Re-validates via `TransferValidator.validate()` |
| BUILD | No | Planet resolution only in `BuildShipCommandHandler` | Implicit (queue empty = auto-pop) |
| IMPLODE_PLANET | **SuperweaponValidator** | `validate_implode_planet()` called | Ability re-check in processor |
| STELLERATE_STAR | **SuperweaponValidator** | `validate_stellerate_star()` called | System check in processor |
| OPEN_WARP_POINT | **SuperweaponValidator** | `validate_open_warp_point()` called | System + target check in processor |
| CLOSE_WARP_POINT | **SuperweaponValidator** | `validate_close_warp_point()` called | System + warp point check in processor |
| CREATE_DYSON_SPHERE | **SuperweaponValidator** | `validate_create_dyson_sphere()` called | System + star check in processor |
| SELF_DESTRUCT | **SuperweaponValidator** | `validate_self_destruct()` called | Ship existence check in processor |

---

## Findings

### CRITICAL: Superweapon Direct Commands Skip Ability Validation at Command Time

**ID:** VC-001
**Location:** `game/strategy/engine/superweapon_command_handlers.py:30-178`
**Issue:** All six direct superweapon command handlers (ImplodePlanet, StellerateStar, OpenWarpPoint, CloseWarpPoint, CreateDysonSphere, SelfDestruct) call their respective `SuperweaponValidator.validate_*()` methods WITHOUT passing `component_registry`. The `component_registry` parameter is Optional and defaults to `None`, which causes the validator to skip the ability check entirely. For example, `ImplodePlanetCommandHandler.execute()` (line 46) calls `validate_implode_planet(session.galaxy, fleet, planet)` - no registry. The validator at line 58-63 of `superweapon_validator.py` only checks abilities `if component_registry is not None`.

This means a fleet WITHOUT the DestroyPlanet ability can successfully queue an IMPLODE_PLANET order. The check only happens at execution time (in `SuperweaponOrderProcessor`), where the fallback code at line 96-97 uses `fleet.ships[0]` as a substitute -- potentially destroying an innocent ship instead of the correct one.

**Impact:** Players can queue superweapon orders on fleets that lack the required abilities. At execution time, the wrong ship may be consumed, or the order may silently succeed without proper ability gating.
**Recommendation:** Pass `session.turn_engine._registries.components` to all superweapon validator calls in the command handlers, consistent with how `ColonizeCommandHandler` passes it via `TurnEngine.validate_colonize_order()`.
**Effort:** Simple

---

### CRITICAL: Superweapon Mission Commands Skip ALL Business Validation

**ID:** VC-002
**Location:** `game/strategy/engine/superweapon_command_handlers.py:225-347`
**Issue:** All five superweapon mission command handlers (`ImplodePlanetMissionCommandHandler`, `StellerateStarMissionCommandHandler`, etc.) only validate pathfinding (via `_setup_mission_move()`). They do NOT call any `SuperweaponValidator` methods. For example, `ImplodePlanetMissionCommandHandler.execute()` resolves fleet and planet, calls `_setup_mission_move()`, then directly queues the action order. It never calls `SuperweaponValidator.validate_implode_planet()`.

Compare with `ColonizeMissionCommandHandler` (lines 276-372) which performs full colony pod validation including pod type matching and chain exhaustion checks before queuing.

**Impact:** Mission commands (move + action) bypass all business-rule validation. A fleet without any superweapon ability can queue a mission to move across the galaxy and attempt planet destruction. The order only fails at execution time, wasting player turns. This is particularly bad for Stellerate Star (suicide weapon) where the fleet would have traveled for many turns before discovering it lacks the ability.
**Recommendation:** Add `SuperweaponValidator` calls to all mission command handlers, matching the pattern used for colonize missions. The validators already exist; they just need to be wired in.
**Effort:** Simple

---

### MAJOR: BUILD Order Has No Validation Whatsoever

**ID:** VC-003
**Location:** `game/strategy/engine/command_handlers.py:206-219`, `game/ui/screens/strategy_build_queue_manager.py:122-142`
**Issue:** The `BuildShipCommandHandler` only resolves the planet and immediately calls `planet.add_production()` without any validation. It does not check:
- Whether the planet belongs to the player's empire
- Whether the planet has a shipyard capable of building the design
- Whether the design exists or is valid
- Whether the player can afford the design

Similarly, `_handle_fleet_build_queue_close()` in the UI directly inserts `FleetOrder(OrderType.BUILD)` into the fleet's order queue without any validation checks.

There is no `BuildValidator` class.

**Impact:** Invalid build orders can be queued. The `ProductionEngine` handles some edge cases during execution (design loading failures, missing save paths), but fundamental precondition checks are absent. The UI's `BuildQueueController` provides informal gating (filtering designs by category/capability), but this is UI-only and not enforced at the command layer.
**Recommendation:** Create a `BuildValidator` class or add validation to `BuildShipCommandHandler` covering: planet ownership, shipyard capability, design existence, and resource affordability. This would be consistent with the existing validator pattern.
**Effort:** Medium

---

### MAJOR: Inconsistent Ownership Validation Across Command Handlers

**ID:** VC-004
**Location:** `game/strategy/engine/command_handlers.py:52-71`
**Issue:** `BaseCommandHandler._resolve_fleet()` accepts an optional `empire_id` parameter for ownership validation, but NO command handler actually passes it. Every handler calls `self._resolve_fleet(session, cmd.fleet_id)` without the ownership check. This means any command can target any fleet, regardless of ownership.

The only handler that does any ownership-related check is `TransferCommandHandler` (lines 411-419), which searches for the owning empire in `session.empires` -- but this is done for context, not for authorization.

**Impact:** In multiplayer or scenarios with AI empires, a player could potentially issue orders to enemy fleets. Currently mitigated by the UI only presenting the player's own fleets, but the command layer lacks enforcement.
**Recommendation:** Either pass `empire_id` to `_resolve_fleet()` in all handlers, or add ownership validation to the `_resolve_fleet()` method by default. The GameSession has `empires` context available.
**Effort:** Medium

---

### MAJOR: ColonizeMissionCommand Duplicates Validator Logic Inline

**ID:** VC-005
**Location:** `game/strategy/engine/command_handlers.py:296-326`
**Issue:** `ColonizeMissionCommandHandler.execute()` performs colony pod validation inline (lines 297-326) by directly calling `ColonizeValidator.find_ship_with_colony_pod()` and `ColonizeValidator.get_available_colony_pods()`. This duplicates logic that already exists inside `ColonizeValidator.validate()` (which handles both pod type matching and chain exhaustion checks in a single call).

Meanwhile, `ColonizeCommandHandler.execute()` (lines 126-171) delegates to `TurnEngine.validate_colonize_order()`, which in turn calls `ColonizeValidator.validate()`.

**Impact:** If the validation logic in `ColonizeValidator.validate()` is updated (e.g., new planet type rules), the inline copy in `ColonizeMissionCommandHandler` may not be updated, leading to divergent behavior. This is a maintenance risk.
**Recommendation:** Have `ColonizeMissionCommandHandler` call `ColonizeValidator.validate()` directly instead of reimplementing the same checks inline.
**Effort:** Simple

---

### MAJOR: LOAD_POPULATION / UNLOAD_POPULATION Orders Created Without Command Handlers

**ID:** VC-006
**Location:** `game/strategy/engine/command_handlers.py:146-157, 340-352`
**Issue:** `LOAD_POPULATION` and `UNLOAD_POPULATION` order types exist in `OrderType` but have NO corresponding command classes or command handlers. They are only created internally by `ColonizeCommandHandler` (line 156) and `ColonizeMissionCommandHandler` (line 351) as implicit "auto-load population" steps.

These orders bypass the normal command validation pipeline entirely. They are constructed with hardcoded parameters and inserted directly into the fleet's order queue. The `TransferValidator` handles them at execution time (the processor checks `OrderType.TRANSFER, OrderType.LOAD_POPULATION, OrderType.UNLOAD_POPULATION` together), but there is no pre-queue validation.

**Impact:** No validation of cargo capacity, population availability, or species existence before these orders are queued. If the auto-load assumptions are wrong (e.g., colony has no population, fleet has no cargo capacity), the order silently fails at execution time, which the player never sees feedback for.
**Recommendation:** Either (a) add pre-queue validation when these orders are created inside the colonize handlers, or (b) create proper command handlers and commands for explicit population transfer orders.
**Effort:** Medium

---

### MAJOR: Superweapon Order Processor Uses Fallback Ship When Registry is None

**ID:** VC-007
**Location:** `game/strategy/engine/superweapon_order_processor.py:96-97, 264-265, 356-357, 434-435`
**Issue:** Multiple processor methods (process_implode_planet, process_open_warp_point, process_close_warp_point, process_create_dyson_sphere) have fallback code like:
```python
if ship is None:
    ship = fleet.ships[0] if fleet.ships else None
```
This fallback activates when `component_registry` is None OR when no ship has the required ability. It silently selects the first ship in the fleet and destroys it, regardless of whether that ship has anything to do with the superweapon.

**Impact:** When the component registry is not available (e.g., in certain test scenarios or edge cases), an arbitrary ship is consumed instead of the correct one. If the validation at command time also fails to check abilities (see VC-001), this compounds into a situation where the wrong ship is always destroyed.
**Recommendation:** Remove the `ships[0]` fallback and instead fail the operation when no ship with the required ability is found, regardless of whether the registry is available. The `component_registry` should always be provided in production code paths.
**Effort:** Simple

---

### MINOR: Validator Interface Inconsistency - Static Methods vs. Instance Methods

**ID:** VC-008
**Location:** `game/strategy/validation/colonize_validator.py`, `game/strategy/validation/transfer_validator.py`, `game/strategy/validation/superweapon_validator.py`
**Issue:** All three validator classes use `@staticmethod` methods exclusively. While this is consistent among themselves, it diverges from the `IValidationRule` protocol defined in `game/core/validation.py` (lines 23-60), which expects instance methods with signature `def validate(self, context: Any) -> ValidationResult`. None of the validators implement this protocol.

Additionally, `ColonizeValidator.validate()` and `TransferValidator.validate()` have different parameter signatures. ColonizeValidator takes `(galaxy, fleet, target_planet, component_registry, skip_chain_check)` while TransferValidator takes `(galaxy, fleet, target, cargo_type, direction, amount, species_id, skip_location_check, projected_cargo)`. There is no common interface.

**Impact:** Validators cannot be used polymorphically. Code cannot treat validators generically (e.g., iterating over validators and calling `.validate(context)`). This is an architectural inconsistency but does not cause bugs.
**Recommendation:** Either adopt the `IValidationRule` protocol for fleet order validators (wrapping the static methods), or document that fleet order validators intentionally use a different pattern. Consider creating a common `IOrderValidator` protocol.
**Effort:** Medium

---

### MINOR: Redundant Validation Between Command Handler and Execution - Intentional Defense-in-Depth

**ID:** VC-009
**Location:** `game/strategy/engine/command_handlers.py:140-141` (ColonizeCommandHandler validates), `game/strategy/engine/fleet_order_processor.py:208-215` (re-validates at execution)
**Issue:** COLONIZE and TRANSFER orders are validated both at command time (in the handler) and at execution time (in `FleetOrderProcessor`). This is redundant -- the same validator is called twice with similar parameters.

For COLONIZE: `ColonizeCommandHandler` calls `validate_colonize_order()` -> `ColonizeValidator.validate()` at line 141. Then `FleetOrderProcessor.process_colonize()` calls `ColonizeValidator.validate()` again at line 209 (with `skip_chain_check=True`).

For TRANSFER: `TransferCommandHandler` calls `TransferValidator.validate()` at line 436. Then `FleetOrderProcessor.process_transfer()` calls `TransferValidator.validate()` again at line 357.

**Impact:** This is actually GOOD practice -- defense-in-depth. Game state can change between command issuance and execution (e.g., planet colonized by another fleet, target destroyed). The execution-time validation catches stale orders. However, this pattern should be documented and applied consistently to ALL order types.
**Recommendation:** Document this as intentional defense-in-depth. Ensure all order types that have command-time validation also have execution-time validation (currently superweapon orders have partial execution-time validation but no command-time ability checks -- see VC-001).
**Effort:** Simple (documentation only)

---

### MINOR: Diagnostic Logging Left in TransferCommandHandler

**ID:** VC-010
**Location:** `game/strategy/engine/command_handlers.py:401-466`
**Issue:** `TransferCommandHandler.execute()` contains 8 `logger.info()` calls prefixed with "DIAG" that appear to be debugging diagnostics left in production code. Examples:
- Line 401: `f"DIAG TransferCommandHandler: cmd fleet_id={cmd.fleet_id}..."`
- Line 434: `f"DIAG TransferCommandHandler: cargo capacity={capacity}..."`
- Line 441: `f"DIAG TransferCommandHandler: validation result is_valid=..."`

Similarly, `TransferValidator._validate_load()` (lines 164-190) has multiple `logger.info("DIAG ...")` calls.

**Impact:** Log noise. These verbose diagnostic messages pollute production logs and make it harder to identify real issues.
**Recommendation:** Either remove these DIAG lines entirely, or downgrade them to `logger.debug()` level.
**Effort:** Simple

---

### MINOR: Movement Validation Inconsistency Between MOVE and WARP

**ID:** VC-011
**Location:** `game/strategy/engine/command_handlers.py:174-203` (MoveCommandHandler), `game/strategy/engine/command_handlers.py:471-511` (WarpCommandHandler)
**Issue:** `MoveCommandHandler` validates by checking path existence (line 187: `path = session.preview_fleet_path(fleet, cmd.target_hex)`), but allows a no-op when the fleet is already at the target (line 190-191). It does NOT check fleet resources or movement capability.

`WarpCommandHandler` validates warp capability (line 484: `fleet.can_use_warp()`), warp point existence (line 494), and provides helpful error messages including the limiting ship's name. But it does NOT check warp resources at command time -- only at movement time in `FleetMovementEngine`.

Neither handler checks whether the fleet has enough fuel/resources to reach the destination.

**Impact:** Players can queue orders that will fail at execution time due to insufficient resources. The fleet will be "stranded" (cleared orders) partway through, which may be confusing. However, this may be intentional since resource state can change (e.g., resupply mid-journey).
**Recommendation:** Consider adding a warning (not error) when resources are insufficient for the full journey, so the UI can inform the player without preventing the order.
**Effort:** Medium

---

### MINOR: InterceptCommandHandler and JoinCommandHandler Have No Target Validity Checks

**ID:** VC-012
**Location:** `game/strategy/engine/command_handlers.py:222-273`
**Issue:** `InterceptCommandHandler` and `JoinCommandHandler` resolve the target fleet but perform no validation beyond existence:
- No check for whether the target fleet is hostile (for intercept, this might be intentional)
- No check for whether target fleet belongs to the same owner (for join, merging with an enemy fleet would be nonsensical)
- No check for whether the target fleet is reachable (path existence)
- No check for whether the fleets are even in the same galaxy sector

**Impact:** A player could issue a JOIN order targeting an enemy fleet. At execution time, `process_join_fleet()` would attempt the merge if co-located, potentially creating weird state. In practice, the UI likely prevents this by only showing friendly fleets as join targets.
**Recommendation:** Add ownership validation for JOIN_FLEET orders (target fleet must have the same `owner_id`). For INTERCEPT/MOVE_TO_FLEET, allow any fleet but document the behavior.
**Effort:** Simple

---

### INFO: No Centralized Validation Error Feedback to UI

**ID:** VC-013
**Location:** Various - `game/strategy/engine/command_handlers.py`, `game/strategy/engine/fleet_order_processor.py`
**Issue:** When validation fails at EXECUTION time (inside `FleetOrderProcessor`), the order is silently popped (`fleet.pop_order()`) with only a `logger.warning()`. There is no mechanism to notify the player that their queued order failed. For example:
- `process_colonize()` line 214: logs warning, pops order, returns `ColonizeResult(colonized=False)`
- `process_transfer()` line 363: logs warning, pops order, returns `TransferResult(success=False)`

The results are returned to `process_end_turn_orders()` but never surfaced to the UI or the event log (no `log_event()` call on failure).

When validation fails at COMMAND time (in handlers), the `ValidationResult` is returned to the GameSession, which does propagate it to the UI. So command-time failures ARE visible to the player.

**Impact:** Players lose orders silently during turn processing with no feedback. For orders that take many turns to reach (long-distance colonize missions), this is especially frustrating -- the fleet arrives, fails silently, and sits idle.
**Recommendation:** Add `log_event()` calls for execution-time validation failures with appropriate `EventType` values (e.g., `ORDER_FAILED`), so they appear in the player's event log.
**Effort:** Medium

---

### INFO: ValidationResult Error Codes Not Consistently Applied

**ID:** VC-014
**Location:** `game/strategy/validation/colonize_validator.py`, `game/strategy/validation/transfer_validator.py`, `game/strategy/engine/command_handlers.py`
**Issue:** `ColonizeValidator` uses structured error codes (e.g., `code="NO_CANDIDATES"`, `code="ALREADY_OWNED"`, `code="NO_COLONY_POD"`, `code="COLONY_POD_EXHAUSTED"`). `TransferValidator` also uses structured codes (e.g., `code="FLEET_NOT_FOUND"`, `code="NO_CARGO_SPACE"`, `code="NO_POPULATION"`).

However, `SuperweaponValidator` does NOT use error codes -- all errors are plain messages. Similarly, `BaseCommandHandler._resolve_fleet()` and `_resolve_planet()` return errors without codes.

The `ValidationResult` class supports both string codes and `ErrorCode` enum values, but most of the codebase uses ad-hoc strings when they use codes at all.

**Impact:** Programmatic error handling (e.g., UI showing specific icons or taking corrective actions based on error type) is only possible for COLONIZE and TRANSFER orders. Other order types cannot be differentiated programmatically.
**Recommendation:** Add error codes to `SuperweaponValidator` methods and `BaseCommandHandler` resolution methods, following the established pattern from `ColonizeValidator`.
**Effort:** Simple

---

## Top 5 Priority Issues

1. **VC-002 (CRITICAL)** - Superweapon mission commands skip ALL business validation. A fleet without any superweapon ability can queue a mission and waste many turns traveling before failing. Fix is simple: add validator calls to all mission handlers.

2. **VC-001 (CRITICAL)** - Superweapon direct commands skip ability validation because `component_registry` is not passed. Fix is simple: pass the registry to validator calls.

3. **VC-003 (MAJOR)** - BUILD orders have no validation at all. No ownership check, no capability check, no design validity check. Needs a `BuildValidator` or inline checks in the handler.

4. **VC-007 (MAJOR)** - Superweapon processors use `fleet.ships[0]` fallback, potentially destroying wrong ships. Combined with VC-001/VC-002, this creates a chain of failures where the wrong ship is consumed for an ability it doesn't have.

5. **VC-013 (INFO)** - Execution-time validation failures are silent. Players lose orders with no feedback, especially painful for long-distance missions. Adding event log entries would significantly improve player experience.
