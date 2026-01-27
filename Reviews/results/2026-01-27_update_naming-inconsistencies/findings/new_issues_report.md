# New Issues Report

## Summary
| Severity | Count |
|----------|-------|
| Critical | 2 |
| Major | 4 |
| Minor | 0 |
| Info | 0 |
| **Total** | **6** |

## New Issues Found

### NEW-01: CRITICAL: Duplicate ProjectileManager Class Definitions
**ID:** NEW-01
**Location:**
- `game/simulation/projectile_manager.py:11`
- `game/simulation/systems/projectile_manager.py:10`
**Issue:** Two separate files define the `ProjectileManager` class with nearly identical implementations. This creates confusion about which is the canonical version.
**Impact:** Import confusion, maintenance burden, potential for inconsistent updates if both files diverge.
**Recommendation:** Keep one canonical version (likely `game/simulation/systems/projectile_manager.py` as it's in the systems layer). Delete or refactor the duplicate in `game/simulation/projectile_manager.py` to be a shim that imports from the canonical location.
**Effort:** Simple

---

### NEW-02: CRITICAL: Multiple Classes Defined in game/ai/core/system.py
**ID:** NEW-02
**Location:** `game/ai/core/system.py`
**Issue:** This file defines multiple classes (`StrategyManager`, `AIController`) that are also defined in separate canonical files:
- `StrategyManager` also in `game/ai/strategy_manager.py:13`
- `AIController` also in `game/ai/controller.py` (implied from imports)
- Additionally, `game/ui/screens/battle.py` imports `AIController` from this legacy location
**Impact:** Legacy code organization problem. Imports are confused between canonical and legacy locations. The file appears to be a consolidation of older code.
**Recommendation:** Delete `game/ai/core/system.py` entirely and update any remaining imports to use canonical locations (`game.ai.strategy_manager` and `game.ai.controller`).
**Effort:** Medium (need to find and update all imports)

---

### NEW-03: MAJOR: Duplicate InputHandler Class Definitions with Different Purposes
**ID:** NEW-03
**Location:**
- `game/core/input_handler.py:5` (general game input, static methods)
- `game/ui/screens/strategy_input_handler.py:16` (strategy-specific input, instance-based)
**Issue:** Two classes with the same name but different designs:
- `game/core/input_handler.py`: Uses static methods, handles general game input (battle keydown)
- `game/ui/screens/strategy_input_handler.py`: Instance-based, handles strategy layer input
**Impact:** Naming confusion despite different purposes. Code that imports InputHandler could get the wrong version.
**Recommendation:** Rename one class to clarify purpose:
- Option A: Rename `game/core/input_handler.py`'s InputHandler to `GameInputHandler`
- Option B: Rename `game/ui/screens/strategy_input_handler.py`'s InputHandler to `StrategyInputHandler`
**Effort:** Simple

---

### NEW-04: MAJOR: Duplicate StrategyManager Class Definitions
**ID:** NEW-04
**Location:**
- `game/ai/strategy_manager.py:13` (canonical version with singleton pattern)
- `game/ai/core/system.py:39` (legacy version, simple class)
**Issue:** The canonical `StrategyManager` in `game/ai/strategy_manager.py` is a proper singleton with thread safety. The version in `game/ai/core/system.py` is a simpler implementation that should have been deleted when the newer version was created.
**Impact:** Two different implementations of the same class. Legacy code may still instantiate the wrong version.
**Recommendation:** Delete the version in `game/ai/core/system.py` (as part of deleting that entire file per NEW-02).
**Effort:** Simple

---

### NEW-05: MAJOR: 20+ Duplicate Ability Class Definitions in abilities.py
**ID:** NEW-05
**Location:**
- `game/simulation/components/abilities.py` (defines all ability classes monolithically)
- `game/simulation/components/abilities/*.py` (individual files define the same classes)
**Issue:** All ability classes are defined in both a monolithic `abilities.py` file AND in individual files within the `abilities/` directory. This is a clear code organization problem from a consolidation or refactoring.
**Impact:** Maintenance nightmare - changes to ability classes need to be made in two places. Import confusion - new code might import from the wrong location.
**Recommendation:**
- Delete `game/simulation/components/abilities.py` (the monolithic file)
- Keep only the individual files in `game/simulation/components/abilities/` (weapons.py, defense.py, resources.py, etc.)
- Update any imports from `game.simulation.components.abilities` to use the specific ability files
**Effort:** Medium (needs verification that all imports are updated)

---

### NEW-06: MAJOR: Duplicate ValidationRule Base Class Definitions
**ID:** NEW-06
**Location:**
- `game/simulation/validation/base.py:21` (proper abstract base with template method pattern)
- `game/simulation/systems/validator.py:12` (simpler abstract base)
**Issue:** Two different implementations of the `ValidationRule` base class:
- `game/simulation/validation/base.py`: Modern implementation with template method pattern, guard clauses, proper documentation
- `game/simulation/systems/validator.py`: Simpler, older implementation
**Impact:** Subclasses might inherit from the wrong base class, leading to inconsistent validation behavior.
**Recommendation:** Use `game/simulation/validation/base.py` as canonical (it's more modern). Update `game/simulation/systems/validator.py` to import `ValidationRule` from the canonical location instead of defining its own.
**Effort:** Simple

---

## Areas Searched
- Scanned all Python files in `game/` directory for duplicate class definitions
- Examined import patterns to identify which versions are canonical vs legacy
- Analyzed file organization in `game/ai/`, `game/simulation/`, `game/ui/screens/`
- Reviewed recently modified files (since 2026-01-26) for new consolidation issues
- Verified the relationship between files in the `game/simulation/components/abilities/` directory and the monolithic `abilities.py`
- Checked for import locations to distinguish canonical classes from legacy code

---

## Relationship to Original Findings

These NEW findings are distinct from the original 14 because:

- **NC-01** reported duplicate `BattleScene` (battle.py vs battle_scene.py) - we found 6 NEW duplicate classes not previously catalogued
- **NC-02 through NC-04** covered Builder/Workshop/Design terminology - these NEW issues are code organization duplicates, not terminology issues
- The original review focused on naming terminology inconsistencies; these NEW issues are structural duplicates from incomplete refactoring

---

**Key Insight:** The codebase appears to have undergone consolidation of files (e.g., from individual modules into larger files, or vice versa) without fully cleaning up the old locations. The `game/ai/core/system.py` file in particular appears to be a "junk drawer" of legacy code that should be deleted entirely.

---

*Report generated: 2026-01-27*
*Validation Agent: New Issue Scout*
