# Consistency Violations Sweep: Foundation

## Summary
- **Shard:** Foundation
- **Files Scanned:** 40
- **Total Issues Found:** 19
- **Critical:** 5 | **Major:** 6 | **Minor:** 8 | **Info:** 0

## Findings

#### CRITICAL: Error Code String Literal vs Enum Inconsistency
**ID:** CON-FND-001
**Location:** `game/ai/strategy_manager.py:48` ("AI001"), `game/core/exceptions.py:18` ("V002"), `game/core/exceptions.py:29` ("P003"), `game/core/validation.py:89` ("E001")
**Issue:** ErrorCode enum exists in error_codes.py but raw strings used in 4 locations. "AI001" and "E001" don't exist in the enum.
**Impact:** Programmatic error handling unpredictable. Violates PROJ-45 error code standardization.
**Recommendation:** Standardize all error codes to use ErrorCode.ENUM_NAME.value pattern.
**Effort:** Medium

#### CRITICAL: Inconsistent Static Method Naming Convention
**ID:** CON-FND-002
**Location:** `game/ai/controller.py:269,277` (_stat_ prefix) vs `game/ai/target_evaluator.py:403,416` (_default_ prefix)
**Issue:** Two different naming prefixes for static utility methods with identical purpose. _stat_get_hp_percent() vs _default_get_hp_percent() do the same thing.
**Impact:** Cognitive load for API discovery. Indicates incomplete refactoring.
**Recommendation:** Rename all _stat_* to _default_* for consistency.
**Effort:** Simple

#### CRITICAL: Missing Return Type on Helper Method
**ID:** CON-FND-003
**Location:** `game/ai/controller.py:97-106` (get_engage_distance_multiplier)
**Issue:** Returns float but has no return type hint. All other AIController methods have return type hints.
**Impact:** Breaks type checking consistency in AIController.
**Recommendation:** Add -> float return type hint.
**Effort:** Simple

#### CRITICAL: Inconsistent IControllable Protocol Documentation
**ID:** CON-FND-004
**Location:** `game/ai/interfaces/controllable.py:138-141`
**Issue:** is_alive() lacks clear semantic documentation. Protocol doesn't clarify if "alive" means "operational", "has HP > 0", or "not derelict". Other boolean methods use get_is_thrusting() getter prefix inconsistently.
**Impact:** Ambiguous semantics across implementations.
**Recommendation:** Add clear docstring. Standardize boolean method naming.
**Effort:** Simple

#### CRITICAL: Invalid Error Code in Documentation Example
**ID:** CON-FND-005
**Location:** `game/core/validation.py:89`
**Issue:** Docstring example shows code="E001" but this code doesn't exist in ErrorCode enum. Valid codes are V###, S###, R###, P###, F###, C###.
**Impact:** Copy-paste errors from documentation. Developers learn wrong pattern.
**Recommendation:** Update to use valid ErrorCode value.
**Effort:** Simple

#### MAJOR: StrategyManager Thread Safety Gap
**ID:** CON-FND-006
**Location:** `game/ai/strategy_manager.py:38-50`
**Issue:** Double-checked locking for instance creation is correct, but load_data() writes to dictionaries without synchronization after lock release.
**Impact:** Potential race conditions in multi-threaded initialization.
**Recommendation:** Document single-thread initialization requirement or wrap loading in consistent locking.
**Effort:** Medium

#### MAJOR: Inconsistent Error Code Format in StrategyManager
**ID:** CON-FND-007
**Location:** `game/ai/strategy_manager.py:48`
**Issue:** Uses "AI001" but ErrorCode enum has no "AI" category. Only V, S, R, P, F, C categories exist.
**Impact:** Code never caught by ErrorCode comparison patterns.
**Recommendation:** Add AI category to ErrorCode or use existing code.
**Effort:** Medium

#### MAJOR: Parameter Naming Inconsistency (policy vs targeting_policy)
**ID:** CON-FND-008
**Location:** `game/ai/controller.py` method signatures
**Issue:** Related methods use different names: policy, rules, targeting_policy, targeting_rules for similar concepts.
**Impact:** API confusing. IDE autocomplete less helpful.
**Recommendation:** Standardize on explicit names: targeting_policy, targeting_rules, movement_policy.
**Effort:** Simple

