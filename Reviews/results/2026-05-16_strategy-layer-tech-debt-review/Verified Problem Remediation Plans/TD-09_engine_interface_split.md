# TD-09: Engine Protocol Monolith Split

**Status:** VERIFIED
**Source review:** `Reviews/results/2026-05-16_strategy-layer-tech-debt-review/report.md` lines 251-264
**Target file:** `game/strategy/interfaces/engines.py`
**Project rules applied:** strict TDD, root-cause fix (no shim re-exports beyond a deliberate stable seam), docs-first, 500-LOC ceiling.

---

## Verification Findings

### Headline numbers

| Metric | Report claim | Actual | Notes |
|---|---|---|---|
| LOC | "~625" (cited as 53-754) | **778** | `wc -l game/strategy/interfaces/engines.py` |
| ABC count | 17 | **18** | Report counted `__all__` (17); `IComponentActivationEngine` is defined but missing from the `__all__` list at line 29-50 |
| Over 500-LOC ceiling | yes | **yes** (+278 LOC) | Confirmed |

### 18-ABC inventory by proposed domain

All lines are inside `game/strategy/interfaces/engines.py`.

**Fleet / movement domain (1)**
- `IMovementEngine` (line 53; ~76 LOC) — fleet movement collection, application, pathfinding.

**Order / action domain (2)**
- `IOrderProcessor` (line 173; ~70 LOC) — instant orders, action-order execution.
- `IActionExecutionEngine` (line 458; ~46 LOC) — tick-based action progress driver (PROJ-187).

**Combat / hazards domain (2)**
- `IConflictEngine` (line 243; ~50 LOC) — multi-empire combat resolution.
- `IEnvironmentalHazardEngine` (line 504; ~41 LOC) — storm tick (PROJ-189).

**Production / construction domain (1)**
- `IProductionEngine` (line 129; ~44 LOC) — per-tick construction (PROJ-75/79/158).

**Resource / logistics domain (3)**
- `IConsumableEngine` (line 293; ~33 LOC) — per-turn consumption spread.
- `IResupplyEngine` (line 326; ~56 LOC) — fuel generation + fleet resupply (PROJ-74).
- `IHarvestingEngine` (line 382; ~43 LOC) — per-tick harvesting (PROJ-75/161).

**Colony / population domain (3)**
- `IPopulationEngine` (line 425; ~33 LOC) — logistic growth.
- `IOrganicsConsumptionEngine` (line 617; ~47 LOC) — per-species multi-resource upkeep (PROJ-284/286).
- `IHappinessEngine` (line 664; ~36 LOC) — happiness derivation (PROJ-284).

**Planet operations domain (2)**
- `IPlanetEnergyEngine` (line 545; ~34 LOC) — per-tick energy gen/consume (PROJ-237).
- `IPlanetActionEngine` (line 579; ~38 LOC) — planet order ticks (PROJ-237).

**Terraforming domain (3)**
- `IQualityEngine` (line 700; ~18 LOC) — quality improvement (PROJ-369).
- `IAtmosphereEngine` (line 718; ~18 LOC) — atmosphere modification (PROJ-369).
- `IWaterEngine` (line 736; ~18 LOC) — water modification (PROJ-369).

**Component lifecycle domain (1)**
- `IComponentActivationEngine` (line 754; ~25 LOC) — activation timer ticks.

### TurnEngineConfig dependency

`game/strategy/engine/turn_engine_config.py` does **not** import any of these ABCs by name. Every engine field is typed `Optional[Any]`. `create_default()` imports the *concrete* engine classes. The only TurnEngine-side ABC import is the TYPE_CHECKING block in `turn_engine.py:102-121` (purely for annotation). **Splitting the file does not change `TurnEngineConfig`'s runtime contract.**

### Import sites (all consumers)

