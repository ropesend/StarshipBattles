# PROJ-131: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Review
- **Review:** [2026-02-13_sweep_full-codebase-sweep](../../Reviews/results/2026-02-13_sweep_full-codebase-sweep/)
- **Type:** Review
- **Date:** 2026-02-13
- **Report:** [View Full Report](../../Reviews/results/2026-02-13_sweep_full-codebase-sweep/report.md)

## Initial Analysis
Findings from review - 245 total findings identified.
- **Critical:** 4
- **Major:** 23
- **Selected for remediation:** 56

## Selected Findings Summary

### TCG-STR-001: No dedicated tests for game/strategy/dat
- **Severity:** Critical
- **Location:** `game/strategy/data/naming.py`
- **Effort:** Simple

### TCG-STR-002: No dedicated tests for game/strategy/dat
- **Severity:** Critical
- **Location:** `game/strategy/data/physics.py`
- **Effort:** Medium

### TCG-UI1-001: BattleStateViewer has no unit tests
- **Severity:** Critical
- **Location:** `game/ui/screens/battle_state_v`
- **Effort:** Medium

### TCG-UI1-002: TestLabValidationManager has no unit tes
- **Severity:** Critical
- **Location:** `game/ui/screens/test_lab/valid`
- **Effort:** Complex

### TCG-STR-003: No dedicated tests for game/strategy/eng
- **Severity:** Major
- **Location:** `game/strategy/engine/commands.`
- **Effort:** Simple

### TCG-STR-004: TurnEngine.validate_colonize_order lacks
- **Severity:** Major
- **Location:** `game/strategy/engine/turn_engi`
- **Effort:** Simple

### TCG-STR-005: FleetOrder.to_dict() serialization has w
- **Severity:** Major
- **Location:** `game/strategy/data/fleet.py::F`
- **Effort:** Medium

### TCG-STR-006: QuickstartBuilder has no comprehensive t
- **Severity:** Major
- **Location:** `game/strategy/quickstart_build`
- **Effort:** Medium

### TCG-STR-007: StrategySessionFacade has incomplete que
- **Severity:** Major
- **Location:** `game/strategy/facade/strategy_`
- **Effort:** Medium

### TCG-STR-008: GameInitializer._setup_initial_scenario
- **Severity:** Major
- **Location:** `game/strategy/engine/game_init`
- **Effort:** Simple

### TCG-STR-009: ShipStatsCalculator.has_warp_capability
- **Severity:** Major
- **Location:** `game/strategy/services/ship_st`
- **Effort:** Medium

### TCG-UI2-001: UIConfig class has no dedicated test cov
- **Severity:** Major
- **Location:** `game/ui/config.py`
- **Effort:** Simple

### TCG-UI2-004: BattleUIService projectile color mapping
- **Severity:** Major
- **Location:** `game/ui/services/battle_ui_ser`
- **Effort:** Simple

### TCG-UI1-005: BuilderScreen (legacy) has no unit tests
- **Severity:** Major
- **Location:** `game/ui/screens/builder/main.p`
- **Effort:** Complex

### TCG-UI1-006: FormationEditorScreen has incomplete tes
- **Severity:** Major
- **Location:** `game/ui/screens/formation_edit`
- **Effort:** Medium

### TCG-UI1-007: PlanetReportPanel has no unit tests
- **Severity:** Major
- **Location:** `game/ui/panels/planet_report_p`
- **Effort:** Medium

### TCG-UI1-008: ShipDetailPanel has no unit tests
- **Severity:** Major
- **Location:** `game/ui/panels/ship_detail_pan`
- **Effort:** Medium

### TCG-UI1-009: BaseGallery abstract class has no unit t
- **Severity:** Major
- **Location:** `game/ui/panels/base_gallery.py`
- **Effort:** Simple

### TCG-UI1-010: DesignReportPanel has no unit tests
- **Severity:** Major
- **Location:** `game/ui/panels/design_report_p`
- **Effort:** Simple

### TCG-UI1-011: Multiple builder submodules have no test
- **Severity:** Major
- **Location:** `game/ui/screens/builder/`
- **Effort:** Complex

### TCG-UI1-012: Multiple test_lab submodules have no tes
- **Severity:** Major
- **Location:** `game/ui/screens/test_lab/`
- **Effort:** Complex

### TCG-UI1-013: GalaxyTest screen module has no tests
- **Severity:** Major
- **Location:** `game/ui/screens/galaxy_test/`
- **Effort:** Simple

### TCG-UI1-014: Formation submodules have no tests
- **Severity:** Major
- **Location:** `game/ui/screens/formation/`
- **Effort:** Medium

### TCG-UI1-015: Workshop helper modules have thin covera
- **Severity:** Major
- **Location:** `game/ui/screens/workshop_*.py`
- **Effort:** Medium

### TCG-UI1-016: Multiple race panel modules lack tests
- **Severity:** Major
- **Location:** `game/ui/panels/race_*.py`
- **Effort:** Medium

