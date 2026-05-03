# Module Review: game/core/

**Module Specialist:** MOD-CORE
**Review Date:** 2026-02-23
**Scope:** Registry pattern, singletons, DI, protocols, JSON utilities, logger, validation, exceptions

---

## Summary

**Total Findings:** 17
**Severity Distribution:**
- Critical: 2
- Major: 5
- Minor: 7
- Info: 3

**Overall Module Health Rating: B+ (Good with notable improvements needed)**

The game/core/ module is generally well-architected with strong patterns for registry management, dependency injection, and error handling. Evidence of thoughtful refactoring (PROJ-27, PROJ-38, PROJ-45, PROJ-50, PROJ-58) with good documentation.

**Key Strengths:**
- Clean layer separation (no upward dependencies)
- Comprehensive exception hierarchy with error codes
- Strong DI patterns with both production and test providers
- Thread-safe singleton implementation
- Extensive protocol definitions for cross-layer contracts

**Key Concerns:**
- Dual registry access patterns create confusion
- Module-level globals alongside singletons
- Logger initialization side effects during import
- Incomplete protocol coverage
- False immutability in frozen dataclasses with mutable dicts

---

## Findings

### MOD-CORE-001: Dual Registry Access Pattern Creates Confusion
**Location:** `game/core/registry.py:80-120, 305-398`
**Severity:** Critical
**Deliberate:** Partially deliberate (transitional state)

**Description:**
Three different ways to access registry data:
1. Direct singleton: `RegistryManager.instance().components`
2. GameRegistries container: `get_default_registries()`
3. DI provider: `get_default_registry_provider()`

Documented as TIER 1/2/3 but creates confusion. TIER 2 is "RECOMMENDED" but TIER 3 (direct singleton) still widely used (30+ files).

**Recommendation:**
Pick ONE canonical pattern (IRegistryProvider DI recommended). Deprecate direct RegistryManager access outside composition root. Remove module-level service locator.

---

### MOD-CORE-002: GameRegistries Uses Mutable Dicts in Frozen Dataclass
**Location:** `game/core/registry.py:56-78`
**Severity:** Major
**Deliberate:** Likely accidental

**Description:**
`GameRegistries` is `frozen=True` but contains mutable `Dict[str, Any]` attributes. Docstring acknowledges this: "The container itself is frozen (immutable), but the dictionaries inside can still be modified." Creates false sense of immutability.

**Recommendation:**
Either remove `frozen=True` (honest API), use `MappingProxyType` for true immutability, or document limitation clearly.

---

### MOD-CORE-003: Logger Initialization Has Import-Time Side Effects
**Location:** `game/core/logger.py:27-41`
**Severity:** Major
**Deliberate:** Likely accidental

**Description:**
`Logger.__init__` calls `self.setup()` which creates file handlers and initializes logging during first import. Creates files on disk during import. Can cause issues in test environments or headless setups.

**Recommendation:**
Separate construction from initialization. Call `setup()` explicitly from composition root. Make `setup()` idempotent.

---

### MOD-CORE-004: Inconsistent Frozen State Management
**Location:** `game/core/registry.py:166-263`
**Severity:** Major
**Deliberate:** Likely deliberate but poorly enforced

**Description:**
RegistryManager has `_frozen` flag to prevent modifications, but:
1. Some operations check `_frozen`, others don't
2. Direct dict access bypasses checks entirely
3. Line 273 references non-existent `reset()` method

**Recommendation:**
Either fully enforce with read-only dict wrappers or remove frozen mechanism. Remove misleading comment about reset().

---

### MOD-CORE-005: Module-Level Globals Alongside Singleton Pattern
**Location:** `game/core/registry.py:81, 380` and `game/core/logger.py:87-92`
**Severity:** Minor
**Deliberate:** Likely transitional (PROJ-58)

**Description:**
Module uses both SingletonMeta and module-level globals (`_default_registries`, `_default_provider`, `_event_handler`). Two parallel state management systems. Conftest must manually clear both.

**Recommendation:**
Store globals inside singleton instances to consolidate state management.

---

### MOD-CORE-006: TestRegistryProvider Lacks Resources Support
**Location:** `game/core/registry.py:332-377`
**Severity:** Minor
**Deliberate:** Likely accidental (incomplete feature)

**Description:**
`TestRegistryProvider.__init__` accepts components, modifiers, vehicle_classes but not resources, despite GameRegistries including resources.

**Recommendation:**
Add `resources` parameter to TestRegistryProvider.

---

### MOD-CORE-007: IRegistryProvider Missing Resources Method
**Location:** `game/core/protocols.py:46-73`
**Severity:** Minor
**Deliberate:** Likely accidental (incomplete protocol)

**Description:**
IRegistryProvider defines methods for components, modifiers, vehicle_classes but not resources. GameRegistries and RegistryManager both have resources, but no type-safe DI access.

