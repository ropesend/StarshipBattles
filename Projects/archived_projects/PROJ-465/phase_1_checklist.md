# Phase 1: Duplication Consolidation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-465 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete — 7 clusters implemented, 10 deferred (see decisions.md)

> **SCOPE REVISION (2026-05-20, Protocol 06):** Per dual independent+Codex
> review, only the byte-identical / trivially-equivalent mechanical dedups
> were implemented this pass. Implemented: DUP-X-1, DUP-X-7, Cluster 8,
> Cluster 10, Cluster 7, DUP-X-5, Cluster 19. Deferred with rationale in
> decisions.md: Cluster 2 (ability classes — UI/scope/activation rows would
> be lost; DI-2026-05-21-005), Cluster 9 (cross-layer base, not mechanical),
> DUP-X-6 (wrapper introduction + behavior change), DUP-X-3 / Cluster 11 /
> Cluster 12+21 / DUP-X-9 (order-dispatch templates that diverge in message/
> event payloads), DUP-X-2 / Cluster 3 / Cluster 6 (cross-layer/UI
> parameterizations, not byte-identical).

**Objective:** Consolidate the 17 verified duplication clusters identified by audit
`2026-05-20_060020_audit_shrink` into shared helpers / base methods, removing the
duplicate sites and updating all callers. Each task is gated on `pytest` passing.

> Strict TDD applies: for each consolidation, run the touched tests first to capture
> current green behavior, extract/route, then re-run. Do not change behavior.

---

## Tasks

### Task 1.1: Unify `_find_ship` into `BaseCommandHandler` (DUP-X-1) [Simple]
**File:** `game/strategy/engine/handlers/base.py`
**Tests:** `pytest tests/unit/strategy/engine/ -k "handler or find_ship"`

- [x] Add protected `@staticmethod _find_ship(fleet, ship_instance_id)` to **`BaseOrderHandler`** (`order_handlers/base.py`) — NOT `BaseCommandHandler`; all 5 copies live in `order_handlers/` and inherit `BaseOrderHandler`
- [x] Remove duplicate `_find_ship` from `order_handlers/launch_fighters.py`
- [x] Remove duplicate `_find_ship` from `order_handlers/launch_satellites.py`
- [x] Remove duplicate `_find_ship` from `order_handlers/lay_mines.py`
- [x] Remove duplicate `_find_ship` from `order_handlers/recover_fighters.py`
- [x] Remove duplicate `_find_ship` from `order_handlers/recover_satellites.py`
- [x] Verify: pytest passes (151 in order_handlers+handlers)

