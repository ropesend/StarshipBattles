# Core Infrastructure Reviewer Report

## Summary
- **Total Issues Found:** 12
- **Critical:** 2, **Major:** 4, **Minor:** 4, **Info:** 2

---

## Critical Issues

### CORE-001: Missing Return Type Hints on Logger Functions
**ID:** CORE-001
**Location:** `game/core/logger.py:67-80`
**Issue:** Functions `log_debug()`, `log_info()`, `log_warning()`, `log_error()`, and `set_logging()` lack return type hints (`-> None`). The Logger class methods similarly lack type hints.
**Impact:** Reduces type safety and IDE support. Makes code harder to understand and prone to misuse.
**Recommendation:** Add `-> None` return type hints to all logger functions. Add parameter type hints (`msg: str`, `enabled: bool`) and method return types to Logger class.
**Effort:** Simple

---

### CORE-002: Incomplete Type Hint Coverage in Core Registry
**ID:** CORE-002
**Location:** `game/core/registry.py:94-256`
**Issue:** RegistryManager methods like `set_validator()` lack parameter type hints. The `_validator` attribute is typed as `Any` without documentation on expected type.
**Impact:** Unclear what type of validator is expected. Makes debugging difficult when wrong types are passed.
**Recommendation:** Add type hint `validator: Optional[ShipDesignValidator]` to `set_validator()`. Document the expected validator interface in class docstring.
**Effort:** Simple

---

## Major Issues

### CORE-003: Inconsistent Singleton Pattern Implementation
**ID:** CORE-003
**Location:** `game/core/logger.py:11-18`, `game/core/registry.py:184-198`, `game/core/profiling.py:44-57`, `game/core/screenshot_manager.py:32-45`
**Issue:** Four different singleton implementations use slightly different patterns. Logger uses `__new__` with `_initialized` flag; RegistryManager and others use double-checked locking with `instance()`. Inconsistent patterns make maintenance harder.
**Impact:** Code reviewers must understand multiple patterns. Higher chance of bugs if pattern isn't correctly replicated.
**Recommendation:** Standardize all singletons to use the thread-safe double-checked locking pattern (RegistryManager/Profiler style). Consider extracting into a base class or using a decorator.
**Effort:** Medium

---

### CORE-004: Deprecated Functions Still Exported and Callable
**ID:** CORE-004
**Location:** `game/core/registry.py:37-57, 298-364`
**Issue:** Five deprecated functions (`get_component_registry()`, `get_modifier_registry()`, `get_vehicle_classes()`, `get_validator()`, `get_resource_registry()`) are in `__all__` exports and actively used in `game/core/resources.py:92` and `game/simulation/battle_state.py`. PROJ-38 deprecation not enforced; no migration timeline specified.
**Impact:** Code emits DeprecationWarnings at runtime. Migration is incomplete (battle_state.py still uses deprecated functions). No clear migration path for consumers.
**Recommendation:** Phase 2 of PROJ-38: Set deprecation deadline (e.g., next release). Update all internal usage to use DI. Add migration guide in registry docstring.
**Effort:** Medium

---

### CORE-005: Backward Compatibility Module-Level Exports Not Documented
**ID:** CORE-005
**Location:** `game/core/paths.py:89-98`
**Issue:** Module-level exports (`ROOT_DIR`, `DATA_DIR`, `ASSET_DIR`, etc.) re-export from Paths class for backward compatibility, but no comment explains why. Similarly, `game/core/constants.py:29-33` re-exports display config from DisplayConfig class without explanation.
**Impact:** New developers don't understand the migration pattern. Risk of accidental removal of backward-compat exports.
**Recommendation:** Add comments: `# Backward compatibility: prefer Paths.ROOT_DIR in new code` on line 89. Document the migration pattern in constants.py.
**Effort:** Simple

---

### CORE-006: Broad Exception Catching Without Context
**ID:** CORE-006
**Location:** `game/core/resources.py:77-79, 111-113` and `game/core/screenshot_manager.py:115-116, 216-217`
**Issue:** Bare `except Exception:` blocks suppress all errors without logging specifics. In resources.py line 77, silently falls back to defaults without logging context.
**Impact:** Makes debugging harder. Hides genuine bugs under fallback behavior.
**Recommendation:** Log exception type/message in except blocks: `except Exception as e: log_warning(f"Failed to load resources: {type(e).__name__}: {e}")`. Distinguish recoverable vs critical errors.
**Effort:** Simple

