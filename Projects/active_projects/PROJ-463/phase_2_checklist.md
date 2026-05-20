# Phase 2: Major (Any narrowing + ignore removal + missing returns)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-463 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Narrow the verified MAJOR domain `-> Any` returns, remove unjustified type-ignores, add the missing public/boundary return annotations, and fix the domain-layer implicit-Optional violations.

---

## Tasks

### Task 2.1: Add targeting-system None-guards [Simple]
**File:** `game/simulation/combat/targeting_system.py`
**Tests:** `pytest tests/ --testmon` and `mypy game/simulation/combat/targeting_system.py`

- [ ] Add None guard for `seeker_ab` before line 199 (`.projectile_speed * .endurance`) and for `proj_ab` before line 304
- [ ] Guard `beam_ab` from `get_ability('BeamWeaponAbility')` before passing to `_get_pdc_valid_targets` (lines 188-189)
- [ ] Verify: pytest passes; `mypy game/simulation/combat/targeting_system.py` shows no new errors

### Task 2.2: Narrow resource-manager ability subtype [Medium]
**File:** `game/simulation/components/component_resource_manager.py`
**Tests:** `pytest tests/ --testmon` and `mypy game/simulation/components/component_resource_manager.py`

- [ ] At lines 50, 62, narrow `get_abilities('ResourceConsumption')` results to `ResourceConsumption` (cast or typed helper) so `.trigger`/`.check_available()`/`.check_and_consume()` are defined; or declare those members on the appropriate protocol
- [ ] Verify: pytest passes; `mypy game/simulation/components/component_resource_manager.py` shows no new errors

### Task 2.3: Narrow ability + simulation protocol Any returns [Medium]
**File:** `game/simulation/components/abilities/base.py`
**Tests:** `pytest tests/ --testmon` and `mypy game/simulation/components/abilities/base.py game/simulation/interfaces/entity_protocols.py game/simulation/interfaces/ai_controller.py game/simulation/components/component_stats_calculator.py`

- [ ] Narrow `Ability.get_effective_stat` (base.py:258) from `-> Any` to `-> float | int | None`
- [ ] Narrow `entity_protocols.py` ICombatShip/IProjectile props (lines 88,93,199,204,265,270,304) to concrete types (`Vector2`/`str`/`dict[str,float]`) via TYPE_CHECKING imports (sim-concrete, narrowable)
- [ ] Narrow `IAIController.ship` (ai_controller.py:49) to `Ship` under TYPE_CHECKING
- [ ] Narrow `evaluate_recursive` (component_stats_calculator.py:305) to a `FormulaResult` recursive union
- [ ] Verify: pytest passes; mypy shows no new errors on the touched files

### Task 2.4: Narrow AI controllable adapter [Medium]
**File:** `game/ai/interfaces/controllable.py`
**Tests:** `pytest tests/ --testmon` and `mypy game/ai/interfaces/controllable.py`

- [ ] Narrow `ShipControllableAdapter.ship` (line 239) from `-> Any` to `ICombatShip` (or `Ship`)
- [ ] Narrow the ~16 delegating methods (lines 268-392) returning `-> Any` to their declared concrete types (`float`/`bool`/`int`/`str`) — resolves 24 `no-any-return` errors
- [ ] Verify: pytest passes; `mypy game/ai/interfaces/controllable.py` shows no new errors

### Task 2.5: Narrow strategy engine lazy-default mutator getters [Medium]
**File:** `game/strategy/engine/order_handlers/base.py`
**Tests:** `pytest tests/ --testmon` and `mypy game/strategy/engine/`

- [ ] Narrow `_get_planet_mutator`/`_get_empire_mutator`/`_get_ship_mutator` `-> Any` to `IPlanetMutator`/`IEmpireMutator`/`IShipInstanceMutator` at the 9 sites: `atmosphere_engine.py:30`, `harvesting_engine.py:196,205`, `planet_modifier_effect_engine.py:34`, `production_spawner.py:103`, `superweapon_order_processor.py:77`, `order_handlers/base.py:143,152`, `environmental_hazard_engine.py:65`
- [ ] Verify: pytest passes; `mypy game/strategy/engine/` shows no new errors on these files

