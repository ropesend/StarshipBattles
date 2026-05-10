# Convention Enforcer Report

**Date:** 2026-03-13
**Scope:** `game/` directory (429 Python files, ~109K lines)
**Layers analyzed:** core (21), simulation (73), strategy (113), ai (10), ui (197), engine (4), research (7), top-level (2)

---

## Summary

- **Total issues found:** 22
- **Critical:** 2
- **Major:** 8
- **Minor:** 9
- **Info:** 3

---

## Convention Compliance Scorecard

| Convention | Compliance Level | Expected | Violations |
|---|---|---|---|
| File naming (snake_case) | 100% | All snake_case | 0 violations |
| Layer separation (imports) | ~97% | No upward imports | 10 pygame leaks |
| `__init__.py` with `__all__` | 88% (37/42 non-empty) | All non-empty inits have `__all__` | 5 missing |
| Module docstrings | 90% (346/381) | 100% | 35 missing |
| `__init__` first in class | 98% (235/240) | Always first | 5 violations |
| Import style (absolute) | 93% dominant | Absolute preferred | Mixed in 20 files |
| TYPE_CHECKING usage | 46% (176/381) | When needed | Widespread, good adoption |
| Interface pattern (Protocol) | ~75% Protocol | Uniform choice | Mixed ABC/Protocol |
| Interface naming (I-prefix) | 90% (61/68) | Consistent I-prefix | 7 without prefix |
| Return type hints | 61% overall | 100% target | 1471 functions missing |
| Single responsibility (file) | ~86% | 1-2 classes per file | 22 files with 4+ classes |
| File size (<500 lines) | 86% | <500 lines | 54 files exceed threshold |
| No pygame outside UI | ~97% | 0 outside UI | 8 non-UI files |
| Enum centralization | Scattered | Centralized per layer | 15 files across all layers |
| Subpackage organization | Partial | Prefix groups = subpackages | 77 files flat in ui/screens |

---

## Findings

### Critical Issues

#### Critical: Duplicate Interface Names Across Layers
**ID:** CE-001
**Location:** `game/core/protocols.py`, `game/simulation/interfaces/entity_protocols.py`, `game/ai/protocols.py`
**Issue:** Two completely separate `ICombatShip` protocols exist (one in core, one in simulation). Two separate `IProjectile` protocols exist (one in ai, one in simulation). These are distinct types with different method sets that share the same name.
**Expected:** Interface names should be globally unique across the codebase, or one should be the canonical definition.
**Impact:** Causes confusion about which `ICombatShip` or `IProjectile` to import. Can cause subtle type-checking bugs where the wrong protocol is used. Makes code review and refactoring error-prone.
**Recommendation:** Rename to disambiguate (e.g., `ICoreShip` vs `ISimCombatShip`) or consolidate into a single canonical definition that both layers reference.
**Effort:** Medium

#### Critical: Mixed ABC vs Protocol for Interface Definitions
**ID:** CE-002
**Location:** `game/strategy/interfaces/engines.py` (12 ABCs), `game/simulation/interfaces/` (17 Protocols), `game/ai/interfaces/` (1 ABC), `game/core/protocols.py` (24 Protocols)
**Issue:** The strategy layer exclusively uses ABC for its interface definitions, while simulation and core exclusively use Protocol. AI uses ABC. These serve the same architectural purpose (defining contracts) but use incompatible mechanisms. ABC requires explicit subclassing; Protocol uses structural typing.
**Expected:** A single consistent pattern across all layers. Given that Protocol is the modern Python approach and already dominant (41 Protocol vs 13 ABC), Protocol should be the standard.
**Impact:** Developers must remember which pattern each layer uses. The mechanisms have different behaviors: ABC forces inheritance while Protocol allows duck typing. This inconsistency creates confusion about the project's interface philosophy.
**Recommendation:** Standardize on `Protocol` with `@runtime_checkable` across all layers. Migrate the 13 ABC-based interfaces in `game/strategy/interfaces/` and `game/ai/interfaces/` to Protocol.
**Effort:** Medium

