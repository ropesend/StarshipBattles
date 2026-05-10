# CENSUS Report: Call Site Census Across 11 Duplication Clusters

**Date:** 2026-02-23
**Scope:** All `game/` and `tests/` directories
**Agent:** CENSUS (data-gathering only)

---

## Summary

- **Total pattern instances counted:** 3,564
- **Clusters analyzed:** 11

---

## Findings

---

### CENSUS-01: HIGH: Font/Color Initialization Census

**ID:** CENSUS-01
**Issue:** Font creation is scattered across 29 files with 69 total calls, using two different APIs (`pygame.font.Font` and `pygame.font.SysFont`). Color tuples appear 639 times across game/ui/ with 249 unique colors.

**Font Calls (69 total):**

**pygame.font.Font() -- 12 instances across 3 files:**
| File | Line | Size |
|------|------|------|
| game/ui/panels/battle_panels.py | 100 | UIConfig.FONT_TITLE |
| game/ui/panels/battle_panels.py | 101 | UIConfig.FONT_NAME |
| game/ui/panels/battle_panels.py | 102 | UIConfig.FONT_STAT |
| game/ui/panels/battle_panels.py | 308 | 28 |
| game/ui/panels/battle_panels.py | 309 | 22 |
| game/ui/panels/battle_panels.py | 310 | 18 |
| game/ui/panels/battle_panels.py | 515 | 72 |
| game/ui/panels/battle_panels.py | 520 | 36 |
| game/ui/panels/battle_panels.py | 538 | 24 |
| game/ui/screens/setup_screen.py | 369 | 36 |
| game/ui/screens/setup_screen.py | 370 | 28 |
| game/ui/screens/setup_renderer.py | 15 | 64 |

**pygame.font.SysFont() -- 57 instances across 26 files:**
| File | Line | Font/Size |
|------|------|-----------|
| game/ui/research/research_renderer.py | 84 | Arial, dynamic |
| game/ui/panels/modifier_impact_grid.py | 83 | Arial, 15 |
| game/ui/panels/modifier_impact_grid.py | 84 | Arial, 14 |
| game/ui/panels/modifier_impact_grid.py | 85 | Arial, 15 bold |
| game/ui/panels/design_report_panel.py | 248 | arial, 18*scale bold |
| game/ui/panels/design_report_panel.py | 249 | arial, 14*scale |
| game/ui/panels/planet_report_panel.py | 225 | arial, 16 bold |
| game/ui/screens/battle_ui.py | 245 | Arial, 28 bold |
| game/ui/screens/battle_ui.py | 251 | Arial, 56 bold |
| game/ui/screens/battle_ui.py | 288 | Arial, 48 bold |
| game/ui/screens/battle_state_viewer.py | 118 | FONT_MAIN, 18 |
| game/ui/screens/battle_state_viewer.py | 119 | FONT_MONO, 13 |
| game/ui/screens/battle_state_viewer.py | 509 | FONT_MAIN, 24 |
| game/ui/screens/battle_state_viewer.py | 510 | FONT_MAIN, 16 |
| game/ui/screens/battle_state_viewer.py | 511 | FONT_MAIN, 14 |
| game/ui/screens/battle_screen.py | 593 | arial, 20 |
| game/ui/panels/strategy_widgets.py | 56 | arial, 8 |
| game/ui/panels/strategy_widgets.py | 115 | arial, 12 |
| game/ui/panels/strategy_widgets.py | 138 | arial, 8 |
| game/ui/screens/design_image_helper.py | 96 | arial, dynamic |
| game/ui/screens/builder/detail_panel.py | 260 | Arial, 14 |
| game/ui/screens/keybindings_scene.py | 408 | arial, 28 |
| game/ui/screens/formation/renderer.py | 260 | Arial, 14 bold |
| game/ui/screens/builder/weapons_panel.py | 116-118 | FONT_NAME, various |
| game/ui/screens/galaxy_test/system_mode.py | 528 | arial, 12 |
| game/ui/screens/galaxy_test/system_mode.py | 559 | arial, 10 |
| game/ui/screens/builder/schematic_view.py | 99, 175 | Arial, 10 |
| game/ui/screens/strategy_renderer.py | 59 | arial, dynamic (cached) |
| game/ui/screens/strategy_ui.py | 316 | arial, 20 |
| game/ui/screens/workshop_screen.py | 510 | Arial, 18 |
| game/ui/screens/test_lab/component_dropdown.py | 35 | FONT_MAIN, 16 |
| game/ui/screens/test_lab/json_viewer.py | 44-45 | FONT_MAIN, 14/18 |
| game/ui/screens/test_lab/dialogs.py | 41-42, 150-152 | FONT_MAIN, 14-24 |
| game/ui/screens/test_lab/results_panel.py | 38-40 | FONT_MAIN, 12-20 |
| game/ui/screens/test_lab/screen.py | 74-77 | FONT_MAIN, 14-48 |
| game/ui/screens/test_lab/ship_panels.py | 74-75 | FONT_MAIN, 12/16 |
| game/ui/screens/test_lab/test_run_card.py | 50-52 | FONT_MAIN, 12-16 |
| game/ui/screens/test_lab/test_run_details.py | 33-36 | FONT_MAIN, 12-20 |

