# Cross-Verification Report
**Generated:** 2026-05-07
**Sources:** `deep_review.md` (Shard 02), `dead_code_validation.md`

## Critical Finding Verification

| Finding ID | Symbol | File | Test refs? | Doc refs? | Data refs? | Production callers? | Verdict |
|------------|--------|------|------------|-----------|------------|---------------------|---------|
| DCV-01 | `IControllableShip` import | `game/ai/controller.py:56` | **0** | **0** | **0** | **0** (symbol doesn't exist) | **CONFIRMED SAFE DELETION** |
| DEEP-02-001 | `create_brick` | `game/simulation/designs.py` | `tests/unit/builder/test_designs.py` | 0 | 0 | 0 (only defined, never imported elsewhere) | **PRODUCT_DECISION** — test-only |
| DEEP-02-001 | `create_interceptor` | `game/simulation/designs.py` | `tests/unit/builder/test_designs.py` | 0 | 0 | 0 (only defined, never imported elsewhere) | **PRODUCT_DECISION** — test-only |
| DEEP-02-002 | `ShipPickerStub` | `game/ui/screens/strategy_windows/ship_picker.py` | `test_strategy_superweapons.py`, `test_strategy_window_manager_public_api.py` | 0 | 0 | `strategy_window_manager.py` (wired in production) | **PRODUCT_DECISION** — active stub, wired + tested |
| DEEP-02-003 | `allocate_crew_and_life_support` | `game/simulation/entities/stat_contributors/command.py` | `tests/unit/simulation/entities/stat_contributors/test_command.py` | 0 | 0 | `ship_stats.py` (ShipStatsCalculator calls it) | **PRODUCT_DECISION** — active helper, wired + tested |
| DEEP-02-019 | `has_superweapons` | `game/ui/screens/builder/stat_getters.py:315` | `tests/unit/ui/screens/builder/test_stat_getters.py` | 0 | 0 | 0 (only defined; no other game/ caller) | **PRODUCT_DECISION** — test-only helper |
| DEEP-02-020 | `validate_positive` import | `game/strategy/data/galaxy.py:6` | `tests/unit/core/test_validation_helpers.py` | `docs/05_ERROR_HANDLING.md` | 0 | YES (`galaxy.py:299` uses it) | **FALSE POSITIVE** — actively used |

## Downgraded to Product Decision

| ID | Symbol | Reason |
|----|--------|--------|
| DEEP-02-019 | `has_superweapons` in `stat_getters.py` | Only referenced by `tests/unit/ui/screens/builder/test_stat_getters.py`. No production usage beyond definition. Functionally dead in production; kept alive only by test. |

## Upgraded to False Positive

| ID | Symbol | Reason |
|----|--------|--------|
| DEEP-02-020 | `validate_positive` import in `galaxy.py` | The import IS actively used at `galaxy.py:299`. Audit incorrectly flagged it as unused. Also documented in `docs/05_ERROR_HANDLING.md`. |

## Confirmed Safe Deletions

| ID | Symbol | LOC | Detail |
|----|--------|-----|--------|
| DCV-01 | `IControllableShip` import + annotation | ~2 | `game/ai/controller.py:56`: TYPE_CHECKING import references a symbol (`IControllableShip`) that does not exist in `game/simulation/interfaces/ai_controller.py`. The module defines `IAIController` / `IAIControllerFactory` only. The annotation at line 86 (`ship: 'IControllableShip'`) is a stale forward reference. MyPy corroborates: `Module "game.simulation.interfaces.ai_controller" has no attribute "IControllableShip" [attr-defined]`. Zero test/doc/data refs. |

## Product Decision Items (Original — Verification Confirmed)

| ID | Symbol | LOC | Original Verdict | Cross-Verification |
|----|--------|-----|-----------------|-------------------|
| DEEP-02-001 | `create_brick` / `create_interceptor` | 68 | PRODUCT_DECISION | **Confirmed.** Only `tests/unit/builder/test_designs.py` references these. No docs or data refs. No production imports. Pure test fixtures that happen to live in production code. |
| DEEP-02-002 | `ShipPickerStub` | 43 | PRODUCT_DECISION | **Confirmed.** Wired in `strategy_window_manager.py`; 2 test files exercise the stub path. No docs/data refs. Active placeholder (PROJ-198). |
| DEEP-02-003 | `allocate_crew_and_life_support` | 44 | PRODUCT_DECISION | **Confirmed.** Called from `ShipStatsCalculator` in `ship_stats.py`; tested via `test_command.py`. No docs/data refs. Correctly placed per architecture; not dead. |

## Summary

| Category | Count |
|----------|-------|
| Confirmed Safe Deletions (truly dead) | 1 |
| Product Decision (keep, referenced) | 6 |
| False Positives (keep, actively used) | 1 |
| **Total findings cross-verified** | **8** |

### Actionable: 1 dead import

The only truly dead code is `IControllableShip` in `game/ai/controller.py:56` — a TYPE_CHECKING import of a symbol that no longer exists. Fix: remove the import line and update the forward-reference annotation at line 86 from `'IControllableShip'` to `'ShipControllableAdapter'` (already imported at line 69).
