# Documentation Gaps

**Theme:** Missing docstrings, broken references, outdated documentation, incomplete API docs, and undocumented complex logic.

---

## Critical Issues

### DOC-001: Broken Project References
**ID:** DOC-001
**Location:** `docs/ARCHITECTURE.md:151-152`
**Issue:** References to PROJ-11 project plan and design documents that have been deleted from the active_projects directory. The file path `../Projects/active_projects/PROJ-11/plan.md` no longer exists.
**Impact:** Developers attempting to review architecture decisions cannot access linked documentation. Broken links reduce documentation credibility.
**Recommendation:** Either restore PROJ-11 project files or remove these references and incorporate the essential information into ARCHITECTURE.md itself.
**Effort:** Medium

---

### DOC-002: Incomplete PROJ References
**ID:** DOC-002
**Location:** `docs/refactoring/REMAINING_ISSUES_PLAN.md:1-16`
**Issue:** Document references completed PROJ work but projects directory only contains PROJ-41. Multiple completed projects lack documentation artifacts.
**Impact:** No historical record of major refactoring work completed. Makes it difficult to understand why certain patterns exist in the codebase.
**Recommendation:** Archive completed project documentation or create project completion summaries in a dedicated "completed_projects" directory.
**Effort:** Medium

---

### DOC-01: EventBus - No Documentation
**ID:** DOC-01
**Location:** `game/ui/screens/builder/event_bus.py`
**Issue:** Complete lack of module and class documentation. 5 public methods with no docstrings.
**Impact:** Critical pub/sub pattern in builder UI with no explanation of event flow
**Recommendation:** Add module docstring explaining event pattern, document all methods
**Effort:** Simple

---

### DOC-02: InteractionController - Incomplete Documentation
**ID:** DOC-02
**Location:** `game/ui/screens/builder/interaction_controller.py`
**Issue:** Class lacks module-level docstring. 14 public/protected methods without docstrings. Complex drag-drop logic unexplained.
**Impact:** Critical interaction handler with unclear component lifecycle
**Recommendation:** Add module docstring with interaction pattern overview
**Effort:** Medium

---

### DOC-03: InputHandler - Minimal Documentation
**ID:** DOC-03
**Location:** `game/core/input_handler.py`
**Issue:** Methods lack documentation. Complex keybinding logic (7 methods) unexplained.
**Impact:** Core input handling with no explanation of speed modifier behavior
**Recommendation:** Document all methods, explain speed multiplier strategy
**Effort:** Simple

---

### DOC-04: WeaponAbility - Incomplete Initialization Documentation
**ID:** DOC-04
**Location:** `game/simulation/components/abilities/weapons.py`
**Issue:** Complex formula parsing logic (30+ lines) lacks documentation. No explanation of formula string format.
**Impact:** Core combat ability initialization unclear
**Recommendation:** Document formula string format, explain fallback chain
**Effort:** Medium

---

### DOC-05: Camera.update() - Missing Zoom Anchor Logic
**ID:** DOC-05
**Location:** `game/ui/renderer/camera.py:24-45`
**Issue:** Complex smooth zoom interpolation with no docstring. Zoom anchor mechanism unexplained.
**Impact:** Smooth camera behavior logic unclear for maintenance
**Recommendation:** Add docstring explaining zoom anchor preservation
**Effort:** Simple

---

### DOC-06: ModifierControlRow - No Class Documentation
**ID:** DOC-06
**Location:** `game/ui/screens/builder/modifier_row.py:6-36`
**Issue:** Complex UI widget class with no docstring. 10+ undocumented methods.
**Impact:** Complex modifier UI with unclear lifecycle
**Recommendation:** Add class docstring explaining pooling/layout pattern
**Effort:** Medium

---

### DOC-07: FleetMovementSimulator - Deprecated but Undocumented
**ID:** DOC-07
**Location:** `game/strategy/engine/fleet_movement.py:63-80`
**Issue:** Deprecation warning exists but migration guide incomplete
**Impact:** Developers may misuse deprecated class
**Recommendation:** Add comprehensive deprecation guide with migration steps
**Effort:** Medium

---

### DOC-08: ModifierLogic - Complex Logic, Minimal Documentation
**ID:** DOC-08
**Location:** `game/ui/screens/builder/modifier_logic.py:10-100`
**Issue:** Complex ability detection (100+ lines) lacks documentation
**Impact:** Critical modifier validation with unclear detection strategy
**Recommendation:** Add method docstrings, explain ability detection strategy
**Effort:** Medium

---

## Major Issues

