# Dead Code Hunter Report

## Summary
- **Total Issues Found:** 11
- **Critical:** 2, **Major:** 4, **Minor:** 5

---

## Critical Issues

### DC-001: Duplicate Battle Panel Systems
**ID:** DC-001
**Location:**
- `game/ui/hud/panels.py` (705 lines)
- `game/ui/panels/battle_panels.py` (20KB)

**Issue:** Two parallel implementations of ShipStatsPanel, SeekerMonitorPanel, and BattleControlPanel classes exist in different locations. This creates confusion about which version is canonical:
- `game/ui/hud/battle.py` imports from `game.ui.hud.panels`
- `game/ui/screens/battle_screen.py` imports from `game.ui.panels.battle_panels`

**Impact:** Code duplication, maintenance burden, potential sync issues between implementations.

**Recommendation:** Consolidate into single location (suggest `game/ui/panels/battle_panels.py` as it has more recent refactoring with `ship_stats_renderer.py` imports).
**Effort:** Medium

---

### DC-002: Stub Functions with NotImplementedError
**ID:** DC-002
**Location:** `game/ai/behaviors.py:79`
**Issue:** Base class `AIBehavior.update()` raises `NotImplementedError` but is never actually called - appears to be incomplete design pattern.
**Code:**
```python
def update(self, target: Any, strategy: Dict[str, Any]) -> None:
    """Execute behavior logic."""
    raise NotImplementedError
```
**Impact:** Dead code if subclasses override before parent is used, confusing interface contract.
**Recommendation:** Use `@abstractmethod` if truly abstract.
**Effort:** Simple

---

## Major Issues

### DC-003: Unreachable Draw Methods
**ID:** DC-003
**Location:**
- `game/ui/hud/panels.py:28` - BattlePanel.draw()
- `game/ui/panels/battle_panels.py:18` - BattlePanel.draw()

**Issue:** Base class methods raise `NotImplementedError` but should use `@abstractmethod` if truly abstract.
**Impact:** Misleading interface, potential for accidental instantiation.
**Recommendation:** Convert to `@abstractmethod`
**Effort:** Simple

---

### DC-004: Empty Service Module
**ID:** DC-004
**Location:** `game/strategy/services/__init__.py` (1 line only comment)
**Issue:** Package is empty except for comment "# Strategy services package"
**Impact:** Dead package namespace, no exports defined
**Recommendation:** Either populate with real services or delete package and import directly from submodules.
**Effort:** Simple

---

### DC-005: Unimplemented Method with TODO
**ID:** DC-005
**Location:** `game/app.py:671`
**Issue:**
```python
available_tech_ids = []  # TODO: Replace with empire.available_tech or similar
```
**Impact:** Placeholder code left in production, no available tech returned to workshop.
**Recommendation:** Implement proper empire tech tracking or remove placeholder.
**Effort:** Medium

---

### DC-006: _ValidatorProxy Never Used
**ID:** DC-006
**Location:** `game/simulation/entities/ship.py:29-34`
**Issue:** `_ValidatorProxy` class is instantiated as `VALIDATOR = _ValidatorProxy()` but the VALIDATOR constant is never referenced in the codebase. Validator is accessed directly via `get_or_create_validator()`.
**Impact:** Dead code adds maintenance burden, confuses developers.
**Recommendation:** Remove `_ValidatorProxy` class and VALIDATOR global.
**Effort:** Simple

---

## Minor Issues

### DC-007: Dead pycache Directories
**ID:** DC-007
**Location:** 36 `__pycache__` directories throughout game/
**Issue:** Compiled Python bytecode cached directories should not be in version control.
**Impact:** Bloats repository.
**Recommendation:** Add to .gitignore if not already present.
**Effort:** Simple

---

### DC-008: Empty Module Exports
**ID:** DC-008
**Location:**
- `game/ai/__init__.py` (0 bytes)
- `game/__init__.py` (0 bytes)
- `game/simulation/__init__.py` (0 bytes)

**Issue:** Package __init__ files are completely empty with no exports defined.
**Impact:** Reduces code discoverability, requires importing from submodules.
**Recommendation:** Define meaningful `__all__` exports.
**Effort:** Simple

---

### DC-009: Debug Flag Always Enabled
**ID:** DC-009
**Location:** `game/core/constants.py:56`
**Issue:**
```python
DEBUG_SCREENSHOTS = True
```
**Impact:** Debug feature cannot be toggled at runtime, potential performance issue if screenshots are continuously saved.
**Recommendation:** Make configurable or disable by default.
**Effort:** Simple

---

### DC-010: Obsolete Commented Code Reference
**ID:** DC-010
**Location:** `game/ui/screens/test_lab.py:88-99`
**Issue:** Obsolete commented code referencing non-existent `menu_screen.create_particles()` method.
**Impact:** Confusion about what code is still valid.
**Recommendation:** Remove obsolete comments.
**Effort:** Simple

---

### DC-011: Protocol Ellipsis Stubs
**ID:** DC-011
**Location:** `game/core/protocols.py` (10 instances)
**Issue:** Protocol property definitions use ellipsis (...) as placeholder implementation.
**Impact:** Acceptable for Protocols, but indicates incomplete specification.
**Recommendation:** Document expected behavior in docstrings.
**Effort:** Simple

---

## Top 5 Priority Issues

1. **DC-001: Duplicate Panel Systems** - Critical - Consolidate to single implementation
2. **DC-005: Unfinished Tech Availability** - Major - Implement proper empire tech tracking
3. **DC-004: Empty Service Package** - Major - Delete or populate
4. **DC-002/DC-003: Stub Methods with NotImplementedError** - Major - Convert to @abstractmethod
5. **DC-006: _ValidatorProxy Never Used** - Major - Remove dead code

---

## Code Quality Observations

**Strengths:**
- Most code is actively used and maintained
- Minimal commented-out code blocks
- No wildcard imports detected (good practice)
- TYPE_CHECKING blocks used correctly for forward references

**Weaknesses:**
- Duplicate implementations create maintenance risk
- Missing @abstractmethod decorators on abstract base classes
- Unfinished TODOs left in production code
- Empty service package suggests architectural rework in progress
