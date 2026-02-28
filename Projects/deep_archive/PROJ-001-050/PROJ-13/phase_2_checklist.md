# PROJ-13 Phase 2: Constants & Magic Numbers

## Phase Overview
Extract magic numbers to configuration constants.

## Tasks

### Create/Update Constants Infrastructure
- [x] Review existing `game/core/constants.py`
- [x] Add LayerDefaults class for layer radius ratios
- [x] Add CombatConstants class for combat values
- [x] PhysicsConstants: Already exists in `game/simulation/physics_constants.py` (K_SPEED, K_THRUST, K_TURN)
- [x] Document each constant with units and acceptable ranges

### Extract Layer Defaults (CQ-009)
- [x] Find all layer radius magic numbers (0.2, 0.5, 0.8)
- [x] Replace with LayerDefaults.CORE_RADIUS_PCT, INNER_RADIUS_PCT, OUTER_RADIUS_PCT
- [x] Update `game/simulation/entities/ship.py`
- [x] Update `game/simulation/entities/ship_component_manager.py`
- [x] Update `game/ui/renderer/game_renderer.py`
- [x] Run tests (1400 passed)

### Extract Combat Constants
- [x] Add DEFAULT_DAMAGE_THRESHOLD to CombatConstants
- [x] Update `game/simulation/components/component.py` to use it
- [x] Find fighter launch speed (100) - already in `BattleConfig.FIGHTER_LAUNCH_SPEED`
- [x] Replace magic number in `game/simulation/systems/battle_engine.py` with BattleConfig.FIGHTER_LAUNCH_SPEED
- [x] Add test `test_fighter_launch_speed_uses_config` to verify
- [x] Find max_targets default (1)
- [x] Add DEFAULT_MAX_TARGETS to CombatConstants
- [x] Update ship.py, ship_stats.py, controller.py, controllable.py, ship_combat_engine.py, ship_stats_renderer.py
- [x] Add tests `TestMaxTargetsDefault` to verify constant usage

### Extract Physics Constants
- [x] Review `game/engine/physics.py` for magic numbers - CLEAN (uses PhysicsConfig)
- [x] Review `game/simulation/physics_constants.py` - EXISTS and well-documented
- [x] No consolidation needed - physics_constants.py is single source of truth for K_SPEED, K_THRUST, K_TURN
- [x] PhysicsConfig in config.py handles runtime settings (tick rate, drag, thresholds)
- [x] All physics constants are documented with formulas

### Create UI Layout Config
- [x] SKIP - UIConfig already exists in `game/core/config.py` with PANEL_MARGIN, PANEL_PADDING, PANEL_GAP, etc.
- [x] Additional layout constants exist in `game/ui/screens/builder_utils.py` (MARGINS dataclass)
- [x] Creating a separate layout_config.py would be duplicative
- [x] Decision: Use existing UIConfig for new layout constants as needed

### Update UI Files
- [x] DEFERRED - Magic pixel values in UI files are context-specific
- [x] UIConfig already provides centralized constants for common values
- [x] Full extraction is low-value given existing infrastructure

### Address CQ-022: Duplicated Default Values
- [x] CQ-022 specifically identified `max_targets` default (1) as duplicated
- [x] RESOLVED: Created CombatConstants.DEFAULT_MAX_TARGETS
- [x] Updated all 6 locations to use the constant
- [x] Tests added to verify constant usage

## Verification
- [x] Magic numbers in core layer files replaced
- [x] Constants documented with units
- [x] All tests pass
- [x] Code more readable and maintainable

## Progress Notes
- Session 2026-01-25: Added LayerDefaults and CombatConstants classes to constants.py
- Refactored layer radius percentages in ship.py, ship_component_manager.py, game_renderer.py
- Refactored damage_threshold default in component.py
- Session 2026-01-25 (continued):
  - Extracted fighter launch speed to use BattleConfig.FIGHTER_LAUNCH_SPEED in battle_engine.py
  - Removed duplicate FIGHTER_LAUNCH_SPEED from CombatConstants (BattleConfig is authoritative)
  - Extracted max_targets default to CombatConstants.DEFAULT_MAX_TARGETS across 6 files
  - Reviewed physics_constants.py - well-organized, no consolidation needed
  - Added tests for fighter launch speed and max_targets constant usage
  - 528 tests passing in combat/ai/simulation suites
- Session 2026-01-25 (final):
  - Confirmed UIConfig already handles UI layout constants (no separate file needed)
  - CQ-022 (duplicated max_targets) fully resolved
  - Phase 2 COMPLETE
