# PROJ-132: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-13 | Project created from review | Review identified 221 findings; 24 selected for remediation |
| 2026-02-13 | Severity-based phasing | Critical findings in Phase 1, Major in Phase 2, etc. |
| 2026-02-13 | ADR-FND-001: Use DI for Camera in ResearchTreeScene | Moved Camera import to factory function, added optional camera parameter. Eliminates layer violation at module level. |
| 2026-02-13 | ADR-FND-002: Accept IControllable as-is | Interface is 477 lines but well-organized with 5 clear sections. All 36 methods are cohesive (ship control). Splitting would create coupling issues where controllers need multiple interfaces. Marking as acceptable design. |
| 2026-02-13 | ADR-FND-003: Accept protocols.py as-is | File is 547 lines (marginal 47-line overage). Contains cohesive set of Protocol definitions for cross-layer type safety. Splitting would fragment protocol discovery. Well-organized with section comments. Acceptable. |
| 2026-02-13 | ADR-SIM-001: Move factory functions to UI layer | Created `game/ui/services/battle_factories.py` with `create_manual_battle`, etc. These functions import from AI layer, which is not allowed in simulation layer. Eliminates bidirectional coupling. |
| 2026-02-13 | ADR-SIM-002: Use protocol types only in battle_engine.py | Removed `AIController` concrete type import, now uses only `IAIController` protocol. Maintains proper layer isolation in type annotations. |
| 2026-02-13 | ADR-SIM-005: Accept late import for ModifierService as-is | ARCHITECTURE.md documents this as intentional design. Real import cycle that cannot be moved to module level. Edge operation (component addition only). Complex restructuring for minimal benefit. |
| 2026-02-13 | ADR-SIM-007: Accept Component.py as-is (monitor only) | INFO severity (lowest). File at 723 lines, below 800-line extraction threshold. Significant delegation already exists. Review recommends monitoring. |
| 2026-02-13 | ADR-STR-001: Accept Galaxy class as-is | Galaxy class is 736 lines, well under 800-line extraction threshold. Methods logically grouped (registration, lookup, generation, serialization). Same pattern as accepted IControllable and protocols.py. |
| 2026-02-13 | ADR-STR-002: Accept ProductionEngine as-is | ProductionEngine is 731 lines, under threshold. Already extracted from TurnEngine (PROJ-12 Phase 3). Well-documented with clear responsibilities. |
| 2026-02-13 | ADR-STR-003: Move hex_to_dict/hex_from_dict to module level | Late imports were unnecessary - no circular dependency risk since core doesn't depend on strategy. Cleaned up 6 late import sites in serialization methods. |
| 2026-02-13 | ADR-STR-004: Accept ShipInstance late imports as documented | Late imports (ShipSerializer lines 172, 503) are explicitly documented as intentional in ARCHITECTURE.md "Intentional Late Imports" section. Cross-layer boundary pattern. |
| 2026-02-13 | ADR-STR-005: Fix outdated documentation in ShipStatsCalculator | Docstring incorrectly claimed "no simulation layer coupling" but imports formula_system and modifiers from simulation. Strategy depends on Simulation is architecturally valid. Updated documentation to accurately describe dependencies. |
| 2026-02-13 | ADR-UI2-001: Accept Ship import in ShipIO as-is | ARCHITECTURE.md explicitly allows UI→Simulation imports (lines 35-37). ShipIO is a bridge service that must return Ship objects to UI. Adding protocol abstraction adds complexity without benefit - service's core logic (tkinter file dialogs) cannot be unit tested anyway. Consistent with accepted cross-layer imports in simulation_adapter.py and ShipInstance. |
| 2026-02-13 | ADR-UI1-001: Accept TestLabScreen as-is | 1911 lines, 75 methods BUT already decomposed into 14 modules (data_extractor, validation_manager, panel_manager, etc.). Remaining screen.py is orchestrator. Pygame rendering must stay in screen class. |
| 2026-02-13 | ADR-UI1-002: Accept FleetReportWindow as-is | 1093 lines, already extracted view_model and filters. Core rendering in window class. Pygame-dependent limits testability. |
| 2026-02-13 | ADR-UI1-003: Accept BuildQueueScreen as-is | 1098 lines, follows same decomposition pattern. Pygame-dependent. |
| 2026-02-13 | ADR-UI1-004: Accept StrategyScreen as-is | 810 lines (just over threshold), extensively decomposed into Renderer, CameraNavigator, FleetOperations, etc. Core screen is coordinator. |
| 2026-02-13 | ADR-UI1-005: Fix private facade access | Added public `facade` property to StrategyScreen. Updated dialogs to use `scene.facade` instead of `scene._facade`. |
| 2026-02-13 | ADR-UI1-006: Fix private method access | Added public `trigger_return_to_test_lab()` to BattleScreen. Updated BattleUI to use public method. |
| 2026-02-13 | ADR-UI1-007: Accept StrategyInputHandler coupling as-is | Internal helper accessing _fleet_ops, _camera_nav etc. is internal coupling within decomposed screen, not encapsulation violation. These modules collaborate as a unit. |
| 2026-02-13 | ADR-UI1-008: Accept deep attribute chains as-is | UI orchestration chains (scene→scene→service→method) are typical for Pygame UI coordination. Adding facades increases complexity without improving testability. |
| 2026-02-13 | ADR-UI1-009: Fix cache access encapsulation | Added `get_components_cache()` public method to TestLabDataExtractor. Updated validation_manager and screen.py to use public accessor. |
| 2026-02-13 | ADR-UI1-011: Fix private attribute mutation | Updated workshop_data_reloader to use existing `viewmodel.clear_selection()` instead of directly mutating `_selected_components`. |
| 2026-02-13 | ADR-UI1-012: Accept event router coupling as-is | Strategy event router checking _quit_confirm_dialog is part of pygame_gui dialog handling. Router tightly coupled to scene by design. |
