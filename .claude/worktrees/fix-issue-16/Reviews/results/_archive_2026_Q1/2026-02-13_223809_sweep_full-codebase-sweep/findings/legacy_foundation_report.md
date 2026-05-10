# Legacy System Holdovers Sweep: Foundation

## Summary
- **Shard:** Foundation (game/core/, game/ai/, game/research/, game/engine/)
- **Files Scanned:** 42
- **Total Issues Found:** 7
- **Critical:** 0 | **Major:** 2 | **Minor:** 4 | **Info:** 1

## Findings

#### MAJOR: Excessive getattr() Fallbacks in AI Combat Utils
**ID:** LEG-FND-001
**Location:** `game/ai/combat_utils.py:44-212`
**Issue:** The combat_utils module contains numerous defensive getattr() calls with fallback values for attributes that should always exist on properly constructed entities. This pattern (18+ occurrences) suggests lingering uncertainty about object interfaces from before the IControllable interface was established.

Examples:
- `getattr(entity, 'position', None)` - position should always exist
- `getattr(comp, 'current_hp', getattr(comp, 'max_hp', 0))` - double fallback
- `getattr(entity, 'id', getattr(entity, 'name', str(id(entity))))` - triple fallback chain

**Impact:** Makes the code harder to reason about, hides potential bugs where None is silently used instead of failing fast, and creates maintenance burden. If an entity lacks `position`, using None will cause downstream errors anyway.
**Recommendation:** After PROJ-24 migration completed (removing __getattr__/__setattr__ delegation), these defensive checks should be audited. Remove fallbacks for attributes guaranteed by IControllable protocol. Keep fallbacks only for truly optional attributes or for handling external entities (missiles, projectiles).
**Effort:** Medium

---

#### MAJOR: Singleton Pattern Still Used for Core Services
**ID:** LEG-FND-002
**Location:** `game/core/singleton.py`, `game/ai/strategy_manager.py`, `game/core/registry.py`, `game/core/logger.py`, `game/core/profiling.py`, `game/core/strategy_metadata.py`
**Issue:** The codebase maintains ~7 singleton classes using SingletonMeta, while simultaneously providing dependency injection infrastructure (IRegistryProvider, GameRegistries, get_default_registry_provider). This creates a hybrid pattern where some code uses DI and other code directly accesses singletons. The CLAUDE.md explicitly states "Dependency injection replaced singletons in many areas" but the transition is incomplete.

Key singletons:
- `StrategyManager.instance()` - used directly in AIController
- `StrategyMetadataService.instance()` - used for UI strategy display
- `Logger.instance()` - global logging
- `Profiler.instance()` - performance tracking
- `RegistryManager.instance()` - wrapped by DefaultRegistryProvider but also accessed directly

**Impact:** Inconsistent architecture makes testing harder (must reset singletons), creates hidden dependencies, and violates the stated architectural direction. Code using `StrategyManager.instance()` cannot be easily unit-tested in isolation.
**Recommendation:** Continue migration to full DI. Priority targets: StrategyManager (pass via constructor to AIController), StrategyMetadataService (inject where needed). Logger and Profiler are lower priority as they're cross-cutting concerns.
**Effort:** Complex (multi-phase refactoring project)

---

#### MINOR: Stale PROJ Reference Comments
**ID:** LEG-FND-003
**Location:** Multiple files including:
- `game/core/config.py:136` - "UIConfig has been moved to game.ui.config (PROJ-113)"
- `game/core/constants.py:38` - "PROJ-113: Colors... moved to game.ui.colors"
- `game/ai/interfaces/__init__.py:5` - "PROJ-12 Phase 5"
- `game/ai/interfaces/controllable.py:286-298` - "PROJ-24 Migration Complete" comment block

**Issue:** Historical PROJ-XX comments remain scattered throughout the codebase. While these provide context, they add noise and reference completed work. The comment at `controllable.py:286-298` is particularly verbose (13 lines) documenting a completed migration.
**Impact:** Minor clutter that makes files harder to read. No functional impact.
**Recommendation:** Remove PROJ comments for fully completed, stable migrations. Keep only comments that provide ongoing architectural context (e.g., "This uses DI per PROJ-27 pattern").
**Effort:** Simple

---