---

### Major Issues

#### Major: Massive Flat Directory in `game/ui/screens/` (77 files)
**ID:** CE-003
**Location:** `game/ui/screens/` (77 Python files at top level, excluding subpackages)
**Issue:** The screens directory contains 77 files at the top level, making it the largest flat directory in the project. Clear prefix-based groups exist but are not organized into subpackages:
- `strategy_*`: 19 files, 7,008 lines
- `build_queue_*`: 7 files, 1,958 lines
- `empire_build_queue_*`: 6 files, 1,725 lines
- `fleet_*`: 6 files, 2,232 lines
- `workshop_*`: 7 files, 2,494 lines

**Expected:** Prefix groups with 5+ files and 1,500+ lines should be subpackages, following the pattern already established by `builder/`, `test_lab/`, `formation/`, and `galaxy_test/`.
**Impact:** Navigating 77 files in a single directory is unwieldy. IDE file lists are cluttered. The existing subpackage pattern proves this project values subdirectory organization, but the largest groups have not been migrated.
**Recommendation:** Create subpackages for at least `strategy/` (19 files) and potentially `build_queue/`, `fleet/`, and `workshop/`.
**Effort:** Complex (many import updates required)

#### Major: Pygame Imports Outside UI Layer
**ID:** CE-004
**Location:** Various (8 non-UI files import pygame directly)
- `game/core/math.py` - mentions pygame.math.Vector2 in comments/docs only
- `game/core/protocols.py` - references pygame event handling in protocol
- `game/core/input_actions.py` - references pygame key names in comments
- `game/simulation/projectile_manager.py` - handles pygame Vector2 in code
- `game/ai/interfaces/controllable.py` - mentions pygame Vector2 in comments
- `game/assets/asset_manager.py` - direct pygame.image calls
- `game/app.py` - pygame.init() (acceptable, entry point)
- `game/exit_dialog.py` - direct pygame.Surface/draw calls

**Expected:** Per architecture docs, only the UI layer should depend on pygame. Core, simulation, and AI layers should be framework-agnostic.
**Impact:** Violates the documented layer separation principle. Makes it harder to test these modules without pygame installed. Prevents potential future framework migration.
**Recommendation:**
- `game/assets/asset_manager.py` should be moved under `game/ui/assets/`
- `game/exit_dialog.py` should be moved under `game/ui/`
- `game/simulation/projectile_manager.py` should eliminate pygame Vector2 handling
- Comment-only references (core/math.py, core/input_actions.py, ai/interfaces) are informational and acceptable
**Effort:** Medium

#### Major: 54 Files Exceed 500-Line Threshold
**ID:** CE-005
**Location:** Various (14% of all files)
**Issue:** 54 files exceed 500 lines, with the worst offenders being:
- `game/ui/screens/strategy_renderer.py` (1,102 lines)
- `game/ui/screens/test_lab/renderer.py` (1,040 lines)
- `game/strategy/engine/command_handlers.py` (1,032 lines)
- `game/ui/screens/race_setup_screen.py` (1,029 lines)
- `game/core/protocols.py` (987 lines, 23 protocols)

**Expected:** Files under 500 lines per project convention (CLAUDE.md: "<50 lines preferred" for functions; the 500-line file threshold is a common project standard).
**Impact:** Large files are harder to navigate, review, and maintain. They tend to accumulate more responsibilities over time.
**Recommendation:** Prioritize splitting files over 800 lines. The `core/protocols.py` monolith (23 protocols) should be split by domain (combat protocols, strategy protocols, entity protocols). Renderer files over 1,000 lines should extract helper classes.
**Effort:** Complex (ongoing, many files)

#### Major: Inconsistent Interface/Protocol Location Pattern
**ID:** CE-006
**Location:** Various
**Issue:** Protocols and interfaces are stored inconsistently across layers:
- `game/core/protocols.py` - single file, no `interfaces/` directory
- `game/simulation/interfaces/` - dedicated directory with 4 files
- `game/strategy/interfaces/` - dedicated directory with 2 files
- `game/ai/interfaces/` - dedicated directory with 1 file + `game/ai/protocols.py` (separate file!)
- `game/ui/interfaces/` - dedicated directory with 1 file