### TCG-UI1-017: StrategyRenderer draw methods test only
- **Severity:** Major
- **Location:** `tests/unit/ui/screens/test_str`
- **Effort:** Medium

### TCG-UI1-018: DesignStatsPanel tests use bypass-init p
- **Severity:** Major
- **Location:** `tests/unit/ui/panels/test_desi`
- **Effort:** Medium

### TCG-STR-010: DensityMap.from_config() lacks test cove
- **Severity:** Minor
- **Location:** `game/strategy/generation/densi`
- **Effort:** Simple

### TCG-STR-011: RegionClassifier._classify_spiral edge c
- **Severity:** Minor
- **Location:** `game/strategy/generation/regio`
- **Effort:** Simple

### TCG-STR-012: calculate_habitability has no negative t
- **Severity:** Minor
- **Location:** `game/strategy/formulas/habitab`
- **Effort:** Simple

### TCG-STR-013: EmpireEconomyCalculator doesn't test des
- **Severity:** Minor
- **Location:** `game/strategy/engine/empire_ec`
- **Effort:** Simple

### TCG-STR-014: Component inspector service lacks edge c
- **Severity:** Minor
- **Location:** `game/strategy/services/compone`
- **Effort:** Simple

### TCG-STR-015: Fleet.trigger_speed_recalculation has no
- **Severity:** Minor
- **Location:** `game/strategy/data/fleet.py::t`
- **Effort:** Simple

### TCG-STR-016: Transfer order validator edge cases
- **Severity:** Minor
- **Location:** `game/strategy/validation/trans`
- **Effort:** Simple

### TCG-UI2-007: InputMapper save_user_overrides file per
- **Severity:** Minor
- **Location:** `game/ui/services/input_mapper.`
- **Effort:** Simple

### TCG-UI2-008: ScreenshotManager capture_strategy_layer
- **Severity:** Minor
- **Location:** `game/ui/services/screenshot_ma`
- **Effort:** Simple

### TCG-UI2-009: BattleOrchestrator lacks tests for AI co
- **Severity:** Minor
- **Location:** `game/ui/orchestration/battle_o`
- **Effort:** Simple

### TCG-UI2-010: SpriteManager thread safety tests are li
- **Severity:** Minor
- **Location:** `game/ui/renderer/sprites.py`
- **Effort:** Medium

### TCG-UI2-011: colors.py basic constants not tested
- **Severity:** Minor
- **Location:** `game/ui/colors.py`
- **Effort:** Simple

### TCG-UI1-019: StrategyScreen tests have incomplete met
- **Severity:** Minor
- **Location:** `tests/unit/ui/screens/test_str`
- **Effort:** Medium

### TCG-UI1-020: Screen transition handling untested
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Simple

### TCG-UI1-021: Input handling edge cases untested
- **Severity:** Minor
- **Location:** `game/ui/screens/strategy_input`
- **Effort:** Simple

### TCG-UI1-022: Source code inspection used instead of b
- **Severity:** Minor
- **Location:** `tests/unit/ui/screens/test_str`
- **Effort:** Simple

### TCG-UI1-023: Mock verification without assertions on
- **Severity:** Minor
- **Location:** `tests/unit/ui/screens/test_str`
- **Effort:** Simple

### TCG-UI1-024: Test helper function tests its own mock
- **Severity:** Minor
- **Location:** `tests/unit/ui/panels/test_desi`
- **Effort:** Simple

### TCG-UI1-025: Missing parameterized edge case tests
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Simple

### TCG-UI1-026: No end-to-end battle UI flow tests
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Medium

### TCG-UI1-027: Strategy screen + build queue integratio
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Medium

### TCG-UI1-028: Workshop + ship I/O roundtrip untested
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Medium

### TCG-UI1-029: No resize handling tests
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Simple

### TCG-STR-017: Test fixtures use hardcoded component ID
- **Severity:** Info
- **Location:** `Unknown`
- **Effort:** Complex

### TCG-STR-018: Heavy mocking in TurnEngine tests
- **Severity:** Info
- **Location:** `tests/unit/strategy/turn_engin`
- **Effort:** Medium

### TCG-UI2-012: Test organization could be improved
- **Severity:** Info
- **Location:** `tests/unit/ui/`
- **Effort:** Complex

### TCG-UI1-030: No error recovery tests for UI screens
- **Severity:** Info
- **Location:** `Unknown`
- **Effort:** Complex

### TCG-UI1-031: No performance/stress tests for panels w
- **Severity:** Info
- **Location:** `game/ui/panels/battle_panels.p`
- **Effort:** Medium

### TCG-UI1-032: UI panels lack null/empty data tests
- **Severity:** Info
- **Location:** `Unknown`
- **Effort:** Simple


## Architecture
[Key architecture points relevant to implementation - to be filled during planning]

## Key Patterns to Reuse
- **[Pattern Name]**: `file:lines` - description

## Dependencies & Risks
1. **[Risk/Dependency]** - mitigation approach

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