#### MINOR: Defensive hasattr() Checks in AI Layer
**ID:** LEG-FND-004
**Location:** `game/ai/interfaces/controllable.py:472`, `game/ai/combat_utils.py:44`, `game/core/math.py:32-36`
**Issue:** Several hasattr() checks exist for attributes that should be guaranteed by protocols or interfaces:
- `controllable.py:472`: `hasattr(master, 'formation') and hasattr(master.formation, 'members')` - formation is a required attribute
- `combat_utils.py:44`: Mock detection via `hasattr(obj, '_mock_name')` - testing concern in production code

**Impact:** Defensive code that masks potential bugs rather than failing fast. The mock detection is particularly problematic as it couples production code to test implementation details.
**Recommendation:** Remove hasattr() checks for protocol-guaranteed attributes. Move mock detection to a test-only utility if needed.
**Effort:** Simple

---

#### MINOR: Unused Error Codes
**ID:** LEG-FND-005
**Location:** `game/core/error_codes.py:63-64, 82-83`
**Issue:** Several error codes appear to be defined but never used:
- `MISSING_REQUIRED = "V003"` - No usage found in codebase
- `STATE_TRANSITION_DENIED = "S004"` - No usage found in codebase

Other codes like `VALIDATION_FAILED`, `STATE_FROZEN`, `RESOURCE_NOT_FOUND` are actively used.
**Impact:** Minor dead code. Error codes may have been added proactively or their usage sites were removed.
**Recommendation:** Either use these codes or remove them. Consider adding a static analysis check to ensure all error codes are used.
**Effort:** Simple

---

#### MINOR: PhysicsBody.update() Rarely Used
**ID:** LEG-FND-006
**Location:** `game/engine/physics.py:82-101`
**Issue:** The PhysicsBody.update() method contains a comment noting "Ship class overrides this with its own cycle-based mixins. This base implementation is here for non-ship PhysicsBody entities if any." This suggests the method may be vestigial - ships use a different update path via mixins, and it's unclear if any non-ship PhysicsBody entities exist.
**Impact:** If no non-ship PhysicsBody entities exist, this is dead code that could confuse maintainers.
**Recommendation:** Search for PhysicsBody instantiations that aren't Ships. If none exist, consider documenting this more clearly or marking the method as abstract to force overrides.
**Effort:** Simple

---

#### INFO: Fallback Behaviors Are Intentional Design
**ID:** LEG-FND-007
**Location:** `game/ai/__init__.py:38-52`, `game/ai/combat_utils.py:79-125`
**Issue:** The AI package extensively documents its "defensive programming with fallback behavior" approach. This is explicitly documented in module docstrings and comments. While this creates some code patterns that look like legacy compatibility shims, they appear to be intentional design for combat robustness.

Example from `game/ai/__init__.py`:
```
**Fallback Behaviors:**
- Position access failures: Falls back to direct attribute
- Target evaluation failures: Target is skipped
- Formation dropout: Logged but continues combat
```

**Impact:** Not an issue - this is documented intentional behavior. Included for completeness.
**Recommendation:** No action needed. The documentation clearly explains the design rationale.
**Effort:** N/A

---

## Top 5 Priority Issues

1. **LEG-FND-001 (MAJOR):** Excessive getattr() fallbacks in combat_utils - 18+ instances of defensive coding that may be unnecessary after IControllable interface completion
2. **LEG-FND-002 (MAJOR):** Hybrid singleton/DI architecture - Creates inconsistent patterns and testing difficulties. StrategyManager.instance() is the highest-impact target for DI conversion.
3. **LEG-FND-004 (MINOR):** hasattr() checks in controllable.py - Mock detection logic in production code couples test and production concerns
4. **LEG-FND-005 (MINOR):** Unused error codes - Dead code that should be cleaned up or used
5. **LEG-FND-003 (MINOR):** Stale PROJ comments - Should be cleaned for code clarity (low priority but easy win)

## Notes

The Foundation shard is generally well-maintained. Most legacy patterns have been properly migrated per the documented project history. The main areas for improvement are:

1. **Completing the DI migration** for singleton services (particularly StrategyManager)
2. **Auditing defensive coding patterns** in the AI layer to determine which fallbacks are still necessary vs. vestigial from pre-interface days
3. **Minor cleanup** of comments and unused error codes

No critical issues were found. The codebase shows evidence of systematic refactoring with proper documentation of migrations.
