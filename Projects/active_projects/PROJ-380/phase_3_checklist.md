# Phase 3: Duplication consolidation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-380 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Consolidate the 9 verified CRITICAL/MAJOR duplications identified by audit `2026-05-07_220215_audit_shrink` that survived independent verification.

Implementation order in this phase: do the lowest-risk Simple-effort items first (DUP-X-02, DUP-X-06, DUP-X-08, DUP-X-09, DUP-X-10), then Medium-effort items (DUP-X-01, DUP-X-07, DUP-X-12), then the Complex item (DUP-X-11). Each task is independently shippable; tests must pass after each.

---

## Tasks

### Task 3.1: Extract `ProviderFactory` base for LLM/Image factories [Simple, DUP-X-02]
**File:** `game/services/llm/factory.py`, `game/ui/services/image/factory.py` (and a new shared base — proposed `game/services/_provider_factory.py` or a generic function in an existing services helper module — pick the location that aligns best with existing layering, document it in **Notes**)
**Tests:** `pytest tests/unit/services/llm/test_factory.py tests/unit/ui/services/image/test_factory.py`

- [x] Decide and record the new module location for the shared base — chose `game/services/provider_factory.py` (services layer, both factories already depend on `game.services.*` or compatible)
- [x] Implement the shared `resolve_provider(...)` generic function accepting `providers`, `env_var`, `default`, `config_error_cls`, `error_code`, `label`
- [x] Refactor `LLMProviderFactory.create` to delegate to `resolve_provider`; preserves `LLM_PROVIDER` env var, `deepseek` default, `LLMConfigError`
- [x] Refactor `ImageProviderFactory.create` to delegate to `resolve_provider`; preserves `IMAGE_PROVIDER` env var, `openai` default, `ImageConfigError`
- [x] Verify: focused tests pass (15/15 across both test_factory.py files); LOC delta = −34 (LLM) + −24 (image) + 90 (new shared) = +32 net but eliminates duplication; the shared module's overhead is mostly docstring

**Notes:** Both factories already use module-scoped `_PROVIDERS` dicts and identical error-handling structure (verified). No existing `ProviderFactory` symbol — extraction target is free.

---

### Task 3.2: Extract `_distribute_cargo_to_fleet` helper [Simple, DUP-X-06]
**File:** `game/strategy/data/fleet_consumable_aggregator.py`
**Tests:** `pytest tests/unit/strategy/data/test_fleet_consumable_aggregator.py` (or whichever fleet-cargo tests exist)

- [x] Add private helper `_distribute_cargo_to_fleet(self, cargo_type, amount, ship_method)` that iterates `self._fleet.ships`, calls `ship_method(...)` per ship, accumulates total, and applies the `if amount <= 0: return 0` guard
- [x] Replace `load_cargo_to_fleet` body with `return self._distribute_cargo_to_fleet(cargo_type, amount, lambda ship, t, a: ship.load_cargo(t, a))`
- [x] Replace `unload_cargo_from_fleet` body identically using `ship.unload_cargo`
- [x] Verify: focused tests pass (61/61 in test_fleet_consumable_aggregator.py); LOC delta ≈ −18

**Notes:** Verification confirmed the two methods are perfect mirrors differing only in ship-method name. (DUP-X-06)

---

### Task 3.3: Add `Camera.hex_at_screen` + `_check_fleet_ability` validator [Simple, DUP-X-08]
**File:** `game/ui/screens/strategy_superweapons.py`, plus the camera module (proposed `game/ui/camera.py` — confirm path during implementation), and 4 caller files: `strategy_fleet_ops.py`, `strategy_click_dispatcher.py`, `strategy_colonization.py`, `strategy_input_handler.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_superweapons.py` then `pytest tests/ --testmon`