Production code — 1 ABC per concrete engine (paired by name):
- `game/strategy/engine/fleet_movement_engine.py:22` -> `IMovementEngine`
- `game/strategy/engine/production_engine.py:27` -> `IProductionEngine`
- `game/strategy/engine/order_processor.py:27` -> `IOrderProcessor`
- `game/strategy/engine/conflict_resolution_engine.py:22` -> `IConflictEngine`
- `game/strategy/engine/consumable_management_engine.py:20` -> `IConsumableEngine`
- `game/strategy/engine/resupply_engine.py:26` -> `IResupplyEngine`
- `game/strategy/engine/harvesting_engine.py:38` -> `IHarvestingEngine`
- `game/strategy/engine/population_engine.py:23` -> `IPopulationEngine`
- `game/strategy/engine/action_execution_engine.py:20` -> `IActionExecutionEngine`
- `game/strategy/engine/environmental_hazard_engine.py:20` -> `IEnvironmentalHazardEngine`
- `game/strategy/engine/planet_energy_engine.py:28` -> `IPlanetEnergyEngine`
- `game/strategy/engine/planet_action_engine.py:25` -> `IPlanetActionEngine`
- `game/strategy/engine/organics_consumption_engine.py:37` -> `IOrganicsConsumptionEngine`
- `game/strategy/engine/happiness_engine.py:35` -> `IHappinessEngine`
- (`IComponentActivationEngine`, `IQualityEngine`, `IAtmosphereEngine`, `IWaterEngine` are referenced only by the package `__init__` and tests — verify when editing.)

Aggregator:
- `game/strategy/interfaces/__init__.py:12-26` re-exports 13 of the 18 (missing `IOrganicsConsumptionEngine`, `IHappinessEngine`, `IQualityEngine`, `IAtmosphereEngine`, `IWaterEngine` — already-existing inconsistency to fix as part of TD-09).

TurnEngine (TYPE_CHECKING only):
- `game/strategy/engine/turn_engine.py:102-121`

Tests / mocks:
- `tests/unit/strategy/mocks/mock_engines.py:23-29` (Movement, Production, OrderProcessor, Conflict, Consumable)
- `tests/integration/strategy/test_economy_e2e.py:25` (`IPopulationEngine`)
- `tests/unit/strategy/turn_engine/test_turn_snapshot_capture_failure.py:27` (`IOrganicsConsumptionEngine`)
- `tests/unit/strategy/turn_engine/test_turn_engine_phase_timing.py:223`
- `tests/unit/strategy/turn_engine/test_turn_engine_phase_320_movement_diff.py:22`
- `tests/unit/strategy/turn_engine/test_turn_engine_init_precedence.py:17` (`IMovementEngine`)
- `tests/unit/strategy/turn_engine/test_turn_engine_end_of_turn_order.py:34`
- `tests/unit/strategy/turn_engine/test_turn_end_of_turn_engine_rollback.py:29`
- `tests/unit/strategy/turn_engine/test_dependency_injection.py:181,190,199,208,217,237,262,297`
- `tests/unit/strategy/turn_engine/test_default_tick_phase_list.py:25`

Total: **30 import sites** across production, tests, and mocks. All consume ABCs by name; none rely on the module being a single file.

### Verdict

**VERIFIED.** File is 778 LOC (over the 500 ceiling by 56%), contains 18 unrelated ABCs spanning 9 domains, mixes ~13 PROJ-tagged generations of contract additions, and `__all__` is already drifting (missing `IComponentActivationEngine`; sibling `__init__.py` already misses 5 of the 18). The remediation suggestion in the report — split by domain, re-export minimal seam — is the correct fix. `TurnEngineConfig` is not blocked by the split because it does not type-name the ABCs.

---

## Affected Code

### Files to be moved / split (1)
- `game/strategy/interfaces/engines.py` (delete after split; see Goal section for layout).

### Files to be updated (production)
All 14 concrete engine modules listed above must update their `from game.strategy.interfaces.engines import I<Name>` line.

`game/strategy/engine/turn_engine.py:102-121` updates its TYPE_CHECKING import block.

`game/strategy/interfaces/__init__.py:12-44` is rewritten to re-export from the new modules.

### Files to be updated (tests / mocks)
12 test files plus `tests/unit/strategy/mocks/mock_engines.py` (see import-site list above).