### DOC-003: Outdated Test Migration Guide
**ID:** DOC-003
**Location:** `docs/test_migration_guide.md:1-50`
**Issue:** Document describes a "TestScenario pattern" and dual pytest/Combat Lab architecture, but the current state of the codebase shows test organization has evolved.
**Impact:** New developers following this guide may implement tests in a pattern no longer used by the project.
**Recommendation:** Audit actual test structure in `tests/`, `simulation_tests/`, and `test_framework/` directories. Either update the guide or mark it as "Legacy - For Reference Only".
**Effort:** Complex

---

### DOC-004: Incomplete Modifier System Documentation
**ID:** DOC-004
**Location:** `docs/modifier_system.md:113-124`
**Issue:** Documentation lists file locations for modifier system but API is documented without showing actual public method signatures. Methods may have changed since documentation was written.
**Impact:** Developers may use incorrect method names when integrating modifier introspection features.
**Recommendation:** Cross-reference source files to verify all documented methods exist with correct signatures.
**Effort:** Simple

---

### DOC-005: Architecture Diagram Misalignment
**ID:** DOC-005
**Location:** `docs/ARCHITECTURE.md:7-21`
**Issue:** Architecture diagram shows layer structure but doesn't reflect actual directory organization. `game/engine/` shown as part of "Core Layer" but reorganization docs suggest it should be separate.
**Impact:** Confusion about actual dependency boundaries and layer separation.
**Recommendation:** Clarify whether `game/engine/` is core infrastructure or separate. Update diagram to match actual structure.
**Effort:** Medium

---

### DOC-006: Naming Conventions Missing New Terms
**ID:** DOC-006
**Location:** `docs/NAMING_CONVENTIONS.md`
**Issue:** Document defines "Battle vs Combat" distinctions, but review of codebase shows additional terms not documented: `Scene` vs `Screen`. Document acknowledges "somewhat interchangeably" but doesn't establish clear rules.
**Impact:** New code may use `Scene` and `Screen` inconsistently.
**Recommendation:** Add section defining `Scene` vs `Screen` distinction with concrete examples.
**Effort:** Simple

---

### DOC-007: Deprecated Code References
**ID:** DOC-007
**Location:** `docs/refactoring/REMAINING_ISSUES_PLAN.md:97-109`
**Issue:** Documentation mentions deprecated code elements but these items don't appear to have been cleaned up.
**Impact:** Unclear what code is safe to use or refactor.
**Recommendation:** Either remove deprecated code or explicitly mark it with deprecation warnings in the source.
**Effort:** Medium

---

### DOC-09: BattleController - Incomplete Return Value Documentation
**ID:** DOC-09
**Location:** `game/simulation/battle_controller.py:90-170`
**Issue:** Methods return BattleResult but structure not documented
**Impact:** Result handling unclear
**Recommendation:** Document BattleResult structure in module docstring
**Effort:** Simple

---

### DOC-10: ModifierService - Confusing Dual-Pattern Documentation
**ID:** DOC-10
**Location:** `game/simulation/services/modifier_service.py:54-80`
**Issue:** Support for both static and instance calling patterns poorly documented
**Impact:** Developers may misuse service
**Recommendation:** Add clear usage examples for both patterns
**Effort:** Medium

---

### DOC-11: ShipCombatEngine.solve_lead() - Algorithm Undocumented
**ID:** DOC-11
**Location:** `game/simulation/entities/ship_combat_engine.py:47-94`
**Issue:** Quadratic formula for projectile interception lacks mathematical explanation
**Impact:** Complex physics algorithm unclear for maintenance
**Recommendation:** Add mathematical background in docstring
**Effort:** Medium

---

### DOC-12: Complex UI Methods Missing Docstrings
**ID:** DOC-12
**Location:** Multiple UI screen files
**Issue:** draw_debug_overlay(), _create_ui(), event handlers lack documentation
**Impact:** Debug visualization and UI logic unmaintainable
**Recommendation:** Add docstrings explaining each method's purpose
**Effort:** Medium

---

### CORE-001: Missing Return Type Hints on Logger Functions
**ID:** CORE-001
**Location:** `game/core/logger.py:67-80`
**Issue:** Functions `log_debug()`, `log_info()`, `log_warning()`, `log_error()`, and `set_logging()` lack return type hints (`-> None`). The Logger class methods similarly lack type hints.
**Impact:** Reduces type safety and IDE support. Makes code harder to understand and prone to misuse.
**Recommendation:** Add `-> None` return type hints to all logger functions. Add parameter type hints (`msg: str`, `enabled: bool`) and method return types to Logger class.
**Effort:** Simple

---

### CORE-002: Incomplete Type Hint Coverage in Core Registry
**ID:** CORE-002
**Location:** `game/core/registry.py:94-256`
**Issue:** RegistryManager methods like `set_validator()` lack parameter type hints. The `_validator` attribute is typed as `Any` without documentation on expected type.
**Impact:** Unclear what type of validator is expected. Makes debugging difficult when wrong types are passed.
**Recommendation:** Add type hint `validator: Optional[ShipDesignValidator]` to `set_validator()`. Document the expected validator interface in class docstring.
**Effort:** Simple

