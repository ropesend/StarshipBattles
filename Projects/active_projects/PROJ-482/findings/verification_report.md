# PROJ-482 — Verification Report

**Source audit:** `Reviews/results/2026-05-20_210540_type-audit/`
**Independent re-verification:** 2026-05-22
**This bundle:** Strategy per-finding

## Batch summary
~28 verified / 0 rejected / 1 uncertain (resolved → included) / 3 out-of-scope (user-deferred), out of ~32 strategy candidates.

The audit's own verifier reported 0/5 CRITICAL and 0/5 MAJOR spot-check false positives. The third-pass skeptical verifier opened every CRITICAL and the entire mutator-helper cluster against current source — all confirmed.

## Verified

### CRITICAL (4 = 3 standalone + 1 combined cluster)

| id | file:line | symbol | suggested |
|----|-----------|--------|-----------|
| CRITICAL-02-01 | strategy/engine/commands/order_metadata_view.py:76 | `_registry` (static) | CommandRegistry |
| Shard03-CR | strategy/engine/superweapon_order_processor.py:85 | `_get_nav_service` | FleetNavigationService |
| TYP-04-MR-002 | strategy/data/star_system.py:85 | `primary_star` (property) | Star \| None |
| Combined cluster | strategy/engine/game_session.py:202,217,227,231,236,240,245,249,254,258 | 10 properties (missing return + `# type: ignore`) | EventBus / IFleetMutator×2 / IPlanetMutator×2 / IEmpireMutator×2 / IShipInstanceMutator×2 / CommandRegistry |

### MAJOR (~13)

| id | file:line | symbol | suggested |
|----|-----------|--------|-----------|
| TYP-03-CF-001 | strategy/engine/game_session.py:403 | handle_command | ValidationResult |
| TYP-01-002a | strategy/engine/harvesting_engine.py:196 | _get_planet_mutator | PlanetWriteService |
| TYP-01-002b | strategy/engine/harvesting_engine.py:205 | _get_empire_mutator | EmpireWriteService |
| TYP-01-003a | strategy/engine/order_handlers/base.py:143 | _get_planet_mutator | PlanetWriteService |
| TYP-01-003b | strategy/engine/order_handlers/base.py:152 | _get_ship_mutator | ShipInstanceWriteService |
| MAJOR-02-01 | strategy/engine/environmental_hazard_engine.py:65 | _get_ship_mutator | IShipInstanceMutator |
| Shard03-01 | strategy/engine/planet_modifier_effect_engine.py:34 | _get_planet_mutator | IPlanetMutator |
| Shard03-02 | strategy/engine/production_spawner.py:103 | _get_planet_mutator | IPlanetMutator / PlanetWriteService |
| Shard03-03 | strategy/engine/superweapon_order_processor.py:77 | _get_empire_mutator | IEmpireMutator |
| TYP-01-004 | strategy/engine/handlers/base.py:323 | _resolve_build_entity | Planet \| Fleet \| None |
| TYP-01-005 | strategy/engine/handlers/base.py:377 | _resolve_queue_owner | Planet \| Fleet \| PlanetaryFacility \| None |
| TYP-01-006 | strategy/engine/handlers/base.py:419 | _build_colonize_target | Planet \| dict[str, Any] |
| MAJOR-02-01 | strategy/services/ability_sources/fleet.py:128 | _walk_strategic_abilities | Generator[tuple[str, dict[str, Any]], None, None] |
| Shard03-MR | app_bootstrap.py:310 | _replay_combat_lab_fallback | Ship |
| Shard03-MR | strategy/engine/game_initializer.py:157 | _at_hex (nested gen) | Iterator[Fleet] |
| Shard03-MR | strategy/engine/game_initializer.py:163 | _in_system (nested gen) | Iterator[Fleet] |

### MINOR (~11)

| id | file:line | symbol | suggested |
|----|-----------|--------|-----------|
| TYP-01-007 | strategy/services/planet_write_service.py:125 | pop_construction_item | dict \| None |
| TYP-01-052 | strategy/engine/superweapon_handlers/open_warp_point.py:38 | _precheck closure | SuperweaponResult \| None |
| TYP-01-053 | strategy/engine/superweapon_handlers/open_warp_point.py:54 | _effect closure | dict[str, str] |
| TYP-01-054 | strategy/engine/superweapon_handlers/stellerate_star.py:47 | _precheck | SuperweaponResult \| None |
| TYP-01-055 | strategy/engine/superweapon_handlers/stellerate_star.py:54 | _effect | dict[str, str] |
| Shard02 | strategy/engine/superweapon_handlers/close_warp_point.py:63 | _precheck | SuperweaponResult \| None |
| Shard02 | strategy/engine/superweapon_handlers/close_warp_point.py:75 | _effect | dict |
| TYP-04-MR-003 | strategy/engine/superweapon_handlers/create_dyson_sphere.py:39 | _precheck | SuperweaponResult \| None |
| TYP-04-MR-004 | strategy/engine/superweapon_handlers/create_dyson_sphere.py:51 | _effect | dict |
| TYP-04-MR-005 | strategy/engine/superweapon_handlers/implode_planet.py:39 | _effect | dict |
| TYP-01-056 | strategy/engine/handlers/construction_queue.py:106 | _resolve_design_data | dict \| None |
| `_json_safe` | strategy/services/replay_verification_coordinator.py:104 | _json_safe | str \| int \| float \| bool \| list \| dict \| None |
| TYP-04-024 | strategy/engine/atmosphere_engine.py:30 | _get_planet_mutator | PlanetWriteService |
| Shard03 | strategy/adapters/simulation_adapter.py:488 | _lookup (nested) | Ship |
| Shard03 | strategy/data/deployed_group.py:48-49 | _register_type / deco | Callable[[type], type] / type |
| Shard03 | strategy/systems/design_catalog.py:236 | load_design_data | DesignLoadResult |

## Uncertain (resolved)

| id | file:line | symbol | user decision | location |
|----|-----------|--------|---------------|----------|
| `_build_capture_context` | strategy/adapters/simulation_adapter.py:426 | INCLUDE — add new `ReplayCaptureContext` type | PROJ-482 Phase 3 Task 3.9 |

## Out of Scope (user-deferred)
- `core/formula_evaluator.py:81` `_eval_node` — recursive AST evaluator narrowing
- `strategy/services/strategic_ability_scanner.py:24-77` `find_*` TypedDict refactor
- `strategy/combat/battle_assembly.py:81` `# type: ignore[return-value]` cast alternative
- All justified `# type: ignore` sites in strategy (e.g. `simulation_adapter.py:488` `no-redef`, `deployed_group.py:51` class-decorator `attr-defined`, `issuer_adapter.py:303` `no-any-return`, `pre_tick_setup_registry.py:90` legacy param-count bridge, `save_game_service.py:74,82` duck-typing, `battle_runner.py:182,192` dynamic injection)

## Rejected
None. (Same prior as PROJ-481: zero rejections is flagged as suspicious in `decisions.md`; the audit reviewer's "0/5 CRITICAL false positives" prior held up on third pass.)
