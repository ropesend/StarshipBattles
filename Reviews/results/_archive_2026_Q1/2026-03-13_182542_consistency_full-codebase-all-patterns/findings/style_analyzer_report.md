# Style Analyzer Report

**Date:** 2026-03-13
**Scope:** Full codebase - `game/` (429 Python files) and `tests/` (900 Python files)

---

### Summary

- Total issues found: 9
- Critical: 0, Major: 3, Minor: 4, Info: 2

---

### Findings

#### MAJOR: Logger declarations interleaved with imports in 88 files

**ID:** SA-01
**Location:** 88 files across all modules (e.g., `game/ai/controller.py:55`, `game/simulation/entities/ship.py:14`, `game/simulation/battle_controller.py:36`)
**Issue:** In 88 out of 139 files that use `logger = logging.getLogger(__name__)`, the logger declaration appears *between* import statements rather than after all imports. The standard Python convention (and PEP 8 recommendation) is to place all imports at the top, followed by module-level declarations. Only 26 files follow the correct pattern (logger after all imports). Some files even have the logger line with no blank line separating it from the surrounding imports, making it look like just another import.

**Examples:**
```python
# game/simulation/entities/ship.py - logger at line 14, more imports at lines 15-27
logger = logging.getLogger(__name__)
from game.core.constants import LayerDefaults, CombatConstants

# game/ai/controller.py - logger at line 55, 14 more import lines follow
logger = logging.getLogger(__name__)

from game.core.math import Vector2, angle_diff
from game.core.config import AIConfig, BattleConfig
```

**Impact:** Inconsistent logger placement creates confusion about where to place the logger when writing new files. It also makes imports harder to scan because they are split into two blocks by the logger line.
**Recommendation:** Standardize on placing `logger = logging.getLogger(__name__)` after all imports, separated by two blank lines. This matches 26 existing files and PEP 8 conventions.
**Effort:** Simple (mechanical change, can be automated)

---

#### MAJOR: UI module has significantly lower type hint coverage than other modules

**ID:** SA-02
**Location:** `game/ui/` (entire module)
**Issue:** Type hint coverage varies dramatically across modules:

| Module       | Param Hints | Return Hints | Functions |
|-------------|-------------|-------------|-----------|
| research    | 100.0%      | 95.0%       | 40        |
| strategy    | 94.0%       | 86.7%       | 825       |
| core        | 93.8%       | 91.4%       | 279       |
| ai          | 86.8%       | 89.4%       | 161       |
| simulation  | 83.7%       | 77.6%       | 697       |
| engine      | 63.6%       | 46.7%       | 15        |
| **ui**      | **57.2%**   | **46.6%**   | **2131**  |
| game (root) | 30.4%       | 2.2%        | 45        |

The `ui` module has 2131 functions - the largest module - and only 57% have parameter type hints and 47% have return type hints. Specific files with near-zero coverage include:
- `game/ui/screens/test_lab/screen.py`: 0/55 functions (0%)
- `game/ui/screens/builder/stats_config.py`: 0/43 (0%)
- `game/ui/screens/strategy_screen.py`: 0/41 (0%)
- `game/ui/screens/workshop_screen.py`: 0/30 (0%)

**Impact:** Missing type hints in the largest module reduces IDE support, makes refactoring riskier, and creates inconsistency with the well-typed core/strategy/simulation modules.
**Recommendation:** Prioritize adding type hints to the largest UI files first. The `research`, `core`, and `strategy` modules demonstrate excellent coverage and should be used as the standard.
**Effort:** Complex (2131 functions, many in large screen files)

---

#### MAJOR: Import ordering not following PEP 8 grouping in 71 files

**ID:** SA-03
**Location:** 71 files across `game/` (e.g., `game/app.py`, `game/ai/protocols.py`, `game/core/config.py`, `game/core/registry.py`)
**Issue:** PEP 8 specifies that imports should be grouped in this order: (1) standard library, (2) third-party packages, (3) local imports, with blank lines between groups. In 71 files, standard library imports (e.g., `import logging`, `from typing import ...`, `from enum import Enum`) appear *after* local `game.*` imports.

