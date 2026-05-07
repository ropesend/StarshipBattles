# Verified Shard 11 — Skeptical Verification Report

## Summary

| Verdict | Count |
|---------|-------|
| CONFIRMED gaps | 2 |
| DISPUTED | 5 |
| INCONCLUSIVE (partial) | 1 |
| **Total claims verified** | **8** (2 CRITICAL + 6 MAJOR) |

**Overall:** 5 of 8 claims (62.5%) are DISPUTED. The Phase 2 report has systematic search-path errors — it searched `tests/unit/engine/` when tests live in `tests/unit/systems/`, missed entire test subdirectories (`tests/unit/strategy/consumable_management_engine/`), and overlooked test content within files it did find.

---

## CRITICAL Claims (2)

### CRITICAL 1: `game/engine/physics.py` — "No unit test file, zero test coverage"

**Verdict: DISPUTED**

**Evidence:** Four (4) test files exercise `PhysicsBody` directly:

1. `tests/unit/systems/test_physics.py` (315 lines) — imports `from game.engine.physics import PhysicsBody` (line 5). Tests:
   - `TestPhysicsBasics` — initialization, default values (`test_initialization`, `test_default_values`)
   - `TestPhysicsMovement` — update movement (`test_update_movement`), angular velocity (`test_angular_velocity`)
   - `TestPhysicsForces` — `apply_force` acceleration, accumulation, velocity update (`test_apply_force_accelerates`, `test_apply_force_accumulates`, `test_apply_force_updates_velocity`)
   - `TestPhysicsDirection` — `forward_vector()` at 0°, 90°, 180°, 270° (`test_forward_vector_angle_0`, `test_forward_vector_angle_90`, `test_forward_vector_angle_180`, `test_forward_vector_angle_270`, `test_forward_vector_is_unit`)
   - `TestApplyForceIntegration` — force→position end-to-end, fractional mass, accumulation, reset after update (`test_apply_force_to_position_integration`, `test_apply_force_with_fractional_mass`, `test_multiple_forces_accumulate_before_update`, `test_apply_force_acceleration_resets_after_update`)

2. `tests/unit/systems/test_physics_edge_cases.py` (133 lines) — imports `from game.engine.physics import PhysicsBody` (line 10). Tests:
   - `test_zero_mass_handling` — verifies zero mass is protected (line 7: `if self.mass > 0` guard), no crash
   - `test_drag_over_1_clamped` — verifies drag > 1 is clamped, no velocity reversal
   - `test_angular_drag_reduces_rotation` — angular drag decay
   - `test_zero_velocity_stays_zero`, `test_very_small_velocity_not_lost`, `test_large_force_velocity_reasonable`
   - `test_drag_reduces_velocity` — deceleration over many ticks
   - `test_very_small_mass_large_acceleration`

3. `tests/unit/simulation/test_physics_formulas.py` (800 lines) — tests formula-level boundaries

4. `tests/unit/simulation/test_physics_constants.py` (108 lines) — tests constant values

**Agent error:** The Phase 2 report searched `tests/unit/engine/` (which contains `collision_edge_cases/` and `test_spatial_exact.py`) and did not discover `tests/unit/systems/test_physics*.py`. The search path was too narrow.

**Coverage mapping to suggested tests:**

| Suggested test | Covered by |
|---|---|
| `test_physics_update_applies_velocity_acceleration` | `test_update_movement` (line 29) |
| `test_physics_drag_clamps_at_1` | `test_drag_over_1_clamped` (line 110) |
| `test_physics_angular_drag_applied` | `test_angular_drag_reduces_rotation` (line 121) |
| `test_physics_apply_force_zero_mass` | `test_zero_mass_handling` (line 61) |
| `test_physics_forward_vector_at_angles` | `test_forward_vector_angle_{0,90,180,270}` (lines 103-140) |
| `test_physics_position_property_delegation` | Implicitly tested via `test_update_movement` and `test_apply_force_to_position_integration` |

