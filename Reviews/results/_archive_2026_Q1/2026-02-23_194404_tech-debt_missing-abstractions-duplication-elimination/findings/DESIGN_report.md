# DESIGN Report: Cross-Cutting Design Principles for Abstraction Work

## Metadata
- **Date:** 2026-02-23
- **Type:** Design Principles Review
- **Scope:** All existing abstractions + recommendations for 11 proposed consolidation clusters
- **Prior Art:** `Reviews/results/2026-02-23_160413_general_duplication-consolidation-analysis/report.md`

## Summary
- **Total issues found:** 23
- **Critical:** 5 | **Major:** 10 | **Minor:** 6 | **Info:** 2

---

## 1. Existing Abstraction Audit

### 1.1 SingletonMeta (`game/core/singleton.py`)
- **Pattern:** Metaclass-based singleton with double-checked locking
- **Consumed as:** `class MyService(metaclass=SingletonMeta)` + `MyService.instance()` or `MyService()`
- **What makes it successful:**
  - Thread-safe with per-class locking
  - `reset()` for test isolation
  - Single module, no dependencies on other game code
  - Clean `__all__` export
- **What could be improved:**
  - Class-level `_instances` dict is a hidden global; tested code must remember to call `reset()`
  - No type parameter on `instance()` return (uses `TypeVar` but IDE inference is imperfect with metaclasses)

### 1.2 GameRegistries (`game/core/registry.py`)
- **Pattern:** Frozen dataclass container + singleton manager + DI providers
- **Consumed as:** `get_default_registries()` or `RegistryManager.instance()` or `TestRegistryProvider(...)`
- **What makes it successful:**
  - Three tiers of access (domain service > DI > direct singleton) with clear documentation
  - Frozen dataclass prevents reference swapping
  - `TestRegistryProvider` gives clean test isolation
  - Well-documented `__all__` exports
- **What could be improved:**
  - Module-level `_default_registries` global alongside `RegistryManager` singleton creates two parallel state mechanisms
  - `freeze()`/`_check_frozen()` logic is manually duplicated per method

### 1.3 EventBus (`game/ui/screens/builder/event_bus.py`)
- **Pattern:** Simple pub/sub with string event types
- **Consumed as:** Instance per screen, `bus.subscribe(event_type, callback)` / `bus.emit(event_type, data)`
- **What makes it successful:**
  - Minimal API (subscribe, unsubscribe, emit)
  - Defensive copy of handler list during emit
  - Error isolation (broad catch prevents one handler from crashing others)
  - Good docstrings
- **What could be improved:**
  - String event types are stringly-typed; companion `BuilderEvents` class defines constants but enforcement is not compile-time
  - No support for typed event data (all `data` is `Any`)

### 1.4 ValidationResult (`game/core/validation.py`)
- **Pattern:** Mutable dataclass DTO + Protocol for validators
- **Consumed as:** `from game.core.validation import ValidationResult` + `result.add_error(...)` / `result.merge(...)`
- **What makes it successful:**
  - Canonical cross-layer DTO (documented consolidation from 5 duplicates)
  - `IValidationRule` Protocol enables structural typing without forced inheritance
  - Builder-like API (`add_error`, `add_warning`, `merge`)
  - Proper `ErrorCode` integration
- **What could be improved:**
  - `message` property silently returns empty string when `is_valid=True` (could be confusing)
  - `__post_init__` is redundant given `field(default_factory=list)`

### 1.5 Builder Layout Constants (`game/ui/screens/builder_utils.py`)
- **Pattern:** Frozen dataclass + module-level singleton instances
- **Consumed as:** `from game.ui.screens.builder_utils import PANEL_WIDTHS, MARGINS`
- **What makes it successful:**
  - Frozen dataclass prevents accidental mutation
  - Pre-created module-level instances (no constructor boilerplate at use sites)
  - Related constants grouped by concern (widths, heights, margins, spacing)
  - Utility functions co-located with the constants they use
- **What could be improved:**
  - Two spacing classes (`Margins` and `BuilderSpacing`) overlap in purpose
  - File located under `screens/` but used by panels too; could be at `ui/` level

### 1.6 BaseGallery (`game/ui/panels/base_gallery.py`)
- **Pattern:** ABC with template method for asset galleries
- **Consumed as:** Subclass `BaseGallery`, implement abstract methods, use inherited gallery infrastructure
- **What makes it successful:**
  - 8 abstract methods define clear extension points
  - Shared infrastructure (button grid, scrolling, highlight) in base class
  - Optional callback injection (`on_select_callback`)
- **What could be improved:**
  - Constructor has 8 parameters (could use a config dataclass)
  - `_sanitize_object_id` is a utility that doesn't need instance state (already `@staticmethod`-worthy)