**Notes:** Path corrected to `BaseOrderHandler`. All 5 copies were already
`@staticmethod` with byte-identical bodies (orchestrator's "lay_mines is the
odd instance-method" note was stale). Characterization tests added in
`tests/unit/strategy/engine/order_handlers/test_base.py`.

### Task 1.2: Replace inline ship-resolution loops with `_find_ship` (DUP-X-7) [Simple, depends on 1.1]
**File:** `game/strategy/engine/handlers/launch_fighters.py`
**Tests:** `pytest tests/unit/strategy/engine/ -k "handler"`

- [x] Added `@staticmethod _find_ship` to `BaseCommandHandler` (`handlers/base.py`) and replaced the 5 byte-identical inline loops with `self._find_ship(fleet, cmd.ship_instance_id)`
- [x] `handlers/launch_fighters.py`, `launch_satellites.py`, `lay_mines.py`, `recover_fighters.py`, `recover_satellites.py`
- [x] Verify: pytest passes (183 incl. base_command_handler + handlers + order_handlers)

**Notes:** `order_queue.py` has a similar loop but compares without `str()`
and is NOT in the cluster — correctly left untouched. Characterization tests
added in `tests/unit/strategy/engine/test_base_command_handler.py`.

### Task 1.3: Template Method for handler validation pipeline (DUP-X-3) [Complex]
**File:** `game/strategy/engine/handlers/base.py`
**Tests:** `pytest tests/unit/strategy/engine/ -k "handler"`

- [ ] Add `_handle_vehicle_order(session, cmd, vehicle_type, design_id_field, order_type, group_name)` template to `BaseCommandHandler`
- [ ] Reduce `handlers/launch_fighters.py` `execute`/`_execute_fleet`/`_execute_planet` (lines 47/57/108) to template calls
- [ ] Reduce `handlers/launch_satellites.py` (lines 46/58/110) to template calls
- [ ] Reduce `handlers/lay_mines.py` (lines 48/63/121) to template calls
- [ ] Reduce `handlers/recover_fighters.py` (lines 41/51/84) to template calls
- [ ] Reduce `handlers/recover_satellites.py` (lines 41/53/85) to template calls
- [ ] Verify: pytest passes; LOC delta ~ -280

**Notes:**

### Task 1.4: Consolidate `_run_with_issuer` variants (Cluster 12+21) [Complex]
**File:** `game/strategy/engine/order_handlers/recover_fighters.py`
**Tests:** `pytest tests/unit/strategy/engine/ -k "recover or launch or issuer"`

- [ ] Extract shared `_run_with_issuer` skeleton (parameterized by group type + converter) to a shared base for the launch/recover order handlers
- [ ] Update `order_handlers/recover_fighters.py::_run_with_issuer` (line 139) to use shared skeleton
- [ ] Update `order_handlers/recover_satellites.py::_run_with_issuer` (line 119)
- [ ] Update `order_handlers/launch_fighters.py::_run_with_issuer` (line 147)
- [ ] Update `order_handlers/launch_satellites.py::_run_with_issuer` (line 130)
- [ ] Delete the original duplicated blocks
- [ ] Verify: pytest passes; LOC delta ~ -170

**Notes:**

### Task 1.5: Shared `execute_for_issuer` base (Cluster 11) [Simple]
**File:** `game/strategy/engine/order_handlers/recover_fighters.py`
**Tests:** `pytest tests/unit/strategy/engine/ -k "recover or issuer"`

- [ ] Move shared `execute_for_issuer` body to a base class for the recover order handlers
- [ ] Update `order_handlers/recover_fighters.py::execute_for_issuer` (line 107)
- [ ] Update `order_handlers/recover_satellites.py::execute_for_issuer` (line 90)
- [ ] Delete the original duplicated blocks
- [ ] Verify: pytest passes; LOC delta ~ -30

**Notes:**

### Task 1.6: Unify ship-to-carried-vehicle converters (DUP-X-9) [Simple]
**File:** `game/strategy/engine/order_handlers/recover_fighters.py`
**Tests:** `pytest tests/unit/strategy/engine/ -k "recover"`

- [ ] Extract shared converter parameterized by design-stat method name
- [ ] Update `order_handlers/recover_fighters.py::_fighter_ship_to_carried_vehicle` (line 261)
- [ ] Update `order_handlers/recover_satellites.py::_satellite_ship_to_carried_vehicle` (line 240)
- [ ] Verify: pytest passes; LOC delta ~ -30

**Notes:**

### Task 1.7: Centralize warp-capability check (DUP-X-6) [Medium]
**File:** `game/strategy/data/fleet.py` (or the `Fleet` definition module)
**Tests:** `pytest tests/unit/strategy/ -k "warp or fleet or navigation or pathfind"`

- [ ] Add `Fleet.can_use_warp() -> bool` wrapper (explicit False when `capabilities` is None)
- [ ] Route `strategy/engine/fleet_movement_engine.py:185` through the wrapper
- [ ] Route `strategy/engine/handlers/movement.py:241`
- [ ] Route `strategy/services/fleet_navigation_service.py:56`
- [ ] Route `strategy/services/galaxy_pathfinding_service.py:152`
- [ ] Route `strategy/data/fleet_consumable_aggregator.py:217` and `:241`
- [ ] Route `strategy/facade/dto/fleet_dto.py:223`
- [ ] Verify: pytest passes; LOC delta ~ -15

**Notes:**

### Task 1.8: Unify `facility_has_ability` implementations (DUP-X-2) [Medium]
**File:** `game/strategy/services/component_abilities.py`
**Tests:** `pytest tests/unit/strategy/ -k "ability or facility or planet_order"`

- [ ] Define canonical `facility_has_ability(facility, ability_name, component_registry)` in `strategy/services/component_abilities.py`
- [ ] Route `strategy/validation/planet_order_validator.py::_facility_has_ability` (line 105) through it
- [ ] Route `ui/screens/planet_menu_items.py::_facility_has_ability` (line 41) through it (requires giving the UI access to component_registry)
- [ ] Route `ui/screens/strategy_detail_formatter.py::_planet_has_ability` (line 303) through it
- [ ] Verify: pytest passes; LOC delta ~ -30

**Notes:** Three implementations currently use three different access paths and may diverge on edge cases — confirm equivalent behavior before/after.

### Task 1.9: Template `_from_dict_payload` for deployed groups (DUP-X-5) [Simple]
**File:** `game/strategy/data/deployed_group.py`
**Tests:** `pytest tests/unit/strategy/data/ -k "deployed_group or fighter or satellite or mine"`

- [x] Added shared `@classmethod _ShipBearingDeployedGroup._from_dict_payload` (`deployed_group.py:306-329`); both ship-bearing subclasses inherit it.
- [x] Removed duplicate `FighterWing._from_dict_payload`
- [x] Removed duplicate `SatelliteConstellation._from_dict_payload`
- [x] `MineGroup` left UNCHANGED — it inherits `DeployedGroup` (not `_ShipBearingDeployedGroup`) and holds `CarriedVehicle`s with sensitivity/mine_positions/scatter_seed; NOT part of this byte-identical pair.
- [x] Verify: pytest passes (26 deployed-group serialization tests)

**Notes:** Implementation differs from the original checklist wording (which
proposed a `_populate_ships_from_payload` helper + a MineGroup edit). Because
the FighterWing and SatelliteConstellation bodies were byte-identical, the
whole `_from_dict_payload` was hoisted to the shared base instead — simpler and
behaviour-identical. MineGroup is correctly excluded.

### Task 1.10: Consume `SimpleMultiplierAbility` for planetary stat modifiers (Cluster 2) [Simple]
**File:** `game/simulation/components/abilities/planetary/stat_modifiers.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/ -k "stat or modifier or shield"`

- [ ] Make the duplicated ability class at `planetary/stat_modifiers.py:50` inherit `SimpleMultiplierAbility` (base.py:480)
- [ ] Make the duplicated ability class at `planetary/stat_modifiers.py:125` inherit `SimpleMultiplierAbility`
- [ ] Verify: pytest passes; LOC delta ~ -30

**Notes:** Audit prose named these `GlobalStatModifierAbility`/`FleetStatModifierAbility`; live class names are `ShieldModifierAbility` (line 20/50) and `DamageModifierAbility` (line 95/125) — the duplicated `__init__`+`get_primary_value`+`get_ui_rows` bodies at lines 50/125 are the targets.

### Task 1.11: Merge `launch_*_in_battle` methods (Cluster 8) [Simple]
**File:** `game/simulation/systems/battle_engine.py`
**Tests:** `pytest tests/unit/simulation/ -k "battle_engine or launch"`

- [ ] Parameterize `launch_fighters_in_battle` (line 499) and `launch_satellites_in_battle` (line 540) into one method (only docstrings differ)
- [ ] Verify: pytest passes; LOC delta ~ -35

**Notes:**

### Task 1.12: Shared `BackgroundCall.cancel()` (Cluster 9) [Simple]
**File:** `game/services/llm/background.py`
**Tests:** `pytest tests/ -k "background"`

- [ ] Extract shared `cancel()` to a `BackgroundCall` base (Pattern #28)
- [ ] Update `services/llm/background.py::cancel` (line 182)
- [ ] Update `ui/services/image/background.py::cancel` (line 139)
- [ ] Verify: pytest passes; LOC delta ~ -20

**Notes:** Two `cancel` bodies are byte-identical per audit; confirm before/after.

### Task 1.13: Unify hit-effect drawing (Cluster 10) [Simple]
**File:** `game/ui/effects/hit_effects.py`
**Tests:** `pytest tests/ -k "hit_effect or effects"`

- [ ] Extract `_draw_radial_hit(effect_type, num_lines, line_step, color, line_color, line_width, line_length_mult)`
- [ ] Update `_draw_armor_hit` (line 146) to call it
- [ ] Update `_draw_component_destroyed` (line 176) to call it
- [ ] Verify: pytest passes; LOC delta ~ -20

**Notes:**

### Task 1.14: Parameterize stat-contributor launch functions (Cluster 19) [Simple]
**File:** `game/simulation/entities/stat_contributors/launch.py`
**Tests:** `pytest tests/unit/simulation/ -k "contributor or launch or stat"`

- [ ] Extract `_contribute_launch(ship, comp, acc, launch_ability, vehicle_fields)`
- [ ] Update `contribute_vehicle_launch` (line 25) to call it
- [ ] Update `contribute_tactical_satellite_launch` (line 69) to call it
- [ ] Verify: pytest passes; LOC delta ~ -40

**Notes:**

### Task 1.15: Parameterize superweapon designation handlers (Cluster 3) [Medium]
**File:** `game/ui/screens/strategy_superweapons.py`
**Tests:** `pytest tests/ -k "superweapon or designation"`

- [ ] Extract `_handle_designation(ability_name, error_msg, target_finder, confirm_builder, confirm_title, confirm_text)`
- [ ] Update `handle_stellerate_star_designation` (line 142)
- [ ] Update `handle_close_warp_designation` (line 239)
- [ ] Update `handle_dyson_sphere_designation` (line 281)
- [ ] Verify: pytest passes; LOC delta ~ -80

**Notes:**

### Task 1.16: Generic selection-modal opener (Cluster 6) [Simple]
**File:** `game/ui/screens/strategy_windows/selection_prompts.py`
**Tests:** `pytest tests/ -k "selection_prompt or modal"`

- [ ] Extract `_open_selection_modal(window_class, width, height, *args, slot_name)`
- [ ] Update `prompt_planet` (line 29)
- [ ] Update `open_system` (line 55)
- [ ] Update `prompt_fleet` (line 74)
- [ ] Verify: pytest passes; LOC delta ~ -25

**Notes:**

### Task 1.17: Shared `DismissableDialog` for single-button dialogs (Cluster 7) [Simple]
**File:** `game/ui/screens/defeat_dialog.py`
**Tests:** `pytest tests/ -k "dialog"`

- [ ] Extract a `DismissableDialog` mixin/base owning the identical `process_event` dismiss handling
- [ ] Update `defeat_dialog.py::process_event` (line 107)
- [ ] Update `turn_failed_dialog.py::process_event` (line 123)
- [ ] Verify: pytest passes; LOC delta ~ -14

**Notes:** Both `process_event` bodies are character-for-character identical per audit.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-20_060020_audit_shrink/`. See `findings/source_audit.md` for the link._
