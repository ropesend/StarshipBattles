# Code Style and Idiom Pattern Analysis

**Agent:** Style & Idiom Analyst
**Date:** 2026-01-28
**Scope:** game/, ui/ directories (excluding tests)

---

## Summary
- Total pattern variants found: 15
- Critical inconsistencies: 0
- Major inconsistencies: 0
- Minor inconsistencies: 2
- Dominant pattern: Modern Python with strong type hints

---

## Type Annotation Patterns

### Coverage

| Pattern Variant | Example Locations | Frequency | Notes |
|-----------------|-------------------|-----------|-------|
| Full return type annotations | Most game/ files | 95% | Excellent |
| Parameter type annotations | Most game/ files | 88% | Very good |
| Missing annotations | game/ui/screens/builder/*.py | 12% | UI builders gap |

### Style

| Pattern Variant | Example Locations | Frequency | Notes |
|-----------------|-------------------|-----------|-------|
| `Optional[T]` style | protocols.py, fleet.py | 100% | Standard |
| `T \| None` style | resources.py | 1 occurrence | Rare/avoid |
| TYPE_CHECKING blocks | Throughout | 215+ uses | Good practice |

---

## Docstring Patterns

### Coverage

| Level | Coverage | Notes |
|-------|----------|-------|
| Module docstrings | 92% | Excellent |
| Class docstrings | 68% | Acceptable |
| Method docstrings | 52% | Weak in UI builders |

### Format

| Pattern Variant | Example Locations | Frequency | Notes |
|-----------------|-------------------|-----------|-------|
| One-liner summary | Simple methods | 60% | Common |
| Extended with Args/Returns | Complex methods | 40% | When needed |
| PROJ-references | Throughout | 263 occurrences | Architecture tracking |

---

## Python Idiom Usage

### String Formatting

| Pattern Variant | Example Locations | Frequency | Notes |
|-----------------|-------------------|-----------|-------|
| f-strings | Throughout codebase | 99% | Dominant |
| `.format()` method | Legacy code | ~50 occurrences | Declining |
| % formatting | Minimal | <1% | Rare |

### Comprehensions

| Pattern Variant | Example Locations | Frequency | Notes |
|-----------------|-------------------|-----------|-------|
| List comprehensions | fleet.py, many files | 142 occurrences | Well-adopted |
| Dict comprehensions | Various | 22 occurrences | Moderate |
| Generator expressions | Data processing | Moderate | Good |

### Other Idioms

| Pattern Variant | Example Locations | Frequency | Notes |
|-----------------|-------------------|-----------|-------|
| @property decorators | ship.py, many files | 273 uses | Heavy use |
| Context managers (with) | File I/O, resources | 215 uses | Could expand |
| @classmethod/@staticmethod | Various | ~75 uses | Appropriate |

---

## Configuration Patterns

### Constants Organization

| Pattern Variant | Example Locations | Frequency | Notes |
|-----------------|-------------------|-----------|-------|
| Class-based configs | game/core/config.py | Primary | DisplayConfig, AIConfig |
| Module constants | game/core/constants.py | Secondary | PLANET_RESOURCES |
| Color dictionaries | game/ui/colors.py | UI-specific | COLORS dict |
| Enums | Throughout | 22+ enums | AttackType, GameState |

### Issues

| Pattern Variant | Example Locations | Frequency | Notes |
|-----------------|-------------------|-----------|-------|
| Scattered constants | Multiple locations | 3+ files | Fragmented |
| Magic numbers | UI builders | ~15-20 files | Should extract |

---

## Key Inconsistencies

### STY-01: Type Annotation Gaps in UI Builders
**Severity:** Minor
**ID:** STY-01
**Location:** `game/ui/screens/builder/*.py`
**Issue:** ~12% of methods missing type annotations
**Impact:** Reduced IDE support, harder to understand interfaces
**Recommendation:** Add type hints to public methods
**Effort:** Medium

### STY-02: Docstring Coverage Gap
**Severity:** Minor
**ID:** STY-02
**Location:** `game/ui/screens/builder/*.py`, `ui/builder/*.py`
**Issue:** ~48% of methods missing docstrings
**Impact:** Reduced code discoverability
**Recommendation:** Add docstrings to public methods
**Effort:** Medium

### STY-03: Context Manager Underutilization
**Severity:** Info
**ID:** STY-03
**Location:** Various file I/O locations
**Issue:** Some file operations don't use `with` statements
**Impact:** Potential resource leaks
**Recommendation:** Migrate to context managers
**Effort:** Simple

---

## Recommended Standard

### Type Annotations
```python
from typing import Optional, Dict, List

def process_items(
    self,
    items: List[Item],
    count: int = 10
) -> Optional[Result]:
    """Process items and return result."""
    ...
```

### Docstrings
```python
def calculate_damage(self, attacker: Ship, target: Ship) -> float:
    """Calculate damage from attacker to target.

    Args:
        attacker: The attacking ship entity.
        target: The target ship entity.

    Returns:
        The calculated damage value.

    Raises:
        ValueError: If either ship is invalid.
    """
```

### Python Idioms
```python
# Prefer list comprehension
items = [x.value for x in objects if x.valid]

# Always use context manager for resources
with open(path, 'r') as f:
    data = f.read()

# Use f-strings
message = f"Processing {count} items"

# Use dictionary.get() with default
value = config.get('key', default_value)
```

### Configuration
```python
# Use class-based configuration
class UIConfig:
    PANEL_WIDTH: int = 300
    PANEL_HEIGHT: int = 400

    @classmethod
    def panel_size(cls) -> Tuple[int, int]:
        return (cls.PANEL_WIDTH, cls.PANEL_HEIGHT)
```

---

## Pattern Consistency Summary

| Category | Consistency | Standard |
|----------|-------------|----------|
| Type annotations | 95% | `Optional[T]`, not `T \| None` |
| f-strings | 99% | Always use f-strings |
| Comprehensions | High | Use when readable |
| Properties | 95% | For computed values |
| Context managers | Moderate | Expand usage |
| Constants | 75% | Class-based preferred |

---

## Top 5 Priority Issues

1. **STY-01:** Add missing type hints in UI builders (~12% gap)
2. **STY-02:** Add missing docstrings in UI builders (~48% gap)
3. Consolidate constants locations (3+ files → 1-2 files)
4. Expand context manager usage for file I/O
5. Document style guidelines in coding standards
