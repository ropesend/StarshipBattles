# PROJ-125: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Review
- **Review:** [2026-02-13_sweep_full-codebase-sweep](../../Reviews/results/2026-02-13_sweep_full-codebase-sweep/)
- **Type:** Review
- **Date:** 2026-02-13
- **Report:** [View Full Report](../../Reviews/results/2026-02-13_sweep_full-codebase-sweep/report.md)

## Initial Analysis
Findings from review - 273 total findings identified.
- **Critical:** 0
- **Major:** 20
- **Selected for remediation:** 78

## Selected Findings Summary

### CON-FND-004: Inconsistent Method Naming for Position/
- **Severity:** Major
- **Location:** `game/ai/interfaces/controllabl`
- **Effort:** Complex

### CON-FND-005: Class Naming Suffix Inconsistency - Serv
- **Severity:** Major
- **Location:** `game/ai/strategy_manager.py`
- **Effort:** Simple

### CON-UI2-003: Mixed Return Type Patterns for Error Han
- **Severity:** Major
- **Location:** `game/ui/services/ship_io.py:42`
- **Effort:** Medium

### CON-UI2-004: Inconsistent Parameter Naming for Regist
- **Severity:** Major
- **Location:** `Unknown`
- **Effort:** Simple

### CON-UI2-005: Missing Type Hints on Public Functions
- **Severity:** Major
- **Location:** `game/ui/renderer/game_renderer`
- **Effort:** Simple

### CON-UI2-006: Docstring Inconsistency - Some Use Googl
- **Severity:** Major
- **Location:** `game/ui/services/screenshot_ma`
- **Effort:** Simple

### CON-UI2-007: Inconsistent Module-Level vs Class-Level
- **Severity:** Major
- **Location:** `game/ui/colors.py:7-14`
- **Effort:** Simple

### SP-001: Inconsistent Constructor Parameter Order
- **Severity:** Major
- **Location:** `Unknown`
- **Effort:** Complex

### DUP-FND-001: Clamp Function Duplication
- **Severity:** Major
- **Location:** `game/core/math.py:187-203`
- **Effort:** Simple

### DUP-FND-002: Entity Position/State Access Patterns in
- **Severity:** Major
- **Location:** `game/ai/combat_utils.py:49-82`
- **Effort:** Medium

### DUP-FND-003: Singleton Pattern Documentation/Structur
- **Severity:** Major
- **Location:** `Unknown`
- **Effort:** Medium

### DUP-STR-001: Mission Command Handler Duplication
- **Severity:** Major
- **Location:** `game/strategy/engine/superweap`
- **Effort:** Simple

### DUP-STR-002: Direct vs Mission Command Validation Asy
- **Severity:** Major
- **Location:** `game/strategy/engine/superweap`
- **Effort:** Medium

### DUP-STR-003: `to_dict` / `from_dict` Boilerplate Patt
- **Severity:** Major
- **Location:** `Unknown`
- **Effort:** Complex

### DUP-STR-004: Fleet Resolution Pattern in Command Hand
- **Severity:** Major
- **Location:** `Unknown`
- **Effort:** Simple

### DUP-STR-005: ColonizeValidator Colony Pod Iteration P
- **Severity:** Major
- **Location:** `game/strategy/validation/colon`
- **Effort:** Simple

### DUP-UI2-001: Duplicated Lazy DI Provider Resolution P
- **Severity:** Major
- **Location:** `game/ui/services/component_ser`
- **Effort:** Medium

### DUP-UI2-002: Directory Creation Pattern Duplicated in
- **Severity:** Major
- **Location:** `game/ui/services/ship_io.py:49`
- **Effort:** Simple

### DUP-UI2-003: Singleton Manager Pattern Triplicated
- **Severity:** Major
- **Location:** `game/ui/assets/ship_theme_mana`
- **Effort:** Medium

### DUP-UI2-004: Service Adapter Wrapping Pattern
- **Severity:** Major
- **Location:** `game/ui/services/ship_io_adapt`
- **Effort:** Medium

### CON-FND-006: Inconsistent Parameter Naming - entity v
- **Severity:** Minor
- **Location:** `game/ai/combat_utils.py`
- **Effort:** Simple

### CON-FND-007: Inconsistent Docstring Format - Google S
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Simple

### CON-FND-008: Boolean Property Naming - is_alive() vs
- **Severity:** Minor
- **Location:** `game/ai/interfaces/controllabl`
- **Effort:** Simple

