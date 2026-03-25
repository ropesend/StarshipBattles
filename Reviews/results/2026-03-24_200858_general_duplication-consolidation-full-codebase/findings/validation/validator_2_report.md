# Validation Report: Validator 2

## Summary
- **Findings Reviewed:** 28
- **Confirmed:** 15
- **Downgraded:** 9
- **Rejected:** 4
- **Rejection Rate:** 14.3%

## Verdicts

#### Finding: DUP-CMP-001
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** ToHitAttackModifier and ToHitDefenseModifier (defense.py lines 53-97) are structurally identical: same __init__, same empty recalculate, same get_primary_value. Only differences are UI label string ('Targeting' vs 'Evasion') and color hint. A parameterized base class would eliminate the duplication.

#### Finding: DUP-CMP-002
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** EmissiveArmor (lines 100-117) shares the same structural pattern as ToHitAttackModifier/ToHitDefenseModifier but has a meaningful semantic difference: it uses `int()` cast on the value and stores it as `amount` instead of `value`. The duplication is real but less than between the two ToHit classes. Downgraded because the behavioral divergence is non-trivial.

#### Finding: DUP-CMP-003
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** ResourceConsumption, ResourceStorage, and ResourceGeneration share the pattern of parsing resource_type/amount from dict-or-scalar in both __init__ and sync_data, plus storing a _base value. However, the classes have significantly different behavior beyond this boilerplate (consumption has triggers, update logic, check_and_consume; generation has rate semantics). The shared boilerplate is ~10 lines per class. This is a minor code smell, not a major duplication issue.

#### Finding: DUP-CMP-004
**Original Severity:** Minor
**Verdict:** REJECTED
**Reason:** The file `game/simulation/components/stat_keys.py` does not exist. The `get_default_stat_multipliers()` function lives only in `modifiers.py` (line 120). There is no duplicate default stats dictionary in a separate stat_keys.py file. The finding references a non-existent file.

#### Finding: DUP-CMP-005
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** WeaponAbility.__init__ (lines 51-110) and sync_data (lines 112-147) both parse damage/range/reload with the same formula-detection logic (`isinstance(raw, str) and raw.startswith('=')` then `safe_evaluate_math_formula`). The parsing pattern is repeated 3 times in __init__ and 3 times in sync_data for the same three fields.

#### Finding: DUP-CMP-006
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** CargoStorage (cargo.py) follows the same pattern as ResourceStorage (resources.py): stores a type string + capacity float, has CAPACITY_MULT stat binding, identical sync_data structure (dict-or-scalar), same recalculate pattern using `get_effective_stat('capacity_mult', 1.0)`. The structural similarity is clear.

#### Finding: DUP-CMP-007
**Original Severity:** Minor
**Verdict:** DOWNGRADED(Trivial)
**Reason:** EmpireStorageAbility (harvester.py) stores resource_type + capacity and has a _base_capacity, superficially similar to ResourceStorage/CargoStorage. However, it exists in a completely different domain (planetary complexes vs ship components), uses a different stat key ('storage_mult' vs 'capacity_mult'), and has no sync_data method. The pattern overlap is natural for "thing that stores stuff" and not worth consolidating across domains.

#### Finding: DUP-CMP-008
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** `apply_modifier_effects` (modifiers.py lines 51-117) reimplements the same operation-dispatch logic that `_apply_effect_to_dict` (lines 15-48) encapsulates. The main function has inline multiply/add_to_mult/add/set branches (lines 85-117) that duplicate the helper's logic, with minor differences for edge cases (checking isinstance, special-casing stat keys). The targeted-ability path correctly uses `_apply_effect_to_dict`, but the global path duplicates it.

#### Finding: DUP-SIM-001
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** ShipPhysicsMixin.update_physics_movement (ship_physics.py lines 29-34) recalculates `current_accel = (thrust * K_THRUST) / (mass * mass)` and `potential_max_speed = (thrust * K_SPEED) / mass` every tick. ShipStatsCalculator._phase_physics_and_limits (ship_stats.py lines 237-241) computes the same formulas: `acceleration_rate = (thrust * K_THRUST) / (mass * mass)` and `max_speed = (thrust * K_SPEED) / mass`. The physics mixin intentionally recomputes from current operational thrust (dynamic), while stats calculator uses total thrust (design-time), so the duplication is architecturally intentional but the formulas are indeed duplicated.