**Unique font sizes (SysFont):**
| Size | Count |
|------|-------|
| 8 | 3 |
| 10 | 2 |
| 12 | 2 |
| 13 | 1 |
| 14 | 11 |
| 15 | 2 |
| 16 | 8 |
| 18 | 4 |
| 20 | 3 |
| 24 | 4 |
| 28 | 2 |
| 48 | 1 |
| 56 | 1 |

**Color Tuple Statistics (639 inline color tuples in game/ui/):**

Top 20 colors by frequency:
| Color | Count |
|-------|-------|
| (255, 255, 255) white | 42 |
| (180, 180, 180) light gray | 27 |
| (100, 100, 100) mid gray | 23 |
| (200, 200, 200) near white | 20 |
| (255, 100, 100) red-ish | 17 |
| (150, 150, 150) gray | 16 |
| (255, 200, 100) orange | 13 |
| (100, 100, 120) blue-gray | 13 |
| (220, 220, 220) light gray | 10 |
| (50, 50, 60) dark gray | 10 |
| (255, 255, 0) yellow | 9 |
| (80, 80, 80) dark gray | 9 |
| (0, 0, 0) black | 8 |
| (100, 255, 100) green | 8 |
| (40, 40, 40) near black | 8 |
| (150, 200, 255) light blue | 8 |
| (255, 50, 50) red | 7 |
| (100, 200, 255) blue | 7 |
| (30, 30, 35) near black | 7 |
| (140, 140, 160) blue-gray | 7 |

**Total unique colors:** 249
**Note:** colors.py already defines a centralized theme system. Many inline tuples duplicate or approximate these named colors.

**Total Instances:** 708 (69 font + 639 color)
**Effort:** Simple

---

### CENSUS-02: HIGH: Pygame Drawing Boilerplate Census

**ID:** CENSUS-02
**Issue:** Massive volume of low-level pygame drawing calls scattered across 95 files in game/ui/. Total: 1,598 drawing-related calls.

**Call Counts:**
| Pattern | Count | Files |
|---------|-------|-------|
| `pygame.Rect(` | 787 | 86 |
| `.blit(` | 302 | 36 |
| `font.render(` | 261 | 28 |
| `pygame.draw.rect(` | 156 | 33 |
| `pygame.draw.line(` | 44 | 17 |
| `pygame.draw.circle(` | 38 | 9 |
| **TOTAL** | **1,598** | **95** |