The AI layer is the worst case: it has BOTH `game/ai/interfaces/` AND `game/ai/protocols.py`, splitting interface definitions across two locations.

**Expected:** Each layer should use a consistent location for interfaces. Either a dedicated `interfaces/` directory or a single `protocols.py` file, not both.
**Impact:** Developers must check multiple locations when looking for interface definitions. The AI layer's split is particularly confusing.
**Recommendation:** Standardize on `interfaces/` directory for layers with multiple protocol files. Move `game/ai/protocols.py` into `game/ai/interfaces/`. Consider moving `game/core/protocols.py` content into `game/core/interfaces/` given it has 23 protocols (split by domain).
**Effort:** Medium

#### Major: Return Type Hint Coverage at 61% Overall, 43% in UI
**ID:** CE-007
**Location:** Primarily `game/ui/` (43% coverage, 1101 functions missing hints)
**Issue:** Return type hint coverage varies dramatically by layer:
- `game/core/`: 91% (excellent)
- `game/ai/`: 89% (excellent)
- `game/strategy/`: 83% (good)
- `game/simulation/`: 74% (acceptable)
- `game/engine/`: 46% (poor)
- `game/ui/`: 43% (poor - 1,101 functions without return types)

**Expected:** CLAUDE.md requires "type hints for function signatures." 100% return type hint coverage on public APIs, 80%+ on all functions.
**Impact:** Missing type hints reduce IDE support, prevent static analysis from catching bugs, and make code harder to understand.
**Recommendation:** Prioritize adding return type hints to `game/ui/` (largest gap). Can be done incrementally, file-by-file. Start with public methods.
**Effort:** Complex (1,101 functions to annotate, but can be done incrementally)

#### Major: `game/strategy/data/` Has 36 Files with Empty `__init__.py`
**ID:** CE-008
**Location:** `game/strategy/data/__init__.py` (empty), 36 Python files in the directory
**Issue:** The `game/strategy/data/` package has an empty `__init__.py` with 36 modules, making it the second-largest flat directory. There are no public re-exports, so consumers must know the exact module path for every import. Compare with `game/simulation/services/__init__.py` which properly re-exports its public API.
**Expected:** Packages with many modules should have `__init__.py` files that define `__all__` and re-export the public API. Other empty `__init__.py` offenders: `game/simulation/components/`, `game/ui/panels/`, `game/ui/renderer/`, `game/ui/screens/`.
**Impact:** Without re-exports, every consumer must know the internal file structure. API discoverability is poor. Refactoring file locations requires updating all call sites.
**Recommendation:** Add re-exports to `game/strategy/data/__init__.py` for the most commonly used types (Fleet, ShipInstance, Galaxy, Empire, etc.). Apply the same treatment to other empty `__init__.py` files in large packages.
**Effort:** Medium

#### Major: Undocumented Top-Level Directories
**ID:** CE-009
**Location:** `game/assets/`, `game/data/`, `game/engine/`, `game/research/`
**Issue:** The project documentation (CLAUDE.md) describes the layer structure as core, simulation, strategy, ai, and ui. However, four additional top-level directories exist that are not documented:
- `game/assets/` (1 file: asset_manager.py - 288 lines, uses pygame)
- `game/data/` (2 JSON files, no Python)
- `game/engine/` (4 files: physics, collision, spatial - 360 lines total)
- `game/research/` (7 files - 935 lines total)

**Expected:** All top-level directories should be part of the documented architecture. Their layer dependencies should be defined.
**Impact:** New contributors won't know about these modules. Layer dependency rules are undefined for these packages. `game/assets/` with its pygame dependency arguably belongs under `game/ui/`.
**Recommendation:** Document `game/engine/` and `game/research/` in CLAUDE.md architecture section. Move `game/assets/asset_manager.py` to `game/ui/assets/`. Consider whether `game/data/` JSON files should be under a documented data directory.
**Effort:** Simple