### Task 2.6: Narrow strategy engine command/turn returns [Medium]
**File:** `game/strategy/engine/game_session.py`
**Tests:** `pytest tests/ --testmon` and `mypy game/strategy/engine/game_session.py game/strategy/engine/turn_engine.py game/strategy/engine/handlers/base.py`

- [ ] Narrow `GameSession.handle_command` (game_session.py:403) from `(command: Any) -> Any` to `(command: Command) -> ValidationResult`
- [ ] Narrow `TurnEngine._time_phase` (turn_engine.py:286) from `-> Any` to a known union (or `object | None`)
- [ ] Narrow `BaseCommandHandler._resolve_build_entity`/`_resolve_queue_owner` (handlers/base.py:323,377) from `-> Any` to concrete entity types
- [ ] Verify: pytest passes; mypy shows no new errors on the touched files

### Task 2.7: Add design-catalog + missing public return types [Simple]
**File:** `game/strategy/systems/design_catalog.py`
**Tests:** `pytest tests/ --testmon` and `mypy <touched files>`

- [ ] Add `-> DesignLoadResult` to `DesignCatalog.load_design_data` (design_catalog.py:236)
- [ ] Add return types to superweapon handler `_precheck`/`_effect` functions: `create_dyson_sphere.py:39,51`, `close_warp_point.py:63,75`, `open_warp_point.py:38,54`, `implode_planet.py:39`, `stellerate_star.py:47,54` (`-> SuperweaponResult | None` / `-> bool`)
- [ ] Add return types to other flagged domain public/boundary functions: `stat_contributors/registry.py:298` (`-> Generator[...]`), `star_system.py:85` primary_star (`-> Star | None`), `game_initializer.py:157,163` generators, `ability_sources/fleet.py:128` generator, `workshop_viewmodel.py:129`, `construction_queue.py:106`
- [ ] Verify: pytest passes; mypy shows no new errors on the touched files

### Task 2.8: Remove unjustified type-ignores / declare attributes [Medium]
**File:** `game/simulation/battle_runner.py`
**Tests:** `pytest tests/ --testmon` and `mypy <touched files>`

- [ ] Declare `replay_id: str | None = None` on `BattleEngine.__init__` and remove `# type: ignore[attr-defined]` at battle_runner.py:182,192
- [ ] Declare `launched_in_battle_id` on `Ship` and remove ignore at `attack_processor.py:123`
- [ ] Add `set_save_root`/`clear_save_root` to the replay-store protocol and remove ignores at `save_game_service.py:74,82`
- [ ] Remove unjustified `# type: ignore[no-redef]` at `simulation_adapter.py:488` and add the missing return annotation on `_lookup`
- [ ] Remove unjustified `# type: ignore[return-value]` at `battle_assembly.py:81`
- [ ] Narrow `issuer_adapter.py:301-303` `getattr` fallback with an `isinstance(HexCoord)` guard and remove `# type: ignore[no-any-return]`
- [ ] Verify: pytest passes; mypy shows no new errors on the touched files

### Task 2.9: Fix domain implicit-Optional violations [Simple]
**File:** `game/simulation/components/abilities/weapons.py` (+ siblings)
**Tests:** `pytest tests/ --testmon` and `mypy <touched files>`

- [ ] Fix `Type = None` → `Type | None = None` at: `weapons.py:17`, `galaxy_layouts_loader.py:36,168`, `star_generator.py:60`, `handlers/base.py:119,166`, `component_stats_calculator.py:125,207,329`, `damage_calculator.py:41`, `transfer_validator.py:92,94,190,222,223,319,320,347,403`, `battle_logger.py:23`
- [ ] Verify: pytest passes; mypy shows no new errors on the touched files

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-19_223900_type-audit/`. See `findings/source_audit.md` for the link._