---

### CRITICAL 2: `game/simulation/combat/fleet_aura_manager.py` — "No unit test file, completely untested"

**Verdict: DISPUTED**

**Evidence:** Seven (7) test files live in `tests/unit/simulation/combat/`:

| Test file | Lines | Coverage |
|-----------|-------|----------|
| `test_fleet_aura_manager_modifier_stack.py` | 507 | ModifierStack consumption, per-team, global, placeholder, empty, None, shield_bonus_add, mixed add/mult, stack_group MAX/SUM, recalculate_stats, zero-value preservation, consecutive battles, destroyed ship |
| `test_fleet_aura_provider_identity.py` | 308 | Single/multi provider, disable, kill, derelict, recovery, same-class-multi-provider, same-stack-group MAX, unregister |
| `test_fleet_aura_register.py` | 139 | `register_ship()`, `_scan_ship`, recalculation, dead ship skip |
| `test_fleet_aura_unregister.py` | 181 | `unregister_ship()`, provider removal, recalculation, teammates lose bonus, team isolation |
| `test_fleet_aura_cache.py` | 88 | Caching, `_providers_dirty`, fingerprint, shared aggregator |
| `test_fleet_aura_extended.py` | 441 | `get_active_bonuses()`, external modifiers, fingerprint changes, component destruction, placeholder logging |
| `test_fleet_aura_unknown_stat_key_warning.py` | 140 | Unknown stat_key warnings, dedup, placeholder path separation |

**Total:** ~1,804 lines of test code across 7 files.

**Agent error:** The Phase 2 report states "No test file found in `tests/unit/simulation/combat/`" — this is factually incorrect. The 7 test files above all live in that exact directory. The report either failed to list the directory or used a search pattern that did not match.

**Coverage mapping to suggested tests:**

| Suggested test | Covered by |
|---|---|
| `test_initialize_scans_ships_for_fleet_scope` | `test_single_provider_contributes_value_to_teammate` (provider_identity:71) |
| `test_initialize_excludes_derelict_ships` | `test_initialize_skips_derelict_provider_ship` (provider_identity:270) |
| `test_derive_external_placeholder_skip` | `test_placeholder_effects_are_silently_ignored` (modifier_stack:112) |
| `test_register_ship_scans_new_ship` | `test_register_ship_scans_new_ship` (register:56) |
| `test_unregister_ship_removes_providers` | `test_unregister_removes_providers_for_ship` (unregister:56) |
| `test_update_skips_when_not_initialized` | Guard at line 298-299: `if not self._initialized: return` |
| `test_recalculate_aggregates_within_group_max` | `test_same_stack_group_entries_compose_max_not_sum` (modifier_stack:292) |
| `test_recalculate_aggregates_across_groups_sum` | `test_different_stack_groups_compose_sum` (modifier_stack:311) |
| `test_recalculate_preserves_zero_values` | `test_zero_value_damage_mult_preserved` (modifier_stack:384) |
| `test_recalculate_drops_providers_with_removed_ability` | Implicit via identity loss in `_recalculate` (line 355-359): `ab not in ability_instances → continue` |
| `test_apply_bonuses_writes_to_external_stats` | `test_shield_bonus_add_reaches_external_stats_per_team` (modifier_stack:192) |
| `test_apply_bonuses_triggers_recalculate_stats` | `test_apply_bonuses_invokes_ship_recalculate_stats` (modifier_stack:335) |
| `test_get_active_bonuses_excludes_dead_derelict` | `test_excludes_dead_providers` (extended:121) + `test_excludes_derelict_providers` (extended:137) |
| `test_provider_fingerprint_detects_operational_change` | `test_fingerprint_changes_on_component_destruction` (extended:301) |
| `test_external_modifier_global_scopes_to_all_teams` | `test_global_modifier_applies_to_every_team` (modifier_stack:94) |
| `test_placeholder_logging_rate_limited_once_per_source` | `test_placeholder_entry_emits_warning_once_per_source` (extended:365) |

