# Phase 12 Analysis: Battle UI Requirements

## Date: 2026-01-29

## Overview

This document analyzes the data and action requirements for the Battle UI layer, identifying what needs to be exposed through the IBattleUI protocol.

---

## Current Architecture

### battle_scene.py

The `BattleScene` class currently:
1. Creates a `BattleService` directly (line 46)
2. Accesses `engine.ships` via property (line 180-181)
3. Accesses `engine.projectiles` via property (line 184-185)
4. Accesses `engine.ai_controllers` via property (line 188-189)
5. Directly iterates ships and projectiles in `draw()` (lines 370-385)
6. Accesses ship properties: `position`, `velocity`, `is_alive`, `name`, `team_id`, `hp`, `max_hp`, `mass`, `thrust`, `fuel`, `turn_speed`, `max_speed`, `is_derelict`, `resources`, `ai_strategy`, `current_shields`, `max_shields`, `current_speed`, `total_shots_fired`, `crew_required`, `crew_onboard`, `current_target`, `secondary_targets`, `max_targets`, `layers`, `source_file`

### panels.py

The HUD panels directly access ship objects:
1. `ShipStatsPanel` iterates `scene.ships` grouped by team_id (lines 68, 80)
2. Accesses detailed ship properties for display (see draw_ship_details)
3. Accesses component properties via `ship.layers` (lines 247-301, 310-357)
4. `SeekerMonitorPanel` tracks projectile objects directly (line 431-441)
5. `BattleControlPanel` checks `ship.is_alive` and `is_derelict` (lines 633-634)

---

## Data Requirements for UI

### 1. Ship Data

The UI needs the following ship data:

| Property | Type | Used In |
|----------|------|---------|
| id | int/str | Unique identification |
| name | str | Display, stats panel |
| team_id | int | Team grouping, colors |
| position | Vector2 | Rendering, camera |
| velocity | Vector2 | Rendering direction |
| heading | float | Rendering rotation |
| is_alive | bool | Filtering, display status |
| is_derelict | bool | Display status |
| hp | float | Stats display |
| max_hp | float | Stats display |
| current_shields | float | Stats display |
| max_shields | float | Stats display |
| current_speed | float | Stats display |
| max_speed | float | Stats display |
| mass | float | Debug display |
| total_thrust | float | Debug display |
| turn_speed | float | Debug display |
| total_shots_fired | int | Stats display |
| crew_onboard | int | Stats display |
| crew_required | int | Stats display |
| current_target | Optional[str] | Stats display (target name) |
| secondary_targets | List[str] | Stats display (target names) |
| max_targets | int | Stats display |
| ai_strategy | str | Stats display |
| source_file | str | Stats display (debug) |
| resources | Dict | Dynamic resource display |
| components | List[ComponentDTO] | Component breakdown |

### 2. Component Data (nested in Ship)

| Property | Type | Used In |
|----------|------|---------|
| name | str | Display |
| layer | LayerType | Grouping |
| current_hp | float | Stats bar |
| max_hp | float | Stats bar |
| is_active | bool | Status display |
| status | ComponentStatus | Status color/text |
| has_weapon | bool | Separate weapon list |
| shots_fired | int | Weapon stats |
| shots_hit | int | Weapon stats |

### 3. Projectile Data

| Property | Type | Used In |
|----------|------|---------|
| id | int/str | Unique identification |
| position | Vector2 | Rendering |
| velocity | Vector2 | Rendering (trail) |
| color | tuple | Rendering |
| radius | float | Rendering |
| damage | float | Seeker panel |
| hp | float | Seeker panel |
| max_hp | float | Seeker panel |
| status | str | Seeker panel |
| endurance | float | Seeker panel (fuel) |
| max_endurance | float | Seeker panel |
| target | Optional[str] | Seeker panel (target name) |
| max_speed | float | Seeker panel |

### 4. Battle State

| Property | Type | Used In |
|----------|------|---------|
| is_started | bool | Flow control |
| is_over | bool | End detection |
| tick_count | int | Display, timing |
| winner | Optional[int] | End screen |
| recent_beams | List[BeamDTO] | Visual effects |

### 5. Beam Data (for visual effects)

| Property | Type | Used In |
|----------|------|---------|
| start | Vector2 | Rendering |
| end | Vector2 | Rendering |
| color | tuple | Rendering |
| timer | float | Visual fade (managed by UI) |

---

## Actions Required

The UI needs to perform these actions:

| Action | Method | Used In |
|--------|--------|---------|
| Check battle over | is_battle_over() | Update loop |
| Get winner | get_winner() | End screen |
| Get tick count | get_tick_count() | Display |
| Get ships | get_ships() | Rendering, stats |
| Get projectiles | get_projectiles() | Rendering, seeker panel |
| Get recent beams | get_recent_beams() | Visual effects |

**Note:** Battle control (start, pause, end) is handled by `BattleService` directly. The `IBattleUI` protocol is **read-only** for UI display purposes.

---

## Design Decisions

### 1. DTOs vs Domain Objects

**Decision:** Use DTOs (Data Transfer Objects) for UI consumption.

**Rationale:**
- UI should not have write access to simulation objects
- DTOs can be frozen/immutable
- Clear separation of concerns
- Easier to mock for testing
- No risk of UI code accidentally modifying simulation state

### 2. Protocol Location

**Decision:** Create `IBattleUI` protocol in `game/ui/interfaces/battle_ui.py`

**Rationale:**
- UI layer owns the interface it needs
- Simulation layer provides implementation via adapter
- Clean dependency direction (UI depends on protocol, implementation adapts simulation)

### 3. Service Location

**Decision:** Create `BattleUIService` in `game/ui/services/battle_ui_service.py`

**Rationale:**
- Follows existing pattern in `game/ui/services/`
- Wraps `BattleService` from simulation layer
- Converts domain objects to DTOs

### 4. DTO Naming

**Decision:** Use `ShipDTO`, `ProjectileDTO`, `ComponentDTO`, `BeamDTO`

**Rationale:**
- Clear distinction from domain objects
- Standard naming convention
- Explicit that these are transfer objects

---

## Next Steps

1. **Task 12.2:** Create IBattleUI protocol with DTOs
2. **Task 12.3:** Create BattleUIService implementation
3. **Task 12.4:** Update battle_scene.py to use DTOs
4. **Task 12.5:** Update panels.py to use DTOs
5. **Task 12.6:** Create MockBattleUIService for testing
6. **Task 12.7:** Update UI tests
7. **Task 12.8:** Integration testing
