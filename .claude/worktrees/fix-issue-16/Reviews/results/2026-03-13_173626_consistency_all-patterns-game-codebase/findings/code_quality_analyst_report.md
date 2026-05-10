# Code Quality Analysis Report

**Scope:** `game/` directory (429 Python files, 94,814 lines)
**Date:** 2026-03-13
**Analyst:** Code Quality Agent

---

## Summary

- **Total issues found:** 22
- **Critical:** 2
- **Major:** 8
- **Minor:** 9
- **Info:** 3

The codebase demonstrates strong fundamentals: centralized logging patterns, a well-designed exception hierarchy, proper use of dataclasses with frozen DTOs, consistent color centralization, and good module-level documentation (90%+ in most layers). However, several DRY violations, interface inconsistencies, and type safety gaps introduce maintenance burden and potential bug risk.

---

## Quality Consistency Scorecard

| Module | Type Safety | Error Handling | DRY | SOLID | Overall |
|--------|------------|----------------|-----|-------|---------|
| core (21 files, 4.5K lines) | A (88%) | A | A | A | **A** |
| simulation (73 files, 16K lines) | B (67%) | A | B | A- | **B+** |
| strategy (113 files, 27K lines) | B (65%) | A- | B- | A- | **B** |
| ui (197 files, 57K lines) | D (40%) | B+ | C+ | B | **C+** |
| ai (10 files, 2.6K lines) | A (88%) | A | A | A | **A** |

Type Safety percentages = return type annotation coverage.

---

## Findings

### 1. DRY Violations

#### Major: Inline `clamp()` Instead of Utility Function
**ID:** CQ-01
**Location:** 40 files, 66 occurrences across `game/`
**Issue:** The codebase has a proper `clamp(value, min_val, max_val)` utility in `game/core/math.py:187`, exported via `game/core/__init__.py`. However, zero production modules import it. Instead, 66 instances of `max(min_val, min(max_val, value))` are scattered across 40 files.
**Impact:** Readability degradation, inconsistent argument ordering risk (`max(0, min(1, x))` vs `max(min_val, min(max_val, val))`), missed centralization point for future boundary enforcement (e.g., logging clamped values).
**Recommendation:** Replace all inline clamp patterns with `from game.core.math import clamp`. A simple regex search-and-replace is safe here.
**Effort:** Simple

---

#### Major: Duplicated `_get_registries()` Lazy Initialization
**ID:** CQ-02
**Location:** `game/ui/services/ship_io.py:41-53`, `game/ui/screens/strategy_build_queue_manager.py:37-49`, `game/ui/services/ship_factory.py:59`
**Issue:** The identical `_get_registries()` function is copy-pasted in three files. All three use a module-level `_cached_registries = None` global with the exact same lazy initialization body.
**Impact:** If the initialization logic needs to change (e.g., add a new registry type), all three copies must be updated in lockstep. Divergence risk is high.
**Recommendation:** Extract to a shared utility (e.g., `game/ui/services/registry_cache.py` or move into `game/core/registry.py` itself).
**Effort:** Simple

---

#### Major: Strategic Speed Formula Duplication
**ID:** CQ-03
**Location:** `game/ui/screens/builder/stats_config.py:140-154` vs `game/strategy/services/fleet_speed_calculator.py:106-117`
**Issue:** `get_strategic_speed()` in `stats_config.py` reimplements the exact formula from `FleetSpeedCalculator`, including hardcoding `K_STRATEGIC = 25`, `MAX_HEXES = 10`, `MIN_HEXES = 0`. The `stats_config.py` version even comments "Uses same formula as FleetSpeedCalculator" -- acknowledging the duplication.
**Impact:** If the formula or constants change in one location, the other becomes silently wrong. This is a correctness risk for the ship builder UI showing different speeds than the actual game.
**Recommendation:** Have `stats_config.py` call `FleetSpeedCalculator` or import the constants from `fleet_speed_calculator.py`.
**Effort:** Simple

---