**Top 10 Files by Drawing Call Density:**
| File | Total Calls |
|------|-------------|
| game/ui/screens/test_lab/test_run_details.py | 175 |
| game/ui/screens/test_lab/screen.py | 140 |
| game/ui/screens/test_lab/test_run_card.py | 56 |
| game/ui/screens/setup_renderer.py | 54 |
| game/ui/screens/builder/weapons_panel.py | 44 |
| game/ui/panels/battle_panels.py | 43 |
| game/ui/panels/ship_stats_renderer.py | 43 |
| game/ui/screens/build_queue_screen.py | 43 |
| game/ui/screens/fleet_report_window.py | 43 |
| game/ui/screens/strategy_renderer.py | 39 |

**Total Instances:** 1,598
**Effort:** Simple

---

### CENSUS-03: MEDIUM: Ability Value Extraction Census

**ID:** CENSUS-03
**Issue:** Repeated type-checking pattern (`isinstance(data, (int, float))` / `isinstance(data, dict)`) for parsing ability data from JSON. This pattern appears 30 times across 8 ability files.

**isinstance(data, (int, float)) -- 8 instances:**
| File | Line |
|------|------|
| game/simulation/components/abilities/base.py | 130 |
| game/simulation/components/abilities/crew.py | 73 |
| game/simulation/components/abilities/resources.py | 39 |
| game/simulation/components/abilities/resources.py | 175 |
| game/simulation/components/abilities/resources.py | 215 |
| game/simulation/components/abilities/propulsion.py | 130 |
| game/simulation/components/abilities/cargo.py | 41 |
| game/simulation/components/abilities/cargo.py | 56 |

**isinstance(data, dict) -- 22 instances:**
| File | Line |
|------|------|
| game/simulation/components/abilities/base.py | 68 |
| game/simulation/components/abilities/base.py | 69 |
| game/simulation/components/abilities/base.py | 87 |
| game/simulation/components/abilities/base.py | 132 |
| game/simulation/components/abilities/base.py | 151 |
| game/simulation/components/abilities/colonize.py | 50 |
| game/simulation/components/abilities/harvester.py | 19 |
| game/simulation/components/abilities/harvester.py | 62 |
| game/simulation/components/abilities/harvester.py | 104 |
| game/simulation/components/abilities/weapons.py | 52, 71, 86, 102, 114, 253, 272, 322 |
| game/simulation/components/abilities/cargo.py | 38, 52 |
| game/simulation/components/abilities/resources.py | 34, 171, 211 |

**.get('value',...) -- 1 instance:**
| File | Line |
|------|------|
| game/simulation/components/abilities/crew.py | 73 |

**Total Instances:** 31
**Effort:** Simple

---

### CENSUS-04: MEDIUM: Ability recalculate/get_ui_rows Census

**ID:** CENSUS-04
**Issue:** 21 recalculate() methods and 35 get_ui_rows() methods across ability files. Most follow identical patterns.

**recalculate() -- 21 instances:**

| File:Class | Complexity | Lines |
|------------|------------|-------|
| base.py:BaseAbility (abstract) | simple | 5 |
| cargo.py:CargoStorage | simple | 2 |
| crew.py:CrewCapacity | simple | 2 |
| crew.py:LifeSupportCapacity | simple | 2 |
| crew.py:CrewRequired | complex | 6 |
| defense.py:ShieldProjection | simple | 3 |
| defense.py:ShieldRegeneration | simple | 3 |
| defense.py:ToHitAttackModifier | simple | 2 |
| defense.py:ToHitDefenseModifier | simple | 2 |
| defense.py:EmissiveArmor | simple | 2 |
| harvester.py:EmpireStorageAbility | simple | 3 |
| markers.py:VehicleLaunchAbility | simple | 2 |
| propulsion.py:CombatPropulsion | simple | 2 |
| propulsion.py:ManeuveringThruster | simple | 2 |
| propulsion.py:StrategicMovement | simple | 2 |
| resources.py:ResourceConsumption | simple | 2 |
| resources.py:ResourceStorage | simple | 2 |
| resources.py:ResourceGeneration | simple | 2 |
| weapons.py:ProjectileWeaponAbility | complex | 12 |
| weapons.py:BeamWeaponAbility | simple | 3 |
| weapons.py:SeekerWeaponAbility | complex | 6 |