A common pattern is module docstring, then local imports, then stdlib imports:
```python
# game/core/config.py
from typing import Tuple  # stdlib - but comes after the class definitions would start

# game/simulation/battle_controller.py
from game.core.exceptions import StateException  # local
import logging  # stdlib AFTER local
```

**Impact:** Inconsistent import ordering makes it harder to quickly scan dependencies and understand what a module relies on. It creates a confusing pattern for new code.
**Recommendation:** Enforce standard PEP 8 import ordering: stdlib, then blank line, then third-party, then blank line, then local. Tools like `isort` can automate this.
**Effort:** Simple (can be fully automated with `isort`)

---

#### MINOR: Mixed use of `Optional[X]` (782 occurrences) vs `X | None` (5 occurrences)

**ID:** SA-04
**Location:** Codebase-wide, with `X | None` only in `game/ui/screens/empire_build_queue_filter_manager.py`, `game/ui/screens/planet_selection_window.py`, `game/simulation/components/component.py`
**Issue:** The codebase overwhelmingly uses `Optional[X]` from `typing` (782 occurrences across 200 files). Only 5 instances use the newer `X | None` syntax (PEP 604, Python 3.10+). Similarly, the codebase uses `typing.Tuple/List/Dict` (1413 occurrences) with only 59 uses of the lowercase `tuple/list/dict` builtins (PEP 585). Only 51 files use `from __future__ import annotations`.

**Impact:** The inconsistency is very minor since 99.4% of the codebase uses the older style consistently. The few `X | None` and `list[x]` usages are outliers that create minor visual inconsistency.
**Recommendation:** Maintain `Optional[X]` and `typing.Tuple/List/Dict` as the standard since they are overwhelmingly dominant and the project targets Python 3.10. If a future migration to PEP 604/585 is desired, do it all at once.
**Effort:** Simple (fix the 5 outlier usages)

---

#### MINOR: 40 classes lack docstrings across game/ (93.6% coverage)

**ID:** SA-05
**Location:** Scattered across modules, including `game/ai/behaviors.py` (AIBehavior, RamBehavior, FleeBehavior), `game/ai/controller.py` (AIController), `game/engine/physics.py` (PhysicsBody), `game/simulation/entities/ship.py` (Ship), `game/simulation/components/component.py` (Component)
**Issue:** While 93.6% of classes have docstrings (586 of 626), 40 classes are missing them. Notably, several of these are *core* classes: `Ship`, `PhysicsBody`, `AIController`, `Component`, and `Projectile`. These are among the most important classes in the codebase but lack the docstrings that less critical classes have.