### 1.7 Ability Base Class (`game/simulation/components/abilities/base.py`)
- **Pattern:** Concrete base class with hook methods (template method + class attribute configuration)
- **Consumed as:** Subclass `Ability`, override class constants (`layer`, `STAT_BINDINGS`), override `__init__` calling `_parse_primary_value()`
- **What makes it successful:**
  - `_parse_primary_value()` as static method eliminates the most-duplicated pattern in the codebase
  - `STAT_BINDINGS` class-level list provides declarative modifier binding
  - Clear hook methods (`update`, `on_activation`, `recalculate`, `get_ui_rows`, `get_primary_value`)
  - `get_effective_stat()` with smart defaults based on key suffix
- **What could be improved:**
  - 16+ subclasses still duplicate the `recalculate()` pattern: `self.field = self._base_field * self.get_effective_stat('key', 1.0)`
  - `sync_data()` requires manual field re-parsing in every subclass
  - `get_ui_rows()` returns raw dicts instead of typed objects

### 1.8 Protocols (`game/core/protocols.py`)
- **Pattern:** `@runtime_checkable` Protocol classes + `TypeGuard` helper functions
- **Consumed as:** `from game.core.protocols import is_fleet, IFleet` + `if is_fleet(obj): ...`
- **What makes it successful:**
  - Structural typing (no forced inheritance)
  - TypeGuard functions enable type narrowing in IDE/mypy
  - Clean grouping by domain (base, strategy, combat, boundary)
  - Comprehensive docstrings with PROJ references
- **What could be improved:**
  - Some protocols overlap (e.g., `IPostBattleShip` and `IResourceHolder` share 4 of 5 properties)

### 1.9 BattleModeHandler (`game/simulation/combat/battle_mode_handler.py`)
- **Pattern:** ABC Strategy pattern with 4 concrete implementations
- **What makes it successful:**
  - Clean separation of mode-specific behavior
  - Small, focused abstract methods
  - Each subclass is under 40 lines

### 1.10 CommandHandlerRegistry (`game/strategy/engine/command_handlers.py`)
- **Pattern:** Protocol + registry + dispatch
- **What makes it successful:**
  - Extensible: new commands = new handler classes, register them
  - No switch/elif dispatch
  - Handlers implement `ICommandHandler` Protocol (structural typing)

---

## 2. Naming Convention Recommendations

### 2.1 Current Patterns Observed

| Category | Existing Pattern | Examples | Count |
|----------|-----------------|----------|-------|
| ABC base classes | `Base*` prefix | `BaseGallery` | 1 |
| ABC base classes | No prefix, just ABC | `BattleModeHandler(ABC)`, `ValidationRule(ABC)` | 3 |
| Protocols | `I*` prefix | `IFleet`, `ICommandHandler`, `IScene` | 28 |
| Mixins | `*Mixin` suffix | `ShipPhysicsMixin` | 1 |
| Utilities | `*_utils.py` module | `builder_utils.py`, `json_utils.py`, `combat_utils.py` | 5 |
| Factories | `*Factory` suffix | `AIControllerFactory`, `ShipFactory` | 2 |
| Services | `*Service` suffix | `BattleService`, `ModifierService` | 12 |
| Handlers | `*Handler` suffix | `CommandHandler`, `BattleModeHandler` | 15+ |
| Validators | `*Validator` suffix | `ColonizeValidator`, `SuperweaponValidator` | 5 |
| Processors | `*Processor` suffix | `FleetOrderProcessor`, `SuperweaponOrderProcessor` | 2 |
| Factory methods | `from_dict()` classmethod | `BattleState.from_dict()`, `Ship.from_dict()` | 15+ |
| Factory methods | `create_*()` function | `create_component()`, `create_ability()` | 10+ |
| DTOs | Frozen dataclass | `FleetDTO`, `SystemDTO` | 12+ |

### 2.2 Recommendations

---

#### MAJOR: Standardize ABC Naming to `Base*` Prefix
**ID:** DESIGN-001
**Issue:** The codebase uses two patterns for abstract base classes: `Base*` prefix (`BaseGallery`) and suffix-less names that happen to be ABCs (`BattleModeHandler(ABC)`, `ValidationRule(ABC)`). This creates confusion about whether a class is abstract or concrete.
**Impact:** New abstractions need a consistent naming convention. Without it, different developers will use different patterns, degrading readability.
**Recommendation:** For new abstractions being created in this consolidation effort, use the `Base*` prefix pattern consistently when the class is meant to be subclassed. This matches `BaseGallery` and is the most common Python convention. Do NOT retroactively rename existing ABCs like `BattleModeHandler` -- that would be churn.

Examples for the 11 clusters:
- `BaseAbilityWithValue` or `ValueAbility` (for the common _parse + recalculate pattern)
- `BaseSuperweaponProcessor` (for superweapon order processing)
- `BaseValidator` (for validator template method)
- `BaseRacePanel` (for race panel initialization)
- `BaseSingletonService` (for singleton service state management)

