# Verification Report — PROJ-463 (domain)

- **Source audit:** `Reviews/results/2026-05-19_223900_type-audit/`
- **Run date:** 2026-05-19 (independent third pass by Claude against live source)
- **Batch summary (whole audit):** 51 verified / 1 rejected / 2 uncertain (resolved) / 0 out-of-scope, out of a 53-item normalized candidate set drawn from ~250 audit findings.

This report covers the domain bundle. The Rejected and Uncertain sections are the audit-wide results (identical narrative across siblings); the Verified table is domain-specific.

## Verified (this bundle)

| id | file | symbol | current | suggested |
|----|------|--------|---------|-----------|
| TYP-A01 | game/simulation/combat/families/seeker.py:38,52,68-76 | SeekerHandler.fire | seeker_ab `Ability \| None` deref'd | add None guard |
| TYP-GS | game/strategy/engine/game_session.py:202..258 | 10 mutator/service properties | `# type: ignore[no-untyped-def]` | `-> IFleetMutator/IPlanetMutator/IEmpireMutator/IShipInstanceMutator/EventBus/CommandRegistry` |
| TYP-A02 | game/simulation/combat/targeting_system.py:188-189,199,304 | find_valid_target/firing_solution | `Ability \| None` deref'd | add None guard |
| TYP-A04 | game/simulation/components/component_resource_manager.py:50,62 | can_afford/consume_activation | `.trigger`/`.check_*` on base Ability | narrow to ResourceConsumption |
| TYP-GES | game/simulation/components/abilities/base.py:258 | get_effective_stat | `-> Any` | `-> float \| int \| None` |
| TYP-SIMPROTO | game/simulation/interfaces/entity_protocols.py:88,93,199,204,265,270,304 | ICombatShip/IProjectile props | `-> Any` | Vector2/str/dict (TYPE_CHECKING) |
| TYP-AIPROTO | game/simulation/interfaces/ai_controller.py:49 | IAIController.ship | `-> Any` | `-> Ship` (TYPE_CHECKING) |
| TYP-CRM | game/simulation/components/component_stats_calculator.py:305 | evaluate_recursive | `-> Any` | FormulaResult recursive union |
| TYP-CTRL | game/ai/interfaces/controllable.py:239,268-392 | ShipControllableAdapter | `-> Any` (24 no-any-return) | ICombatShip/float/bool/int/str |
| TYP-FLOW1 | 9 sites / 6 strategy engine files | _get_*_mutator | `-> Any` | IPlanet/IEmpire/IShipInstance Mutator |
| TYP-HCMD | game/strategy/engine/game_session.py:403 | handle_command | `(command: Any) -> Any` | `(command: Command) -> ValidationResult` |
| TYP-TPHASE | game/strategy/engine/turn_engine.py:286 | _time_phase | `-> Any` | union / object \| None |
| TYP-BASEH | game/strategy/engine/handlers/base.py:323,377 | _resolve_build_entity/_resolve_queue_owner | `-> Any` | concrete entity types |
| TYP-DCAT | game/strategy/systems/design_catalog.py:236 | load_design_data | no return annotation | `-> DesignLoadResult` |
| TYP-SWHANDLERS | 5 superweapon_handlers files | _precheck/_effect | no return annotation | `-> SuperweaponResult \| None` / `-> bool` |
| TYP-MISC-MR | stat_contributors/registry:298, star_system:85, game_initializer:157,163, ability_sources/fleet:128, workshop_viewmodel:129, construction_queue:106 | various public/boundary fns | no return annotation | concrete per audit |
| TYP-IGN-BR | game/simulation/battle_runner.py:182,192 | engine.replay_id | `# type: ignore[attr-defined]` | declare `replay_id: str \| None` on BattleEngine |
| TYP-IGN-AP | game/simulation/systems/attack_processor.py:123 | launched_in_battle_id | `# type: ignore[attr-defined]` | declare on Ship |
| TYP-IGN-SAVE | game/strategy/systems/save_game_service.py:74,82 | set/clear_save_root | `# type: ignore[attr-defined]` | add to replay-store protocol |
| TYP-IGN-SIMADP | game/strategy/adapters/simulation_adapter.py:488 | _lookup | `# type: ignore[no-redef]` (unjustified) | remove ignore + add return type |
| TYP-IGN-BA | game/strategy/combat/battle_assembly.py:81 | tuple(float(v)...) | `# type: ignore[return-value]` (unjustified) | remove ignore |
| TYP-ISSUER | game/strategy/engine/issuer_adapter.py:301-303 | return gh | `# type: ignore[no-any-return]` | isinstance(HexCoord) guard |
| TYP-PIMPL2 (domain part) | weapons.py:17, galaxy_layouts_loader, star_generator, damage_calculator, transfer_validator, battle_logger, component_stats_calculator, handlers/base | implicit Optional params | `Type = None` | `Type \| None = None` |
| STRICT-ai | game/ai/ | — (layer) | est. ~40 errors | adopt `--strict` |
| STRICT-simulation | game/simulation/ | — (layer) | est. ~417 errors | adopt `--strict` |
| STRICT-strategy | game/strategy/ | — (layer) | est. ~452 errors | adopt `--strict` |

Note on strict-migration counts: per-layer numbers are audit estimates (its scanner attributed errors by path; `mypy <path>` follows imports). Aggregate re-run: 2,269 errors / 325 files, consistent with the audit's 2,108 real errors. Confirm per-layer counts at task start. No layer is at zero.

(`TYP-PIMPL2` and `TYP-MISC-MR` are multi-layer findings; only their simulation/strategy/ai sites are in this bundle. Core/UI/top-level sites are in PROJ-462/PROJ-464.)

## Rejected (audit-wide)

| id | original audit recommendation | contrary evidence | rationale |
|----|-------------------------------|-------------------|-----------|
| TYP-APP | Narrow `game/app.py` Game scene accessor properties from `-> Any` to `-> IScene` | `game/app.py:198-233` route through `_route_get`; Shard 04 minor#5 rates acceptable | Scene proxies are intentionally loose for `Game.__new__(Game)` tests; narrowing breaks mocks. Separate hardening question. Codex concurred. |

## Uncertain (resolved)

| id | verifier question | decision |
|----|-------------------|----------|
| TYP-COREPROTO | Some core protocol Any narrowable, but position/location seams must stay Any | **INCLUDE (PROJ-462)** with boundary-preserving carve-out. Not in this bundle. |
| TYP-SR | StrategyRenderer props: narrowable vs acceptable; MagicMock-scene tests | **INCLUDE (PROJ-464)** as a renderer-scene Protocol seam cleanup. Not in this bundle. |

## Out of Scope

None promoted. Justified ignores were already excluded by the audit's `findings/verification.md` and never entered the candidate set.