### Files NOT touched
- `game/strategy/engine/turn_engine_config.py` (no symbolic dependency).
- `game/strategy/engine/turn_phase_registry.py` (no ABC import — uses concrete engines).
- Battle resolver / `interfaces/battle_resolver.py` (already separate).

---

## Goal / End State

### New module layout under `game/strategy/interfaces/engines/`

Convert `engines.py` into a package. Each module holds ABCs for one domain and ends well under 200 LOC. The package `__init__.py` re-exports every ABC so existing `from game.strategy.interfaces.engines import I<Name>` continues to work (zero-churn re-export shim — same module path).

```
game/strategy/interfaces/engines/
    __init__.py                # explicit re-exports, declarative __all__
    movement.py                # IMovementEngine
    orders.py                  # IOrderProcessor, IActionExecutionEngine
    combat.py                  # IConflictEngine, IEnvironmentalHazardEngine
    production.py              # IProductionEngine
    logistics.py               # IConsumableEngine, IResupplyEngine, IHarvestingEngine
    population.py              # IPopulationEngine, IOrganicsConsumptionEngine, IHappinessEngine
    planet_ops.py              # IPlanetEnergyEngine, IPlanetActionEngine
    terraforming.py            # IQualityEngine, IAtmosphereEngine, IWaterEngine
    components.py              # IComponentActivationEngine
```

Expected LOC per module (annotations preserved verbatim):

| Module | ABCs | Est. LOC |
|---|---|---|
| movement.py | 1 | ~85 |
| orders.py | 2 | ~125 |
| combat.py | 2 | ~100 |
| production.py | 1 | ~50 |
| logistics.py | 3 | ~140 |
| population.py | 3 | ~125 |
| planet_ops.py | 2 | ~80 |
| terraforming.py | 3 | ~70 |
| components.py | 1 | ~35 |
| `__init__.py` | (re-export) | ~50 |

All under 200 LOC; max is `logistics.py` at ~140. Comfortably under the 500-line ceiling.

### Re-export shim policy

`game/strategy/interfaces/engines/__init__.py` re-exports every ABC with an explicit `__all__`. This is **not** a compatibility shim in the AGENTS.md "no fallback systems" sense — it is the public seam for the package, exactly equivalent to the current single-file module path. The point is that `from game.strategy.interfaces.engines import IFoo` continues to work for the 30 consumers without forcing a sweeping rename in the same change.

The outer `game/strategy/interfaces/__init__.py` is rewritten to import from `game.strategy.interfaces.engines` (the new package) and add the 5 ABCs it currently omits (`IOrganicsConsumptionEngine`, `IHappinessEngine`, `IQualityEngine`, `IAtmosphereEngine`, `IWaterEngine`). This closes an existing drift bug uncovered during verification — not scope creep.

### Hard rule
After this change, the leaf modules under `engines/` are the source of truth; `engines/__init__.py` is the only place re-exporting them; the outer `interfaces/__init__.py` re-exports through the package. **No other module may import from a sibling leaf — concrete engines and tests import via `game.strategy.interfaces.engines` (the package path), not `game.strategy.interfaces.engines.movement` etc.** That keeps the API surface narrow and lets future domain regrouping happen inside the package.

---

## Execution Preconditions

1. Reconfirm the import-site inventory before editing:
   ```text
   rg -n "from game\.strategy\.interfaces(\.engines)? import|from game\.strategy\.interfaces\.engines import" game tests
   ```
2. Confirm the current single-file baseline:
   ```text
   python - <<'PY'
   from pathlib import Path
   print((Path('game/strategy/interfaces/engines.py')).exists())
   PY
   ```
3. Confirm there is not already a competing package directory at
   `game/strategy/interfaces/engines/` from parallel work. If that directory
   already exists, stop and merge with that work instead of creating a second
   layout.

## Concrete File Touch Plan

- Delete:
  - `game/strategy/interfaces/engines.py`