**Summary:** 18 simple (base * multiplier), 3 complex

**get_ui_rows() -- 35 instances:**

| File:Class | Pattern | Lines |
|------------|---------|-------|
| base.py:BaseAbility (abstract) | label-value dict list | 7 |
| cargo.py:CargoStorage | label-value dict list | 9 |
| colonize.py:ColonizePlanet | other (conditional) | 12 |
| crew.py:CrewCapacity | label-value dict list | 2 |
| crew.py:LifeSupportCapacity | label-value dict list | 2 |
| crew.py:CrewRequired | label-value dict list | 2 |
| defense.py:ShieldProjection | label-value dict list | 2 |
| defense.py:ShieldRegeneration | label-value dict list | 2 |
| defense.py:ToHitAttackModifier | label-value dict list | 4 |
| defense.py:ToHitDefenseModifier | label-value dict list | 4 |
| defense.py:EmissiveArmor | label-value dict list | 2 |
| harvester.py:ResourceHarvesterAbility | other (multi-row) | 14 |
| harvester.py:EmpireStorageAbility | other (multi-row) | 14 |
| harvester.py:SpaceShipyardAbility | other (multi-row) | 29 |
| markers.py:VehicleLaunchAbility | label-value dict list | 5 |
| markers.py:CommandAndControl | label-value dict list | 2 |
| markers.py:RequiresCommandAndControl | label-value dict list | 2 |
| markers.py:RequiresCombatMovement | label-value dict list | 2 |
| markers.py:StructuralIntegrity | label-value dict list | 2 |
| propulsion.py:CombatPropulsion | label-value dict list | 2 |
| propulsion.py:ManeuveringThruster | label-value dict list | 2 |
| propulsion.py:StrategicMovement | label-value dict list | 2 |
| propulsion.py:WarpJump | label-value dict list | 8 |
| resources.py:ResourceConsumption | label-value dict list | 20 |
| resources.py:ResourceStorage | label-value dict list | 5 |
| resources.py:ResourceGeneration | label-value dict list | 5 |
| superweapons.py:DestroyPlanet | other (fixed rows) | 7 |
| superweapons.py:DestroyStar | other (fixed rows) | 7 |
| superweapons.py:OpenWarpPoint | other (fixed rows) | 7 |
| superweapons.py:CloseWarpPoint | other (fixed rows) | 7 |
| superweapons.py:CreateDysonSphere | other (fixed rows) | 7 |
| superweapons.py:SelfDestruct | other (fixed rows) | 7 |
| weapons.py:ProjectileWeaponAbility | label-value dict list | 6 |
| weapons.py:BeamWeaponAbility | label-value dict list | 4 |
| weapons.py:SeekerWeaponAbility (implied, not shown) | label-value dict list | 4 |

**Summary:** 23 use "label-value dict list" pattern, 12 use "other" patterns (conditional, multi-row, fixed rows)

**Total Instances:** 56
**Effort:** Simple

---

### CENSUS-05: HIGH: ValidationResult Construction Census

**ID:** CENSUS-05
**Issue:** 124 ValidationResult() constructor calls in game/, 97 in tests/. Most follow repetitive patterns of fleet/planet-not-found errors.

**Game code -- 124 instances by file:**
| File | Count |
|------|-------|
| game/strategy/engine/command_handlers.py | 24 |
| game/strategy/validation/superweapon_validator.py | 24 |
| game/strategy/engine/superweapon_command_handlers.py | 20 |
| game/strategy/validation/transfer_validator.py | 17 |
| game/simulation/validation/ship_validator.py | 10 |
| game/strategy/validation/colonize_validator.py | 9 |
| game/ui/screens/race_validator.py | 9 |
| game/strategy/facade/strategy_session_facade.py | 5 |
| game/core/validation.py | 3 |
| game/simulation/validation/base.py | 2 |
| game/strategy/data/race_config.py | 1 |

