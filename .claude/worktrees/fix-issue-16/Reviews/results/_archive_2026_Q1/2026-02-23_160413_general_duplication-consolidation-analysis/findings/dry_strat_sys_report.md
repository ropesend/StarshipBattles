# DRY-STRAT-SYS: Strategy Engine, Services, Facade, Systems Report

## Summary
- **Total duplication findings:** 15
- **Critical:** 3, **Major:** 6, **Minor:** 6

## Findings

### CRITICAL: Fleet/Planet Lookup Duplication (Three-Site)
**ID:** CQ-001
**Location:** `game_session.py:208-232`, `strategy_session_facade.py:79-90`, `command_handlers.py:84-91`
**Issue:** Fleet lookup logic duplicated across three locations with variations: O(1) galaxy lookup + O(n) fallback vs direct O(n) iteration. Facade adds no value - just delegates.
**Impact:** Maintenance burden; inconsistent performance; confusion about canonical lookup.
**Recommendation:** Make GameSession._get_fleet_by_id canonical; remove facade wrapper; update all handlers.
**Effort:** Simple

### CRITICAL: Superweapon Order Processor Pattern Duplication
**ID:** CQ-002
**Location:** `fleet_order_processor.py:158-277`, `superweapon_order_processor.py:48-589`, `superweapon_command_handlers.py:27-343`
**Issue:** 500+ lines of near-identical order processing: validate → find ship → execute → pop order → check empty → log event. This pattern repeats for every superweapon type across two files.
**Impact:** Bug divergence; adding new superweapons requires changes in two places; massive testing burden.
**Recommendation:** Create SuperweaponProcessorBase with common lifecycle; subclasses implement only `_execute_action()`. Would eliminate 60-70% of duplication.
**Effort:** Complex

### CRITICAL: Validator Common Pattern Extraction
**ID:** CQ-003
**Location:** `colonize_validator.py:51-175`, `superweapon_validator.py:35-309`, `transfer_validator.py:20-224`
**Issue:** All validators follow identical pattern: check entity exists → check target → check permissions → check location → return ValidationResult. Also duplicate ability-finding logic.
**Impact:** Changes to error handling require updates in three places; inconsistent validation flow.
**Recommendation:** Create ValidatorBase with template method pattern; consolidate error codes to enum.
**Effort:** Medium

### MAJOR: Command Handler Duplication
**ID:** CQ-004
**Location:** `command_handlers.py:73-340`, `superweapon_command_handlers.py:222-343`
**Issue:** All mission handlers repeat identical pattern: resolve fleet → setup move → queue action order. Only the action order differs.
**Impact:** Adding new mission handlers requires copy-paste.
**Recommendation:** Create MissionCommandHandler base class with template method.
**Effort:** Simple

### MAJOR: Order Processing Lifecycle Duplication
**ID:** CQ-005
**Location:** `fleet_order_processor.py:63-277`, `superweapon_order_processor.py:69-580`
**Issue:** Every order processor method follows: get order → validate type → execute → pop order → return. Repeated 10+ times.
**Recommendation:** Create OrderProcessor abstraction with `_validate_and_get_order()` and `_execute()`.
**Effort:** Medium

### MAJOR: DTO Conversion Pattern Duplication
**ID:** CQ-006
**Location:** `empire_dto.py`, `fleet_dto.py`, `planet_dto.py` (5+ from_X methods)
**Issue:** Every DTO implements near-identical `from_X()` classmethod pattern.
**Impact:** Copy-paste temptation when adding new DTOs.
**Recommendation:** Create DTOFactory or use dataclass-based auto-generation.
**Effort:** Medium

### MAJOR: Event Logging Duplication
**ID:** CQ-007
**Location:** 7+ locations in fleet_order_processor.py and superweapon_order_processor.py
**Issue:** Every event log follows: `log_info(...)` then `log_event(EventType.X, category=..., empire_id=..., message=...)` repeated 7+ times.
**Recommendation:** Create `EventLogger.log_order_completion(order_type, empire, message, **details)`.
**Effort:** Simple

### MAJOR: Validator Entity Resolution Duplication
**ID:** CQ-008
**Location:** `superweapon_validator.py` (4 methods), `transfer_validator.py:74-81`, command handlers
**Issue:** `galaxy.get_system_at_location()` called in every validator method independently. No "find system containing X" utility.
**Recommendation:** Add utility methods to Galaxy or create SpatialValidator.
**Effort:** Simple

### MAJOR: Validation Result Creation Duplication
**ID:** CQ-013
**Location:** 36 ValidationResult creations across 3 validators
**Issue:** `ValidationResult(is_valid=False, errors=["..."], error_code="...")` repeated 36 times with inconsistent error_code usage.
**Recommendation:** Create `ValidationBuilder.invalid(message, code)`.
**Effort:** Simple

### Minor: Component Inspection Extraction (Partially Done)
**ID:** CQ-009
**Issue:** ComponentInspector created (good!) but ColonizeValidator still has own `_iterate_colony_pods`.
**Recommendation:** Deprecate custom iterators; use ComponentInspector directly.
**Effort:** Simple

### Minor: Error Code Standardization
**ID:** CQ-010
**Issue:** Inconsistent error code patterns across validators. No centralized enum.
**Recommendation:** Create ValidationErrorCode enum.
**Effort:** Simple

### Minor: Fleet Utility Method Consolidation
**ID:** CQ-011
**Issue:** Fleet lookup via empire iteration duplicated. Addressed by CQ-001.
**Effort:** Covered by CQ-001

### Minor: Path Setup Pattern in Mission Handlers
**ID:** CQ-012
**Issue:** `_setup_mission_move` logic duplicated between regular and superweapon mission handlers.
**Recommendation:** Extract to shared utility at module level.
**Effort:** Simple

### Minor: EventType/EventCategory String Handling
**ID:** CQ-014
**Issue:** Two locations manually handle enum-to-string `.value` coercion.
**Recommendation:** Move coercion to EventType/EventCategory utilities.
**Effort:** Simple

### Minor: Facade Delegation Pattern
**ID:** CQ-015
**Issue:** Facade is thin wrapper - 40+ methods that mostly delegate. Unique value is DTO conversion only.
**Recommendation:** Design decision - document that facade is primarily DTO safety contract.
**Effort:** N/A

## Top 5 Priority Consolidation Opportunities
1. **CQ-002**: Superweapon processor consolidation - 500+ lines, Complex, Highest ROI
2. **CQ-001**: Fleet lookup canonicalization - Simple, Clarifies responsibility
3. **CQ-003**: Validator base pattern - Medium, Standardizes error handling
4. **CQ-004**: Mission command handler base - Simple, Eliminates copy-paste
5. **CQ-005**: Order processing lifecycle - Medium, Centralizes order completion
