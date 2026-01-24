# PROJ-11 Phase 1: Core Math Abstraction

## Phase Overview
Create framework-agnostic math utilities to replace pygame dependencies.

## Tasks

### Create game/core/math.py
- [ ] Create new file `game/core/math.py`
- [ ] Implement Vector2 class with all required methods:
  - [ ] `__init__`, `__add__`, `__sub__`, `__mul__`, `__rmul__`, `__truediv__`
  - [ ] `__neg__`, `__eq__`, `__repr__`
  - [ ] `length()`, `length_squared()`
  - [ ] `normalize()`, `normalize_ip()`
  - [ ] `dot()`, `distance_to()`, `distance_squared_to()`
  - [ ] `rotate()`, `angle_to()`
  - [ ] `copy()`, `as_tuple()`, `as_int_tuple()`
- [ ] Add type hints throughout
- [ ] Add docstrings for public methods
- [ ] Export from `game/core/__init__.py`

### Unit Tests for Vector2
- [ ] Create `tests/unit/core/test_math.py`
- [ ] Test all arithmetic operations
- [ ] Test normalization (including zero vector)
- [ ] Test rotation at various angles
- [ ] Test distance calculations
- [ ] Test edge cases (division by zero, etc.)
- [ ] Compare results with pygame.math.Vector2 for verification

### Helper Functions (if needed)
- [ ] `clamp(value, min_val, max_val)`
- [ ] `lerp(a, b, t)` - linear interpolation
- [ ] `angle_diff(a, b)` - shortest angular distance

## Verification
- [ ] All Vector2 unit tests pass
- [ ] No pygame imports in game/core/math.py
- [ ] Verify API compatibility with pygame.math.Vector2
