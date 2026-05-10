# Review Report: PROJ-369 TurnEngine Decomposition

**Request ID:** req_20260506_071706_deac7e
**Review Type:** code
**Review Mode:** normal
**Branch:** feat/03c-phase-aware-execution (HEAD: 82b5cbc20)
**Completed:** 2026-05-06T07:25:00Z
**Reviewer:** OpenCode via ocode-review-request
**Scope:** See `scope.md`
**Limitations:** review conducted inline (no sub-agents) — all scope files read in full; 8 focus areas addressed. `docs/systems/strategy_layer.md` and `docs/02_PATTERNS.md` sampled for relevant sections but not exhaustively re-read.

---

## Verification Matrix

No parent request — not a follow-up review.

---

## Findings Summary

| Severity | Count |
|----------|-------|
| CRIT | 0 |
| MAJ | 1 |
| MIN | 3 |
| INFO | 8 |

---

## CRITICAL

*None.* All 135 turn engine tests pass. Both production construction sites (`game_session.py:105-117`, `game_session.py:397-409`) wire `ai_factory` through `TurnEngineConfig.create_default()`. No silent fallback remains.

---

## MAJOR

### MAJ-001: `build_test_turn_engine` mutates config in place before `dataclasses.replace`

**File:** `tests/fixtures/turn_engine.py:104`
**Line:** 104
**Severity:** MAJ

The `battle_resolver` escape hatch at line 103-104 mutates the frozen config's `conflict_engine` in place:

```python
if battle_resolver is not None:
    cfg.conflict_engine._battle_resolver = battle_resolver
```

This is a private-attribute reach-through on a frozen dataclass. It works because `TurnEngineConfig` is frozen (dataclass `frozen=True`), which prevents `cfg.conflict_engine = ...` but does NOT prevent mutating the engine object's private `_battle_resolver` attribute.

**Risk:** If `dataclasses.replace(cfg, ...)` is called **after** this mutation (line 107), the new config clone will carry the mutated `conflict_engine._battle_resolver` — which is actually the intended behavior and is relied upon by test `test_dependency_injection.py:229` (`assert engine._battle_resolver is mock_resolver`). However, the mutation order also means that if code between lines 104 and 107 raises, the original config's `conflict_engine` is permanently mutated. Low practical risk since lines 104-107 are adjacent, but the pattern is fragile.

**Suggested remediation:** Swap the resolver via `dataclasses.replace` on the config itself — add a `battle_resolver` field to `TurnEngineConfig` (the conflict engine reads whatever is bound at construction time). Alternatively, construct a new `ConflictResolutionEngine` via `dataclasses.replace(cfg, conflict_engine=ConflictResolutionEngine(battle_resolver, ...))` — but this requires re-supplying `registries` and `event_bus`. The current approach is pragmatic; document the mutation-order invariant explicitly in the docstring at line 102.

---

## MINOR

### MIN-001: `TickContext` dual-use with `tick=0` sentinel is semantically awkward for end-of-turn field access

**File:** `game/strategy/engine/turn_phase_registry.py:52-54`
**Severity:** MIN

`TickContext`'s docstring says it is "also reused for the end-of-turn descriptor block" with `tick=0` sentinel. This works correctly (all pre/post hooks that depend on `ctx.tick` check explicitly), but `TickContext` carries mid-tick scratch fields (`move_queue`, `pre_movement_locations`, `moved_fleet_ids`) that are meaningless during end-of-turn iteration. A future descriptor edit that reads `ctx.move_queue` during end-of-turn would get `None` silently.

**Suggested remediation:** Extract a `PhaseContext` base class with the shared fields (`tick`, `empires`, `galaxy`, `component_registry`, `save_path`), with `TickContext` adding the mid-tick scratch fields. Non-blocking — the sentinel pattern is correctly documented and the risk surface is the three end-of-turn descriptors (all of which pass `(ctx.empires,)` only).

### MIN-002: AST guard `test_no_function_local_engine_imports` has a narrow match pattern

**File:** `tests/unit/strategy/turn_engine/test_no_lazy_fallback_init.py:108-110`
**Severity:** MIN

The check at lines 108-110 matches imports where `module.startswith("game.strategy.engine.") and module.endswith("_engine")`. A future regression that imports from `game.strategy.engine.foo_helper` (no `_engine` suffix) or uses `from game.strategy.engine import FooEngine` (top-level import, not function-local) would slip past. This is a narrowness concern similar to the PROJ-368 MAJ-002 finding (operator-filter narrowness).

**Suggested remediation:** Broaden the filter to `module.startswith("game.strategy.engine.")` without requiring `_engine` suffix, or add a positive allowlist of the 18 known engine module names and flag any import not in the allowlist.

### MIN-003: `interfaces/engines.py` at 778 LOC — justifiable but split shape exists

**File:** `game/strategy/interfaces/engines.py` (778 LOC)
**Severity:** MIN

The file contains only ABC/Protocol declarations and `__all__` — zero implementation. The `decisions.md` justification is real: "interfaces-only" files are a recognized exception to the 500 LOC ceiling per pattern docs. However, a clean split is available and low-cost:

- `_engines_tick.py` (~600 LOC): IMovementEngine, IProductionEngine, IOrderProcessor, IConflictEngine, IConsumableEngine, IPopulationEngine, IResupplyEngine, IHarvestingEngine, IActionExecutionEngine, IEnvironmentalHazardEngine, IPlanetEnergyEngine, IPlanetActionEngine, IComponentActivationEngine, IOrganicsConsumptionEngine, IHappinessEngine
- `_engines_terraforming.py` (~180 LOC): IQualityEngine, IAtmosphereEngine, IWaterEngine