---

### CORE-005: Backward Compatibility Module-Level Exports Not Documented
**ID:** CORE-005
**Location:** `game/core/paths.py:89-98`
**Issue:** Module-level exports (`ROOT_DIR`, `DATA_DIR`, `ASSET_DIR`, etc.) re-export from Paths class for backward compatibility, but no comment explains why. Similarly, `game/core/constants.py:29-33` re-exports display config from DisplayConfig class without explanation.
**Impact:** New developers don't understand the migration pattern. Risk of accidental removal of backward-compat exports.
**Recommendation:** Add comments: `# Backward compatibility: prefer Paths.ROOT_DIR in new code` on line 89. Document the migration pattern in constants.py.
**Effort:** Simple

---

### CORE-011: PROJ-38 Deprecation Status Unclear
**ID:** CORE-011
**Location:** `game/core/registry.py:1-35`
**Issue:** PROJ-38 deprecation plan documented but no deadline, migration priority, or completion criteria. Utility functions have DeprecationWarning but code actively using them isn't flagged.
**Impact:** Unclear when deprecated functions can be removed. No sense of urgency for migration.
**Recommendation:** Add to registry.py docstring: "PROJ-38 Migration Timeline: Phase 1 (done) - Add DI. Phase 2 (TODO) - Migrate internal usage. Phase 3 (TODO) - Remove deprecated functions (v2.0)".
**Effort:** Simple

---

### SIM-019: Complex Battle Calculation Formulas Lack Comments
**ID:** SIM-019
**Location:** `game/simulation/entities/ship_combat_engine.py:47-94`, `game/simulation/entities/ship_physics.py:13-65`
**Issue:** Complex mathematical formulas have minimal comments explaining the math.
**Recommendation:** Add detailed comments explaining what problem each formula solves.
**Effort:** Simple

---

### SIM-026: Missing Documentation on Component System
**ID:** SIM-026
**Location:** `game/simulation/components/component.py:1-59`
**Issue:** Component lifecycle documented in docstring but not in separate documentation.
**Recommendation:** Create `docs/component_system.md` with architecture diagrams.
**Effort:** Simple

---

## Minor Issues

### DOC-008: Adding Abilities Guide - Missing Error Handling Section
**ID:** DOC-008
**Location:** `docs/adding_abilities.md:207-254`
**Issue:** The "Write Tests" section doesn't mention what exceptions an ability might raise.
**Recommendation:** Add section on exception handling in ability implementation.
**Effort:** Simple

---

### DOC-009: Missing Documentation for New UI Components
**ID:** DOC-009
**Location:** `docs/NAMING_CONVENTIONS.md:88-99`
**Issue:** Documentation doesn't mention modern UI components like `workshop_screen.py`, `workshop_context.py`, `workshop_viewmodel.py` representing MVVM patterns.
**Recommendation:** Add section documenting the Workshop/ViewModel pattern.
**Effort:** Medium

---

### DOC-010: Incomplete API Documentation
**ID:** DOC-010
**Location:** `docs/adding_abilities.md:156-163`
**Issue:** Documents `get_effective_stat()` method but doesn't explain the stat resolution order.
**Recommendation:** Add detailed example showing stat resolution with both global and targeted modifiers.
**Effort:** Simple

---

### DOC-011: Missing Layer Iteration Documentation
**ID:** DOC-011
**Location:** `docs/adding_abilities.md` (not present)
**Issue:** The ability system heavily uses component layer iteration, but there's no documentation on how to iterate layers correctly.
**Recommendation:** Add section on iterating component layers with examples.
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

## Documentation Coverage Summary

### Docstring Coverage by Area

| Level | Coverage | Notes |
|-------|----------|-------|
| Module docstrings | 92% | Excellent |
| Class docstrings | 68% | Acceptable |
| Method docstrings | 52% | Weak in UI builders |

### Documentation by Module

| Module | Has Docs | Quality | Gap |
|--------|----------|---------|-----|
| Core | Yes | Good | Missing type hints |
| Simulation | Yes | Moderate | Missing algorithm explanations |
| Strategy | Partial | Weak | Missing service documentation |
| UI/Screens | No | Poor | Widespread gaps |
| AI | Minimal | Poor | Targeting logic undocumented |

---

## Top Priority Issues

1. **DOC-01: EventBus - Complete Documentation Void** - No docs for critical pub/sub pattern
2. **DOC-04: WeaponAbility Formula Parsing** - Core combat with unclear formula handling
3. **DOC-09: BattleController Return Values** - Developers unsure what results contain
4. **DOC-02: InteractionController State Machine** - Complex drag-drop with no docs
5. **DOC-001/DOC-002: Broken Project References** - High visibility issue that damages documentation credibility
