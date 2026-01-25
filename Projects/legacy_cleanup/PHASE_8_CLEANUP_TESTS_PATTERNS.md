# Phase 8: Clean Up Tests & Patterns

**Project:** Legacy Code Cleanup
**Phase:** 8 of 8 (Final Phase)
**Risk Level:** Low
**Dependencies:** Phase 7 complete

---

## High-Level Project Context

This phase is part of a comprehensive 8-phase legacy code cleanup effort:

| Phase | Name | Status |
|-------|------|--------|
| 1 | Delete Dead Code | Complete |
| 2 | Remove Shims & Aliases | Complete |
| 3 | Consolidate Re-exports | Complete |
| 4 | Enforce Layer Boundaries | Complete |
| 5 | Standardize Registry Access | Complete |
| 6 | Type Safety via Protocols | Complete |
| 7 | Standardize Data Formats | Complete |
| **8** | **Clean Up Tests & Patterns** | **THIS PHASE (FINAL)** |

**Overall Goal:** Clean up legacy code, enforce architectural boundaries, and standardize patterns across the Starship Battles codebase.

---

## Phase 8 Objectives

1. Remove test fixture aliases
2. Consolidate bug reproduction tests
3. Standardize code patterns (f-strings, exception types, naming)
4. Consolidate duplicate utility functions
5. Final cleanup and verification

---

## Detailed Tasks

### 8.1 Remove Test Fixture Aliases

**File:** `tests/unit/entities/conftest.py`
| Line | Alias | Canonical |
|------|-------|-----------|
| 24-25 | `basic_ship` | `basic_cruiser_ship` |

**File:** `tests/unit/combat/conftest.py`
| Line | Alias | Canonical |
|------|-------|-----------|
| 21 | `basic_combat_ship` | `basic_cruiser_ship` |
| 22 | `armed_combat_ship` | `armed_ship` |

**Steps for each alias:**
1. Search for all usages of the alias fixture
2. Update tests to use canonical fixture name
3. Remove the alias definition

**Example:**
```python
# Before
@pytest.fixture
def basic_combat_ship(basic_cruiser_ship):
    """Alias for backward compatibility."""
    return basic_cruiser_ship

# After: Delete this fixture entirely
```

### 8.2 Consolidate Bug Reproduction Tests

**Directory:** `tests/repro_issues/` (28 files)

Files: `test_bug_01_crew_delay.py` through `test_bug_27_ordertype.py`

**For each file, determine:**
1. Is the bug fixed?
2. Is there a regression test in the main test suite?
3. Does this test provide unique coverage?

**Actions:**
- If bug is fixed AND covered by main tests → Delete file
- If bug is fixed BUT unique coverage → Merge into appropriate test file
- If bug is not fixed → Keep, but consider if it should be addressed

**Likely merge targets:**
- Combat bugs → `tests/unit/combat/test_*.py`
- Strategy bugs → `tests/unit/strategy/test_*.py`
- Entity bugs → `tests/unit/entities/test_*.py`

### 8.3 Standardize String Formatting

**Migrate `.format()` to f-strings in these files:**

| File | Approximate Count |
|------|-------------------|
| `game/research/systems/research_service.py` | 2-3 |
| `game/ui/panels/ship_detail_panel.py` | 3-4 |
| `game/ui/screens/planet_list_filters.py` | 2-3 |
| `game/core/logger.py` | 1-2 |

**Before:**
```python
message = "Ship {} has {} HP remaining".format(ship.name, ship.hp)
```

**After:**
```python
message = f"Ship {ship.name} has {ship.hp} HP remaining"
```

### 8.4 Standardize Exception Types

**Files using generic `Exception`:**
| File | Line | Current |
|------|------|---------|
| `game/core/logger.py` | 35 | `raise Exception("Profiler is a singleton...")` |
| `game/core/profiling.py` | 35 | `raise Exception(...)` |
| `game/core/registry.py` | 50 | `raise Exception(...)` |
| `game/core/screenshot_manager.py` | 27 | `raise Exception(...)` |

**Change to:**
```python
raise RuntimeError("Singleton already initialized")
```

Or create custom exception:
```python
# game/core/exceptions.py
class SingletonError(RuntimeError):
    """Raised when attempting to create multiple singleton instances."""
    pass
```

### 8.5 Fix ALL_CAPS Instance Properties

**Issue:** Instance properties using ALL_CAPS (should be class constants or lowercase)

| File | Line | Property | Fix |
|------|------|----------|-----|
| `game/ui/screens/strategy_scene.py` | 67 | `self.HEX_SIZE = 10` | `self.hex_size = 10` or class constant |
| `game/ui/screens/strategy_scene.py` | 68 | `self.DETAIL_ZOOM_LEVEL = 3.0` | `self.detail_zoom_level = 3.0` |
| `game/ui/screens/strategy_fleet_ops.py` | 34 | `@property def HEX_SIZE` | `@property def hex_size` |

**Recommendation:** If value is constant, use class-level constant. If it varies per instance, use lowercase.

### 8.6 Consolidate Duplicate Utility Functions

#### 8.6.1 Color Calculation Functions