**Impact:** The missing docstrings on high-importance core classes is worse than missing them on minor utility classes. `Ship` and `Component` are foundational abstractions that would especially benefit from class-level documentation.
**Recommendation:** Add docstrings to the 40 missing classes, prioritizing the core/simulation ones (Ship, PhysicsBody, AIController, Component, Projectile).
**Effort:** Medium (40 classes, requires understanding each class's purpose)

---

#### MINOR: 35 game/ files and 89 test files lack module docstrings

**ID:** SA-06
**Location:** 35 files in `game/` (9.2% of non-init files), 89 test files in `tests/`
**Issue:** Module docstrings are present in 90.8% of `game/` files, showing strong overall coverage. The 35 missing files are primarily in `game/simulation/components/abilities/` (7 files) and `game/strategy/data/` (6 files). In tests, 89 `test_*.py` files lack module docstrings.

The game files without module docstrings tend to start directly with imports, missing the opportunity to explain the module's purpose:
```python
# game/simulation/components/abilities/defense.py - starts with imports
from typing import Dict, Any, List
```

**Impact:** Low impact in game/ since 90.8% coverage is good. Test files are less critical but docstrings help explain what area each test file covers.
**Recommendation:** Add module docstrings to the 35 game/ files. Test files are lower priority but would benefit from a one-line docstring indicating the test subject.
**Effort:** Simple for game/ (35 files), Medium for tests/ (89 files)

---

#### MINOR: Inconsistent use of `from __future__ import annotations` (51 of 429 files)

**ID:** SA-07
**Location:** 51 files across `game/` use `from __future__ import annotations`, 378 do not
**Issue:** Only 12% of files use the future annotations import. This creates an inconsistency where some files get deferred annotation evaluation and others do not. This can lead to subtle behavioral differences, particularly around `isinstance()` checks with type aliases and `get_type_hints()` calls.

**Impact:** Since the project is on Python 3.10+ and primarily uses `Optional[X]` style, the future import is not strictly needed. But the 51 files that do use it create inconsistency.
**Recommendation:** Either adopt `from __future__ import annotations` everywhere (enables PEP 604/585 syntax across all Python 3.10+ versions) or remove it from the 51 files that use it. Given the codebase uses `Optional[X]` consistently, removing the future import from the 51 outlier files is simpler.
**Effort:** Simple (remove from 51 files, or add to all 378)

---

#### INFO: String formatting is highly consistent (f-strings dominant)

**ID:** SA-08
**Location:** Codebase-wide
**Issue:** String formatting is very consistent:
- **f-strings:** 1967 lines (dominant style)
- **`.format()`:** 4 lines (all in template/format-string contexts where f-strings can't be used, e.g., `self.ui_format.format(val)` in ability base class)
- **% formatting:** 0 lines
- **String concatenation:** negligible

The 4 `.format()` usages are legitimate - they use stored format strings (`'{:.0f}'.format(val)`) which cannot be replaced with f-strings since the format string is a data-driven template.

**Impact:** None. This is an example of excellent consistency.
**Recommendation:** No action needed. The current pattern is clean and the few `.format()` usages are justified.
**Effort:** N/A

---

#### INFO: Naming conventions are highly consistent

**ID:** SA-09
**Location:** Codebase-wide
**Issue:** Naming conventions are remarkably consistent across the codebase:
- **snake_case:** Used universally for functions, methods, variables, and modules. Zero camelCase methods found.
- **UPPER_CASE:** Used consistently for constants (class attributes and module-level).
- **Boolean prefixes:** `is_`, `has_`, `can_` used consistently for boolean properties and functions.
- **Private methods:** 1080 single-underscore private methods vs 2815 public methods (28% private) - reasonable ratio.
- **No bare `except`:** Zero instances found. Exception handling uses specific exception types.
- **Google-style docstrings:** 338 files use `Args:/Returns:/Raises:` format. Zero files use Sphinx (`:param`) or NumPy style.
- **Quote style:** Double quotes are dominant (42309 vs 17335 single quotes), consistent with docstrings and string literals using double quotes. Single quotes are used appropriately for dict keys and short strings.
- **PROJ- comments:** 363 cross-references to project IDs in comments, providing traceability. Only 2 TODO comments exist (both legitimate).

**Impact:** None. This is excellent naming discipline across a large codebase.
**Recommendation:** No action needed. Continue following current conventions.
**Effort:** N/A

---

### Top 5 Priority Issues

1. **SA-01 (Major):** Logger declarations interleaved with imports in 88 files - Easy to fix, affects readability across the whole codebase, and can be automated.

2. **SA-03 (Major):** Import ordering violations in 71 files - Easy to fix with `isort`, establishes clean patterns for new code.

3. **SA-02 (Major):** UI module type hint coverage at 57%/47% vs 85-100% in other modules - Highest effort but highest long-term value. The UI module is the largest and least typed.

4. **SA-05 (Minor):** Core classes (Ship, PhysicsBody, AIController, Component) missing docstrings - These are the most-read classes and should be documented first.

5. **SA-04 (Minor):** 5 files using `X | None` instead of `Optional[X]` - Quick fix to eliminate outliers and maintain consistency.