- Add:
  - `game/strategy/interfaces/engines/__init__.py`
  - `game/strategy/interfaces/engines/movement.py`
  - `game/strategy/interfaces/engines/orders.py`
  - `game/strategy/interfaces/engines/combat.py`
  - `game/strategy/interfaces/engines/production.py`
  - `game/strategy/interfaces/engines/logistics.py`
  - `game/strategy/interfaces/engines/population.py`
  - `game/strategy/interfaces/engines/planet_ops.py`
  - `game/strategy/interfaces/engines/terraforming.py`
  - `game/strategy/interfaces/engines/components.py`
- Modify:
  - `game/strategy/interfaces/__init__.py`
  - New test: `tests/unit/strategy/interfaces/test_engines_package_layout.py`

### Files that should usually remain untouched

- Concrete engine modules under `game/strategy/engine/`
- `game/strategy/engine/turn_engine_config.py`
- `game/strategy/engine/turn_phase_registry.py`
- Existing tests that already import from the package-root path

If the executor finds themselves editing concrete engine files, they should stop
and first prove with a failing test that package-root re-exports are
insufficient.

## Weak-LLM Guardrails

- Treat this as a symbol-preserving file-layout change. Do not redesign the interfaces while splitting them.
- Keep package-root re-exports in place until the focused layout test and existing regression suites pass.
- Do not edit concrete engine implementations unless a consumer import actually breaks.
- Use one new focused test to drive the split and grep the repo for remaining old-path imports before deleting the monolith.
- Because this is mechanical, prefer small commits and name-preserving moves over opportunistic cleanup mixed into the same change.

## Per-Phase Success Criteria

- Phase 0 is done only when the new layout test is red because `engines` is
  still a module.
- Phase 1 is done only when `game.strategy.interfaces.engines` is a package and
  the layout test is green.
- Phase 2 is done only when every name in `engines.__all__` is also importable
  from `game.strategy.interfaces`.
- Phase 3 is done only when the strategy turn-engine tests pass without any
  consumer import changes.
- Phase 4 is done only when docs no longer describe `engines.py` as a monolithic
  single file.

---

## Remediation Plan