**Effort:** Simple (naming convention, no code changes to existing classes)

---

#### MINOR: Keep `I*` Prefix for Protocols
**ID:** DESIGN-002
**Issue:** The codebase consistently uses `I*` prefix for Protocol classes (28 instances). This is a strong existing convention.
**Impact:** Any new protocols should follow this pattern for consistency.
**Recommendation:** Continue using `I*` prefix for all Protocol definitions. Use Protocol (not ABC) when the contract is purely structural and you want duck typing. Reserve ABC for when you need shared implementation code.

Examples:
- `IResourceManager` (for the resource management protocol in XL-002)
- `ISerializable` (if a serialization protocol is created)

**Effort:** Simple

---

#### MINOR: Keep `*_utils.py` for Utility Modules
**ID:** DESIGN-003
**Issue:** Utility modules consistently use `*_utils.py` naming. Five exist already.
**Impact:** New utility modules (e.g., `numeric_utils.py`) should follow this pattern.
**Recommendation:** Use `*_utils.py` for modules containing pure/static utility functions. Keep utilities co-located with their primary consumers when possible. Only use `game/core/*_utils.py` for truly cross-layer utilities.

New modules to create:
- `game/core/numeric_utils.py` (for `is_numeric()`, `coerce_numeric()`)
- `game/strategy/generation/hex_utilities.py` already exists as `game/core/hex_math.py`; extend it rather than creating a new module

**Effort:** Simple

---

#### MINOR: Standardize Factory Methods to `from_*()` for Deserialization, `create_*()` for Construction
**ID:** DESIGN-004
**Issue:** Both `from_dict()` and `create_*()` are used, but they serve different purposes. `from_dict()` is consistently used for deserialization (15+ classes). `create_*()` is used for constructing new objects with business logic (10+ functions).
**Impact:** The serialization abstraction (XL-006) needs a consistent pattern.
**Recommendation:** Maintain the existing split:
- `from_dict()` / `from_json()`: Deserialization classmethods (reconstruct from saved data)
- `create_*()`: Factory functions/methods (construct with business logic, validation, defaults)

This is already consistent. The `Serializable` base class should provide `to_dict()` and `from_dict()`.

**Effort:** Simple

---

## 3. Composition vs Inheritance Decision Framework

### 3.1 Decision Matrix

| Mechanism | When to Use | Key Signal | Existing Examples |
|-----------|------------|------------|-------------------|
| **Base class (ABC)** | Shared state AND behavior; subclasses are a "kind of" the base | Multiple methods with shared instance state | `BaseGallery`, `BattleModeHandler`, `Ability` |
| **Mixin** | Shared behavior, no/minimal state; cross-cutting concern | Behavior added to unrelated class hierarchies | `ShipPhysicsMixin` |
| **Utility function** | Stateless operations; pure transforms | No `self` needed; input -> output | `hex_math.py`, `json_utils.py`, `combat_utils.py` |
| **Protocol** | Interface contracts; structural typing | Multiple unrelated implementations; cross-layer boundaries | `ICommandHandler`, `IFleet`, `IValidationRule` |
| **Frozen dataclass** | Immutable value objects; configuration | No behavior, just data | `GameRegistries`, `PanelWidths`, DTOs |
| **Registry pattern** | Extensible dispatch; plugin-like | New variants added without modifying existing code | `CommandHandlerRegistry`, `RegistryManager` |

### 3.2 Recommendations for Each Consolidation Cluster

---

#### CRITICAL: Mechanism Assignments for 11 Clusters
**ID:** DESIGN-005
**Issue:** Each of the 11 consolidation clusters identified in the prior art report needs the correct abstraction mechanism. Using the wrong mechanism creates either unnecessary coupling (inheritance) or insufficient code sharing (protocol alone).
**Impact:** This is the highest-impact design decision. Wrong mechanism choice creates refactoring debt immediately.
**Recommendation:**

