# Consistency Violations Sweep: Strategy

## Summary
- **Shard:** Strategy
- **Files Scanned:** 94
- **Total Issues Found:** 20
- **Critical:** 3 | **Major:** 8 | **Minor:** 5 | **Info:** 4

## Findings

#### CRITICAL: Duplicate Method Names with Inconsistent Semantics
**ID:** CON-STR-001
**Location:** `game/strategy/data/fleet.py:121-129`
**Issue:** Two methods with identical functionality but different names: add_ship(ship) and add_ship_instance(instance). Both append ship and trigger speed recalculation.
**Impact:** API ambiguity. Maintenance burden (bugs must be fixed in both). No clear convention.
**Recommendation:** Keep only add_ship(). Delete add_ship_instance() and update call sites.
**Effort:** Simple

#### CRITICAL: Inconsistent Return Type Annotations in Serialization
**ID:** CON-STR-002
**Location:** `game/strategy/data/planet.py:275`, `game/strategy/data/stars.py:45`, `game/strategy/data/empire.py:134` (use `dict`) vs `game/strategy/data/fleet.py:321` (uses `Dict[str, Any]`)
**Issue:** to_dict() methods use bare `dict` or `Dict[str, Any]` inconsistently.
**Impact:** Type checkers cannot verify code using ambiguous dict annotations.
**Recommendation:** Standardize all to Dict[str, Any]. Consider StateDict type alias.
**Effort:** Medium

#### CRITICAL: Overuse of Any Type Hint
**ID:** CON-STR-003
**Location:** `game/strategy/engine/commands.py` (16 occurrences of target_hex: Any)
**Issue:** Command constructors use Any when HexCoord is the actual expected type.
**Impact:** Type safety compromised. IDE cannot provide proper parameter documentation.
**Recommendation:** Replace Any with specific types throughout commands module.
**Effort:** Simple

#### MAJOR: Missing Return Type Hints on Public Methods
**ID:** CON-STR-004
**Location:** `game/strategy/data/galaxy.py:127-195`, `game/strategy/engine/game_session.py:161-194`
**Issue:** Critical public methods lack return type annotations (get_system_by_name, get_fleet_path_projection, etc.).
**Impact:** IDE cannot infer return types for downstream code.
**Recommendation:** Add explicit return type annotations to all public methods.
**Effort:** Medium

#### MAJOR: Inconsistent Parameter Documentation Format
**ID:** CON-STR-005
**Location:** colonize_validator.py, transfer_validator.py, superweapon_validator.py
**Issue:** Methods document some parameters with full type and description, others omit type entirely.
**Impact:** Developers must read code to understand parameter types.
**Recommendation:** Add type hints to all function signatures AND docstrings.
**Effort:** Simple

#### MAJOR: Inconsistent Parameter Naming Convention (fleet vs fleet_id)
**ID:** CON-STR-007
**Location:** `game/strategy/engine/game_session.py:168-206`
**Issue:** Some methods accept domain objects (fleet), others accept IDs (fleet_id). No convention established.
**Impact:** API confusing. Users must check each method.
**Recommendation:** Use IDs for public APIs (facade), domain objects internally.
**Effort:** Medium

#### MAJOR: Inconsistent Boolean Method Naming
**ID:** CON-STR-008
**Location:** fleet.py: is_building(), has_space_shipyard(), can_build_type(), can_use_warp()
**Issue:** All three prefixes (is_, has_, can_) used somewhat arbitrarily.
**Impact:** Developers must remember which prefix applies to each method.
**Recommendation:** Establish policy: is_ for state, has_ for possession, can_ for permission.
**Effort:** Medium

#### MAJOR: Inconsistent Docstring Format
**ID:** CON-STR-009
**Location:** Throughout strategy layer
**Issue:** Three different styles: Full with Args/Returns, Minimal one-line, Mixed partial.
**Impact:** Generated documentation inconsistent. IDE help varies.
**Recommendation:** Adopt Google-style docstrings for all public methods.
**Effort:** Medium

#### MAJOR: Inconsistent Error Handling Return Values
**ID:** CON-STR-010
**Location:** command_handlers.py (ValidationResult), fleet_movement_engine.py (MovementResult dataclass)
**Issue:** No consistent error reporting pattern. Some use ValidationResult, others custom dataclasses.
**Impact:** Difficult to compose error handling across layers.
**Recommendation:** Standardize on ValidationResult for operations that can fail.
**Effort:** Medium