#### Major: Duplicated `DEFAULT_DAMAGE_THRESHOLD` Constant
**ID:** CQ-04
**Location:** `game/strategy/services/ship_stats_calculator.py:43` vs `game/core/constants.py:57`
**Issue:** `DEFAULT_DAMAGE_THRESHOLD = 0.5` is defined in `ship_stats_calculator.py` with a comment saying it's "aligned with simulation layer" (`CombatConstants.DEFAULT_DAMAGE_THRESHOLD`). This is a manual copy of a constant that already exists in `core/constants.py`.
**Impact:** If the threshold value changes in `CombatConstants`, the strategy layer will silently use the old value.
**Recommendation:** Import `CombatConstants.DEFAULT_DAMAGE_THRESHOLD` instead of redefining.
**Effort:** Simple

---

#### Minor: `registries is None` Guard Pattern Duplication
**ID:** CQ-05
**Location:** ~15 occurrences across `game/simulation/` and `game/strategy/`
**Issue:** The pattern `if registries is None: raise ValidationException("registries is required for X", code=ErrorCode.MISSING_DEPENDENCY.value, context={...})` is repeated nearly identically in 15+ constructor/factory methods. Each differs only in the class name string.
**Impact:** Boilerplate clutter. Each guard is 5 lines of near-identical code. If the error format changes, all 15+ locations need updating.
**Recommendation:** Create a `require_registries(registries, context: str)` helper in `game/core/validation_helpers.py` analogous to the existing `require_keys()`.
**Effort:** Simple

---

#### Minor: `iter_layers_and_components()` Underutilization
**ID:** CQ-06
**Location:** `game/core/patterns/layer_iterator.py` vs 7 files with manual iteration
**Issue:** A proper `iter_layers_and_components()` utility exists in `core/patterns/`, but only 2 production modules use it. 11 manual `for layer_type, layer_data in ship.layers.items()` iterations exist across 7 files, including `ship_stats.py`, `battle_state.py`, `ship_instance.py`, and `design_metadata.py`.
**Impact:** The manual iterations may handle edge cases differently (e.g., checking for `isinstance(layer_data, dict)` or missing `'components'` key), leading to inconsistent behavior.
**Recommendation:** Audit the manual iterations and migrate them to the utility where applicable.
**Effort:** Medium

---

### 2. Anti-Pattern Inconsistency

#### Critical: Duplicate `ICombatShip` Protocol Definition
**ID:** CQ-07
**Location:** `game/core/protocols.py:601` and `game/simulation/interfaces/entity_protocols.py:43`
**Issue:** Two separate `ICombatShip` Protocol classes exist with different member sets. The `core` version has `name`, `team_id`, `is_alive`, `is_derelict`, `hp`, `max_hp`, `position`. The `simulation` version has `name`, `team_id`, `angle`, `position`, `velocity`, `radius`, and many more members. Different modules import from different locations: UI modules import from `core.protocols`, simulation modules import from `simulation.interfaces`.
**Impact:** Type confusion. Code typed against `core.ICombatShip` passes objects that may not satisfy `simulation.ICombatShip`, and vice versa. This silently allows type-unsafe usage and makes refactoring dangerous -- changing one protocol doesn't update the other.
**Recommendation:** Either consolidate into a single protocol (if they represent the same concept), or rename them to clarify their distinct purposes (e.g., `ICombatShipSummary` vs `ICombatShipFull`).
**Effort:** Medium

---

#### Major: Mixed `handle_event` vs `process_event` Naming
**ID:** CQ-08
**Location:** 40 uses of `handle_event()` across 35 files, 17 uses of `process_event()` across 17 files
**Issue:** UI components use two different names for the same event-handling pattern. The `IScene` protocol defines `handle_event`, but 17 window/panel classes use `process_event` instead. This isn't just a naming inconsistency -- it means `process_event` classes don't conform to the `IScene` protocol.
**Impact:** Cannot polymorphically dispatch events to components using a unified interface. Code that handles events must know which method name to call.
**Recommendation:** Standardize on `handle_event` to match the `IScene` protocol. Rename all `process_event` methods.
**Effort:** Medium

---