- [x] Added `Camera.hex_at_screen(screen_x, screen_y, hex_size) -> HexCoord` wrapping `screen_to_world` + `pixel_to_hex` (hex_size kept as a parameter — Camera is layer-agnostic and shouldn't depend on game hex_size)
- [x] Added module-level `_check_fleet_ability(fleet, ability_name, error_msg)` in `strategy_superweapons.py` (kept local to file — the only caller; no need to elevate to a shared module)
- [x] Replaced the 5 designation handlers in `strategy_superweapons.py` to use both helpers
- [x] Replaced remaining `pixel_to_hex(world_pos.x, world_pos.y, ...)` sites: 2 in `strategy_click_dispatcher.py`, 2 in `strategy_fleet_ops.py`, 1 in `strategy_colonization.py`, 1 in `strategy_input_handler.py`. Removed 4 now-dead `from game.core.hex_math import pixel_to_hex` imports. `strategy_render/grid.py` retains its import (different shape — operates on world coords directly).
- [x] Verify: focused tests pass (2945 passed, 1 skipped across `tests/unit/ui/screens/`); LOC delta ≈ −15 (5 designation sites + 6 misc sites - 1 helper added)

**Notes:** Verified `Camera.hex_at_screen` and `_check_fleet_ability` do not already exist. Audit-claimed 11 `pixel_to_hex` sites confirmed. (DUP-X-08)

---

### Task 3.4: Extract `_get_cell_detail` helper in event log data source [Simple, DUP-X-09]
**File:** `game/ui/screens/event_log_data_source.py`
**Tests:** `pytest tests/unit/ui/screens/test_event_log_data_source.py` (or the closest equivalent)

- [x] Added private `_get_cell_detail(self, row_index, detail_key) -> Optional[Any]` implementing the shared 4-step pattern with falsy→None coercion (preserves both callers' behaviour where empty strings became `None`)
- [x] Replaced `get_cell_replay_id` body with `return self._get_cell_detail(row_index, "replay_id")`
- [x] Replaced `get_cell_replay_unavailable_reason` body with `return self._get_cell_detail(row_index, "replay_unavailable_reason")`
- [x] Verify: 95 passed in test_event_log_data_source.py + test_event_log_replay_button.py; LOC delta ≈ −12

**Notes:** Two methods, identical guard sequence verified. `_get_cell_detail` does not already exist. (DUP-X-09)

---

### Task 3.5: Extract `_format_result_error` helper in fleet ops [Simple, DUP-X-10]
**File:** `game/ui/screens/strategy_fleet_ops.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_fleet_ops.py` (or closest equivalent)

- [x] Added module-private `_format_result_error(result, operation) -> dict` that emits the WARNING log AND returns the full `{'type': 'error', 'message': msg}` payload (so callers `return _format_result_error(result, "Move")`)
- [x] Replaced the duplicated block in `execute_move`
- [x] Replaced the duplicated block in `execute_intercept`
- [x] Replaced the duplicated block in `execute_join`
- [x] Verify: tests/unit/ui/screens/test_strategy_fleet_ops.py -> 13 passed; LOC delta ≈ −8

**Notes:** Audit's claim of additional sites in `strategy_click_dispatcher.py:274` and `strategy_superweapons.py` was NOT confirmed during verification — scope is limited to the 3 fleet_ops sites. (DUP-X-10, scope-reduced)

---

### Task 3.6: Consolidate 5 superweapon mission command handlers behind `MissionCommandHandler` [Medium, DUP-X-01]
**File:** `game/strategy/engine/superweapon_command_handlers.py`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_command_handlers.py` then `pytest tests/integration/strategy/`

- [x] Implemented `MissionCommandHandler(BaseCommandHandler)` template class in the same module — uses a `_validate_mission` hook returning `(ValidationResult, target)` plus `_ORDER_TYPE` / `_ORDER_LABEL` class attributes. The template's `execute` does the shared 5-step (fleet → validate → bail → move → emit). Planet resolution for ImplodePlanet is folded into its `_validate_mission` (returns the planet-error result directly when it fails)
- [x] Refactored `ImplodePlanetMissionCommandHandler` (planet-resolution + validate inside `_validate_mission`)
- [x] Refactored `StellerateStarMissionCommandHandler`
- [x] Refactored `OpenWarpPointMissionCommandHandler` (target_dict)
- [x] Refactored `CloseWarpPointMissionCommandHandler` (target_dict)
- [x] Refactored `CreateDysonSphereMissionCommandHandler`
- [x] All 5 handlers remain in `register()` unchanged (still extend BaseCommandHandler via the new MissionCommandHandler subclass)
- [x] Verify: tests/unit/strategy/engine/test_superweapon_command_handlers.py -> 24 passed; tests/integration/strategy/ -> 504 passed (1 pre-existing unrelated failure in test_save_round_trip_phase4.py::test_pathfinder_attached_after_init excluded). LOC delta ≈ −33 (subclass code shrinks; template adds ~50)

**Notes:** All 5 handlers register via `@command_spec` + `CommandRegistry`; the consolidation must not break that wiring. `MissionCommandHandler` does not already exist. (DUP-X-01)

---

### Task 3.7: Extract `_handle_input_mode_click` base in strategy click dispatcher [Medium, DUP-X-07]
**File:** `game/ui/screens/strategy_click_dispatcher.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_click_dispatcher.py` then `pytest tests/integration/ui/`

- [x] Narrowed scope: the audit's claim of "9 handlers sharing left-click+right-click skeleton" was overstated — left-click bodies diverge significantly across the 9 handlers (each does something different: prompt move/intercept choice, queue colonize mission, open transfer dialog, etc.). Only the right-click cancel block (3 lines) is truly duplicated. Extracted a `_cancel_input_mode(*, on_cancel=None) -> bool` helper rather than the wider `_handle_input_mode_click(...)`. This is cleaner — the left-click logic stays where it belongs, while the cancel block is consolidated.
- [x] Replaced the right-click branch in `_handle_move_mode_click`
- [x] Replaced the right-click branch in `_handle_join_mode_click`
- [x] Replaced the right-click branch in `_handle_colonize_mode_click`
- [x] Replaced the right-click branch in `_handle_transfer_mode_click`
- [x] Replaced the right-click branch in `_handle_drop_cargo_mode_click`
- [x] Replaced the right-click branch in `_handle_load_cargo_mode_click`
- [x] Replaced the right-click branch in `_handle_warp_target_click`
- [x] Replaced the right-click branch in `_handle_superweapon_click`
- [x] Refactored `_handle_edit_move_click` via the `on_cancel` callback that resets `_edit_move_ghost_hex`, `_edit_move_order_index`, `_edit_move_fleet`
- [x] Verify: tests/unit/ui/screens/test_strategy_click_dispatcher.py -> 13 passed; tests/unit/ui/screens/ -> 2945 passed; LOC delta ≈ −16 (8 × 3-line block → 1-line; edit-move 5 lines → 5 lines via callback; +30 line helper)

**Notes:** Verification flagged `_handle_edit_move_click` as DIVERGENT (extra state-var resets) — the `on_cancel` parameter is the agreed accommodation. Audit's claim of "full clones" for cargo/transfer handlers was overstated; only the right-click block duplicates. (DUP-X-07)

---

### Task 3.8: Extract `_iter_ability_sources` helper in ability iterator [Medium, DUP-X-12]
**File:** `game/strategy/services/ability_iterator.py`
**Tests:** `pytest tests/unit/strategy/services/test_ability_iterator.py` then `pytest tests/integration/strategy/`

- [ ] Implement `_iter_ability_sources(container, adapter_cls, *, filter_fn=bool, hex_coord=None)` generator capturing the shared skeleton (nil-check → iterate → conditional adapter creation → yield)
- [ ] Refactor `_facility_provider` to delegate
- [ ] Refactor `_storm_provider` to delegate
- [ ] Refactor `_star_provider` to delegate
- [ ] Refactor `_planet_intrinsic_provider` (line 217) to delegate
- [ ] Refactor `_fleet_provider` to delegate
- [ ] Refactor `_system_archetype_provider` to delegate
- [ ] Refactor `_warp_point_provider` (line 288) to delegate
- [ ] Verify: focused + integration tests pass; ability iteration produces identical results before/after; LOC delta ≈ −25

**Notes:** Verified all 7 providers share the same skeleton differing only in container attribute name and adapter class. `_iter_ability_sources` does not already exist. (DUP-X-12)

---

### Task 3.9: Add base serialization for `BattleEndCondition` hierarchy [Complex, DUP-X-11]
**File:** `game/simulation/systems/battle_end_conditions.py`
**Tests:** `pytest tests/unit/simulation/systems/test_battle_end_conditions.py` then `pytest tests/integration/simulation/`

- [ ] Add a base method (e.g., `BattleEndCondition._serialize_fields() -> dict`) that subclasses override to declare their fields, plus a base `to_dict` that returns `{"type": cls._TYPE_TAG, **self._serialize_fields()}` and a base `from_dict` classmethod that dispatches by `type` tag
- [ ] Migrate `TickLimitCondition` to use the base
- [ ] Migrate `TeamEliminatedCondition` to use the base
- [ ] Migrate `TeamIncapacitatedCondition` to use the base
- [ ] Migrate `EscapeCondition` to use the base
- [ ] Migrate `ShipDestroyedCondition` to use the base
- [ ] Migrate `NeverCondition` to use the base
- [ ] Migrate `MassRatioCondition` to use the base
- [ ] Migrate `AnyCondition` to use the base (note: contains nested condition list — confirm recursion path)
- [ ] Migrate `AllCondition` to use the base (also nested — confirm recursion path)
- [ ] Run round-trip serialization tests for every condition type to confirm `to_dict` → `from_dict` is lossless and matches the previous wire format byte-for-byte (or document any necessary save-format migration)
- [ ] Verify: focused + integration tests pass; no save-file shape changes; LOC delta ≈ −40

**Notes:** Verified 9 subclasses with 18 near-identical serialization methods. Tagged Complex by audit because of nested-condition recursion in `AnyCondition` / `AllCondition` and the round-trip equivalence requirement. (DUP-X-11)

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-07_220215_audit_shrink/`. See [findings/source_audit.md](findings/source_audit.md) for the link._