---

### Minor Issues

#### Minor: 5 `__init__.py` Files Missing `__all__`
**ID:** CE-010
**Location:**
- `game/research/__init__.py` (8 lines, has docstring but no exports)
- `game/strategy/facade/__init__.py` (5 lines, has docstring but no exports)
- `game/ui/components/__init__.py` (1 line, just a docstring)
- `game/ui/screens/builder/__init__.py` (7 lines, has imports but no `__all__`)
- 6 empty `__init__.py` files (game/, simulation/components/, strategy/data/, ui/panels/, ui/renderer/, ui/screens/)

**Expected:** Non-empty `__init__.py` files should define `__all__` to document the public API.
**Impact:** Without `__all__`, wildcard imports (`from package import *`) are undefined, and the package's public API is ambiguous.
**Recommendation:** Add `__all__` to the 5 non-empty init files missing it. Empty inits are acceptable for pure namespace packages.
**Effort:** Simple

#### Minor: 35 Files Missing Module Docstrings
**ID:** CE-011
**Location:** Various (see list below)
**Issue:** 35 of 381 non-init Python files (9%) lack module-level docstrings. Concentrations:
- `game/simulation/components/abilities/` - 7 files (base.py, crew.py, defense.py, markers.py, propulsion.py, resources.py, weapons.py)
- `game/strategy/data/` - 5 files (empire.py, galaxy.py, naming.py, pathfinding.py, physics.py, stars.py)
- `game/ui/screens/builder/` - 6 files
- `game/core/` - 2 files (constants.py, hex_math.py)

**Expected:** All Python modules should have a module docstring explaining their purpose.
**Impact:** Module docstrings help IDE tooltips, documentation generators, and developer navigation. The abilities/ subdirectory is notably inconsistent: its `__init__.py` has a docstring but most implementation files do not.
**Recommendation:** Add one-line module docstrings to all 35 files. Can be done mechanically.
**Effort:** Simple

#### Minor: Inconsistent Relative vs Absolute Imports
**ID:** CE-012
**Location:** 20 files use both relative and absolute imports; 42 files total use relative imports
**Issue:** The codebase is 93% absolute imports (1,663 occurrences in 358 files) but has pockets of relative imports (119 occurrences in 42 files). 20 files mix both styles. Relative imports concentrate in:
- `game/simulation/components/abilities/` (most files use `from .base import Ability`)
- `game/ui/screens/test_lab/` (8 relative imports in screen.py)
- `game/simulation/entities/ship.py` (8 relative imports)
- `game/ui/screens/builder/` (several files)

**Expected:** Consistent absolute imports throughout (the dominant pattern). Relative imports only in `__init__.py` files.
**Impact:** Mixed import styles in the same file are confusing and can mask import order issues. Relative imports break when files are moved.
**Recommendation:** Convert all relative imports in non-`__init__.py` files to absolute imports. This affects ~70 import statements across 26 regular files.
**Effort:** Simple (mechanical find-and-replace per package)

#### Minor: Files With 4+ Classes Lacking Decomposition
**ID:** CE-013
**Location:** Various (22 files with 4+ classes)
**Issue:** While some multi-class files are appropriate (e.g., closely related dataclasses, enum + related types), several files contain too many unrelated or large classes:
- `game/strategy/engine/commands.py`: 29 classes (505 lines) - all command dataclasses
- `game/core/protocols.py`: 23 classes (987 lines) - all protocols, should be split by domain
- `game/strategy/engine/command_handlers.py`: 19 classes (1,032 lines) - should be split
- `game/ai/behaviors.py`: 12 classes (523 lines) - all behavior subclasses
- `game/strategy/engine/superweapon_command_handlers.py`: 11 classes

**Expected:** Files with 4+ substantive classes should be evaluated for decomposition. Small data classes (dataclasses, enums) can reasonably coexist. Large handler/behavior classes should be split.
**Impact:** Large multi-class files are hard to navigate and tend to accumulate more classes over time.
**Recommendation:** Split `command_handlers.py` (1,032 lines, 19 classes) into domain-specific handler files. Split `core/protocols.py` (987 lines, 23 protocols) by domain. `commands.py` (all frozen dataclasses) and `behaviors.py` (all small subclasses) are acceptable as-is.
**Effort:** Medium