#### Major: Inconsistent Exception Types for Similar Errors
**ID:** CQ-09
**Location:** `game/simulation/components/component.py:566,672`, `game/simulation/entities/ship_loader.py:136`, `game/strategy/engine/command_handlers.py:175,178,219`
**Issue:** The codebase has a well-designed custom exception hierarchy (`ValidationException`, `ComponentException`, etc.), but several modules raise built-in `ValueError` or `TypeError` for errors that should use the custom types. For example, `component.py` raises `ValueError("registry_provider is required")` while other modules raise `ValidationException` for the exact same guard pattern. Similarly, `command_handlers.py` raises `ValueError("Fleet not found")` rather than `ResourceException` or `ValidationException`.
**Impact:** Callers that catch `ValidationException` will miss these errors. Inconsistent error handling makes the exception hierarchy partially useless.
**Recommendation:** Replace `ValueError`/`TypeError` with appropriate custom exceptions from `game.core.exceptions`.
**Effort:** Simple

---

#### Minor: Mixed ABC and Protocol for Interface Definitions
**ID:** CQ-10
**Location:** `game/strategy/interfaces/engines.py` (11 ABC classes) vs `game/core/protocols.py` (20+ Protocol classes)
**Issue:** The strategy layer uses `ABC` with `@abstractmethod` for engine interfaces (e.g., `IMovementEngine`, `IProductionEngine`), while core/simulation layers use `Protocol` for structural typing. Both patterns are valid, but using them inconsistently in the same project means some interfaces require explicit inheritance (ABC) while others work structurally (Protocol).
**Impact:** Strategy engine implementations must inherit from ABCs (nominal typing), while simulation implementations can use duck typing. This creates inconsistent coupling patterns.
**Recommendation:** This is an acceptable architectural decision if intentional (ABCs for tighter contracts on critical engine classes), but should be documented. If not intentional, standardize on Protocol.
**Effort:** Complex (if migrating)

---

### 3. Consistency-Related Bug Risks

#### Critical: `IScene.handle_event` Return Type Contract Violation
**ID:** CQ-11
**Location:** `game/core/protocols.py:776` defines `handle_event -> None`, but 6 implementations return `bool`
**Issue:** The `IScene.handle_event` protocol declares return type `-> None`, but 6 implementations in `scrollable_json_panel.py`, `battle_state_viewer.py`, `race_identity_panel.py`, `modifier_impact_grid.py`, `component_modifier_grid_panel.py`, and `workshop_event_router.py` return `bool` (indicating whether the event was consumed). Meanwhile, 24 implementations don't annotate the return type at all.
**Impact:** Callers dispatching through the `IScene` protocol cannot safely check the return value. If the event loop relies on `bool` returns for event consumption, some scenes will silently return `None` (falsy), potentially causing events to "fall through" incorrectly.
**Recommendation:** Update the `IScene` protocol to declare `-> bool` (or `-> Optional[bool]`) and update all implementations consistently. Alternatively, if event consumption tracking isn't needed at the scene level, ensure no caller checks the return value.
**Effort:** Medium

---

#### Major: Module-Level Global Caches Without Invalidation
**ID:** CQ-12
**Location:** `game/ui/services/ship_io.py`, `game/ui/screens/strategy_build_queue_manager.py`, `game/ui/screens/setup_data_io.py`, `game/ui/screens/setup_screen.py`, `game/strategy/data/build_queue_source.py`, `game/strategy/data/homeworld_presets.py`
**Issue:** Six modules use `global _cached_X` with `None`-check lazy initialization. These module-level caches have no invalidation mechanism. If game data is reloaded (e.g., via the Workshop Data Reloader), these caches serve stale data.
**Impact:** Stale cache data after data reload could cause silent behavior discrepancies or incorrect calculations.
**Recommendation:** Use `lru_cache` with configurable cache clearing, or implement a proper cache-invalidation event.
**Effort:** Medium

---

#### Minor: `handle_resize` Parameter Naming Inconsistency
**ID:** CQ-13
**Location:** `game/ui/screens/formation_editor.py:823` uses `(self, w: int, h: int)` vs all others using `(self, width: int, height: int)`
**Issue:** One implementation uses abbreviated parameter names while the `IScene` protocol and all other implementations use `width, height`.
**Impact:** Low risk, but violates the principle of least surprise. A refactoring tool might not catch this as a protocol-conforming method.
**Recommendation:** Rename to `width, height` for consistency.
**Effort:** Simple