#### Finding: DUP-SIM-002
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Ship.__init__ (lines 78-88) and Ship.change_class (lines 466-476) both contain identical hull auto-equip logic: get default_hull_id from class_def, create_component, append to HULL layer, set layer_assigned and ship reference. The code is copy-pasted between the two methods.

#### Finding: DUP-SIM-003
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Ship.add_component (lines 502-531) and Ship.add_components_bulk (lines 538-576) share nearly identical boilerplate: validate_addition call, append to layer, set layer_assigned/ship, recalculate_stats, late-import ModifierService, create service with registries, ensure_mandatory_modifiers. The bulk method clones and loops but duplicates all the per-component setup logic.

#### Finding: DUP-SIM-004
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** `_has_attrs` is defined identically in both `ability_protocols.py` (line 315) and `entity_protocols.py` (line 480). Both are `def _has_attrs(obj, *attrs): return all(hasattr(obj, attr) for attr in attrs)`. This is a private helper duplicated across two files in the same package.

#### Finding: DUP-SIM-005
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** `max_mass_budget` is looked up from `vehicle_classes` in three places in ship_stats.py: line 396 in `_phase_resource_allocation`, line 479 in `_check_mass_limits` (which resets it to 1000 first), and line 482 which looks it up again. The _check_mass_limits method even overwrites the value that _phase_resource_allocation already set.

#### Finding: DUP-SIM-006
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Ship has both `get_ability_total` (line 617, delegates to stat_querier which uses calculate_ability_totals with stack_group rules) and `get_total_ability_value` (line 621, delegates to stat_querier which sums get_primary_value()). These are two different aggregation APIs with overlapping but subtly different semantics (stack groups vs simple sum). The overlap creates confusion about which to use.

#### Finding: DUP-SIM-007
**Original Severity:** Minor
**Verdict:** DOWNGRADED(Trivial)
**Reason:** Ship.cached_summary (line 534) returns `self._cached_summary`. ShipStatQuerier.cached_summary (line 144) returns `self._ship._cached_summary`. The querier property is a trivial passthrough to the same underlying data. This is the standard facade/delegate pattern used throughout the codebase, not problematic duplication.

#### Finding: DUP-SIM-008
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** ShipValidatorHelper calls `validate_design` in three separate methods: check_validity (line 44), get_validation_warnings (line 55), and get_missing_requirements (line 64). Each creates the validator and runs validate_design independently. If a caller invokes all three, the same validation runs three times.

#### Finding: DUP-SIM-009
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Ship.add_component (lines 521-525) and Ship.add_components_bulk (lines 566-570) both contain the same late import + service creation pattern: `from game.simulation.services.modifier_service import ModifierService` followed by `service = ModifierService(modifier_registry=self._registries.modifiers)`. In the bulk method, this import and instantiation happens inside a loop, creating a new service instance per component.

#### Finding: DUP-SIM-010
**Original Severity:** Minor
**Verdict:** DOWNGRADED(Trivial)
**Reason:** Ship.layers_dict (lines 801-815) serializes layers with component IDs and modifiers. ShipSerializer.to_dict (ship_serialization.py) also serializes layers with component IDs and modifiers. However, layers_dict is a lightweight helper property while ShipSerializer.to_dict is the full serialization method that includes additional fields, skips HULL layer, and filters hull_ components. They serve different purposes and the overlap is partial.

#### Finding: DUP-SYS-001
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** BattleController delegates query methods (is_battle_over, get_winner, get_all_ships, get_alive_ships) to BattleService, which in turn delegates to BattleEngine. This is a standard three-layer architecture pattern (Controller -> Service -> Engine), not problematic duplication. Each layer adds value: Controller adds state checks and retreat handling, Service adds null-safety guards for engine. This is the facade/delegate pattern explicitly endorsed by the codebase's architecture docs.