| # | Cluster | Recommended Mechanism | Rationale |
|---|---------|----------------------|-----------|
| 1 | Ability parameter parsing (CQ-001) | **Static method on Ability base** (already done: `_parse_primary_value()`) | Stateless parsing; already in base class. Mark as COMPLETED. |
| 2 | Ability recalculation (CQ-002) | **Template method in Ability base** | Shared pattern: `self.field = self._base * self.get_effective_stat(key)`. Add `_apply_stat_bindings()` that auto-applies `STAT_BINDINGS`. Subclasses only need declarative binding list. |
| 3 | Superweapon order processing (STRAT-SYS CQ-002) | **ABC base class: `BaseSuperweaponProcessor`** | Shared state (fleet, empire, galaxy) + shared lifecycle (validate -> find ship -> execute -> pop order -> log). Subclasses implement only `_execute_action()`. |
| 4 | Validator common pattern (STRAT-SYS CQ-003) | **Utility functions, NOT base class** | The validators (`ColonizeValidator`, `SuperweaponValidator`, `TransferValidator`) have different signatures and different validation logic. Extract shared helpers: `_check_fleet_exists()`, `_check_ability_on_ship()`, `_check_at_system()`. These are better as composable utility functions than a forced template method. |
| 5 | Section header UI (UI CQ-103) | **Utility function** | Already done: `create_section_header()` exists in `game/ui/utils.py`. Ensure adoption. |
| 6 | Slider widget (UI CQ-104) | **Composite widget class: `SliderRow`** | Has state (slider element, value label, synchronization). Not inheritance -- composition of existing pygame_gui widgets. |
| 7 | Race panel init (UI CQ-102) | **ABC base class: `BaseRacePanel`** | 4 panels share identical 25-line init pattern. They are a "kind of" panel with shared lifecycle. |
| 8 | Singleton service state (CORE CQ-001) | **Mixin: `ServiceStateMixin`** | Shared behavior (clear, loaded flag, lazy loading) that cuts across unrelated singleton hierarchies (`RegistryManager`, `StrategyManager`, `AssetManager`). Cannot use ABC because these already have `SingletonMeta` as metaclass. |
| 9 | Numeric type checking (XL-001) | **Utility functions in `game/core/numeric_utils.py`** | Pure stateless operations: `is_numeric(v)`, `coerce_numeric(data, key, default)`. |
| 10 | Serialization boilerplate (XL-006) | **Mixin: `SerializableMixin`** | Cross-cutting concern. Classes already have their own inheritance hierarchies. A mixin with `to_dict()`/`from_dict()` auto-generation using `__serialize_fields__` class attribute. |
| 11 | Resource management (XL-002) | **Protocol: `IResourceManager`** | Three parallel systems with near-identical API but different domains. Protocol defines the shared contract without forcing a common base. |

**Effort:** Medium (per-cluster decisions are Simple, but 11 clusters total)

---

#### MAJOR: Avoid Validator Base Class -- Use Composable Helpers Instead
**ID:** DESIGN-006
**Issue:** The prior art report suggests `ValidatorBase with template method` for the 3 validators. However, examining the actual code reveals that `ColonizeValidator`, `SuperweaponValidator`, and `TransferValidator` have fundamentally different method signatures, different validation chains, and different return semantics. Forcing them into a template method would require an awkward `context` parameter bag.
**Impact:** A forced base class would be worse than the duplication it replaces. The validators are NOT polymorphic -- nobody calls them through a common base reference.
**Recommendation:** Instead, extract shared validation steps as composable utility functions:
```python
# game/strategy/validation/validation_helpers.py
def check_fleet_exists(fleet) -> Optional[ValidationResult]:
    """Returns error result if fleet is None, else None."""

def check_ability_on_fleet(fleet, ability_name, registry) -> Optional[ValidationResult]:
    """Returns error result if no ship has the ability, else None."""

def check_at_system(galaxy, fleet) -> Tuple[Optional[ValidationResult], Optional[StarSystem]]:
    """Returns (error_result, None) or (None, system)."""
```
Each validator composes these helpers as needed. This matches the existing pattern where `_iterate_colony_pods` was extracted as a helper function for `ColonizeValidator`.

**Effort:** Simple

---

## 4. Parameterization Strategy

### 4.1 Current Patterns Observed

| Strategy | Existing Usage | When Used |
|----------|---------------|-----------|
| Class attributes | `Ability.layer`, `Ability.STAT_BINDINGS`, `TransferValidator.VALID_CARGO_TYPES` | Simple configuration that differs per subclass |
| Constructor injection | `BaseGallery.__init__(panel, manager, ...)`, `RegistryManager.__init__()` | Dependencies and required collaborators |
| Template method | `BaseGallery._get_label_text()`, `BaseGallery._discover_assets()` | Behavior override points where subclass provides specific logic |
| Frozen dataclass | `PanelWidths`, `Margins`, `GameRegistries` | Immutable configuration bundles |
| Module-level constants | `PANEL_WIDTHS = PanelWidths()` | Pre-created config instances |

### 4.2 Recommendations

---

#### MAJOR: Use Declarative Class Attributes + Auto-Apply for Ability Recalculation
**ID:** DESIGN-007
**Issue:** 16+ ability subclasses manually implement `recalculate()` with identical logic: `self.field = self._base_field * self.get_effective_stat(key, 1.0)`. The `STAT_BINDINGS` list already declares which stats affect which attributes, but the base class doesn't use this information for automatic recalculation.
**Impact:** The most impactful single change: eliminates 16+ manual `recalculate()` methods and prevents the pattern from being re-duplicated in future abilities.
**Recommendation:** Add `_apply_stat_bindings()` to the `Ability` base class that reads `STAT_BINDINGS` and automatically applies multipliers:

