# Legacy System Holdovers Sweep: Foundation

## Summary
- **Shard:** Foundation (game/core/, game/ai/, game/research/, game/engine/)
- **Files Scanned:** 42
- **Total Issues Found:** 8
- **Critical:** 0 | **Major:** 2 | **Minor:** 4 | **Info:** 2

## Methodology Applied
This sweep exhaustively scanned all 42 Python files across the assigned directories:
- game/core/: 18 files
- game/ai/: 9 files
- game/research/: 11 files
- game/engine/: 4 files

Analysis phases completed:
1. Dead Code Paths - Searched for uncalled functions, unused classes, always-true/false guards
2. Compatibility Shims & Wrappers - Looked for "legacy", "deprecated", "fallback" patterns
3. Obsolete Patterns - Checked for direct singleton access, inline calculations, raw dict access
4. Orphaned Resources - Searched for unused constants/enums, unused imports
5. Incomplete Migrations - Looked for mixed old/new patterns, TODO comments

## Findings

#### MAJOR: hasattr defensive checks in collision.py suggest loose interface contracts
**ID:** LEG-FND-001
**Location:** `game/engine/collision.py:107`
**Issue:** The code uses `hasattr(source_ship, 'get_total_sensor_score')` to check if a method exists before calling it, indicating an optional interface that should be formalized.
**Impact:** This defensive check suggests uncertainty about the interface contract. Ships in combat should always have sensor score capability, or the interface should explicitly declare it optional via Protocol.
**Recommendation:** Either formalize via Protocol (IHasSensorScore) or ensure all ships have this method.
**Effort:** Medium

#### MAJOR: getattr with fallback defaults for core combat attributes
**ID:** LEG-FND-002
**Location:** `game/engine/collision.py:138,147-148`
**Issue:** The ramming logic uses `getattr(s, 'ai_strategy', '')` and `getattr(s, 'hp', 100)` to access attributes with fallback defaults, suggesting the Ship interface is not fully typed.
**Impact:** Fallback values of `''` for ai_strategy and `100` for hp could mask bugs where entities without proper attributes are passed. If hp defaults to 100, ramming damage calculations may be wildly incorrect.
**Recommendation:** Ensure all combatants have explicit `ai_strategy` and `hp` attributes via protocol or interface validation at entity creation.
**Effort:** Medium

#### MINOR: Fallback resource file handling in resources.py
**ID:** LEG-FND-003
**Location:** `game/core/resources.py:7-10,67-98`
**Issue:** The `load_resources_data()` function has extensive fallback handling for missing/malformed JSON files, returning `_get_default_resources()` for any error condition.
**Impact:** While this is reasonable defensive coding for data loading, the fallback pattern means corrupted or missing resource files will silently use defaults rather than fail loudly, potentially masking configuration issues.
**Recommendation:** Consider adding a `strict=True` parameter that raises exceptions for production builds while allowing fallback for development. Document clearly when defaults are used.
**Effort:** Simple

#### MINOR: Input action key name fallback logic
**ID:** LEG-FND-004
**Location:** `game/core/input_actions.py:286`
**Issue:** Comment says "Fallback: strip K_ prefix" when getting human-readable key names, suggesting this is handling a case that may no longer be needed with pygame's current API.
**Impact:** Low - this is just string formatting for display purposes.
**Recommendation:** Verify if pygame 2.x still requires this fallback. If pygame now provides clean key names, this can be simplified.
**Effort:** Simple

#### MINOR: AI combat_utils uses defensive fallback patterns extensively
**ID:** LEG-FND-005
**Location:** `game/ai/combat_utils.py:79-125`
**Issue:** Functions like `get_position()` and `get_rotation()` use try/except with logged warnings and fallbacks. While intentionally defensive, the docstrings explicitly document "fallback behavior" patterns.
**Impact:** These fallbacks are intentional for combat robustness but could mask interface violations. The pattern is documented and consistent, but creates implicit contract flexibility.
**Recommendation:** No immediate action needed - this is documented defensive programming. Consider adding runtime warnings in debug mode when fallbacks are used.
**Effort:** Simple

