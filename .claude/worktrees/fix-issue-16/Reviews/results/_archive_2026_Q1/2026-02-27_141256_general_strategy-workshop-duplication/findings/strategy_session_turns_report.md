# Strategy Session & Turn Logic DRY Analysis

### Summary
- Total issues found: 12
- Critical: 0, Major: 6, Minor: 5, Info: 1

### Findings

#### MAJOR: Mission Move Setup Logic Duplicated Across 6 Handlers
**ID:** CQ-40
**Location:** `superweapon_command_handlers.py:185-222`, `command_handlers.py:328-364`, and 4 superweapon mission handlers (lines 241-346)
**Issue:** Nearly identical "move then act" setup pattern appears in 7 handlers. All share identical pattern: determine start hex, calculate path, queue MOVE if needed.
**Impact:** 7 handlers contain near-identical 20-line blocks. Any bug fix must be applied in 7 places.
**Recommendation:** Extract to `MissionSetupHelper.setup_mission_move()`. Extend ColonizeMissionCommandHandler to use same helper.
**Effort:** Simple

#### MAJOR: Fleet Resolution Pattern in 19 Command Handlers
**ID:** CQ-41
**Location:** 19 handlers across `command_handlers.py` and `superweapon_command_handlers.py`
**Issue:** 19 handlers use identical pattern: `fleet, error = self._resolve_fleet(session, cmd.fleet_id); if error: return error`. Inconsistent error messages in 2 handlers.
**Impact:** Pattern duplication in 19 places (3 lines each). If error handling changes, must update 19 locations.
**Recommendation:** Create wrapper method or decorator in `BaseCommandHandler` to eliminate the boilerplate.
**Effort:** Simple

#### MAJOR: Path Stripping Logic Duplicated 4 Times
**ID:** CQ-42
**Location:** `game_session.py:178-179`, `command_handlers.py:362-364`, `command_handlers.py:201`, `superweapon_command_handlers.py:218-220`
**Issue:** All handlers remove start hex from path if it matches fleet location. Code appears 4 times with slight variations. MoveCommandHandler doesn't strip start hex - potential inconsistency.
**Impact:** Inconsistent path stripping logic. Bug risk.
**Recommendation:** Extract `PathHelper.strip_start_hex(fleet, path)` utility.
**Effort:** Simple

#### MAJOR: Same-Location Movement Check Scattered Across 5 Handlers
**ID:** CQ-43
**Location:** `command_handlers.py:162, 190, 355, 449, 501`
**Issue:** Multiple handlers check if fleet needs to move to target location. Semantically identical but written 5 different ways.
**Impact:** 5 locations doing same logic with different structures. Inconsistent error handling.
**Recommendation:** Create `CommandHelper.add_move_order_if_needed(fleet, target_hex)`.
**Effort:** Simple

#### MAJOR: Tick Interval Calculation Duplicated in 2 Engines
**ID:** CQ-44
**Location:** `fleet_movement_engine.py:228-230` and `action_execution_engine.py:124`
**Issue:** Both engines calculate tick interval with identical formula: `interval = max(1, int(100 // speed))`.
**Impact:** Formula duplication. If speed calculation changes, both need updating.
**Recommendation:** Extract to `SpeedHelper.get_tick_interval(speed)` utility.
**Effort:** Simple

#### MAJOR: Planet Existence/Location Check Duplicated in 5+ Command Handlers
**ID:** CQ-45
**Location:** `command_handlers.py:137-139, 291-295, 422-425`, `superweapon_command_handlers.py:41-43, 236-238`
**Issue:** Three slightly different approaches handling "resolve planet, maybe optional" semantics.
**Impact:** Cognitive burden. Inconsistent error handling for missing planets.
**Recommendation:** Standardize with optional parameter: `_resolve_planet_optional(session, planet_id, required=False)`.
**Effort:** Simple

#### Minor: Superweapon Handler Structure Has Copy-Paste Pattern
**ID:** CQ-46
**Location:** `superweapon_command_handlers.py:30-178` (6 handlers)
**Issue:** All 6 direct superweapon handlers follow identical 3-step pattern (resolve fleet, resolve target, validate, apply).
**Impact:** Hard to add new superweapon: must copy-paste entire handler class.
**Recommendation:** Create `SuperweaponCommandHandler` base class with template method pattern.
**Effort:** Medium

#### Minor: Validation Result Error Message Inconsistency
**ID:** CQ-47
**Location:** Multiple locations across `command_handlers.py`
**Issue:** Error messages inconsistent in format and terminology across 15+ handlers.
**Impact:** Inconsistent messaging. Hard to test for specific errors.
**Recommendation:** Define error message constants in central `CommandErrors` class.
**Effort:** Simple

#### Minor: Moving Fleet Auto-Queueing Order Pattern Duplicated
**ID:** CQ-48
**Location:** `command_handlers.py:159-164, 449-451, 501-503`
**Issue:** Multiple handlers auto-queue a MOVE order if fleet isn't at destination. 10 lines per handler x 3 handlers.
**Impact:** Code duplication. If move-queueing logic changes, update 3+ places.
**Recommendation:** Extract `CommandHelper.queue_move_to_planet_if_needed()`.
**Effort:** Simple

#### Minor: Log Message Structure Follows Repeated Pattern
**ID:** CQ-49
**Location:** 15+ handlers across both command handler files
**Issue:** Log messages follow identical template: `"GameSession: Issued {ORDER_TYPE} Order for Fleet {fleet.id}"` in 15+ handlers.
**Impact:** Minor. If log format standardizes, update 15+ locations.
**Recommendation:** Create `CommandHelper.log_order_issued(logger, fleet, order_type)`.
**Effort:** Simple

#### Minor: Empire Finding Logic in TransferCommandHandler
**ID:** CQ-50
**Location:** `command_handlers.py:410-415`
**Issue:** TransferCommandHandler manually finds owning empire via O(N) loop when O(1) lookup via `fleet.owner_id` exists.
**Impact:** Inconsistent with other handlers. Unnecessary linear search.
**Recommendation:** Use `fleet.owner_id` for direct lookup.
**Effort:** Simple

#### Info: Order Type Categorization Properly Centralized
**ID:** CQ-51
**Location:** `fleet.py:39-61`
**Issue:** Good pattern - `MOVEMENT_ORDER_TYPES` and `ACTION_ORDER_TYPES` frozensets properly centralized. No consolidation needed.
**Impact:** None - this is the right approach.
**Recommendation:** No action needed.
**Effort:** N/A

### Top 5 Priority Issues
1. **CQ-40**: Mission Move Setup (MAJOR) - 140 lines duplication across 7 handlers
2. **CQ-41 + CQ-45**: Fleet/Planet Resolution (MAJOR) - 19 handlers with boilerplate
3. **CQ-42**: Path Stripping Logic (MAJOR) - Potential bug in MoveCommandHandler
4. **CQ-43 + CQ-48**: Movement Order Auto-Queueing (MAJOR) - Same-location checks in 5 handlers
5. **CQ-44**: Tick Interval Formula (MAJOR) - Simple consolidation