```python
class Ability:
    def _apply_stat_bindings(self) -> None:
        """Auto-apply stat bindings from STAT_BINDINGS declarations."""
        for binding in self.STAT_BINDINGS:
            base_value = getattr(self, binding.base_attribute, None)
            if base_value is None:
                continue
            stat_value = self.get_effective_stat(binding.stat_key.value)
            if binding.operation == 'multiply':
                setattr(self, binding.attribute_name, base_value * stat_value)
            elif binding.operation == 'add':
                setattr(self, binding.attribute_name, base_value + stat_value)

    def recalculate(self) -> None:
        """Default implementation: auto-apply stat bindings."""
        self._apply_stat_bindings()
```

Subclasses with standard bindings delete their `recalculate()` override entirely. Subclasses with custom logic still override as before.

**Effort:** Medium

---

#### MAJOR: Use Constructor Injection for All New Service Dependencies
**ID:** DESIGN-008
**Issue:** The codebase has a mix of singleton access (`RegistryManager.instance()`) and constructor injection (`registry: IRegistryProvider`). The DI approach is documented as preferred (Tier 2) in `registry.py`.
**Impact:** New abstractions should consistently use constructor injection for testability.
**Recommendation:** All new base classes and services should accept their dependencies via constructor parameters. Use Protocol types for dependency parameters (e.g., `registry: IRegistryProvider`, not `registry: RegistryManager`). The singleton service locator (`get_default_registries()`) should only be used at composition roots (app.py, test fixtures).

**Effort:** Simple (design convention, no existing code changes)

---

#### MAJOR: Use Frozen Dataclass for New Configuration Bundles
**ID:** DESIGN-009
**Issue:** The builder uses frozen dataclasses for layout constants (`PanelWidths`, `Margins`) with module-level singleton instances. This pattern is clean and well-established.
**Impact:** New UI consolidation work (SliderRow, section headers, BaseRacePanel) needs consistent configuration.
**Recommendation:** For any new configuration bundle:
1. Define as `@dataclass(frozen=True)`
2. Create a module-level instance for default values
3. Allow constructor override for testing/customization

Example for SliderRow:
```python
@dataclass(frozen=True)
class SliderConfig:
    label_width: int = 150
    slider_width: int = 200
    value_label_width: int = 60
    height: int = 30
    spacing: int = 5

DEFAULT_SLIDER_CONFIG = SliderConfig()
```

**Effort:** Simple

---

## 5. Module Placement Recommendations

---

#### CRITICAL: Module Placement Map for All Proposed Abstractions
**ID:** DESIGN-010
**Issue:** New abstractions need clear home locations that respect layer boundaries. Misplacement creates circular imports or layer violations.
**Impact:** Every proposed abstraction needs a home. Wrong placement costs refactoring time later.
**Recommendation:**

| Abstraction | Recommended Location | Rationale |
|-------------|---------------------|-----------|
| `numeric_utils.py` | `game/core/numeric_utils.py` | Used by simulation, strategy, and UI layers |
| `_apply_stat_bindings()` | `game/simulation/components/abilities/base.py` (extend existing) | Extension of existing `Ability` class |
| `BaseSuperweaponProcessor` | `game/strategy/engine/superweapon_order_processor.py` (extend existing) | Co-located with existing concrete processor |
| Validator helpers | `game/strategy/validation/validation_helpers.py` (new) | Co-located with validators that use them |
| `SliderRow` widget | `game/ui/widgets/slider_row.py` (new `widgets/` package) | Reusable widget, not tied to one screen |
| `BaseRacePanel` | `game/ui/panels/base_race_panel.py` | Co-located with concrete race panels |
| `ServiceStateMixin` | `game/core/service_mixin.py` (new) | Cross-cutting core concern |
| `SerializableMixin` | `game/core/serializable.py` (new) | Cross-cutting core concern |
| `IResourceManager` | `game/core/protocols.py` (extend existing) | Cross-layer protocol, alongside other protocols |
| `SectionHeader` utility | `game/ui/utils.py` (already exists there) | Already consolidated |
| `UIRowBuilder` | `game/simulation/components/abilities/ui_colors.py` (extend existing) | Co-located with ability UI concerns |

**General placement rules:**
- `game/core/`: Cross-layer utilities and protocols (no pygame imports)
- `game/simulation/.../abilities/`: Ability-specific base class extensions
- `game/strategy/engine/` or `game/strategy/validation/`: Strategy-specific templates
- `game/ui/widgets/`: Reusable UI composites (new package)
- `game/ui/panels/`: Panel base classes

**Effort:** Simple (directory structure decisions)

---

