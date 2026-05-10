# Convention Enforcer Report

**Date:** 2026-03-13
**Scope:** Full codebase - `game/` (429 files), `tests/` (900 files)

---

### Summary
- Total issues found: 14
- Critical: 1, Major: 5, Minor: 6, Info: 2

---

### Findings

#### MAJOR: Test directory structure does not mirror source structure
**ID:** CE-01
**Location:** `tests/unit/` (17 orphaned directories)
**Issue:** Many test directories under `tests/unit/` do not mirror the `game/` package structure. There are 17 directories (builder/, combat/, components/, entities/, modifiers/, systems/, workshop/, abilities/, services/, test_lab/, validation/, fixtures/, performance/, regressions/, repro_issues/, quickstart/, simulation_tests/) that have no corresponding `game/` top-level module. These tests actually cover code in `game/simulation/`, `game/ui/`, etc., but are organized by concept rather than by source location.
**Impact:** Makes it difficult to find tests for a given source file. Developers cannot reliably navigate from a source module to its tests. Some tests may be duplicated or forgotten.
**Recommendation:** Consolidate orphaned test directories into the mirrored structure. For example, `tests/unit/builder/` tests should move to `tests/unit/ui/builder/` or `tests/unit/ui/screens/builder/`, `tests/unit/combat/` to `tests/unit/simulation/combat/`, `tests/unit/entities/` to `tests/unit/simulation/entities/`, etc.
**Effort:** Complex

---

#### MAJOR: Inconsistent relative vs absolute import convention
**ID:** CE-02
**Location:** `game/simulation/` (44 relative imports in non-init files), `game/ui/` (25 relative), vs `game/strategy/` (0 relative), `game/core/` (0 relative)
**Issue:** The codebase overwhelmingly uses absolute imports (1086 absolute vs 112 relative across all of `game/`). However, `game/simulation/components/abilities/` uses relative imports extensively (35 of 44 simulation relative imports), and `game/ui/screens/builder/` and `game/ui/screens/test_lab/` also use relative imports. Meanwhile `game/strategy/` and `game/core/` use zero relative imports outside of `__init__.py` files.
**Impact:** Inconsistency creates confusion about which style to follow. Absolute imports are the dominant convention but two subpackages break it.
**Recommendation:** Standardize on absolute imports for all non-`__init__.py` files, matching the dominant pattern used in `game/strategy/`, `game/core/`, `game/ai/`, and `game/engine/`. Relative imports in `__init__.py` files are fine (that is the expected pattern for re-exports).
**Effort:** Medium

---

#### MAJOR: `__init__.py` re-exports are unused
**ID:** CE-03
**Location:** `game/core/__init__.py`, `game/simulation/__init__.py`, `game/strategy/__init__.py`, `game/ai/__init__.py`, `game/engine/__init__.py`
**Issue:** These `__init__.py` files define comprehensive public APIs with detailed docstrings and `__all__` lists, re-exporting key symbols. However, zero production code uses these re-exports. All 404 core imports go directly to submodules (e.g., `from game.core.constants import GameState` instead of `from game.core import GameState`). Only 9 test files use `from game.core import ...`. The simulation, strategy, ai, and engine packages have exactly 0 consumers of their re-exports.
**Impact:** The `__init__.py` re-exports create a maintenance burden (must be kept in sync with source modules) for zero benefit. They provide a misleading "Public API" that nobody uses.
**Recommendation:** Either (a) adopt the re-export pattern and update all imports to use it, or (b) strip the re-exports and use `__init__.py` only for docstrings and package markers. Option (b) is simpler and matches actual usage. If kept, add a lint rule to enforce using the re-exported names.
**Effort:** Medium

---

#### CRITICAL: Missing `__init__.py` in key game packages
**ID:** CE-04
**Location:** `game/simulation/entities/`, `game/simulation/systems/`, `game/strategy/engine/`, `game/strategy/systems/`, `game/assets/`, `game/data/`
**Issue:** Six directories containing Python modules have no `__init__.py` file. These are not small directories -- `game/simulation/entities/` has 13 Python files, `game/strategy/engine/` has 20. While Python 3 supports implicit namespace packages, this project explicitly uses `__init__.py` everywhere else (42 of 48 subdirectories have them). The missing files break the convention and can cause issues with some tools (IDE auto-imports, pytest collection, etc.).
**Impact:** Inconsistency in package structure. Potential for subtle import issues. The `game/ui/__init__.py` explicitly pre-imports submodules for pytest-xdist race conditions -- the same issue could affect these packages.
**Recommendation:** Add `__init__.py` to all six directories. For `game/simulation/entities/` and `game/strategy/engine/` (heavily used packages), consider adding re-export patterns matching the established convention.
**Effort:** Simple