#### Minor: `ui_colors.py` in Simulation Layer
**ID:** CE-014
**Location:** `game/simulation/components/abilities/ui_colors.py` (22 constants)
**Issue:** A file named `ui_colors.py` exists in the simulation layer. While the file contains only pure data (RGB color tuples as hex strings), its name and purpose (`"Color constants for ability UI display hints"`) tie it conceptually to the UI layer.
**Expected:** Simulation layer files should not have UI-specific naming or purpose. The data might be acceptable in the simulation layer if it's considered part of the ability metadata, but the naming creates confusion.
**Impact:** The name suggests a layer violation even though the file contains no UI framework imports. May lead developers to look in the wrong layer for UI color definitions.
**Recommendation:** Either move to `game/ui/` or rename to `ability_display_hints.py` to clarify it's ability metadata rather than UI code.
**Effort:** Simple

#### Minor: Singleton Pattern Still Used in 12 Files
**ID:** CE-015
**Location:** Various (12 files with `_instance` patterns)
**Issue:** The project's CLAUDE.md specifically says "Dependency injection over singletons." However, 12 files still use singleton-like patterns with `_instance` class variables or the `Singleton` metaclass from `game/core/singleton.py`.
**Expected:** Prefer dependency injection for all shared state.
**Impact:** Singletons make testing harder and create hidden global state. Some of these (like `RegistryManager`) may be intentional central registries, but others could benefit from DI.
**Recommendation:** Audit each singleton usage. `RegistryManager` and `AssetManager` are likely intentional infrastructure singletons. Others should be evaluated for conversion to DI.
**Effort:** Medium

#### Minor: `game/exit_dialog.py` is a Top-Level File
**ID:** CE-016
**Location:** `game/exit_dialog.py` (101 lines, uses pygame directly)
**Issue:** This file sits at the top level of `game/` but contains pygame rendering code (Surface, draw.rect). It logically belongs in the UI layer.
**Expected:** All pygame-dependent rendering code should be under `game/ui/`.
**Impact:** Breaks layer separation. Makes it unclear where UI components live.
**Recommendation:** Move to `game/ui/exit_dialog.py` or `game/ui/screens/exit_dialog.py`.
**Effort:** Simple

#### Minor: `game/assets/asset_manager.py` Uses Pygame, Should Be in UI
**ID:** CE-017
**Location:** `game/assets/asset_manager.py` (288 lines, imports pygame directly)
**Issue:** The asset manager loads images using `pygame.image.load()` and handles `pygame.error`. It is a pygame-dependent module sitting outside the UI layer.
**Expected:** Pygame-dependent code belongs in the UI layer. `game/ui/assets/` already exists (contains `ship_theme_manager.py`).
**Impact:** Creates a dependency path from a top-level package to pygame that bypasses the UI layer boundary.
**Recommendation:** Move `game/assets/asset_manager.py` to `game/ui/assets/asset_manager.py`.
**Effort:** Simple

#### Minor: Tkinter Usage in 10 UI Files
**ID:** CE-018
**Location:** 10 files in `game/ui/` import tkinter
**Issue:** The UI layer uses both pygame and tkinter. Tkinter is used for file dialogs (ship I/O, screenshots, presets) and some setup screens.
**Expected:** A single UI framework dependency (pygame). Tkinter usage creates a secondary framework dependency.
**Impact:** Two UI frameworks increase complexity. Tkinter dialogs may look inconsistent with the pygame-rendered game. However, pygame lacks native file dialog support, making tkinter a pragmatic choice.
**Recommendation:** This is an acknowledged pragmatic choice. Consider documenting tkinter as an approved secondary dependency for file dialogs. Long-term, evaluate pygame-gui file dialog widgets as replacements.
**Effort:** Complex (if migrating away from tkinter)