#### MAJOR: Create `game/ui/widgets/` Package for Reusable UI Components
**ID:** DESIGN-011
**Issue:** The codebase has `game/ui/panels/` for panel classes and `game/ui/screens/` for screen classes, but no dedicated location for reusable composite widgets (SliderRow, text input with label, dropdown with label). These are currently built inline in 20+ locations.
**Impact:** Without a widgets package, new reusable UI components have no canonical home, leading to further inline duplication.
**Recommendation:** Create `game/ui/widgets/__init__.py` with:
- `slider_row.py` - SliderRow composite (resolves UI CQ-104: 21 instances)
- `labeled_input.py` - LabeledTextInput (resolves UI CQ-105: 15+ instances)
- `labeled_dropdown.py` - LabeledDropdown (resolves UI CQ-106: 10+ instances)

These are composite widgets (not subclasses of pygame_gui widgets), constructing and managing multiple pygame_gui elements together.

**Effort:** Medium

---

## 6. Migration Policy

---

#### CRITICAL: All-at-Once Migration per Abstraction, Phased Across Abstractions
**ID:** DESIGN-012
**Issue:** Per CLAUDE.md: "When a new system replaces an old one, ERADICATE the old system completely." This must be reconciled with practical migration of 11 clusters affecting 100+ files.
**Impact:** Partial migration is the primary source of codebase confusion and tech debt.
**Recommendation:**

**Per-abstraction migration strategy: ALL-AT-ONCE**
When introducing an abstraction (e.g., `_apply_stat_bindings()` in Ability base):
1. Implement the abstraction
2. Write tests for the abstraction itself
3. Migrate ALL consumers in a single project phase
4. Delete all old patterns
5. Verify full test suite passes

**Cross-abstraction phasing: SEQUENTIAL, DEPENDENCY-ORDERED**
Not all 11 clusters should be migrated simultaneously. Order by dependency:
1. **Foundation layer first:** `numeric_utils.py` (XL-001), `ServiceStateMixin` (CORE CQ-001)
2. **Simulation layer:** `_apply_stat_bindings()` (SIM-COMP CQ-002)
3. **Strategy layer:** Validator helpers, `BaseSuperweaponProcessor`
4. **UI layer:** `SliderRow`, `BaseRacePanel`, section headers
5. **Cross-cutting last:** `SerializableMixin` (XL-006), `IResourceManager` (XL-002)

**Effort:** Medium (planning is Simple; execution is Complex)

---

#### MAJOR: No Backward Compatibility Layers -- Ever
**ID:** DESIGN-013
**Issue:** During migration, there is a temptation to add `if hasattr(self, 'recalculate_v2')` or `try: new_method() except: old_method()` patterns. CLAUDE.md explicitly forbids this.
**Impact:** Even temporary compatibility layers tend to become permanent. They also double the testing surface.
**Recommendation:**
- No fallback code paths
- No `@deprecated` wrappers
- No feature flags for old vs new
- When the abstraction is ready and tested, switch ALL consumers in one commit
- If a consumer cannot be migrated, it means the abstraction design is wrong -- fix the abstraction, don't add a shim

**Effort:** Simple (policy decision)

---

#### MINOR: Migration Verification Checklist
**ID:** DESIGN-014
**Issue:** Each abstraction migration needs a verification step to ensure complete eradication of the old pattern.
**Impact:** Without verification, old patterns survive as orphaned code.
**Recommendation:** After each abstraction migration, run a grep to verify zero remaining instances of the old pattern:
```bash
# Example: After migrating recalculate() to _apply_stat_bindings()
rg "self\.\w+ = self\._base_\w+ \* self\.get_effective_stat" game/simulation/components/abilities/
# Should return 0 results (all migrated to declarative bindings)
```

Include this verification step in each project's completion checklist.

**Effort:** Simple

---

## 7. Testing Strategy for Abstractions

---

#### CRITICAL: Base Classes Must Have Their Own Unit Tests
**ID:** DESIGN-015
**Issue:** The existing `Ability` base class has no dedicated unit test file. Testing relies on subclass behavior, which means base class changes can break unexpectedly.
**Impact:** Every new abstraction needs its own test suite to verify the shared behavior independently of consumers.
**Recommendation:**

For each new abstraction:
1. **Unit tests for the base/mixin itself:**
   - Create a minimal test subclass/consumer inside the test file
   - Test all shared behavior through this test consumer
   - Test edge cases (empty inputs, None values, missing attributes)

2. **Migration equivalence tests:**
   - Before migrating a consumer, capture its behavior with a "golden" test
   - After migration, the same test must still pass
   - This is the existing test suite -- no new tests needed, just ensure green

3. **No property-based testing for these abstractions:**
   - The abstractions are mostly boilerplate reduction (mechanical transforms)
   - Property-based testing is overkill; standard example-based tests suffice
   - Exception: `numeric_utils.py` could benefit from hypothesis-based testing for edge cases