---

## MAJOR Claims (6)

### MAJOR 1: `AIController._acquire_targets` — "No direct test of dead-target clearing"

**Verdict: DISPUTED**

**Evidence:** `tests/unit/ai/test_ai_controller_edge_cases.py:202-220` — test `test_update_with_dead_target`:

```python
def test_update_with_dead_target(self, mock_ship, mock_grid):
    """Update clears dead target and finds new one."""
    # Setup dead target
    dead_target = MagicMock()
    dead_target.is_alive = False
    mock_ship.get_current_target = MagicMock(return_value=dead_target)

    controller = AIController(mock_ship, mock_grid, enemy_team_id=1)
    # ...
    controller.update()

    # Should have cleared the dead target
    mock_ship.set_current_target.assert_called()
```

This directly tests the path at `controller.py:374-376`: dead target → `target = None` → `self.ship.set_current_target(None)`. It exercises the update loop including `_acquire_targets` which is called as part of `update()`.

Additionally, `test_dead_ship_no_action` in `test_ai_controller_unit.py:160-172` verifies that `update()` returns early for dead ships and `set_current_target` is NOT called — covering the other dead-ship branch.

---

### MAJOR 2: `ConsumableManagementEngine` — "No unit test file found"

**Verdict: DISPUTED**

**Evidence:** Four (4) test files in `tests/unit/strategy/consumable_management_engine/`:

| File | Lines | Coverage |
|------|-------|----------|
| `test_characterization.py` | 223 | `__init__` raises on None registries, `_validate_tick_inputs` raises on None ships, non-combat-capable skip, zero-cost skip, 1/100th per-tick consumption, consume-fail→auto-disable handoff, layer list/dict format dispatch, unknown component ID skip, trigger/resource mismatch, multiple-component disable |
| `test_auto_disable.py` | 366 | Component disable on depletion, per-turn-per-tick, total_cost calc, registry lookup |
| `test_consumption.py` | 83 | Per-turn consumption flow |
| `test_initialization.py` | 55 | `__init__` strict DI, `ResourceDepletion` dataclass |

**Agent error:** The Phase 2 report searched for `tests/unit/strategy/engine/test_consumable*.py` but tests live in `tests/unit/strategy/consumable_management_engine/` (directory, not `engine/` subdirectory). Search pattern mismatch.

**Coverage mapping to suggested tests:**

| Suggested test | Covered by |
|---|---|
| `test_process_per_turn_consumption_spreads_over_100_ticks` | `test_per_tick_consumption_is_one_hundredth_of_per_turn_total` (characterization:66) |
| `test_auto_disable_components_for_depleted_resource` | `test_failed_consume_resource_triggers_auto_disable_and_returns_depletion` (characterization:83) |
| `test_validate_tick_inputs_raises_on_none_ships` | `test_validate_tick_inputs_raises_when_fleet_ships_is_none` (characterization:36) |
| `test_consumption_skips_non_combat_capable_ships` | `test_non_combat_capable_ship_is_skipped` (characterization:49) |
| `test_consumption_zero_cost_no_op` | `test_zero_cost_resource_is_skipped` (characterization:58) |

---

### MAJOR 3: `HarvestingEngine._get_harvest_booster_mult` — "Untested path with late imports"

**Verdict: CONFIRMED**

**Evidence:** 
- `_get_harvest_booster_mult` at `harvesting_engine.py:388-419` contains a late-import chain for `find_abilities_in_scope` and `aggregate_multipliers`, iterates over 4 scopes (planet/sector/system/empire), and aggregates results via two-phase stacking.
- Grep for `_get_harvest_booster_mult` across the entire `tests/` directory: **zero matches**.
- The 3 existing harvesting test files (`test_harvesting_engine.py`, `test_harvesting_engine_habitability.py`, `test_harvesting_size_scaling.py`) cover `process_harvesting_tick`, `recalculate_storage`, per-tick harvesting, depletion, and storage overflow — but never call `_get_harvest_booster_mult` either directly or indirectly (the `_process_facility` path that calls it would require colony/empire mocks with mock galaxy and strategic ability scanner).