#### MAJOR: Inconsistent to_dict/from_dict Signatures
**ID:** CON-STR-011
**Location:** empire.py (from_dict(data, galaxy=None)), fleet.py (from_dict(data)), galaxy.py (from_dict(data, naming_data_path=None))
**Issue:** No uniform deserialization protocol. Each class has unique requirements.
**Impact:** Makes generic serialization frameworks difficult.
**Recommendation:** All from_dict() should be self-contained, accepting only data dict.
**Effort:** Complex

#### MAJOR: Inconsistent Return Documentation
**ID:** CON-STR-006
**Location:** Throughout strategy layer
**Issue:** Some methods document return types in docstrings, others rely only on type hints or neither.
**Impact:** Dict return structures not documented.
**Recommendation:** Document return structure for every method, especially Dict returns.
**Effort:** Medium

#### MINOR: Comment Style Inconsistency in Data Structures
**ID:** CON-STR-012
**Location:** fleet.py:18-33, empire.py:18-33, planet.py:125-145
**Issue:** Inline comments use different formats and spacing.
**Impact:** Cosmetic.
**Recommendation:** Standardize comment format.
**Effort:** Simple

#### MINOR: Enum Value Naming Consistent
**ID:** CON-STR-013
**Location:** fleet.py:15-28, event_types.py:6-19
**Issue:** All enum values use UPPER_CASE consistently. No issues found.
**Impact:** None - observation.
**Recommendation:** None needed.
**Effort:** None

#### MINOR: Private Method Naming Consistent
**ID:** CON-STR-014
**Location:** Throughout modules
**Issue:** All private methods use single underscore consistently. No double-underscore abuse found.
**Impact:** None - good compliance.
**Recommendation:** None needed.
**Effort:** None

#### MINOR: Type Import Organization
**ID:** CON-STR-015
**Location:** Some files missing typing imports for hints used
**Issue:** Some files use type hints without importing from typing.
**Impact:** Low - may cause runtime issues if hints evaluated.
**Recommendation:** Ensure all type imports present.
**Effort:** Simple

#### MINOR: Dataclass Field Ordering
**ID:** CON-STR-016
**Location:** fleet_movement_engine.py:25-31
**Issue:** Need to verify non-default fields come before default fields.
**Impact:** Could cause runtime errors if violated.
**Recommendation:** Audit all dataclass definitions.
**Effort:** Simple

#### INFO: Late Import Comments Inconsistent
**ID:** CON-STR-017
**Location:** fleet.py:146-148, game_session.py:181
**Issue:** Comments explaining late imports vary in detail.
**Impact:** Low - documentation inconsistency.
**Recommendation:** Standardize late import comment format.
**Effort:** Simple

#### INFO: Missing TypedDict for Complex Returns
**ID:** CON-STR-018
**Location:** Service layer methods returning Dict[str, Any]
**Issue:** Complex dict returns without documenting structure.
**Impact:** Callers must inspect code to understand dict keys.
**Recommendation:** Create TypedDict definitions for common return types.
**Effort:** Medium

#### INFO: Inconsistent Logging Levels
**ID:** CON-STR-019
**Location:** fleet_movement_engine.py:101-118
**Issue:** Same condition sometimes logged as debug, sometimes as warning.
**Impact:** Difficult to configure logging for specific scenarios.
**Recommendation:** Establish convention: debug for decisions, warning for user-visible failures.
**Effort:** Simple

#### INFO: Inconsistent None Checking Patterns
**ID:** CON-STR-020
**Location:** Throughout modules
**Issue:** Mixed patterns: `if x is None`, `if not x`, `if x` for None checks.
**Impact:** Low readability variation.
**Recommendation:** Use explicit `if obj is None` for clarity.
**Effort:** Simple

## Top 5 Priority Issues
1. **CON-STR-001**: Duplicate add_ship methods - clear API confusion
2. **CON-STR-002**: Inconsistent return type annotations - blocks type checking
3. **CON-STR-003**: Overuse of Any type - compromises type safety
4. **CON-STR-007**: fleet vs fleet_id parameter naming - confusing API
5. **CON-STR-010**: Inconsistent error handling returns - composability issues