Example test structure:
```
tests/unit/core/test_numeric_utils.py          # New
tests/unit/simulation/abilities/test_base.py   # Extend existing
tests/unit/strategy/validation/test_helpers.py # New
tests/unit/ui/widgets/test_slider_row.py       # New
```

**Effort:** Medium

---

#### MAJOR: Migration Tests Should Be the Existing Test Suite, Not New Tests
**ID:** DESIGN-016
**Issue:** There's a temptation to write separate "migration verification" tests that test old-vs-new behavior. With 7353 tests already passing, the existing suite IS the migration test.
**Impact:** Redundant migration tests add maintenance burden and test execution time.
**Recommendation:**
- Run full test suite after each consumer migration
- If all 7353 tests pass, the migration is verified
- Only write NEW tests for the base abstraction itself (see DESIGN-015)
- Delete any tests that were testing the old duplicated pattern directly (if they exist)

**Effort:** Simple

---

## Additional Design Findings

---

#### MAJOR: SuperweaponValidator Has the Template Method Pattern -- Invert the Extraction
**ID:** DESIGN-017
**Issue:** `SuperweaponValidator` has 6 nearly identical `validate_*` static methods that all follow: check ability -> check location -> check target -> return result. This IS a template method pattern, but it's currently implemented as 6 separate methods.
**Impact:** The pattern should be extracted, but as a private helper within `SuperweaponValidator`, not as a separate base class.
**Recommendation:** Extract a private `_validate_superweapon()` method within `SuperweaponValidator`:
```python
@staticmethod
def _validate_superweapon(
    galaxy, fleet, ability_name: str,
    component_registry=None,
    require_system: bool = False,
    require_stars: bool = False,
    extra_checks: Callable = None,
) -> ValidationResult:
    """Common validation for all superweapon orders."""
```
Each public method becomes a thin wrapper calling `_validate_superweapon()` with specific parameters. This reduces 6 methods from ~30 lines each to ~5 lines each while keeping the same public API.

**Effort:** Simple

---

#### MAJOR: UI Row Generation Should Use Typed Objects, Not Raw Dicts
**ID:** DESIGN-018
**Issue:** `get_ui_rows()` in 20+ ability classes returns `List[Dict[str, str]]` with keys `label`, `value`, `color_hint`. This is a typed pattern masquerading as a dict.
**Impact:** When the UIRowBuilder is created, it should define a proper type.
**Recommendation:** Create a frozen dataclass for UI rows:
```python
@dataclass(frozen=True)
class AbilityUIRow:
    label: str
    value: str
    color_hint: str = HINT_DEFAULT
```
Add a convenience method to `Ability`:
```python
def _ui_row(self, label: str, value: str, color_hint: str = HINT_DEFAULT) -> Dict[str, str]:
    return {'label': label, 'value': value, 'color_hint': color_hint}
```
This can be migrated incrementally: the dict format still works everywhere, but new code uses the helper.

**Effort:** Simple

---

#### MINOR: EventBus Could Use Enum Event Types
**ID:** DESIGN-019
**Issue:** `EventBus` uses string event types with companion `BuilderEvents` constant class. String-based dispatch is error-prone (typos, no autocomplete).
**Impact:** Low urgency, but relevant if EventBus is adopted more widely.
**Recommendation:** For new EventBus consumers, define event types as string enums:
```python
class BuilderEvents(str, Enum):
    SHIP_UPDATED = 'SHIP_UPDATED'
    SELECTION_CHANGED = 'SELECTION_CHANGED'
```
The `str` base allows backward compatibility with existing string comparisons.

**Effort:** Simple

---

#### INFO: Positive Pattern -- Protocol + TypeGuard is the Gold Standard for Interfaces
**ID:** DESIGN-020
**Issue:** The `game/core/protocols.py` pattern of `@runtime_checkable Protocol` + `TypeGuard` helper function is a mature, well-executed pattern. It should be the standard for all new interface contracts.
**Impact:** Sets the standard for interface definition going forward.
**Recommendation:** All new protocols should follow this template:
```python
@runtime_checkable
class IMyInterface(Protocol):
    """Docstring with PROJ reference."""
    def my_method(self) -> ReturnType: ...

def is_my_interface(obj: Any) -> TypeGuard[IMyInterface]:
    """Check if obj satisfies the IMyInterface Protocol."""
    return isinstance(obj, IMyInterface)
```

**Effort:** N/A (information)

---

#### INFO: Positive Pattern -- Frozen Dataclass + Module Singleton for Constants
**ID:** DESIGN-021
**Issue:** `builder_utils.py` demonstrates an excellent pattern: `@dataclass(frozen=True)` for type-safe, immutable constant groups with module-level pre-created instances.
**Impact:** This should be the standard for all new configuration bundles.
**Recommendation:** Use this pattern for:
- Slider configuration (`SliderConfig`)
- Race panel configuration
- Any new UI layout constants
- Serialization field declarations

