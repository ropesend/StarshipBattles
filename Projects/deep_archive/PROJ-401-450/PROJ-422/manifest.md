# PROJ-422 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.
>
> Derived from [TD-09_engine_interface_split.md](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/TD-09_engine_interface_split.md) §"Concrete File Touch Plan".

## Files

### Production — deleted

| File | Type | Notes |
|------|------|-------|
| `game/strategy/interfaces/engines.py` | Production | Delete after Phase 1 split. 778 LOC, 18 ABCs — replaced by the new `engines/` package. Root-cause removal per AGENTS.md (no parallel old + new path). |

### Production — added

| File | Type | Notes |
|------|------|-------|
| `game/strategy/interfaces/engines/__init__.py` | Production (new) | Explicit re-exports of all 18 ABCs from the 9 leaf modules. Declarative `__all__` sorted by domain. Public seam — not a compat shim. |
| `game/strategy/interfaces/engines/movement.py` | Production (new) | `IMovementEngine` (~85 LOC) — fleet movement collection, application, pathfinding. |
| `game/strategy/interfaces/engines/orders.py` | Production (new) | `IOrderProcessor`, `IActionExecutionEngine` (~125 LOC) — instant orders + tick-based action progress driver (PROJ-187). |
| `game/strategy/interfaces/engines/combat.py` | Production (new) | `IConflictEngine`, `IEnvironmentalHazardEngine` (~100 LOC) — multi-empire combat + storm ticks (PROJ-189). |
| `game/strategy/interfaces/engines/production.py` | Production (new) | `IProductionEngine` (~50 LOC) — per-tick construction (PROJ-75/79/158). |
| `game/strategy/interfaces/engines/logistics.py` | Production (new) | `IConsumableEngine`, `IResupplyEngine`, `IHarvestingEngine` (~140 LOC) — per-turn consumption, fuel generation + fleet resupply (PROJ-74), per-tick harvesting (PROJ-75/161). Largest leaf; still well under 200 LOC. |
| `game/strategy/interfaces/engines/population.py` | Production (new) | `IPopulationEngine`, `IOrganicsConsumptionEngine`, `IHappinessEngine` (~125 LOC) — logistic growth, multi-resource upkeep (PROJ-284/286), happiness derivation (PROJ-284). |
| `game/strategy/interfaces/engines/planet_ops.py` | Production (new) | `IPlanetEnergyEngine`, `IPlanetActionEngine` (~80 LOC) — per-tick energy gen/consume + planet order ticks (PROJ-237). |
| `game/strategy/interfaces/engines/terraforming.py` | Production (new) | `IQualityEngine`, `IAtmosphereEngine`, `IWaterEngine` (~70 LOC) — PROJ-369 trio. |
| `game/strategy/interfaces/engines/components.py` | Production (new) | `IComponentActivationEngine` (~35 LOC) — activation timer ticks. Was missing from `engines.__all__`; added here. |

### Production — modified

| File | Type | Notes |
|------|------|-------|
| `game/strategy/interfaces/__init__.py` | Production (rewrite) | Re-export every ABC the engines package exposes. Currently re-exports 13 of 18; adds the 5 missing: `IOrganicsConsumptionEngine`, `IHappinessEngine`, `IQualityEngine`, `IAtmosphereEngine`, `IWaterEngine`. Updates `__all__` accordingly. |

### Production — NOT touched (verified)

| File | Type | Notes |
|------|------|-------|
| `game/strategy/engine/turn_engine_config.py` | Production | No symbolic dependency — every engine field is `Optional[Any]`; `create_default()` imports concrete classes only. Split does not affect runtime contract. |
| `game/strategy/engine/turn_phase_registry.py` | Production | No ABC import — uses concrete engines directly. |
| `game/strategy/interfaces/battle_resolver.py` | Production | Already separate from `engines.py`. |
| All 14 concrete engine modules under `game/strategy/engine/` | Production | Each imports its paired ABC via `from game.strategy.interfaces.engines import I<Name>` — that path remains valid via the package `__init__.py` re-export. No edits needed. |
| `game/strategy/engine/turn_engine.py` (lines 102-121, TYPE_CHECKING block) | Production | Imports ABCs via the package path; the re-export keeps it valid. No edits needed. If this turns out to need edits, the split design is wrong — stop and reassess. |

### Test — added

| File | Type | Notes |
|------|------|-------|
| `tests/unit/strategy/interfaces/test_engines_package_layout.py` | Test (new) | ~6 small tests authored in Phase 0 (red), green after Phase 1. Asserts: `engines` is a package (`__path__` exists); each leaf module loads; each ABC importable from the package root; each leaf's `__all__` matches the layout table verbatim; every name in `engines.__all__` also in `game.strategy.interfaces.__all__`; no leftover `engines.py` module file. |

### Test — NOT modified (verified by import-site sweep)

| File | Type | Notes |
|------|------|-------|
| `tests/unit/strategy/mocks/mock_engines.py` | Test | Imports `IMovementEngine`, `IProductionEngine`, `IOrderProcessor`, `IConflictEngine`, `IConsumableEngine` via package path — re-export keeps it valid. |
| `tests/integration/strategy/test_economy_e2e.py` | Test | Imports `IPopulationEngine` via package path. |
| `tests/unit/strategy/turn_engine/test_turn_snapshot_capture_failure.py` | Test | Imports `IOrganicsConsumptionEngine`. |
| `tests/unit/strategy/turn_engine/test_turn_engine_phase_timing.py` | Test | ABC import on line 223. |
| `tests/unit/strategy/turn_engine/test_turn_engine_phase_320_movement_diff.py` | Test | ABC import on line 22. |
| `tests/unit/strategy/turn_engine/test_turn_engine_init_precedence.py` | Test | `IMovementEngine` import on line 17. |
| `tests/unit/strategy/turn_engine/test_turn_engine_end_of_turn_order.py` | Test | ABC import on line 34. |
| `tests/unit/strategy/turn_engine/test_turn_end_of_turn_engine_rollback.py` | Test | ABC import on line 29. |
| `tests/unit/strategy/turn_engine/test_dependency_injection.py` | Test | ABC imports on lines 181, 190, 199, 208, 217, 237, 262, 297. |
| `tests/unit/strategy/turn_engine/test_default_tick_phase_list.py` | Test | ABC import on line 25. |

(All test files keep their existing import line untouched — that is the whole point of the re-export seam. If any test file is found to need editing, stop and prove with a failing test that the seam is insufficient.)

### Docs — likely candidates (Phase 4 sync)

| File | Type | Notes |
|------|------|-------|
| `docs/systems/strategy_layer.md` | Docs | Likely references `engines.py` as a single file; update to package layout. |
| `docs/architecture/*.md` (any page listing the engine interface count) | Docs | Update if it cites "778 LOC engines.py" or similar. Grep during Phase 0 surfaces candidates. |

(`docs/_ignore/` is the user's scratch space — leave it alone per AGENTS.md.)