| File | Function | Thresholds |
|------|----------|------------|
| `game/ui/panels/ship_detail_panel.py` | `get_damage_color()` | >75% Green, 50-75% Yellow |
| `game/ui/panels/ship_stats_renderer.py` | `get_hp_bar_color()` | >50% Green, 20-50% Yellow |

**Decision:** Create unified function in `game/ui/utils.py` or keep separate if thresholds are intentionally different.

**If unifying:**
```python
# game/ui/utils.py
def get_health_color(percent: float, thresholds: Tuple[float, float] = (0.5, 0.2)) -> Color:
    """Get color based on health percentage.

    Args:
        percent: Health as 0.0-1.0
        thresholds: (yellow_threshold, red_threshold)

    Returns:
        Green if above yellow threshold, yellow if above red, else red
    """
    yellow, red = thresholds
    if percent > yellow:
        return GREEN
    elif percent > red:
        return YELLOW
    return RED
```

#### 8.6.2 Modifier Validation Functions

| File | Function |
|------|----------|
| `game/simulation/components/modifier_schema.py` | `validate_modifier_v2()` |
| `game/simulation/components/modifier_effects.py` | `validate_modifier_definition()` |

**Analysis:** Determine if these serve different purposes:
- Schema validation (structure/format)
- Effect validation (formula/logic)

If same purpose → Consolidate. If different → Keep separate but clarify names.

### 8.7 Consolidate Duplicate Classes

#### 8.7.1 ValidationResult Classes

| File | Class | Fields |
|------|-------|--------|
| `game/simulation/validation/base.py` | `ValidationResult` | `is_valid`, `errors[]`, `warnings[]`, `merge()` |
| `game/strategy/engine/turn_engine.py` | `ValidationResult` | `is_valid`, `message`, `error_code` |
| `game/ui/screens/race_validator.py` | `ValidationResult` | `is_valid`, `message` |

**Recommendation:** Use `game/simulation/validation/base.py` as canonical.

**Steps:**
1. Update turn_engine.py to use canonical ValidationResult
2. Update race_validator.py to use canonical ValidationResult
3. Remove duplicate class definitions

### 8.8 Remove Obsolete Tests

**File:** `tests/unit/combat/test_combat.py` (Lines 151-153)
- Comment: "Test is obsolete post-Phase 5"
- Action: Delete the obsolete test

**Skipped tests to evaluate:**
| File | Reason |
|------|--------|
| `simulation_tests/tests/test_projectile_weapons.py:97` | "Target ship engine configuration issue" |
| `simulation_tests/tests/test_seeker_weapons.py:250` | "Requires Point Defense target ships" |

For each: Fix the issue and enable the test, or delete if no longer relevant.

---

## Verification Checklist

After completing all tasks:

- [ ] All test fixture aliases removed
- [ ] Tests updated to use canonical fixture names
- [ ] Bug reproduction tests consolidated/removed
- [ ] `.format()` migrated to f-strings
- [ ] Generic `Exception` replaced with specific types
- [ ] ALL_CAPS instance properties fixed
- [ ] Duplicate utility functions consolidated
- [ ] Duplicate ValidationResult classes consolidated
- [ ] Obsolete tests removed
- [ ] Skipped tests evaluated
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Application launches and runs correctly
- [ ] Full test coverage maintained or improved

---

## Files Modified

**Test Infrastructure:**
- `tests/unit/entities/conftest.py`
- `tests/unit/combat/conftest.py`
- `tests/repro_issues/*.py` (consolidate/remove)
- `tests/unit/combat/test_combat.py`

**Code Style:**
- `game/research/systems/research_service.py`
- `game/ui/panels/ship_detail_panel.py`
- `game/ui/screens/planet_list_filters.py`
- `game/core/logger.py`
- `game/core/profiling.py`
- `game/core/registry.py`
- `game/core/screenshot_manager.py`

**Naming:**
- `game/ui/screens/strategy_scene.py`
- `game/ui/screens/strategy_fleet_ops.py`

**Consolidation:**
- `game/ui/utils.py` (new or existing)
- `game/strategy/engine/turn_engine.py`
- `game/ui/screens/race_validator.py`

---

## Final Verification

After all 8 phases are complete:

```bash
# Run all tests
pytest tests/ -v

# Run integration tests
pytest tests/integration/ -v

# Run simulation tests
pytest simulation_tests/ -v

# Check for deprecation warnings
python -W error::DeprecationWarning -c "from game.app import StarshipBattlesGame"

# Check for circular imports
python -c "import game.simulation; import game.strategy; import game.ai; import game.ui; print('All imports OK')"

# Launch application
python -m game.app
```

---

## Project Completion Summary

After Phase 8, the legacy cleanup project will have achieved:

1. **Dead code removed** - Marked files, debug tools, commented code
2. **Shims eliminated** - Builder→Workshop, aliases removed
3. **Imports consolidated** - Canonical paths, no re-exports
4. **Layer boundaries enforced** - Clean architecture, headless simulation
5. **Registry access standardized** - Tiered pattern documented
6. **Type safety improved** - Protocols, reduced duck typing
7. **Data formats unified** - Single format per data type
8. **Tests and patterns cleaned** - Consistent style, no duplicates

---

*End of Phase 8 Plan*

---

*End of Legacy Code Cleanup Project*