#### MINOR: Research system standalone sandbox design
**ID:** LEG-FND-006
**Location:** `game/research/__init__.py:1-8`
**Issue:** The research module's docstring describes it as "A standalone sandbox for testing tech tree balance" - suggesting this is a feature prototype not fully integrated with the main game.
**Impact:** If this is truly a standalone sandbox, it may have interfaces and patterns that diverge from the rest of the codebase. The camera injection pattern (PROJ-132) shows integration work is ongoing.
**Recommendation:** Clarify whether this module will remain a sandbox or be integrated. If sandbox, document its standalone nature more prominently.
**Effort:** Simple

#### INFO: getattr usage in AI behaviors is appropriate for formation handling
**ID:** LEG-FND-007
**Location:** `game/ai/behaviors.py:281,334,336`
**Issue:** Formation behavior uses `getattr(master, 'is_derelict', False)`, `getattr(master, 'is_thrusting', False)`, etc.
**Impact:** None - this is appropriate defensive coding for optional state attributes on formation masters. Ships may or may not be thrusting at any given moment.
**Recommendation:** None needed - this is correct pattern for querying optional state.
**Effort:** N/A

#### INFO: AI controllable adapter uses getattr for optional attributes
**ID:** LEG-FND-008
**Location:** `game/ai/interfaces/controllable.py:406,426,430`
**Issue:** The adapter uses `getattr(self._ship, 'max_targets', DEFAULT)`, `getattr(self._ship, 'ai_strategy', 'standard_ranged')`, etc.
**Impact:** None - the adapter intentionally provides defaults for optional ship configuration attributes. This is the adapter's purpose: to provide a consistent interface regardless of ship configuration.
**Recommendation:** None needed - this is correct adapter pattern.
**Effort:** N/A

## Top 5 Priority Issues

1. **LEG-FND-001 (MAJOR)** - `hasattr` check for `get_total_sensor_score` in collision.py indicates loose interface contract. Should be formalized.

2. **LEG-FND-002 (MAJOR)** - `getattr` with fallback defaults for `hp` and `ai_strategy` in ramming logic could mask bugs with incorrect default values.

3. **LEG-FND-003 (MINOR)** - Silent fallback to default resources could mask configuration issues in production.

4. **LEG-FND-005 (MINOR)** - Extensive fallback patterns in combat_utils, while documented, create implicit interface flexibility.

5. **LEG-FND-006 (MINOR)** - Research module's "sandbox" status unclear - may diverge from main codebase patterns.

## Notable Clean Findings

The following areas showed NO legacy issues:

- **game/core/singleton.py** - Clean, modern metaclass implementation
- **game/core/registry.py** - Well-structured DI patterns (PROJ-27, PROJ-38)
- **game/core/exceptions.py** - Clean exception hierarchy with error codes
- **game/core/validation.py** - Consolidated ValidationResult from PROJ-21, PROJ-43
- **game/core/hex_math.py** - Clean hexagonal math with no legacy patterns
- **game/core/profiling.py** - Modern singleton with context managers
- **game/ai/target_evaluator.py** - Clean rule evaluation with explicit helpers
- **game/ai/ai_factory.py** - Two-phase initialization pattern, well-documented
- **game/ai/strategy_manager.py** - Uses SingletonMeta correctly
- **game/research/** - Modern dataclass-based design throughout
- **game/engine/spatial.py** - Simple, clean spatial grid implementation
- **game/engine/physics.py** - Clean physics body with clear documentation

No TODO/FIXME/HACK/XXX comments found in any scanned files.
No deprecated/legacy/compat keywords found in comments (only in legitimate error code names).
No ImportError fallback patterns found.
No commented-out old code found.
