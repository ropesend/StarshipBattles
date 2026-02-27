# Phase 2: Quick Wins & Bug Fixes

**Findings:** CQ-42, CQ-44, CQ-50, CQ-26, CQ-27, CQ-07
**Effort:** Simple
**Goal:** Fix easy consolidations and the path stripping bug

## Tasks

### 2.1 Fix path stripping inconsistency (CQ-42) - BUG FIX
- [ ] Create `PathHelper.strip_start_hex(fleet_location, path)` utility
- [ ] Apply in `game_session.py:preview_fleet_path()`
- [ ] Apply in `command_handlers.py:ColonizeMissionCommandHandler`
- [ ] Apply in `command_handlers.py:MoveCommandHandler` (fix: add missing stripping)
- [ ] Apply in `superweapon_command_handlers.py:_setup_mission_move()`
- [ ] Write test for PathHelper
- [ ] Run full test suite

### 2.2 Extract tick interval formula (CQ-44)
- [ ] Create `SpeedHelper.get_tick_interval(speed)` utility (or add to existing module)
- [ ] Replace formula in `fleet_movement_engine.py`
- [ ] Replace formula in `action_execution_engine.py`
- [ ] Write test for formula
- [ ] Run targeted tests

### 2.3 Fix O(N) empire lookup (CQ-50)
- [ ] Replace linear loop in `TransferCommandHandler` with `fleet.owner_id` lookup
- [ ] Run targeted tests

### 2.4 Extract zone registration helper (CQ-26)
- [ ] Create `Galaxy.register_zones_from_system(system)` method
- [ ] Call from `add_system()`
- [ ] Call from `from_dict()`
- [ ] Run targeted tests

### 2.5 Extract warp point index helper (CQ-27)
- [ ] Create `Galaxy._rebuild_warp_point_index(system)` method
- [ ] Call from `add_system()`
- [ ] Call from `from_dict()`
- [ ] Call from `generate_warp_lanes()`
- [ ] Run targeted tests

### 2.6 Extract cost accumulation helper (CQ-07)
- [ ] Create `FleetResourceAggregator._accumulate_ship_costs(cost_getter)` method
- [ ] Replace both cost accumulation loops
- [ ] Run targeted tests

## Completion Checklist
- [ ] All tasks above completed
- [ ] Full test suite passes
- [ ] Path stripping bug verified fixed