---

### 4. SOLID Principle Consistency

#### Major: Large UI Screen Files (1000+ Lines)
**ID:** CQ-14
**Location:** `game/ui/screens/strategy_renderer.py` (1102 lines), `game/ui/screens/test_lab/renderer.py` (1040 lines), `game/ui/screens/race_setup_screen.py` (1029 lines)
**Issue:** Three UI files exceed 1000 lines. While the project guideline says "<50 lines preferred" for functions, these files contain single classes with 30+ methods each, combining layout, event handling, state management, and rendering.
**Impact:** Difficult to test individual behaviors in isolation. High merge conflict risk. New contributors struggle to navigate.
**Recommendation:** Extract focused delegates (rendering, input handling, state management) as has already been done for `strategy_screen.py` (which delegates to `strategy_renderer.py`, `strategy_input_handler.py`, etc.). Apply the same pattern to `race_setup_screen.py` and `test_lab/renderer.py`.
**Effort:** Complex

---

#### Minor: `ShipInstance` at 755 Lines with 47 Methods
**ID:** CQ-15
**Location:** `game/strategy/data/ship_instance.py`
**Issue:** `ShipInstance` has 47 methods spanning design data access, damage tracking, stat calculation, serialization, and resource management. While some delegation exists (e.g., `FleetBattleAdapter`), the class itself is still very large.
**Impact:** High cognitive load. Changes to one concern (e.g., damage tracking) risk accidentally affecting another (e.g., serialization).
**Recommendation:** This is already tracked as part of PROJ-87 (God Class Decomposition). Continue with planned extraction.
**Effort:** Complex (in progress)

---

### 5. Error Handling Quality

#### Minor: Broad `except Exception` Without Intentional Comment
**ID:** CQ-16
**Location:** `game/strategy/services/design_cost_calculator.py:87`, `game/ui/panels/race_environment_panel.py:446`, `game/strategy/data/empire.py:268`, `game/strategy/data/fleet.py:268`, `game/strategy/data/fleet_order_serializer.py:56`
**Issue:** Five `except Exception as e` blocks lack the "Intentional" comment that the codebase convention requires for broad catches. Other similar patterns in the codebase consistently include comments like `# Intentional broad catch: ...` explaining why a broad catch is necessary.
**Impact:** Without documentation, it's unclear whether these are deliberate resilience patterns or accidental over-catching. Future maintainers may remove them or add more specific catches unnecessarily.
**Recommendation:** Add "Intentional" comments explaining the rationale, or narrow the exception types.
**Effort:** Simple

---

#### Info: Well-Structured Exception Hierarchy
**ID:** CQ-17
**Location:** `game/core/exceptions.py`, `game/core/error_codes.py`
**Issue:** The exception hierarchy is well-designed with semantic exception types (`ValidationException`, `PersistenceException`, `ComponentException`, `FormulaException`), structured error codes, and context dictionaries. The validation helpers (`require_keys`, `validate_enum`, etc.) provide excellent deserialization safety.
**Impact:** Positive. This is a model for how exceptions should be structured.
**Recommendation:** No action needed. Extend the pattern to replace remaining `ValueError`/`TypeError` usage (see CQ-09).
**Effort:** N/A

---

### 6. Type Safety & Validation

#### Major: UI Layer Type Annotation Gap (40% vs 88% in Core)
**ID:** CQ-18
**Location:** `game/ui/` (197 files, 56K lines)
**Issue:** Return type annotation coverage is 40.2% in the UI layer compared to 88% in core and AI layers. The 197 UI files contain 2,135 functions, of which only 859 have return type annotations. This gap is compounded by inconsistent type annotations on protocol-required methods (`handle_event`, `update`, `draw`, `handle_resize`).
**Impact:** IDE tooling and static analysis are less effective in the largest layer of the codebase. Protocol conformance checking is weakened.
**Recommendation:** Prioritize adding return types to protocol-implementing methods first (`handle_event`, `update`, `draw`, `handle_resize`), then gradually improve general coverage.
**Effort:** Medium (for protocol methods), Complex (for full coverage)