**Recommendation:**
Add `get_resources()` to IRegistryProvider protocol.

---

### MOD-CORE-008: Paths Module Has Global Initialization Side Effects
**Location:** `game/core/paths.py:21-43`
**Severity:** Minor
**Deliberate:** Likely deliberate but problematic

**Description:**
`_find_project_root()` executes at import time, walking up directory tree. Raises ResourceException if project root not found. Makes module unusable in unusual environments.

**Recommendation:**
Make `_find_project_root()` lazy — only execute when first path is accessed.

---

### MOD-CORE-009: ValidationResult.merge Doesn't Merge Error Codes
**Location:** `game/core/validation.py:132-145`
**Severity:** Minor
**Deliberate:** Likely accidental (oversight)

**Description:**
`merge()` method merges errors and warnings but silently drops `error_code` from other result. Error code information lost during validation composition.

**Recommendation:**
Add error code merging logic (e.g., if self.error_code is None, use other.error_code).

---

### MOD-CORE-010: Vector2 Missing Type Hints for Magic Methods
**Location:** `game/core/math.py:12-236`
**Severity:** Info
**Deliberate:** Likely accidental

**Description:**
`__add__`, `__sub__` etc. lack proper type hints for `other` parameter.

**Recommendation:**
Add Vector2Like Protocol or Union type hints.

---

### MOD-CORE-011: HexCoord Missing Type Hints in Magic Methods
**Location:** `game/core/hex_math.py:69-113`
**Severity:** Info
**Deliberate:** Likely accidental

**Description:**
Similar to Vector2 — some arithmetic operations lack proper typing for `other` parameter.

---

### MOD-CORE-012: Profiler Records Are Not Thread-Safe
**Location:** `game/core/profiling.py:35-77`
**Severity:** Minor
**Deliberate:** Likely deliberate (acceptable limitation)

**Description:**
Profiler singleton's `records` list accessed without locking. Multiple threads calling `record()` could corrupt the list. SingletonMeta is thread-safe but instance operations are not.

**Recommendation:**
Document as single-threaded only, or add threading.Lock.

---

### MOD-CORE-013: Error Code Documentation Is Incomplete
**Location:** `game/core/error_codes.py:1-148`
**Severity:** Info
**Deliberate:** Likely deliberate (minimalist approach)

**Description:**
ErrorCode enum has docstrings but lacks usage examples, exception type mapping guidance, or cross-references.

**Recommendation:**
Add error codes by exception type mapping in module docstring.

---

### MOD-CORE-014: Constants Module Has Mixed Responsibilities
**Location:** `game/core/constants.py:1-110`
**Severity:** Minor
**Deliberate:** Likely deliberate (convenience)

**Description:**
Mixes enums, configuration classes, raw constants, and feature flags. "Junk drawer" pattern. Colors already moved to game.ui.colors (PROJ-113) suggesting known issue.

**Recommendation:**
Consider splitting into enums.py, defaults.py, feature_flags.py.

---

### MOD-CORE-015: json_utils Swallows Errors Too Broadly
**Location:** `game/core/json_utils.py:33-68, 99-143`
**Severity:** Minor
**Deliberate:** Likely deliberate (defensive programming)

**Description:**
Both `load_json()` and `save_json()` catch broad exception categories. IOError catches many things beyond "file not found". TypeError in save could hide serialization bugs.

**Recommendation:**
Be more specific: separate FileNotFoundError, PermissionError, json.JSONDecodeError handling.

---

### MOD-CORE-016: Logger log_event Global State Without Reset
**Location:** `game/core/logger.py:87-109`
**Severity:** Minor
**Deliberate:** Likely accidental

**Description:**
Module-level `_event_handler` global set via `set_event_handler()` but no formal lifecycle management. Persists across test boundaries unless manually cleared.

**Recommendation:**
Move into Logger singleton state, or add explicit cleanup function.

---

### MOD-CORE-017: SingletonMeta Reset Not Documented in Public API
**Location:** `game/core/singleton.py:84-98`
**Severity:** Info
**Deliberate:** Likely deliberate (internal API)

**Description:**
`SingletonMeta.reset()` is critical for testing but not exported in `__init__.py` or documented. Appears private when it's essential for test isolation.

**Recommendation:**
Export SingletonMeta from game.core. Add usage example in docs.

---

## Top 5 Priority Issues

1. **MOD-CORE-001 (Critical):** Dual Registry Access Pattern — consolidate on IRegistryProvider DI pattern
2. **MOD-CORE-003 (Major):** Logger Import-Time Side Effects — separate construction from initialization
3. **MOD-CORE-004 (Major):** Inconsistent Frozen State Management — enforce or remove frozen mechanism
4. **MOD-CORE-002 (Major):** GameRegistries False Immutability — document or fix frozen=True with mutable dicts
5. **MOD-CORE-005 (Minor):** Module-Level Globals Alongside Singletons — consolidate state management