This is a mechanical split. Strict TDD applies — a verifying test runs first, fails (proves the new layout doesn't exist), then passes after the move. Phases are small enough that an LLM can execute the whole arc in one pass; "phases" here are review checkpoints, not work days.

### Phase 0: docs + structural test (TDD anchor)

1. Read `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`, `docs/03_CONVENTIONS.md`. Search for any "engines.py" mention; queue updates.
2. Add `tests/unit/strategy/interfaces/test_engines_package_layout.py`. Tests (initially red):
   - The package `game.strategy.interfaces.engines` resolves to a package (`__path__` exists).
   - Each ABC name listed in §"Inventory" resolves through `from game.strategy.interfaces.engines import <Name>` AND through the leaf module path AND through `game.strategy.interfaces` (top-level).
   - `engines.__all__` lists exactly the 18 names.
   - Each leaf module's `__all__` lists exactly the ABCs the layout assigns to it.
   - Loading the package does not raise on import.
3. Run the test, confirm it fails for the right reason (`engines` is still a module, not a package).

### Phase 1: introduce the package

1. Create `game/strategy/interfaces/engines/` directory.
2. Create the 9 leaf modules. For each ABC, **cut** (do not duplicate) the class plus its TYPE_CHECKING imports verbatim from `engines.py`. Keep docstrings, PROJ tags, and method signatures byte-identical.
3. Each leaf module gets its own `from __future__ import annotations` + minimal TYPE_CHECKING block (only the symbols the ABCs in that module reference — e.g. `MovementResult` only in `movement.py`).
4. Each leaf module declares `__all__` listing its ABCs.
5. Author `engines/__init__.py`:
   ```python
   from game.strategy.interfaces.engines.movement import IMovementEngine
   from game.strategy.interfaces.engines.orders import (
       IOrderProcessor,
       IActionExecutionEngine,
   )
   # ... etc, one block per leaf
   __all__ = [<all 18 names, sorted by domain>]
   ```
6. Delete the old `game/strategy/interfaces/engines.py` (root-cause fix per AGENTS.md — no parallel "old + new" path).
7. Rerun the Phase-0 test. Should now be green.

### Phase 2: align top-level interfaces aggregator

1. Update `game/strategy/interfaces/__init__.py` to import every ABC the engines package exposes (currently misses 5). Update its `__all__` accordingly.
2. Add a one-line regression test in the layout test: every name in `engines.__all__` must also be importable from `game.strategy.interfaces`. This catches future drift.

### Phase 3: validate consumers (no code changes expected)

1. Run the full strategy-engine test suite:
   ```
   pytest tests/unit/strategy/turn_engine tests/integration/strategy tests/unit/strategy/interfaces -q
   ```
2. Run the AST-guard test that already polices TurnEngine: `tests/.../test_no_lazy_fallback_init.py::test_no_function_local_engine_imports_in_TurnEngine_methods` — confirms the split didn't introduce new function-local imports.
3. Run the sharded baseline (Tools/test_sharded/test_sharded.py) to be safe — the move touches a widely-imported module.

### Phase 4: docs sync

1. Update any doc that referenced `interfaces/engines.py` as a single file. Likely candidates per the docs structure note in memory:
   - `docs/systems/strategy_layer.md`
   - any `docs/architecture/*.md` page that lists the engine interface count.
2. If `docs/_ignore/` shows up in the grep — leave it alone per AGENTS.md.

### Phase 5: clean review

1. `git status --short` — confirm the only deletions are `engines.py` and the only additions are the 9 leaf modules + `__init__.py` + the new test.
2. Inspect each leaf module to confirm: no copy/paste duplicates, no orphan TYPE_CHECKING imports, docstring fidelity preserved.
3. Confirm the new package's `__init__.py` re-exports exactly 18 names and matches `__all__`.

---

## Test Strategy

### New test (added in Phase 0, drives the work)
`tests/unit/strategy/interfaces/test_engines_package_layout.py` — single file, ~6 small tests:
1. `test_engines_is_a_package` — `game.strategy.interfaces.engines` has a `__path__`.
2. `test_each_leaf_module_loads` — import each of the 9 leaf modules without error.
3. `test_each_abc_importable_from_package_root` — for every name in the expected 18-tuple, `getattr(engines, name)` is a class and subclass of `ABC`.
4. `test_each_leaf_exports_expected_abcs` — leaf module `__all__` matches the layout table verbatim.
5. `test_top_level_interfaces_reexports_all_engines` — every name in `engines.__all__` is also in `game.strategy.interfaces.__all__`.
6. `test_no_dangling_engines_py_module` — `pathlib.Path('game/strategy/interfaces/engines.py')` does not exist (root-cause fix; no leftover file).

### Existing tests (regression coverage — already pass)
- `tests/unit/strategy/mocks/mock_engines.py` — instantiated by the DI test suite.
- `tests/unit/strategy/turn_engine/test_dependency_injection.py` — imports 7 ABCs; failure here would catch a broken re-export.
- `tests/unit/strategy/turn_engine/test_default_tick_phase_list.py` — imports a batch of ABCs.
- `tests/integration/strategy/test_economy_e2e.py` — exercises the population engine via its ABC.

### Test commands run before declaring done
```
pytest tests/unit/strategy/interfaces -q                       # new layout test
pytest tests/unit/strategy/turn_engine -q                      # DI / phase coverage
pytest tests/integration/strategy -q                           # end-to-end smoke
python Tools/test_sharded/test_sharded.py                      # full baseline
```

---

## Risks & Mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| Circular import when an ABC's TYPE_CHECKING block names a class in another strategy submodule | Low — all current TYPE_CHECKING imports are forward-only string references; no eager imports added by the split | Keep `from __future__ import annotations` on every leaf; never widen TYPE_CHECKING into runtime |
| A test imports an ABC via the leaf module path (e.g. `from game.strategy.interfaces.engines.movement import IMovementEngine`) and later refactors break | Low — current tests use the package path | Layout test asserts top-level path is canonical; rule documented in this file |
| Drift between `engines/__init__.py __all__` and the per-leaf `__all__` | Medium — easy to forget when adding new ABCs | Layout test enumerates expected mapping in code; new ABCs must update both lists or test fails |
| Re-export-only `__init__.py` is misread as a fallback shim and removed by a later cleanup | Low | Module docstring explicitly states "package entry point, not a backward-compat shim — delete only when all 30 consumers are rewritten to use leaf module paths" |
| Existing `interfaces/__init__.py` drift (5 missing names) hides a real test gap | Already present | Phase 2 closes it; layout test enforces forever after |
| Touch volume causes spurious test churn in `--testmon` | Low | Move is symbol-preserving; `testmon` re-runs are exactly the 30 import-site consumers |

---

## Dependencies / Order

### Hard dependencies
None. The split is symbol-preserving, so no other TD item must land first.

### Coupling to TD-04 (phase registry partial declarativeness)
TD-04 wants to extract hook bodies from `turn_phase_registry.py` into phase classes. Those phase classes will likely depend on `IMovementEngine`, `IConflictEngine`, etc. The split planned here makes that future work **easier**, not harder — TD-04 can `from game.strategy.interfaces.engines.movement import IMovementEngine` for narrower-domain phase classes if desired, or keep using the package-root import.

**Ordering recommendation:** do TD-09 **before** TD-04. TD-04 is the bigger refactor; landing TD-09 first means TD-04 can pull narrower contracts when wiring its new phase classes, instead of importing from a 778-LOC pile.

Treat that as a soft preference, not a blocker. TD-04 can proceed first if sequencing pressure demands it.

### Soft adjacency
- TD-02 (`GameSession` lifecycle) doesn't touch engine interfaces directly but does construct `TurnEngineConfig`. No ordering constraint.
- TD-07 (ability metadata convergence) is unrelated to ABC layout.

### Out of scope for TD-09
- Renaming `IOrganicsConsumptionEngine` (PROJ-286 deferred rename — documented as deliberate).
- Reducing ABC count by merging contracts.
- Adding the missing 5 ABCs to the public `interfaces/__init__.py` __all__ list (Phase 2 closes this drift; flagged here for transparency, not as scope creep).
- Concrete engine restructure (TD-04, TD-05).

---

### Ordering conclusion for this owned set

- TD-09 has no hard dependency on TD-07, TD-08, or TD-10.
- It is the safest plan to execute first because it is mechanical,
  symbol-preserving, and intentionally avoids consumer churn.
- Recommended owned-only order starts with **TD-09** unless an external
  prerequisite blocks all work.

---

## Acceptance Criteria

- [ ] `game/strategy/interfaces/engines.py` has been replaced by a package layout without changing the public symbols available to production callers.
- [ ] Package-root imports continue to work for all existing consumers.
- [ ] No concrete engine modules required logic changes just to accommodate the split.
- [ ] The new structural layout test is present and passes.
- [ ] Focused interface/import regression coverage is green before the sharded run.
- [ ] `python Tools/test_sharded/test_sharded.py` is green.

---

## Estimated Scope

LLM time:
- Phase 0 (docs read + layout test): a few minutes.
- Phase 1 (split + delete old file): a few minutes (mechanical cut/paste across 18 ABCs).
- Phase 2 (top-level aggregator): under a minute.
- Phase 3 (test runs): the real bottleneck — full sharded suite is the dominant cost (several minutes per run; budget 2 runs).
- Phase 4 (docs sync): under a minute.
- Phase 5 (final review): under a minute.

**Total wall time: dominated by test-run cost, ~10-15 minutes including the sharded baseline. Active edit time: a few minutes.** The change is symbol-preserving and almost entirely mechanical; the risk profile is dominated by `pytest` cost, not engineering judgment.

### Diff shape
- 1 file deleted (`engines.py`, 778 LOC).
- 10 files added (9 leaf modules + new `engines/__init__.py`).
- 1 file rewritten (`interfaces/__init__.py`).
- 1 test added (`test_engines_package_layout.py`).
- 0 concrete engine files modified (paths preserved by package shim).
- 0 test files modified (paths preserved by package shim).
- Possibly 1-2 doc files touched in Phase 4.

Net production code: -778 + ~860 ≈ +80 LOC (the cost of 10 module headers + an explicit `__init__.py`). Per-file LOC drops below the 500 ceiling for every artifact, which is the entire point.