**By category:**
| Category | Count |
|----------|-------|
| single-error (is_valid=False, errors=[...]) | 43 |
| success-default (ValidationResult()) | 27 |
| other (multi-error, variable construction) | 53 |
| success-explicit (is_valid=True) | 1 |

**Frequently repeated error strings:**
- "Fleet not found." -- appears in command_handlers.py (8x), superweapon_command_handlers.py (12x), strategy_session_facade.py (2x)
- "Planet not found." -- appears in command_handlers.py (3x), superweapon_command_handlers.py (2x), strategy_session_facade.py (1x)
- "Fleet does not exist." -- appears in transfer_validator.py, colonize_validator.py

**Test code -- ~97 instances (estimated from grep counts)**

**Total Instances:** ~221 (124 game + ~97 tests)
**Effort:** Simple

---

### CENSUS-06: MEDIUM: Command Handler Classes Census

**ID:** CENSUS-06
**Issue:** 21 command handler classes across 2 files, all following an identical single-method pattern (validate-then-execute). Heavy repetition of fleet/planet resolution boilerplate.

**command_handlers.py -- 10 classes:**
| Class | Line | Methods |
|-------|------|---------|
| ICommandHandler (Protocol) | 25 | 1 |
| CommandHandlerRegistry | 41 | 3 |
| ColonizeCommandHandler | 73 | 1 |
| MoveCommandHandler | 135 | 1 |
| BuildShipCommandHandler | 167 | 1 |
| InterceptCommandHandler | 183 | 1 |
| JoinCommandHandler | 208 | 1 |
| ColonizeMissionCommandHandler | 237 | 1 |
| ClearOrdersCommandHandler | 343 | 1 |
| TransferCommandHandler | 361 | 1 |

**superweapon_command_handlers.py -- 11 classes:**
| Class | Line | Methods |
|-------|------|---------|
| ImplodePlanetCommandHandler | 27 | 1 |
| StellerateStarCommandHandler | 56 | 1 |
| OpenWarpPointCommandHandler | 80 | 1 |
| CloseWarpPointCommandHandler | 108 | 1 |
| CreateDysonSphereCommandHandler | 132 | 1 |
| SelfDestructCommandHandler | 156 | 1 |
| ImplodePlanetMissionCommandHandler | 222 | 1 |
| StellerateStarMissionCommandHandler | 250 | 1 |
| OpenWarpPointMissionCommandHandler | 273 | 1 |
| CloseWarpPointMissionCommandHandler | 300 | 1 |
| CreateDysonSphereMissionCommandHandler | 323 | 1 |

**Repeated patterns:**
| Pattern | command_handlers.py | superweapon_command_handlers.py |
|---------|--------------------|---------------------------------|
| Fleet resolution | 15 | 22 |
| Planet resolution | 14 | 4 |
| Ownership validation | 2 | 0 |

**Total Instances:** 21 classes, 37 fleet-resolution patterns, 18 planet-resolution patterns
**Effort:** Simple

---

### CENSUS-07: LOW: JSON Loaders Census

**ID:** CENSUS-07
**Issue:** JSON loading calls are relatively consolidated. Only 9 json.load/json.loads calls in game/ code. Two central loading functions exist in json_utils.py.

**json.load() -- 4 instances:**
| File | Line | Context |
|------|------|---------|
| game/core/json_utils.py | 58 | Central loader (load_json_file) |
| game/core/json_utils.py | 96 | Central loader (load_json_raw) |
| game/ui/screens/builder/stats_config.py | 300 | Stats config loading |
| game/ui/screens/formation_editor.py | 208 | Formation data loading |

