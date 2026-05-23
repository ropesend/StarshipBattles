# PROJ-483 — Verification Report

**Source audit:** `Reviews/results/2026-05-20_210540_type-audit/`
**Independent re-verification:** 2026-05-22
**This bundle:** Foundation per-finding + strict quick wins (research / services / assets / engine / ai / core)

## Batch summary
~31 verified (per-finding + included UNCERTAINs) / 6 strict-mode adoption items / 0 rejected / 5 out-of-scope, out of ~42 Foundation candidates.

## Verified — per-finding

### CRITICAL (1)

| id | file:line | symbol | suggested |
|----|-----------|--------|-----------|
| TYP-04-MR-001 | simulation/entities/stat_contributors/registry.py:298 | `iter_for` (generator) | `Iterator[StatContributorEntry]` (called from `ship_stats.py:307`) |

### MAJOR (~5)

| id | file:line | symbol | suggested |
|----|-----------|--------|-----------|
| TYP-04-001 | simulation/systems/attack_processor.py:142 | `_spawn_from_carried_vehicle` | `Ship \| None` |
| TYP-04-002 | simulation/systems/fighter_reboard.py:294 | `_ensure_overflow_fighter_group` | `FighterWing \| SatelliteConstellation` |
| TYP-04-003 | simulation/systems/fighter_reboard.py:301 | `_ensure_overflow_group` | `FighterWing \| SatelliteConstellation` |
| TYP-01-001 | core/registry.py:248,339 | `get_validator` (method + module-level) | `Optional[Callable[..., Any]]` |
| TYP-01-010 | simulation/components/component_stats_calculator.py:305 | `evaluate_recursive` (nested) | `str \| dict[str, Any] \| list[Any] \| float \| int` |

### MINOR — per-finding (~3)

| id | file:line | symbol | suggested |
|----|-----------|--------|-----------|
| (proto-side of TYP-01-007) | core/protocols/strategy_mutators.py:118 | `IPlanetMutator.pop_construction_item` | `dict \| None` (coordinates with PROJ-482 Phase 3 Task 3.6) |

## Verified — Protocol narrowings (user-opted-in, was UNCERTAIN)

### AI cluster (5)

| file:line | symbol | suggested |
|-----------|--------|-----------|
| ai/interfaces/controllable.py:41 | `IControllable.get_position` | `'Vector2'` |
| ai/interfaces/controllable.py:46 | `IControllable.get_velocity` | `'Vector2'` |
| ai/interfaces/controllable.py:258 | `ShipControllableAdapter.get_position` | `'Vector2'` |
| ai/protocols.py:42 | `IGridEntity.position` | `'Vector2'` |
| ai/protocols.py:75 | `IProjectile.type` | `'AttackType'` |

### Core Protocols cluster (~16, judgment applied per item)

| file:line | symbol | suggested |
|-----------|--------|-----------|
| core/protocols/strategy_entities.py:30 | `IStarSystem.global_location` | `'HexCoord'` |
| core/protocols/strategy_entities.py:64 | `IStar.star_type` | `'StarType'` |
| core/protocols/strategy_entities.py:77 | `IPlanet.planet_type` | `'PlanetType'` (only if enum exists) |
| core/protocols/strategy_entities.py:104 | `IPlanet.location` | `'HexCoord \| None'` |
| core/protocols/strategy_entities.py:115 | `IPlanet.populations` | judgment — if shape known |
| core/protocols/strategy_entities.py:125 | `IPlanet.facilities` | judgment — if shape known |
| core/protocols/strategy_entities.py:250 | `IFleet.location` | `'HexCoord'` |
| core/protocols/strategy_entities.py:290,295,300 | `IFleet.capabilities/.resources/.battle` | judgment per item |
| core/protocols/strategy_entities.py:313 | `IWarpPoint.location` | `'HexCoord'` |
| core/protocols/strategy_entities.py:322,327,331 | `ISectorEnvironment.local_hex/.system/.calculate_radiation` | judgment per item |
| core/protocols/ui.py:62 | `ICamera.position` | `'Vector2'` |
| core/protocols/ui.py:66 | `ICamera.world_to_screen` | accept and return `'Vector2'` |
| core/protocols/ui.py:78 | `ICamera.screen_to_world` | accept and return `'Vector2'` |
| core/protocols/strategy_domain.py:32 | `IEmpire.color` | `tuple[int, int, int]` |
| core/protocols/strategy_domain.py:107 | `IEmpire.built_ship_designs` | `set[str]` |
| simulation/interfaces/entity_protocols.py:88,93 | `ICombatShip.position/.velocity` | `'Vector2'` |
| simulation/interfaces/entity_protocols.py:199,204 | `ICombatShip.resources/.combat_engine` | judgment per item |
| simulation/interfaces/entity_protocols.py:265,270 | `IProjectile.position/.velocity` | `'Vector2'` |
| simulation/interfaces/entity_protocols.py:304 | `IProjectile.type` | `'AttackType'` |

## Verified — strict-mode adoption (6 layers, Phase 4)

| Layer | Audit estimate | Verifier-measured | Plan |
|-------|---------------|-------------------|------|
| research | 0 | 0 | config-only enable |
| services | 0 (READY) | 1 (likely env stub) | investigate + enable |
| assets | 0 (READY) | 15 | fix 15 errors + enable |
| engine | ~5 | 14 | fix 14 errors + enable |
| ai | ~54 | 60 (drops after Phase 3) | fix remainder + enable |
| core | ~85 | 116 (drops after Phase 3) | fix remainder + enable |

## Out of Scope

| id | file:line | reason |
|----|-----------|--------|
| `load_json` | core/json_utils.py:79 | JSON inherently returns `Any` |
| `load_json_required` | core/json_utils.py:119 | same |
| `ILocatable.location` | core/protocols/common.py:27 | intentional cross-coordinate-system duck-typing seam |
| `IResourceHolder.resources` | core/protocols/boundary.py:92 | documented cross-layer seam |
| (sim entity proto subset — overlaps with Phase 3 judgment list) | various | mirror core duck-typing pattern; the rest of the cluster IS in scope |
| `core/formula_evaluator.py:81` `_eval_node` | recursive AST evaluator narrowing | user-deferred |
| sim/strategy/ui mypy `--strict` adoption | layer-scoped | DEFERRED — verifier counts 622/1070/2571 are multi-week dedicated work |

## Uncertain (resolved)
All UNCERTAIN items in this bundle were resolved via Phase D Step 2/3 user opt-in:
- 16 Protocol narrowings → INCLUDE (with TYPE_CHECKING string annotations)
- 5 AI controllable/protocol narrowings → INCLUDE

## Rejected
None. (Same prior as siblings: zero rejections is flagged as suspicious in `decisions.md`; the audit reviewer's "0/5 CRITICAL false positives" prior held up on third pass.)