---

### Info Observations

#### Info: Well-Organized Subpackage Pattern in Simulation and Strategy
**ID:** CE-019
**Location:** `game/simulation/`, `game/strategy/`
**Issue (positive):** These layers have clean subpackage organization:
- simulation: combat/, components/, entities/, interfaces/, managers/, services/, systems/, validation/
- strategy: adapters/, data/, engine/, events/, facade/, formulas/, generation/, interfaces/, services/, systems/, validation/

This provides a template for organizing the less-structured UI layer.
**Impact:** Positive pattern to replicate.

#### Info: Dataclass Usage Concentrated in Strategy Commands
**ID:** CE-020
**Location:** `game/strategy/engine/commands.py` (28 dataclasses), various (113 total)
**Issue (observation):** Dataclass usage is appropriate and concentrated where it should be (DTOs, command objects, value objects). The `commands.py` file has 28 frozen dataclasses representing the command pattern -- this is a valid use of many classes in one file since they are all small, related data containers.

#### Info: Good TYPE_CHECKING Adoption
**ID:** CE-021
**Location:** 176 files (46% of codebase)
**Issue (positive):** TYPE_CHECKING is widely and correctly used to avoid circular imports and runtime overhead. This is a mature pattern indicating good awareness of import cycle management.

---

## Top 5 Priority Issues

Ranked by impact and fixability:

### 1. CE-001 (Critical): Duplicate Interface Names (`ICombatShip`, `IProjectile`)
**Why first:** Name collisions in interface definitions can cause real bugs. Fixing is surgical and high-value. Two distinct types sharing a name is an active source of confusion.
**Fix approach:** Rename the less-used variant or consolidate.
**Effort:** Medium

### 2. CE-003 (Major): `game/ui/screens/` Flat Directory (77 files)
**Why second:** The 77-file flat directory is the single biggest navigability issue. The `strategy_*` prefix group alone (19 files, 7K lines) is larger than many complete packages. The project already has a subpackage pattern established.
**Fix approach:** Create `game/ui/screens/strategy/` subpackage first (highest file count). Consider `build_queue/`, `fleet/`, `workshop/` next.
**Effort:** Complex but high payoff

### 3. CE-002 (Critical): Mixed ABC vs Protocol
**Why third:** Inconsistent interface mechanisms create architectural confusion. Protocol is the modern standard and already dominant (41 vs 13).
**Fix approach:** Migrate 13 ABC-based interfaces in strategy/interfaces and ai/interfaces to Protocol.
**Effort:** Medium

### 4. CE-004 (Major): Pygame Imports Outside UI Layer
**Why fourth:** Documented layer violation with concrete files to move. Two files (`exit_dialog.py`, `assets/asset_manager.py`) are simple relocations.
**Fix approach:** Move files, update imports.
**Effort:** Simple to Medium

### 5. CE-008 (Major): Empty `__init__.py` in Large Packages
**Why fifth:** The 36-file `game/strategy/data/` with no re-exports is a discoverability problem. Adding `__all__` and key re-exports is low-risk, high-value.
**Fix approach:** Add re-exports for most commonly used types.
**Effort:** Simple

---

## Appendix: Full File Size Distribution

| Range | Count | Percentage |
|-------|-------|------------|
| 0-100 lines | ~80 | 21% |
| 101-300 lines | ~170 | 45% |
| 301-500 lines | 76 | 20% |
| 501-800 lines | 35 | 9% |
| 801+ lines | 19 | 5% |

## Appendix: Top-Level Directory File Counts

| Directory | Python Files | Documented Layer |
|-----------|-------------|-----------------|
| game/ui/ | 197 | Yes |
| game/strategy/ | 113 | Yes |
| game/simulation/ | 73 | Yes |
| game/core/ | 21 | Yes |
| game/ai/ | 10 | Yes |
| game/research/ | 7 | No |
| game/engine/ | 4 | No |
| game/assets/ | 1 | No |
| game/ (top-level) | 2 | N/A |
| game/data/ | 0 (JSON only) | No |
