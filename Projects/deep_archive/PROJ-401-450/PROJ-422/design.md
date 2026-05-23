# PROJ-422: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.
>
> **Canonical source:** [TD-09_engine_interface_split.md](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/TD-09_engine_interface_split.md). This file distills that plan; if the two diverge, the TD plan wins.

## Verification Evidence (already verified before scaffold)

The source plan was independently verified before reaching this project. Key reproduced numbers:

| Metric | Confirmed value | Source check |
|---|---|---|
| `engines.py` LOC | **778** (over the 500 ceiling by 56%) | `wc -l game/strategy/interfaces/engines.py` |
| ABC count | **18** (report claimed 17; `IComponentActivationEngine` missing from `__all__` is an existing drift bug) | Inventory walk |
| Domains spanned | **9** (movement, orders, combat, production, logistics, population, planet ops, terraforming, components) | Inventory walk |
| Total consumer import sites | **30** (production + tests + mocks) | rg sweep |
| `TurnEngineConfig` symbolic dependency on these ABCs | **none** — every engine field is `Optional[Any]`; `create_default()` imports concrete classes only | Direct inspection of `turn_engine_config.py` |
| TurnEngine ABC imports | **TYPE_CHECKING only** (`turn_engine.py:102-121`) | Direct inspection |

**Verdict:** the split is mechanical and symbol-preserving. The file is unambiguously over the 500-LOC ceiling, spans unrelated domains, and `__all__` is already drifting. The TD plan's remediation — split by domain, re-export minimal seam — is the correct fix.

## Goal / End State (target architecture)

Convert `engines.py` into a package at `game/strategy/interfaces/engines/`. Each leaf module owns one domain's ABCs and ends well under 200 LOC. The package `__init__.py` re-exports every ABC so existing `from game.strategy.interfaces.engines import I<Name>` continues to work for all 30 consumers without forcing a rename pass.

```
game/strategy/interfaces/engines/
    __init__.py                # explicit re-exports, declarative __all__ of 18 names
    movement.py                # IMovementEngine                                                   (~85 LOC)
    orders.py                  # IOrderProcessor, IActionExecutionEngine                           (~125 LOC)
    combat.py                  # IConflictEngine, IEnvironmentalHazardEngine                       (~100 LOC)
    production.py              # IProductionEngine                                                 (~50 LOC)
    logistics.py               # IConsumableEngine, IResupplyEngine, IHarvestingEngine             (~140 LOC)
    population.py              # IPopulationEngine, IOrganicsConsumptionEngine, IHappinessEngine   (~125 LOC)
    planet_ops.py              # IPlanetEnergyEngine, IPlanetActionEngine                          (~80 LOC)
    terraforming.py            # IQualityEngine, IAtmosphereEngine, IWaterEngine                   (~70 LOC)
    components.py              # IComponentActivationEngine                                        (~35 LOC)
```

Max leaf size is `logistics.py` at ~140 LOC — comfortably below the 500 ceiling and the 200 internal target.

### Re-export shim policy

`engines/__init__.py` is the **public seam** for the package, not a "fallback shim" in the AGENTS.md "no compatibility shims" sense. It is exactly equivalent to the current single-file module path; deleting it would be a sweeping breaking change. The seam stays.

### Hard rule (architectural invariant)

After the split, leaf modules under `engines/` are the source of truth; `engines/__init__.py` is the only place re-exporting them; the outer `interfaces/__init__.py` re-exports through the package. **No other module may import from a sibling leaf** — concrete engines and tests import via `game.strategy.interfaces.engines` (the package path), not `game.strategy.interfaces.engines.movement` etc. This keeps the public API surface narrow and lets future domain regrouping happen inside the package without churning consumers.

## Architecture Analysis

### ABC inventory by domain (18 total, 9 domains)

- **Fleet / movement (1):** `IMovementEngine`
- **Order / action (2):** `IOrderProcessor`, `IActionExecutionEngine`
- **Combat / hazards (2):** `IConflictEngine`, `IEnvironmentalHazardEngine`
- **Production (1):** `IProductionEngine`
- **Resource / logistics (3):** `IConsumableEngine`, `IResupplyEngine`, `IHarvestingEngine`
- **Colony / population (3):** `IPopulationEngine`, `IOrganicsConsumptionEngine`, `IHappinessEngine`
- **Planet operations (2):** `IPlanetEnergyEngine`, `IPlanetActionEngine`
- **Terraforming (3):** `IQualityEngine`, `IAtmosphereEngine`, `IWaterEngine`
- **Component lifecycle (1):** `IComponentActivationEngine`

### Pre-existing drift this project closes

1. `engines.__all__` (lines 29-50 in the current monolith) lists 17 names. `IComponentActivationEngine` is defined at line 754 but missing from the `__all__` block.
2. `game/strategy/interfaces/__init__.py:12-26` re-exports only 13 of the 18 ABCs. Missing: `IOrganicsConsumptionEngine`, `IHappinessEngine`, `IQualityEngine`, `IAtmosphereEngine`, `IWaterEngine`.

Phase 2 + the new layout test fix both gaps and enforce them going forward.

## Risks & Mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| Circular import when an ABC's TYPE_CHECKING block names a class in another strategy submodule | Low — all current TYPE_CHECKING imports are forward-only string references; no eager imports added by the split | Keep `from __future__ import annotations` on every leaf; never widen TYPE_CHECKING into runtime |
| A test imports an ABC via the leaf module path (e.g. `from game.strategy.interfaces.engines.movement import IMovementEngine`) and later refactors break | Low — current tests all use the package path | Layout test asserts top-level path is canonical; rule documented above and in the TD plan |
| Drift between `engines/__init__.py __all__` and the per-leaf `__all__` | Medium — easy to forget when adding new ABCs | Layout test enumerates the expected mapping in code; adding a new ABC requires updating both lists or the test fails |
| Re-export `__init__.py` is misread as a fallback shim and removed by a later cleanup | Low | Module docstring explicitly states "package entry point, not a backward-compat shim — delete only when all 30 consumers are rewritten to use leaf module paths" |
| Existing `interfaces/__init__.py` drift (5 missing names) hides a real test gap | Already present | Phase 2 closes it; layout test enforces forever after |
| Touch volume causes spurious test churn in `--testmon` | Low | Move is symbol-preserving; `testmon` re-runs are exactly the 30 import-site consumers |

## Cross-Plan Coupling (per EXECUTION_ORDER.md)

- **Soft preference: TD-09 → TD-04.** TD-04 (phase registry hooks, PROJ-428) extracts hook bodies from `turn_phase_registry.py` into phase classes that will depend on `IMovementEngine`, `IConflictEngine`, etc. Running TD-09 first means TD-04 can pull narrower-domain contracts from the split package instead of a 778-LOC pile. **Not a hard blocker** — TD-04 can proceed against the monolith if sequencing demands it.
- **No hard prerequisites** for TD-09 itself; it sits at position 1 of 10 in the recommended linear order specifically because it is symbol-preserving and de-risks every later plan that touches engine interfaces.
- **Out of scope for TD-09 (deliberate):** renaming `IOrganicsConsumptionEngine` (PROJ-286 deferred rename), merging ABCs, concrete engine restructure (TD-04, TD-05).

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
