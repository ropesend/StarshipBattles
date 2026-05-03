# Architecture Consolidation Review

### Summary
- Total issues found: 11
- Critical: 2, Major: 5, Minor: 3, Info: 1

### Findings

#### CRITICAL: Parallel Delegate/Manager Hierarchies
**ID:** AR-01
**Location:** Strategy: `fleet.py`, `fleet_battle_adapter.py`, `fleet_resource_aggregator.py`, `fleet_capability_calculator.py`, `ship_instance.py`, `ship_resource_manager.py`, `ship_cargo_manager.py`, `ship_display_formatter.py`. UI: `workshop_viewmodel.py`, `workshop_data_loader.py`, `workshop_event_router.py`, `workshop_data_reloader.py`, `builder/event_bus.py`, `builder/modifier_logic.py`, `builder/interaction_controller.py`.
**Issue:** Both layers independently implement extracted delegate/manager patterns for the same functional concerns (formatters, managers, event bus) with different naming schemes and approaches.
**Impact:** Two different extraction approaches. Developers must understand both.
**Recommendation:** Extract unified `DelegateManager` pattern in `game/core/patterns/`. Refactor both layers to inherit from base.
**Effort:** Complex

#### CRITICAL: Layer Iteration Pattern - 19+ Duplications
**ID:** AR-02
**Location:** Strategy: `ship_instance.py`, `design_metadata.py`, `ship_stats_calculator.py`, multiple engines. Simulation: `ship.py`, `ship_serialization.py`, `ship_validator.py`. UI: `stats_config.py`, `layer_panel.py`, `weapons_viewmodel.py`, `design_stats_panel.py`.
**Issue:** Core pattern for iterating ship layers and components appears 19+ times with inconsistent format handling.
**Impact:** Bug fixes must be applied in 19+ locations. Different error handling per location.
**Recommendation:** Create `LayerIterator` in `game/core/patterns/layer_iterator.py` with canonical iteration methods.
**Effort:** Medium

#### MAJOR: DTO vs Summary vs Info - Three Parallel Representations
**ID:** AR-03
**Location:** Strategy DTOs: `fleet_dto.py`, `empire_dto.py`. UI Wrappers: `fleet_data_source.py`, `strategy_detail_formatter.py`. Formatter Output: string-based representations.
**Issue:** Same domain objects represented three different ways: frozen DTOs, UI summaries, formatted strings.
**Impact:** Updates to Fleet schema require changes in 3 parallel locations.
**Recommendation:** Consolidate into single DTO hierarchy in `game/strategy/facade/dto/`.
**Effort:** Major

#### MAJOR: ValidationService vs Strategy Validators
**ID:** AR-04
**Location:** Strategy: `colonize_validator.py`, `transfer_validator.py`, `superweapon_validator.py`. UI: `validation_service.py`, `race_validator.py`.
**Issue:** Two independent validation hierarchies with inconsistent error representation (ValidationResult vs bool/string).
**Impact:** Duplicate ship validation logic. UI cannot reuse strategy validators.
**Recommendation:** Create unified `ValidationFramework` in `game/core/validation/`.
**Effort:** Major

#### MAJOR: Adapter/Service Pattern Proliferation
**ID:** AR-05
**Location:** 13+ service/adapter classes across strategy and UI layers with no unifying interface.
**Issue:** Mix of singletons, stateless utilities, stateful managers, and adapters with inconsistent constructor patterns.
**Impact:** No predictable service pattern. Dependency confusion. Testing complexity.
**Recommendation:** Establish `Service` base class framework in `game/core/services/`. Consolidate 13+ services into 4-5 cohesive services.
**Effort:** Complex

#### MAJOR: Similar Calculation Patterns Without Shared Base
**ID:** AR-06
**Location:** Strategy: `ship_stats_calculator.py`, `fleet_speed_calculator.py`, `empire_economy_calculator.py`. UI: embedded in `StatsConfig`, `WeaponsViewModel`.
**Issue:** Calculators follow similar patterns but don't inherit from common base. No standardized calc API.
**Impact:** Logic for "iterate component layer, aggregate values" duplicated. UI and strategy calculators may diverge.
**Recommendation:** Create `Calculator` framework in `game/core/calculations/`.
**Effort:** Major

#### MAJOR: Data Container Inconsistency
**ID:** AR-07
**Location:** Workshop: `workshop_context.py` (WorkshopContext). Builder: no equivalent context class.
**Issue:** Workshop has well-designed context configuration dataclass. Builder scatters equivalent configuration across function signatures.
**Impact:** Adding new configuration requires updating 5+ function signatures in Builder.
**Recommendation:** Create `BuilderContext` dataclass mirroring `WorkshopContext`.
**Effort:** Simple

#### Minor: Formatting Function Duplication
**ID:** AR-08
**Location:** Strategy: `ship_display_formatter.py`. UI: `stats_config.py` (fmt_time, fmt_decimal, fmt_score), `strategy_detail_formatter.py`.
**Issue:** Multiple similar formatting functions for display across layers.
**Impact:** Format strings may differ between UI views.
**Recommendation:** Create shared `DisplayFormatters` module in `game/core/display/`.
**Effort:** Simple

#### Minor: Event System Inconsistency
**ID:** AR-09
**Location:** UI: `builder/event_bus.py`. Strategy: `events/event_log.py`, `events/event_types.py`.
**Issue:** Two different event systems: UI simple pub/sub vs Strategy structured domain events.
**Impact:** Hard to propagate domain events to UI.
**Recommendation:** Unify event system. Move core events to `game/core/events/`.
**Effort:** Medium

#### Minor: Display ID Generation Not Centralized
**ID:** AR-10
**Location:** `ship_display_formatter.py`, `ship_detail_panel.py`, `fleet_data_source.py`
**Issue:** Ship display ID generation implemented in multiple places.
**Impact:** Display ID format change requires hunting through files.
**Recommendation:** Centralize in `ShipDisplayFormatter.get_display_id()`.
**Effort:** Simple

#### Info: Cross-Layer Iteration - Missing Component Accessor
**ID:** AR-11
**Location:** UI accesses `ship.layers` directly; Strategy uses `ShipInstance.get_components_by_layer()`.
**Issue:** UI layer sometimes accesses ship structure directly, sometimes via accessor methods.
**Impact:** UI tightly coupled to Ship internal structure.
**Recommendation:** Define `IShipStructure` protocol in `game/core/protocols.py`.
**Effort:** Simple

### Top 5 Priority Issues
1. **AR-02**: Layer Iteration Pattern (CRITICAL) - 19+ duplications, highest consolidation value
2. **AR-01**: Parallel Delegate Hierarchies (CRITICAL) - Unifies extraction pattern
3. **AR-03**: DTO Parallel Representations (MAJOR) - Single source of truth
4. **AR-04**: Validation Framework (MAJOR) - Reusable across layers
5. **AR-05**: Service Framework (MAJOR) - Predictable API, centralized DI