---

#### MAJOR: Repro scripts scattered in tests root
**ID:** CE-05
**Location:** `tests/repro_colonize_population.py`, `tests/repro_facade_colonies.py`, `tests/repro_load_cargo_bug.py`, `tests/repro_warp_bug.py`
**Issue:** Four standalone reproduction scripts sit directly in the `tests/` root directory. A separate `tests/repro_issues/` directory exists with 26 properly organized bug reproduction test files following a `test_bug_NN_*.py` naming convention. The root-level repro scripts do not follow the `test_` naming convention and are not organized with the others.
**Impact:** Clutters the tests root. These files may not be discovered by pytest. Inconsistent with the organized `tests/repro_issues/` directory.
**Recommendation:** Move these four files into `tests/repro_issues/`, renaming them to follow the `test_bug_NN_*.py` convention or at minimum the `test_*.py` prefix.
**Effort:** Simple

---

#### MINOR: `exit_dialog.py` lives at wrong layer
**ID:** CE-06
**Location:** `game/exit_dialog.py`
**Issue:** `exit_dialog.py` is a UI component (draws Pygame surfaces, handles mouse clicks) that lives at the `game/` root instead of in `game/ui/`. It is only imported by `game/app.py`. The project's architecture defines `game/ui/` as the top layer for all Pygame rendering.
**Impact:** Violates the layer separation convention. Minor but confusing for developers looking for UI code.
**Recommendation:** Move to `game/ui/dialogs/exit_dialog.py` or `game/ui/widgets/exit_dialog.py`.
**Effort:** Simple

---

#### MINOR: Dual asset modules (`game/assets/` and `game/ui/assets/`)
**ID:** CE-07
**Location:** `game/assets/asset_manager.py`, `game/ui/assets/ship_theme_manager.py`
**Issue:** Asset management is split across two locations: `game/assets/` (general AssetManager, no `__init__.py`) and `game/ui/assets/` (ShipThemeManager, proper `__init__.py`). Both are UI concerns (loading images, managing sprites). Six files import from `game.assets.asset_manager` and eight from `game.ui.assets`.
**Impact:** Confusing split of related functionality. `game/assets/` has no `__init__.py`, making it a second-class citizen in the package structure.
**Recommendation:** Consolidate into `game/ui/assets/` since both are UI-layer concerns, or if `AssetManager` is needed by non-UI code, move it to `game/core/`.
**Effort:** Medium

---

#### MINOR: `__init__.py` missing `__all__` in 3 non-trivial files
**ID:** CE-08
**Location:** `game/research/__init__.py` (8 lines), `game/strategy/facade/__init__.py` (5 lines), `game/ui/screens/builder/__init__.py` (7 lines)
**Issue:** These three `__init__.py` files have imports but no `__all__` declaration, while 38 other `__init__.py` files consistently define `__all__`. The `builder/__init__.py` imports 7 symbols without declaring which are public.
**Impact:** Minor inconsistency. Without `__all__`, `from package import *` would export everything, though wildcard imports are not used in this codebase.
**Recommendation:** Add `__all__` to these three files to match the codebase convention.
**Effort:** Simple

---

#### MINOR: `__init__.py` missing module docstrings in 2 files
**ID:** CE-09
**Location:** `game/strategy/services/__init__.py`, `game/ui/screens/builder/__init__.py`
**Issue:** These two non-trivial `__init__.py` files lack module docstrings, while 40 other `__init__.py` files consistently have them. The convention is well-established: descriptive docstrings with "Public API" sections for major packages.
**Impact:** Trivial inconsistency but breaks the otherwise clean pattern.
**Recommendation:** Add docstrings matching the established format.
**Effort:** Simple

---

#### MAJOR: JSON data files split between `data/` and `game/data/` without clear convention
**ID:** CE-10
**Location:** `data/` (18 JSON files), `game/data/` (2 JSON files)
**Issue:** Game configuration data is split between `data/` (root-level, 18 files like components.json, modifiers.json) and `game/data/` (2 files: homeworld_presets.json, race_names.json). The `Paths` class references only `data/` (root) via `DATA_DIR`. The `game/data/` files are loaded via ad-hoc path construction (`os.path.join(Paths.GAME_DIR, "data", ...)`) bypassing the centralized `Paths` class.
**Impact:** Inconsistent data file location makes it unclear where new data files should go. The `game/data/` files bypass the `Paths` abstraction, creating fragile path references.
**Recommendation:** Move `game/data/*.json` to `data/` and add corresponding entries to the `Paths` class, or document why certain data lives in `game/data/` vs `data/`.
**Effort:** Simple