**Risk level:** Low-Medium. This is a private method only called during harvesting in the full strategy pipeline. However, the late-import chain (`from game.strategy.services.strategic_ability_scanner import ...`) and multi-scope aggregation have no verification of correctness.

---

### MAJOR 4: `FleetMovementEngine._filter_jump_past_collisions` — "Complex FEAT-28 logic"

**Verdict: PARTIALLY CONFIRMED / PARTIALLY DISPUTED**

**Evidence:** `tests/unit/strategy/fleet_movement_engine/test_characterization.py:238-258` — `test_filter_jump_past_drops_larger_fleet_on_swap_parity_with_id_tiebreak`:

- **CONFIRMED covered:** Tie-breaking on fleet ID string comparison (`str(fleet_a.id) < str(fleet_b.id)` at line 330 of fleet_movement_engine.py:330). The test has equal ship counts and verifies smaller-id fleet is dropped.
- **CONFIRMED covered:** Swap parity detection (both fleets heading to each other's current hex). The test sets up `MOVE_TO_FLEET` orders targeting each other with swapped destinations.
- **CONFIRMED covered:** Larger fleet drops. Implicitly tested (equal ships, smaller id dropped).
- **NOT covered:** The exact "larger fleet drops" path (`ships_a > ships_b → drop fleet_a` at line 324-325) is not exercised — the test uses equal ship counts.
- **NOT covered:** `JOIN_FLEET` order type matching. The test only uses `MOVE_TO_FLEET`. The code at line 301 also accepts `JOIN_FLEET` but no test exercises this.
- **NOT covered:** Non-pursuit order pass-through (`order_a.type not in _PURSUIT → continue` at line 306). No test verifies that fleets with `MOVE` or other order types are not filtered.
- **NOT covered:** Multiple overlaps / `drop_ids` with multiple fleet pairs. The test has exactly one pair.
- **NOT covered:** `isinstance(fleet_b, Fleet)` guard at line 309 — target is not a Fleet should pass through.

**Overall:** Limited verification exists (1 test for 1 scenario). The report's specific untested-path claims are mostly accurate. The one test that DOES exist covers the tiebreak path the report flagged as untested, but the other paths remain unverified.

---

### MAJOR 5: `calculate_queue_turn_spend` (build_queue_helpers.py) — "Zero unit tests found"

**Verdict: DISPUTED**

**Evidence:** `tests/unit/ui/screens/test_build_queue_helpers.py` — `TestQueueTurnSpend` class (lines 355-589) has **14 tests**:

| Test | Coverage |
|------|----------|
| `test_single_item_gets_full_rate` | Item taking multiple turns gets the full build rate |
| `test_single_item_completes_within_turn` | Item completing in <1 turn shows only remaining |
| `test_multiple_items_all_complete_within_turn` | 3×749 within 3000 capacity |
| `test_bug_98_scenario_five_items` | 5×749: items 1-4 complete, 5 gets remainder (4) |
| `test_bug_98_scenario_six_items` | 6th item gets 0 |
| `test_partially_consumed_first_item` | Uses less capacity for partial items |
| `test_empty_queue` | `[]` returns `[]` |
| `test_zero_rate_blocks_all_items` | All items get 0 spend |
| `test_multi_resource_limiting_resource` | Multi-resource proportional consumption |
| `test_multi_resource_item_completes_mid_turn` | Remaining capacity passes to next item |
| `test_fully_consumed_item_passes_all_capacity` | Complete item passes full capacity |
| `test_missing_rate_for_required_resource` | Missing rate blocks item |
| `test_partial_item_proportional_non_limiting_resources` | BUG-98: non-limiting resources proportionally reduced |
| `test_partial_item_five_resources_proportional` | All 5 resource types proportionally reduced |

**Agent error:** The Phase 2 report asserts "Zero unit tests found" for `calculate_queue_turn_spend` — but the test file `tests/unit/ui/screens/test_build_queue_helpers.py` (which the Phase 2 report's own table correctly lists as one of the test files read) contains exactly these tests. The report explicitly imported `calculate_queue_turn_spend` from the module (line 206-208 of the test file). The Phase 2 discovery agent appears to have not actually read or analyzed the test content despite listing this file.

---

### MAJOR 6: `filter_planets` / effects_predicate — "`test_effects_predicate_mixed_yes_no_composes_and` untested"

**Verdict: DISPUTED**

**Evidence:** `tests/unit/ui/screens/test_planet_list_filters.py:270-290` — `test_yes_and_no_compose_as_and`:

```python
def test_yes_and_no_compose_as_and(self):
    """{Thermal: NO, Shield: YES} → both conditions must hold simultaneously."""
    pred = effects_predicate({
        'EnvironmentalDamage:thermal': FilterState.NO,
        'ShieldModifier': FilterState.YES,
    })
    # only_shield: NO satisfied, YES satisfied → True
    # only_thermal: NO violated → False
    # both: NO violated → False
    # neither: YES violated → False
    assert pred(only_shield) is True
    assert pred(only_thermal) is False
    assert pred(both) is False
    assert pred(neither) is False
```

This directly tests the exact scenario described in the Phase 2 report: mixed YES/NO effect filters composing as AND.

Additionally covered:
- `TestEffectsPredicate` (9 tests): no-ops, YES-only, NO-only, YES+NO AND, IGNORE mixed, EnvironmentalDamage subtype distinction, NO excludes thermal
- `TestFilterPlanetsWithEffects` (1 test): effects AND type compose as AND through `filter_planets` pipeline

---

## Agent Errors (Search / Analysis Failures)

1. **`physics.py` search path error:** Searched `tests/unit/engine/` instead of broader paths. Tests live in `tests/unit/systems/test_physics*.py`.

2. **`fleet_aura_manager.py` file discovery failure:** Found 7 test files in `tests/unit/simulation/combat/test_fleet_aura*.py` when globbing. Phase 2 report claimed none found. The files are unmistakably in the expected directory.

3. **`consumable_management_engine.py` search pattern error:** Searched `tests/unit/strategy/engine/test_consumable*.py` but tests live in `tests/unit/strategy/consumable_management_engine/` (separate directory).

4. **`build_queue_helpers.py` content blindness:** The Phase 2 report correctly found `tests/unit/ui/screens/test_build_queue_helpers.py` (in its own file coverage table) yet reported "Zero unit tests found" for `calculate_queue_turn_spend`. The test file has 14 dedicated tests for this function (lines 355-589). The discovery agent did not read/analyze the test content, despite listing the file.

5. **Summary miscount:** The report header says "Major: 4" but 6 items are tagged `[MAJOR]` in the body (controller `_acquire_targets`, `ConsumableManagementEngine`, `HarvestingEngine._get_harvest_booster_mult`, `FleetMovementEngine._filter_jump_past_collisions`, `calculate_queue_turn_spend`, `filter_planets` effects_predicate).

---

## Overall Assessment

- **2 genuine gaps confirmed** (both MAJOR): `_get_harvest_booster_mult` and partially `_filter_jump_past_collisions`
- **5 claims DISPUTED** due to undiscovered or unanalyzed existing test coverage
- **1 claim PARTIALLY CONFIRMED** with limited existing coverage
- The Phase 2 report's search methodology was systematically flawed: too-narrow directory searches, failure to read test file content after discovery, and incorrect directory path assumptions