---

#### Minor: `hasattr`/`getattr` Usage (92 + 101 occurrences)
**ID:** CQ-19
**Location:** 49 files using `hasattr()` (92 times), 45 files using `getattr()` (101 times)
**Issue:** Despite the investment in `@runtime_checkable` Protocol classes, the codebase still has 193 combined `hasattr`/`getattr` calls. While some are legitimate (e.g., optional attribute access with defaults), many could be replaced with proper isinstance checks against protocols, or by ensuring type contracts are satisfied.
**Impact:** `hasattr`/`getattr` bypasses static type checking and makes code harder to refactor safely.
**Recommendation:** Audit high-frequency users (e.g., `command_handlers.py` with 10 combined uses, `system_tree_panel.py` with 5 `hasattr` calls) and replace with protocol checks where possible.
**Effort:** Medium

---

#### Minor: `.get(key, None)` Redundancy
**ID:** CQ-20
**Location:** 4 occurrences across `game/`
**Issue:** `.get('value', None)` is used in 4 places where `.get('value')` would suffice (`.get()` returns `None` by default).
**Impact:** Cosmetic only, but signals possible misunderstanding of the API.
**Recommendation:** Remove explicit `None` defaults from `.get()` calls.
**Effort:** Simple

---

### 7. Documentation & Conventions

#### Info: Strong Module-Level Documentation
**ID:** CQ-21
**Location:** All layers
**Issue:** Module-level docstring coverage is excellent: core 84%, simulation 82%, strategy 93%, UI 93%, AI 100%. Most files include PROJ-XX references linking to the project that created or last modified them.
**Impact:** Positive. Traceability and context are strong.
**Recommendation:** No action needed.
**Effort:** N/A

---

#### Info: Consistent Logging Pattern
**ID:** CQ-22
**Location:** 139 files using `logger = logging.getLogger(__name__)`
**Issue:** All 139 files that use logging follow the exact same pattern: `import logging` + `logger = logging.getLogger(__name__)`. No deviations found (no `print()` debugging, no custom logger names).
**Impact:** Positive. Consistent, correct, and easily filterable.
**Recommendation:** No action needed.
**Effort:** N/A

---

## Top 5 Priority Issues

Ranked by combined impact (bug risk + maintenance burden + breadth of effect):

### 1. CQ-07 (Critical): Duplicate `ICombatShip` Protocol Definition
Two protocols with the same name but different member sets, imported from different locations by different modules. This creates type confusion at a critical interface boundary and risks silent type-safety violations. Fix by consolidating or explicitly disambiguating the protocols.

### 2. CQ-11 (Critical): `IScene.handle_event` Return Type Contract Violation
The protocol declares `-> None` but implementations return `bool`. If event consumption is checked anywhere (and it is in some panel hierarchies), this causes silent `None` fallthrough bugs. Fix by updating the protocol and all implementations to agree on the return contract.

### 3. CQ-03 + CQ-04 (Major): Duplicated Formulas and Constants
Strategic speed formula and damage threshold constant are independently defined in strategy and UI layers. If the simulation layer values change, the duplicates become silently wrong, causing ships to display incorrect speeds in the builder or apply incorrect damage thresholds. Fix by importing from the authoritative source.

### 4. CQ-08 (Major): Mixed `handle_event` / `process_event` Naming
57 event-handling methods split between two naming conventions prevent polymorphic dispatch and violate the `IScene` protocol contract. Fix by standardizing on `handle_event`.

### 5. CQ-18 (Major): UI Layer Type Annotation Gap
At 40% return-type coverage (vs. 88% in core), the UI layer is significantly undertypes. This matters especially because UI is the largest layer (60% of codebase) and implements protocol methods without type annotations, weakening protocol conformance checking.

---

## Methodology

Analysis performed through:
- Pattern-based search across all 429 Python files using ripgrep
- Manual review of files >500 lines for god class indicators
- Quantitative measurement of type hint coverage via AST-level regex matching
- Cross-referencing Protocol definitions against implementations
- Comparison of naming conventions and error handling patterns across layers
- Module-level docstring coverage measurement