---

#### MINOR: Missing `__init__.py` in many test directories
**ID:** CE-11
**Location:** 14 test directories including `tests/unit/ai/`, `tests/unit/core/`, `tests/unit/strategy/`, `tests/unit/engine/`, etc.
**Issue:** Multiple test directories containing test files lack `__init__.py`. While pytest can discover tests without them, the project uses `__init__.py` in some test directories (e.g., `tests/unit/simulation/__init__.py`) but not others. The `tests/unit/simulation/` has one, but `tests/unit/core/`, `tests/unit/ai/`, `tests/unit/strategy/` (174 test files!) do not.
**Impact:** Inconsistency. Could cause issues with test collection in some configurations or with pytest-xdist (as noted in `game/ui/__init__.py` comments about race conditions).
**Recommendation:** Either add `__init__.py` to all test directories (safer, consistent) or remove them from the ones that have them. Given the xdist race condition precedent, adding them is safer.
**Effort:** Simple

---

#### MINOR: Large files exceed preferred size limits
**ID:** CE-12
**Location:** 54 files over 500 lines, 4 files over 1000 lines
**Issue:** The CLAUDE.md guidelines state "Keep functions focused and small (<50 lines preferred)" and the project has active god-class decomposition projects (PROJ-86 through PROJ-89). The largest files are: `strategy_renderer.py` (1102), `test_lab/renderer.py` (1040), `command_handlers.py` (1032), `race_setup_screen.py` (1029), `protocols.py` (987).
**Impact:** Known issue being addressed by active projects. Documenting for completeness.
**Recommendation:** Continue with PROJ-86 through PROJ-89 decomposition work.
**Effort:** Complex (already planned)

---

#### INFO: `game/data/` is a directory with JSON files but no Python code, yet sits inside `game/` package
**ID:** CE-13
**Location:** `game/data/`
**Issue:** `game/data/` contains only 2 JSON files and no Python modules. Unlike `game/strategy/data/` and `game/research/data/` (which contain Python data model classes), this directory is a pure data store. It has no `__init__.py` and is arguably misplaced inside the Python package.
**Impact:** Minimal. Could cause confusion about the difference between `data/` (root) and `game/data/`.
**Recommendation:** See CE-10 -- consolidate with `data/`.
**Effort:** Simple

---

#### INFO: Test helper classes inline in test files rather than in shared fixtures
**ID:** CE-14
**Location:** Multiple integration test files (e.g., `test_colonize_logic.py`, `test_command_handlers.py`, `test_economy_e2e.py`)
**Issue:** Mock classes like `MockGalaxy`, `MockPlanet`, `MockSystem`, `MockPlanetType` are duplicated across multiple integration test files rather than being shared via conftest.py or a test fixtures module. For example, `MockPlanetType(Enum)` appears in at least 3 separate files with near-identical implementations.
**Impact:** Minor code duplication. When the mocked interfaces change, multiple files must be updated.
**Recommendation:** Extract common mock classes into shared fixtures (conftest.py or `tests/fixtures/`). The project already has a `tests/fixtures/` directory that could house these.
**Effort:** Medium

---

### Top 5 Priority Issues

1. **CE-04 (CRITICAL):** Missing `__init__.py` in 6 game packages -- simple fix, prevents potential import issues in heavily-used packages like `game/simulation/entities/` (13 files) and `game/strategy/engine/` (20 files).

2. **CE-01 (MAJOR):** Test directory structure divergence -- 17 orphaned test directories make it hard to find tests for source code. Most impactful for developer productivity.

3. **CE-10 (MAJOR):** JSON data split between `data/` and `game/data/` -- easy consolidation that eliminates ad-hoc path construction bypassing the `Paths` class.

4. **CE-02 (MAJOR):** Inconsistent import style -- 44 relative imports in `game/simulation/` break the otherwise-universal absolute import convention. Should be standardized.

5. **CE-03 (MAJOR):** Unused `__init__.py` re-exports -- significant maintenance burden (hundreds of lines of re-export code and docstrings) with zero consumers. Should either be adopted or removed.