Both re-exported from `engines.py` for backward compatibility. Recommend as a future PROJ-3XX cleanup task, not blocking.

---

## INFO

### INFO-001: `_NullBattleResolver` deletion — verified clean

All 75 grep hits for `_NullBattleResolver` are comments, docs, test assertions confirming deletion, or archived project files. The symbol is not importable (`test_NullBattleResolver_symbol_absent` passes). The `ValueError` at `conflict_resolution_engine.py:454-460` message is clear: "ConflictResolutionEngine was constructed without a battle_resolver; combat cannot resolve. Provide ai_factory= to TurnEngineConfig.create_default(...) so a SimulationBattleResolver is wired."

### INFO-002: `TurnEngineConfig.create_default()` construction order — verified correct

The 18 engines are constructed in `turn_engine_config.py:167-201`. Construction order respects dependency: `OrderProcessor(event_bus=event_bus)` at line 165 is constructed before `ActionExecutionEngine(order_processor=order_processor, ...)` at line 182. No other construction-order dependencies exist. The 3 new terraforming engines (`QualityEngine`, `AtmosphereEngine`, `WaterEngine`) receive `registries=` matching the deleted lazy-bodies. `battle_resolver` is `None` when `ai_factory is None`, with a clear docstring explaining the raise-on-combat contract.

### INFO-003: Test migration soundness — spot-checked 8 test files, all clean

Spot-checked: `test_dependency_injection.py`, `test_turn_engine_lazy_properties.py`, `test_turn_engine_end_of_turn_order.py`, `test_phase_isolation_with_mock_context.py`, `test_no_lazy_fallback_init.py`, `conftest.py`, `test_turn_engine_phase_320_movement_diff.py`, `test_turn_engine_validation.py`. All use `build_test_turn_engine(registries, ...)` or the `turn_engine`/`turn_engine_factory` fixtures. No direct `TurnEngine(registries=..., config=...)` calls found outside `tests/fixtures/turn_engine.py:109` (the helper itself).

The grep for `TurnEngine(` in tests confirms only 3 files contain the literal: `tests/fixtures/turn_engine.py` (the helper), `test_dependency_injection.py` (doc comments), and `test_turn_engine_lazy_properties.py` (doc comments). The 110-site migration is complete.

### INFO-004: `_run_phases` unification — verified compatible

Both paths (`_process_tick` for ticks 1-100, `process_turn` for end-of-turn with `tick=0`) route through the same `_run_phases` method (lines 309-343). Error handling is uniform — `_time_phase` wraps all non-EnginePhaseError exceptions. The pre/post hooks that gate on tick number (e.g., `_log_turn_start_tick_1` checking `ctx.tick == 1`) are safe: `tick=0` never matches tick-1 gates. The `run_phases_called_exactly_twice_in_process_turn` AST guard (line 148 of the test) confirms the invariant is pinned.

### INFO-005: AST guards (7 invariants) — all meaningful and passing

All 7 guards in `test_no_lazy_fallback_init.py` pass (confirmed by `pytest tests/unit/strategy/turn_engine/ -q` → 135 passed):
1. Zero `if self._<x>_engine is None:` lazy-fallback patterns
2. Zero function-local engine imports inside TurnEngine methods
3. `TurnEngine.__init__` ≤ 8 params (actual: 8: registries, config, ai_factory, race_registry, event_bus, battle_resolver, tick_phases, end_of_turn_phases)
4. `_NullBattleResolver` symbol absent from module
5. `_run_phases` called exactly once in `process_turn` + exactly once in `_process_tick`
6. Zero inline `self.<x>_engine.<m>(...)` calls in `process_turn`
7. `TurnEngineConfig.create_default` is the only function-local engine import site

None are tautological. Each locks a real PROJ-369 contract. See MIN-002 for the one coverage gap concern (narrow import pattern match).

### INFO-006: Sharded suite errors — not reproducing

The agent reported "3-5 non-deterministic errors in `tests/unit/workshop/` characterized as pycache/import-mismatch." Running `pytest tests/unit/workshop/ -x -q` resulted in **137 passed, 0 failed**. The non-deterministic errors do not reproduce on this checkout. No evidence PROJ-369 disturbed workshop tests.

### INFO-007: `turn_engine.py` at 700 LOC — splittable, clear seam exists

Over the 500-LOC ceiling but down from the 802-LOC baseline. A natural seam: extract `_time_phase` (lines 251-296, ~46 LOC) + `_run_phases` (lines 309-343, ~35 LOC) → `turn_phase_executor.py` (~110 LOC). The 18 property declarations (lines 351-449, ~100 LOC) could also be a `_turn_engine_properties.py` mixin. The remaining core (`__init__`, `process_turn`, `_process_tick`, `validate_colonize_order`, `_log_empire_state`, `_reset_phase_times`) would be ~490 LOC. Recommend targeting this in a follow-up project.

### INFO-008: `create_default_turn_engine` factory — confirmed deleted

The symbol is no longer importable (`test_dependency_injection.py:349` + `test_turn_engine_lazy_properties.py:269` confirm). The two references in `test_dependency_injection.py` and `test_turn_engine_lazy_properties.py` are test assertions that the symbol is absent (not usages). Canonical entry is `TurnEngineConfig.create_default(registries, ...) + TurnEngine(registries=..., config=cfg)`.