**json.loads() -- 5 instances:**
| File | Line | Context |
|------|------|---------|
| game/simulation/battle_state.py | 547 | BattleState.from_json() |
| game/strategy/data/ship_instance.py | 661 | ShipInstance.from_json() |
| game/ui/screens/battle_state_viewer.py | 168 | Battle viewer parsing |
| game/ui/screens/battle_state_viewer.py | 547 | Diff comparison |
| game/ui/screens/battle_state_viewer.py | 548 | Diff comparison |

**Note:** Most loading is already routed through `json_utils.py`. Only 2 files bypass it.

**Total Instances:** 9
**Effort:** Simple

---

### CENSUS-08: MEDIUM: DTO Serialization Census

**ID:** CENSUS-08
**Issue:** 29 to_dict() methods and 26 from_dict() methods spread across 18 files. Additionally, 98 @dataclass decorations across 51 files.

**to_dict() -- 29 instances across 18 files:**
| File | Count | Classes |
|------|-------|---------|
| game/simulation/battle_state.py | 5 | ComponentState, ShipState, ProjectileState, BattleState, BattleResults |
| game/strategy/data/galaxy.py | 3 | WarpPoint, StarSystem, Galaxy |
| game/strategy/events/event_log.py | 2 | Event, EventLog |
| game/research/data/research_tracker.py | 2 | NodeState, ResearchTracker |
| game/strategy/data/stars.py | 2 | Spectrum, Star |
| game/strategy/data/fleet.py | 2 | FleetOrder, Fleet |
| game/strategy/engine/game_config.py | 2 | PlayerConfig, GameConfig |
| game/strategy/data/ship_instance.py | 1 | ShipInstance |
| game/strategy/data/planet.py | 1 | Planet |
| game/strategy/data/empire.py | 1 | Empire |
| game/strategy/data/race_config.py | 1 | RaceConfig |
| game/strategy/data/design_metadata.py | 1 | DesignMetadata |
| game/strategy/engine/game_session.py | 1 | GameSession |
| game/strategy/services/fleet_navigation_service.py | 1 | NavigationResult |
| game/simulation/entities/ship_serialization.py | 1 | ShipSerializer |
| game/simulation/entities/ship.py | 1 | Ship |
| game/simulation/components/modifier_effects.py | 1 | ModifierEffect |
| game/core/input_actions.py | 1 | KeyBinding |

**from_dict() -- 26 instances across 16 files:**
| File | Count | Classes |
|------|-------|---------|
| game/simulation/battle_state.py | 5 | ComponentState, ShipState, ProjectileState, BattleState, BattleResults |
| game/strategy/data/galaxy.py | 3 | WarpPoint, StarSystem, Galaxy |
| game/strategy/data/stars.py | 2 | Spectrum, Star |
| game/strategy/events/event_log.py | 2 | Event, EventLog |
| game/strategy/engine/game_config.py | 2 | PlayerConfig, GameConfig |
| game/research/data/research_tracker.py | 2 | NodeState, ResearchTracker |
| game/simulation/entities/ship_serialization.py | 1 | ShipSerializer |
| game/simulation/entities/ship.py | 1 | Ship |
| game/strategy/data/empire.py | 1 | Empire |
| game/strategy/data/fleet.py | 1 | Fleet |
| game/strategy/data/planet.py | 1 | Planet |
| game/strategy/data/race_config.py | 1 | RaceConfig |
| game/strategy/data/design_metadata.py | 1 | DesignMetadata |
| game/strategy/data/ship_instance.py | 1 | ShipInstance |
| game/strategy/engine/game_session.py | 1 | GameSession |
| game/core/input_actions.py | 1 | KeyBinding |

**@dataclass -- 98 instances across 51 files:**
Top files by @dataclass count:
| File | Count |
|------|-------|
| game/strategy/engine/commands.py | 20 |
| game/ui/interfaces/battle_ui.py | 5 |
| game/simulation/battle_state.py | 5 |
| game/ui/screens/builder_utils.py | 5 |
| game/strategy/facade/dto/fleet_dto.py | 3 |
| game/strategy/facade/dto/system_dto.py | 3 |
| game/strategy/facade/dto/empire_dto.py | 3 |
| game/strategy/services/fleet_navigation_service.py | 3 |
| game/strategy/engine/fleet_order_processor.py | 3 |
| game/strategy/data/planet.py | 3 |