**Effort:** N/A (information)

---

#### MINOR: Mixin vs ABC Decision for Singleton Services
**ID:** DESIGN-022
**Issue:** The prior art report suggests `BaseSingletonService` for the 4 services that duplicate state management (clear, loaded flag, lazy loading). However, these classes already use `SingletonMeta` as their metaclass, and Python does not allow metaclass conflicts.
**Impact:** Using ABC as base class would conflict with `SingletonMeta`. The abstraction mechanism MUST be a mixin, not an ABC.
**Recommendation:** Use a plain mixin class (no metaclass):
```python
class ServiceStateMixin:
    """Mixin for singleton services with common lifecycle."""
    _loaded: bool = False

    def _ensure_loaded(self):
        if not self._loaded:
            self._do_load()
            self._loaded = True

    def clear(self):
        self._loaded = False
        self._do_clear()

    def _do_load(self): ...  # Override in subclass
    def _do_clear(self): ...  # Override in subclass
```

Usage: `class RegistryManager(ServiceStateMixin, metaclass=SingletonMeta):`

**Effort:** Simple

---

#### MINOR: SerializableMixin Design -- Use `__serialize_fields__` Declaration
**ID:** DESIGN-023
**Issue:** 20+ classes implement `to_dict()`/`from_dict()` independently. A mixin could auto-generate these, but Python lacks reflection-based serialization without explicit field declaration.
**Impact:** The serialization mixin needs a clean declaration mechanism that doesn't require heavy metaclass machinery.
**Recommendation:** Use class-level `__serialize_fields__` list:
```python
class SerializableMixin:
    __serialize_fields__: List[str] = []

    def to_dict(self) -> Dict[str, Any]:
        result = {}
        for field in self.__serialize_fields__:
            value = getattr(self, field)
            if hasattr(value, 'to_dict'):
                value = value.to_dict()
            elif isinstance(value, list):
                value = [v.to_dict() if hasattr(v, 'to_dict') else v for v in value]
            result[field] = value
        return result
```

Note: This is the highest-effort abstraction and should be done LAST. Many classes have custom serialization logic (enums, nested objects, version migration) that doesn't fit a simple mixin. Audit each class before migration.

**Effort:** Complex

---

## Top 5 Priority Issues

1. **DESIGN-005 (CRITICAL):** Mechanism assignments for 11 clusters -- the foundational decision that all other work depends on. Getting the mechanism wrong means rework.

2. **DESIGN-007 (MAJOR):** Auto-apply stat bindings in Ability base class -- eliminates the most-duplicated boilerplate pattern (16+ classes) with a single base class change.

3. **DESIGN-010 (CRITICAL):** Module placement map -- every new file needs a home. Decides before code is written.

4. **DESIGN-012 (CRITICAL):** Migration policy (all-at-once per abstraction) -- prevents half-migrated states that create confusion.

5. **DESIGN-015 (CRITICAL):** Base class testing strategy -- every new abstraction must have its own tests before consumer migration begins.

---

## Cross-Reference: Prior Art Clusters to Design Decisions

| Prior Art Finding | This Report's Recommendation | Key Decision |
|-------------------|------------------------------|--------------|
| CQ-001: Ability param parsing | DESIGN-005 #1: Already done (`_parse_primary_value`) | COMPLETED |
| CQ-002: Ability recalculation | DESIGN-005 #2 + DESIGN-007: Template method with auto `_apply_stat_bindings()` | ABC extension |
| STRAT-SYS CQ-002: Superweapon processing | DESIGN-005 #3: `BaseSuperweaponProcessor` ABC | ABC base class |
| STRAT-SYS CQ-003: Validator pattern | DESIGN-005 #4 + DESIGN-006: Composable helpers, NOT base class | Utility functions |
| UI CQ-103: Section headers | DESIGN-005 #5: Already exists in `ui/utils.py` | Adoption only |
| UI CQ-104: Slider widget | DESIGN-005 #6 + DESIGN-011: `SliderRow` in `ui/widgets/` | Composite class |
| UI CQ-102: Race panel init | DESIGN-005 #7: `BaseRacePanel` ABC | ABC base class |
| CORE CQ-001: Singleton services | DESIGN-005 #8 + DESIGN-022: `ServiceStateMixin` (not ABC) | Mixin |
| XL-001: Numeric type checking | DESIGN-005 #9 + DESIGN-003: `core/numeric_utils.py` | Utility functions |
| XL-006: Serialization | DESIGN-005 #10 + DESIGN-023: `SerializableMixin` (do last) | Mixin |
| XL-002: Resource management | DESIGN-005 #11: `IResourceManager` Protocol | Protocol |

---

*Report compiled: 2026-02-23*