#### MAJOR: Missing Type Hints on Module-Level Functions
**ID:** CON-FND-009
**Location:** `game/ai/target_evaluator.py:35-132`
**Issue:** _get_position(entity), _get_rotation(entity), _get_all_components(entity) lack return type hints. _safe_distance has correct hint.
**Impact:** Type checkers can't validate usage.
**Recommendation:** Add return type hints to all 6 functions.
**Effort:** Simple

#### MAJOR: Inconsistent Import Organization
**ID:** CON-FND-010
**Location:** `game/ai/target_evaluator.py:1-23`
**Issue:** Imports not organized by category (stdlib, third-party, first-party).
**Impact:** Less readable than PEP 8 standard.
**Recommendation:** Reorder imports following PEP 8.
**Effort:** Simple

#### MAJOR: Boolean Parameter Naming
**ID:** CON-FND-011
**Location:** `game/ai/controller.py:108` (check_missiles=False)
**Issue:** "check_missiles" ambiguous - could mean "verify missiles are valid" vs "search for missiles".
**Impact:** Minor semantic clarity issue.
**Recommendation:** Rename to include_missiles=False.
**Effort:** Simple

#### MINOR: Non-standard Class Suffixes
**ID:** CON-FND-012
**Location:** Protocol classes in game/core/protocols.py
**Issue:** All protocols use I prefix consistently (IFleet, IPlanet, ICombatant). No violations found.
**Impact:** None - good compliance.
**Recommendation:** None needed.
**Effort:** None

#### MINOR: Mixed Dictionary vs Object Access Patterns
**ID:** CON-FND-013
**Location:** `game/ai/controller.py:94-96`
**Issue:** Mix of method calls (ship.get_ai_strategy()) and dict access (resolved['targeting']).
**Impact:** Low - pattern works but stylistically inconsistent.
**Recommendation:** Wrap dictionaries in DTO classes.
**Effort:** Medium

#### MINOR: Incomplete Docstrings in Public Methods
**ID:** CON-FND-014
**Location:** `game/ai/controller.py:92`, `game/ai/strategy_manager.py:132-135`
**Issue:** Some public methods lack parameter documentation. Return dict structure not documented.
**Impact:** Developers must read code to understand dict keys.
**Recommendation:** Add Returns section to docstrings.
**Effort:** Simple

#### MINOR: Unused Static/Instance Method Duplication
**ID:** CON-FND-015
**Location:** `game/ai/controller.py:268-274`
**Issue:** _stat_* static methods and _get_* instance methods both delegate to same TargetEvaluator methods. Wrappers that could be eliminated.
**Impact:** Code duplication, but works correctly.
**Recommendation:** Delete wrappers, use TargetEvaluator directly.
**Effort:** Simple

#### MINOR: Inconsistent Constants Naming
**ID:** CON-FND-016
**Location:** `game/ai/behaviors.py:87,103,120`
**Issue:** Behaviors define class-level constants that copy from AIConfig, adding extra indirection.
**Impact:** Another level of constant indirection.
**Recommendation:** Reference AIConfig directly in methods.
**Effort:** Simple

#### MINOR: Missing Docstrings on Test/Debug Classes
**ID:** CON-FND-017
**Location:** `game/ai/behaviors.py:396-472`
**Issue:** Test behavior classes (DoNothingBehavior, StationaryFireBehavior) lack docstrings.
**Impact:** Test code harder to understand.
**Recommendation:** Add brief docstrings.
**Effort:** Simple

#### MINOR: Inconsistent Return Value Convention
**ID:** CON-FND-018
**Location:** `game/research/data/tech_tree.py:123-145`
**Issue:** Some methods assign to cache then return; others return directly. Stylistically inconsistent.
**Impact:** Low - caching pattern is correct.
**Recommendation:** None needed.
**Effort:** None

#### MINOR: Missing Registry Exception Handling
**ID:** CON-FND-019
**Location:** `game/core/registry.py:222-260` (hydrate method)
**Issue:** hydrate() clears and updates dicts non-atomically. If clear succeeds but update fails, state is partially modified.
**Impact:** Unlikely to fail in practice.
**Recommendation:** Document non-transactional nature or add rollback.
**Effort:** Simple

## Top 5 Priority Issues
1. **CON-FND-001**: Error code string vs enum - must standardize for PROJ-45
2. **CON-FND-002**: Static method naming - easy fix, high impact on consistency
3. **CON-FND-005**: Invalid error code in docs - prevents copy-paste errors
4. **CON-FND-006**: StrategyManager thread safety - review locking pattern
5. **CON-FND-007**: StrategyManager error code format - align with ErrorCode enum