**Total Instances:** 153 (29 to_dict + 26 from_dict + 98 @dataclass)
**Effort:** Simple

---

### CENSUS-09: MEDIUM: Event Handling Census

**ID:** CENSUS-09
**Issue:** Event type checks are dispersed across many UI files. Each screen independently checks for MOUSEBUTTONDOWN/KEYDOWN/MOUSEMOTION, with no shared event routing abstraction (except strategy screens which have a router).

**Event type checks:**
| Event | Checks | Files |
|-------|--------|-------|
| `event.type == pygame.MOUSEBUTTONDOWN` | 18 | 17 |
| `event.type == pygame.KEYDOWN` | 18 | 16 |
| `event.type == pygame.MOUSEMOTION` | 4 | 4 |
| MOUSEBUTTONUP references | 11 | 7 |
| MOUSEWHEEL references | 22 | 16 |
| **TOTAL** | **73** | **~30 unique** |

**Files with event handling (MOUSEBUTTONDOWN check locations):**
| File | Line |
|------|------|
| game/ui/screens/battle_screen.py | 312 |
| game/ui/research/research_scene.py | 233 |
| game/ui/screens/battle_state_viewer.py | 310, 609 |
| game/ui/screens/builder/interaction_controller.py | 72 |
| game/ui/screens/build_queue_screen.py | 997 |
| game/ui/screens/fleet_report_window.py | 892 |
| game/ui/screens/formation_editor.py | 544 |
| game/ui/screens/galaxy_test/screen.py | 204 |
| game/ui/screens/setup_screen.py | 230 |
| game/ui/screens/strategy_input_handler.py | 71 |
| game/ui/screens/strategy_event_router.py | 112 |
| game/ui/screens/workshop_event_router.py | 90 |
| game/ui/screens/test_lab/test_run_details.py | 82 |
| game/ui/screens/test_lab/screen.py | 713 |
| game/ui/screens/test_lab/component_dropdown.py | 46 |
| game/ui/screens/test_lab/results_panel.py | 104 |
| game/ui/screens/test_lab/ship_panels.py | 122 |

**Total Instances:** 73
**Effort:** Simple

---

### CENSUS-10: MEDIUM: Validators Census

**ID:** CENSUS-10
**Issue:** 7 validator classes across the codebase, with varying sizes. Some are large (ShipDesignValidator at 17 methods).

**Validator classes:**
| File | Class | Line | Methods |
|------|-------|------|---------|
| game/strategy/validation/transfer_validator.py | TransferValidator | 10 | 4 |
| game/strategy/validation/superweapon_validator.py | SuperweaponValidator | 14 | 7 |
| game/strategy/validation/colonize_validator.py | ColonizeValidator | 47 | 5 |
| game/simulation/validation/ship_validator.py | ShipDesignValidator | 373 | 17 |
| game/ui/screens/race_validator.py | RaceValidator | 20 | 2 |
| game/simulation/entities/ship_validator_helper.py | ShipValidatorHelper | 15 | 4 |
| game/core/validation.py | (example in docstring) | 36 | - |

**Total Instances:** 6 concrete validators (39 methods total)
**Effort:** Simple

---

### CENSUS-11: HIGH: Test Fixtures Census

**ID:** CENSUS-11
**Issue:** 1,080 @pytest.fixture declarations across 348 test files, with 514 unique fixture names. Significant duplication in common fixture names.