---

## Minor Issues

### CORE-007: Type Hint Inconsistency - Union vs str | (Python 3.10+)
**ID:** CORE-007
**Location:** `game/core/resources.py:22`
**Issue:** Uses `str | None` (PEP 604 style, Python 3.10+) while other files use `Optional[str]` (typing module). Inconsistent type hint style across codebase.
**Impact:** Reduces consistency. May confuse readers familiar with older typing style.
**Recommendation:** Standardize on `Optional[str]` or `str | None` project-wide. Current codebase uses `Optional`, so fix resources.py line 22.
**Effort:** Simple

---

### CORE-008: Missing Input Validation in ValidationResult
**ID:** CORE-008
**Location:** `game/core/validation.py:51-57`
**Issue:** `__post_init__` checks `if self.errors is None` but dataclass with `default_factory=list` can't be None. Defensive check is redundant.
**Impact:** Slight code smell; suggests developer wasn't confident in dataclass semantics.
**Recommendation:** Remove lines 54-57 (the None checks). Keep the docstring explaining field behavior.
**Effort:** Simple

---

### CORE-009: Inconsistent Error Messages and Formatting
**ID:** CORE-009
**Location:** `game/core/registry.py:269, 296` and `game/core/screenshot_manager.py:28`
**Issue:** Error messages vary in capitalization and punctuation. Inconsistent tone.
**Impact:** Professional polish; makes code feel less polished.
**Recommendation:** Standardize error message format across modules.
**Effort:** Simple

---

### CORE-010: Indentation Inconsistency in Frozen Check
**ID:** CORE-010
**Location:** `game/core/registry.py:175, 269`
**Issue:** Lines use single-space incorrect indentation (13 spaces instead of 12). This is a PEP 8 violation.
**Impact:** Hard to spot in review; violates PEP 8.
**Recommendation:** Fix indentation to standard 12 spaces (3 levels).
**Effort:** Simple

---

## Info Issues

### CORE-011: PROJ-38 Deprecation Status Unclear
**ID:** CORE-011
**Location:** `game/core/registry.py:1-35`
**Issue:** PROJ-38 deprecation plan documented but no deadline, migration priority, or completion criteria. Utility functions have DeprecationWarning but code actively using them isn't flagged.
**Impact:** Unclear when deprecated functions can be removed. No sense of urgency for migration.
**Recommendation:** Add to registry.py docstring: "PROJ-38 Migration Timeline: Phase 1 (done) - Add DI. Phase 2 (TODO) - Migrate internal usage. Phase 3 (TODO) - Remove deprecated functions (v2.0)".
**Effort:** Simple

---

### CORE-012: Engine Collision System Using hasattr/getattr Over Protocols
**ID:** CORE-012
**Location:** `game/engine/collision.py:109-121, 149, 157-159`
**Issue:** CollisionSystem uses `hasattr()/getattr()` checks instead of protocol-based duck typing. Protocols exist in `game/core/protocols.py` (ICombatant, IDamageable) but aren't used here.
**Impact:** Reduces type safety and IDE support. Doesn't leverage existing protocol infrastructure.
**Recommendation:** Replace hasattr checks with protocol checks or add type hints.
**Effort:** Medium

---

## Top 5 Priority Issues

1. **CORE-002: Incomplete Type Hint Coverage** - Type safety foundation affects entire core infrastructure
2. **CORE-001: Missing Return Type Hints on Logger** - Logger is heavily used throughout codebase
3. **CORE-004: Deprecated Functions Not Enforced** - PROJ-38 migration incomplete
4. **CORE-003: Inconsistent Singleton Pattern** - Four different implementations makes codebase harder to maintain
5. **CORE-006: Broad Exception Catching** - Silently fails make debugging difficult

---

## Architecture Notes

**Dependency Injection Status (PROJ-27/38):**
- Protocol-based DI pattern well-designed (`IRegistryProvider`, `DefaultRegistryProvider`, `TestRegistryProvider`)
- PROJ-27 protocols implemented correctly in `game/core/protocols.py`
- PROJ-38 migration incomplete - deprecated utility functions still used in core code

**Singleton Pattern:**
- 4 different singleton implementations (Logger, RegistryManager, Profiler, ScreenshotManager)
- Recommend standardization for maintainability

**Configuration Management:**
- Excellent consolidation in `game/core/config.py` (centralized magic numbers)
- DisplayConfig, AIConfig, PhysicsConfig, BattleConfig well-organized