### CON-FND-009: Inconsistent Type Hint Coverage
- **Severity:** Minor
- **Location:** `game/core/logger.py:27-41`
- **Effort:** Simple

### CON-FND-010: Inconsistent Import Organization
- **Severity:** Minor
- **Location:** `game/ai/controller.py:51-66`
- **Effort:** Simple

### CON-FND-011: Magic Numbers in AI Layer
- **Severity:** Minor
- **Location:** `game/ai/controller.py:445`
- **Effort:** Simple

### CON-FND-012: Inconsistent Error Handling - Broad Exce
- **Severity:** Minor
- **Location:** `game/ai/controller.py:217-223`
- **Effort:** Simple

### CON-FND-013: Inconsistent `__all__` Export Patterns
- **Severity:** Minor
- **Location:** `game/core/constants.py:1-15`
- **Effort:** Simple

### CON-FND-014: Redundant Protocol Definition
- **Severity:** Minor
- **Location:** `game/core/validation.py:23-60`
- **Effort:** Simple

### CON-UI2-008: Inconsistent Boolean Method Naming
- **Severity:** Minor
- **Location:** `game/ui/services/component_ser`
- **Effort:** N

### CON-UI2-009: Redundant Exception Handling in ship_io.
- **Severity:** Minor
- **Location:** `game/ui/services/ship_io.py:71`
- **Effort:** Simple

### CON-UI2-010: Inconsistent Import Organization
- **Severity:** Minor
- **Location:** `game/ui/renderer/sprites.py:1-`
- **Effort:** Simple

### CON-UI2-011: Method Prefix Inconsistency - get_ vs lo
- **Severity:** Minor
- **Location:** `game/ui/assets/ship_theme_mana`
- **Effort:** Simple

### CON-UI2-012: Inconsistent Private Method Naming
- **Severity:** Minor
- **Location:** `game/ui/assets/ship_theme_mana`
- **Effort:** N

### CON-UI2-013: Magic Numbers in game_renderer.py
- **Severity:** Minor
- **Location:** `game/ui/renderer/game_renderer`
- **Effort:** Medium

### CON-UI2-014: Inconsistent Error Logging Format
- **Severity:** Minor
- **Location:** `game/ui/services/ship_io.py:72`
- **Effort:** Simple

### CON-UI2-015: Unused Comments as Section Headers
- **Severity:** Minor
- **Location:** `game/ui/renderer/game_renderer`
- **Effort:** Simple

### NC-001: Mixed Screen/Scene Terminology
- **Severity:** Minor
- **Location:** `game/ui/screens/menu_scene.py`
- **Effort:** Simple

### NC-002: Inconsistent Event Handler Prefixes
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Medium

### NC-003: Inconsistent Module Naming for Related C
- **Severity:** Minor
- **Location:** `game/ui/screens/`
- **Effort:** N

### SP-002: Inconsistent UI Manager Attribute Names
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Medium

### API-001: Mixed Callback Parameter Names
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** N

### API-002: Inconsistent Event Handler Return Types
- **Severity:** Minor
- **Location:** `BattlePanel.handle_click()`
- **Effort:** Medium

### PP-003: Inconsistent Type Hint Coverage
- **Severity:** Minor
- **Location:** `game/ui/screens/builder/compon`
- **Effort:** Medium

### PP-004: Missing Module Docstrings
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Simple

### PP-005: Inconsistent Future Annotations Usage
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Simple

### MOD-003: Inconsistent Panel Base Class Usage
- **Severity:** Minor
- **Location:** `game/ui/panels/`
- **Effort:** Simple

### MOD-004: Inconsistent Error Logging
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Simple

### DUP-FND-004: Entity ID Extraction Pattern Duplication
- **Severity:** Minor
- **Location:** `game/ai/combat_utils.py:65`
- **Effort:** Simple

### DUP-FND-005: Flee Direction Calculation
- **Severity:** Minor
- **Location:** `game/ai/behaviors.py:70-84`
- **Effort:** Simple

### DUP-FND-006: Tech Tree Validation Method Patterns
- **Severity:** Minor
- **Location:** `game/research/data/tech_tree.p`
- **Effort:** Simple

### DUP-FND-007: Serialization to_dict/from_dict Patterns
- **Severity:** Minor
- **Location:** `game/research/data/research_tr`
- **Effort:** Complex