**Top 20 most-duplicated fixture names:**
| Fixture Name | Occurrences |
|--------------|-------------|
| mock_component | 45 |
| mock_ship | 40 |
| setup | 39 |
| mock_fleet | 24 |
| mock_galaxy | 21 |
| setup_tmpdir | 17 |
| mock_registries | 16 |
| setup_mocks | 16 |
| setup_and_teardown | 14 |
| setup_teardown | 13 |
| mock_manager | 12 |
| handler | 12 |
| mock_scene | 12 |
| mock_empire | 11 |
| init_pygame | 10 |
| mock_planet | 10 |
| pygame_init | 9 |
| mock_owner | 9 |
| mock_ui_manager | 9 |
| mock_race_config | 8 |

**Top 15 files by fixture count:**
| File | Fixture Count |
|------|---------------|
| tests/conftest.py | 6 |
| tests/unit/test_framework/services/conftest.py | 18 |
| tests/unit/strategy/conftest.py | 13 |
| tests/unit/simulation/components/abilities/test_ability_base.py | 13 |
| tests/unit/strategy/validation/test_colonize_validator.py | 13 |
| tests/unit/simulation/test_battle_state_serialization.py | 17 |
| tests/unit/simulation/services/test_modifier_service.py | 17 |
| tests/unit/simulation/components/abilities/test_ability_base.py | 13 |
| tests/unit/strategy/data/test_fleet_resource_aggregator.py | 11 |
| tests/unit/ui/screens/test_race_validator.py | 11 |
| tests/unit/simulation/entities/test_projectile.py | 9 |
| tests/unit/ui/test_theme_discovery.py | 7 |
| tests/unit/strategy/generation/test_astrophysics.py | 9 |
| tests/unit/strategy/generation/density/conftest.py | 10 |
| tests/fixtures/test_scenarios.py | 8 |

**Duplication hotspots:** `mock_component` (45x), `mock_ship` (40x), and `setup` (39x) are defined independently in dozens of files rather than shared from a central fixture.

**Total Instances:** 1,080
**Effort:** Simple

---

## Aggregate Statistics

| Cluster | ID | Pattern | Count | Files Affected | Severity |
|---------|----|---------|-------|---------------|----------|
| 1. Font/Color Init | CENSUS-01 | Font + Color creation | 708 | ~50 | HIGH |
| 2. Drawing Boilerplate | CENSUS-02 | Pygame draw/blit/render | 1,598 | 95 | HIGH |
| 3. Ability Value Extract | CENSUS-03 | isinstance checks | 31 | 8 | MEDIUM |
| 4. recalculate/get_ui_rows | CENSUS-04 | Repeated methods | 56 | 10 | MEDIUM |
| 5. ValidationResult | CENSUS-05 | Constructor calls | 221 | 20 | HIGH |
| 6. Command Handlers | CENSUS-06 | Handler classes | 21 + 55 patterns | 2 | MEDIUM |
| 7. JSON Loaders | CENSUS-07 | json.load calls | 9 | 5 | LOW |
| 8. DTO Serialization | CENSUS-08 | to_dict/from_dict/@dataclass | 153 | 51 | MEDIUM |
| 9. Event Handling | CENSUS-09 | Event type checks | 73 | 30 | MEDIUM |
| 10. Validators | CENSUS-10 | Validator classes | 6 classes (39 methods) | 6 | MEDIUM |
| 11. Test Fixtures | CENSUS-11 | @pytest.fixture | 1,080 | 348 | HIGH |
| **TOTALS** | | | **~3,564** | | |

### Highest-Impact Clusters (by raw count):
1. **Drawing Boilerplate** (1,598 instances) -- largest single source of repetition
2. **Test Fixtures** (1,080 instances) -- most files affected (348)
3. **Font/Color Init** (708 instances) -- 249 unique colors, mostly unnamed
4. **ValidationResult** (221 instances) -- high repetition of error strings

### Most Consolidated Clusters (lowest concern):
1. **JSON Loaders** (9 instances) -- already well-centralized
2. **Ability Value Extraction** (31 instances) -- contained to 8 files
3. **Validators** (6 classes) -- reasonable current size