#### Finding: DUP-SYS-002
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** BattleController.run_ticks (lines 287-310) and BattleService.run_ticks (lines 239-264) both implement the same loop: iterate count times, check is_battle_over(), call update/engine.update(). The Controller version adds retreat handling, but the core loop structure is duplicated. The Controller should delegate to the Service rather than reimplementing the loop.

#### Finding: DUP-SYS-003
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** `game/core/config.py::BattleConfig` (line 111) is a constants-only class holding static configuration values (TARGET_QUERY_RADIUS, COLLISION_BUFFER, etc.). `game/simulation/battle_config.py::BattleConfig` (line 27) is a dataclass holding per-battle instance configuration (mode, seed, max_ticks). They serve completely different purposes despite sharing a name. The naming collision is confusing but there is no actual functional duplication. The real issue is the name conflict, not duplicated logic.

#### Finding: DUP-SYS-004
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** BattleEngine.is_battle_over (lines 520-530) counts team1_alive and team2_alive using `sum(1 for s in self.ships if s.team_id == X and s.is_alive ...)`. BattleEngine.get_winner (lines 635-641) performs the identical counting: `sum(1 for s in self.ships if s.team_id == X and s.is_alive)`. The alive-counting logic is duplicated between these two methods in the same class.

#### Finding: DUP-SYS-005
**Original Severity:** Minor
**Verdict:** REJECTED
**Reason:** The finding claims "repeated DI guard clause boilerplate" across multiple files. While Ship.__init__ does have a registries-None check, this is a standard validation pattern. The DI guard is a one-liner in each class and is not meaningfully duplicable -- each class validates its own specific required dependencies. This is not duplication; it is standard defensive programming.

#### Finding: DUP-SYS-006
**Original Severity:** Minor
**Verdict:** REJECTED
**Reason:** BattleStateManager (battle_state_manager.py) does not contain any list/tuple format validation logic. The class has capture_state, restore_config_from_state, extract_ships_from_state, and validate_state methods, none of which perform list/tuple format validation. The finding does not match the actual code.

#### Finding: DUP-SYS-007
**Original Severity:** Minor
**Verdict:** DOWNGRADED(Minor)
**Reason:** BattleController.save_state (line 450) delegates to `self._state_manager.capture_state(engine, config)`. BattleController.start (line 206) calls `BattleState.capture_from_engine(engine, ...)` directly. The state_manager.capture_state itself calls BattleState.capture_from_engine. So there are two code paths that call capture_from_engine: start() calls it directly, while save_state() goes through the manager. This is a minor inconsistency rather than duplication -- start() should arguably use the state manager too.

#### Finding: DUP-SYS-008
**Original Severity:** Minor
**Verdict:** DOWNGRADED(Trivial)
**Reason:** BattleService has "No active battle" checks in multiple methods (add_ship, remove_ship, update, run_ticks, etc.), each checking `self._engine is None`. This is standard guard-clause programming in a stateful service. Each method needs its own guard because it may be called independently. This is not consolidatable duplication.

#### Finding: DUP-SYS-009
**Original Severity:** Minor
**Verdict:** REJECTED
**Reason:** BattleController.run_headless has a safety limit `if tick >= max_ticks: break` (line 281). BattleEngine.is_battle_over checks `self.tick_counter >= self.end_condition.absolute_max_ticks` (line 505). These are different limits: max_ticks is the user-configured battle duration, while absolute_max_ticks is a safety ceiling (default 1M ticks). The Controller's check uses config.max_ticks which is the intended duration, not the safety ceiling. They serve different purposes and are not duplicates.

#### Finding: DUP-SD-01
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** `generate_from_blueprint` (lines 445-550) and `_generate_random_stars` (lines 552-625) share extensive duplicated logic: both generate a primary star with the same pattern (generate mass, determine type/radius, map to hex, generate spectrum, create Star object at HexCoord(0,0)), then generate companions with identical placement logic (hex_ring, occupied_hexes check, while-loop retry). The companion generation loop (lines 514-548 vs 591-623) is nearly line-for-line identical. Only the mass generation method differs (constrained vs unconstrained).