### DUP-STR-006: Gaussian Factor Calculation Pattern
- **Severity:** Minor
- **Location:** `game/strategy/formulas/habitab`
- **Effort:** Simple

### DUP-STR-007: Path Start Hex Determination Logic
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Simple

### DUP-STR-008: Ship Ability Check Wrappers
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Simple

### DUP-STR-009: Resource Dictionary Accumulation Pattern
- **Severity:** Minor
- **Location:** `game/strategy/services/ship_st`
- **Effort:** Simple

### DUP-UI2-005: Font Creation Throughout UI Without Cent
- **Severity:** Minor
- **Location:** `game/ui/renderer/game_renderer`
- **Effort:** Simple

### DUP-UI2-006: Image Scaling Utility Functions Have Ove
- **Severity:** Minor
- **Location:** `game/ui/utils.py:32-64`
- **Effort:** Simple

### DUP-UI2-007: Placeholder Surface Creation Pattern
- **Severity:** Minor
- **Location:** `game/ui/utils.py:141-143`
- **Effort:** Simple

### DUP-UI2-008: Error Exception Handling Pattern in Ship
- **Severity:** Minor
- **Location:** `game/ui/services/ship_io.py:71`
- **Effort:** Simple

### DUP-UI2-009: Tkinter Initialization Error Handling
- **Severity:** Minor
- **Location:** `game/ui/services/ship_io.py:21`
- **Effort:** Medium

### DUP-UI2-010: Return Value Conventions Partially Docum
- **Severity:** Minor
- **Location:** `game/ui/services/ship_io_adapt`
- **Effort:** Simple

### CON-FND-015: os.path vs pathlib.Path Mixed Usage
- **Severity:** Info
- **Location:** `game/core/paths.py:53-103`
- **Effort:** Simple

### CON-FND-016: ResourceType is a Class, Not an Enum
- **Severity:** Info
- **Location:** `game/core/constants.py:83-92`
- **Effort:** Simple

### CON-FND-017: TechNode/TechTree Separate from Core Reg
- **Severity:** Info
- **Location:** `game/research/data/tech_tree.p`
- **Effort:** N

### CON-FND-018: Research Layer Has Direct pygame Import
- **Severity:** Info
- **Location:** `game/research/ui/research_scen`
- **Effort:** Complex

### CON-UI2-016: Cross-Layer Imports Documented But Incon
- **Severity:** Info
- **Location:** `game/ui/orchestration/battle_o`
- **Effort:** Simple

### CON-UI2-017: DTO Classes Could Use __slots__
- **Severity:** Info
- **Location:** `game/ui/interfaces/battle_ui.p`
- **Effort:** Simple

### CON-UI2-018: UIConfig Class Has No Methods
- **Severity:** Info
- **Location:** `game/ui/config.py:17-67`
- **Effort:** N

### SP-003: Two Initialization Naming Conventions
- **Severity:** Info
- **Location:** `Unknown`
- **Effort:** Simple

### API-003: Consistent Pattern
- **Severity:** Info
- **Location:** `Unknown`
- **Effort:** N

### PP-001: Good Pattern Adoption
- **Severity:** Info
- **Location:** `strategy_ui.py`
- **Effort:** N

### MOD-001: Well-Organized Module Structure
- **Severity:** Info
- **Location:** `game/ui/screens/builder/`
- **Effort:** N

### DUP-FND-008: Well-Consolidated Utilities
- **Severity:** Info
- **Location:** `game/core/`
- **Effort:** N

### DUP-STR-010: Validated Design Component Iteration
- **Severity:** Info
- **Location:** `Unknown`
- **Effort:** Medium

### DUP-STR-011: Well-Consolidated Component Inspector
- **Severity:** Info
- **Location:** `game/strategy/services/compone`
- **Effort:** N

### DUP-UI2-011: Camera Zoom Clamping Pattern
- **Severity:** Info
- **Location:** `game/ui/renderer/camera.py:114`
- **Effort:** Simple

### DUP-UI2-012: Vector2 Import and Usage Consistency
- **Severity:** Info
- **Location:** `game/ui/interfaces/battle_ui.p`
- **Effort:** Simple


## Architecture
[Key architecture points relevant to implementation - to be filled during planning]

## Key Patterns to Reuse
- **[Pattern Name]**: `file:lines` - description

## Dependencies & Risks
1. **[Risk/Dependency]** - mitigation approach

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
