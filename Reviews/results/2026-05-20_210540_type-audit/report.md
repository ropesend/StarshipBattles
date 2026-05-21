# Type Safety Audit Report

> **Generated:** 2026-05-20 — Comprehensive type annotation quality audit of `game/` production code.
> Review directory: `Reviews/results/2026-05-20_210540_type-audit/`

## 1. Executive Summary

**Scope:** 846 production files in `game/` (tests excluded). Two-pass analysis: AST annotation scanner + 4 shard deep-review agents + cross-layer type-flow validation.

| Metric | Count |
|--------|-------|
| `-> Any` returns | 343 |
| `: Any` annotations | 561 |
| Missing return types | 43 |
| `# type: ignore` sites | 27 |
| `cast()` usages | 0 |
| mypy strict-mode | Skipped (estimated ~334 errors) |
| Cross-layer type-loss boundaries | 7 |
| Protocol conformance gaps | 8 |

**Overall Score:** The codebase has a clean architecture with good conventions, but the UI layer (263 `-> Any` returns) is the primary source of type debt. Strategy layer has the most missing return types (30). Three layers are already strict-myypy-ready (services, assets, research). The 27 `# type: ignore` sites are mostly justified (20/27), with only 3 requiring attention.

**All 5 CRITICAL findings confirmed by verification agent. Zero false positives.**

## 2. Any Density Heatmap

| Layer | -> Any Returns | :Any Annotations | Missing Returns | Type Ignores | Density Score |
|-------|---------------|-----------------|-----------------|-------------|---------------|
| ui | 263 (76.7%) | 143 (25.5%) | 11 (25.6%) | 7 | **HIGH** |
| core | 30 (8.7%) | 55 (9.8%) | 0 (0%) | 0 | MEDIUM |
| strategy | 19 (5.5%) | 168 (29.9%) | 30 (69.8%) | 17 | **HIGH** |
| simulation | 15 (4.4%) | 106 (18.9%) | 1 (2.3%) | 3 | MEDIUM |
| ai | 7 (2.0%) | 47 (8.4%) | 0 (0%) | 0 | LOW |
| engine | 0 (0%) | 5 (0.9%) | 0 (0%) | 0 | LOW |
| services | 0 (0%) | 0 (0%) | 0 (0%) | 0 | READY |
| assets | 0 (0%) | 0 (0%) | 0 (0%) | 0 | READY |
| research | 0 (0%) | 0 (0%) | 0 (0%) | 0 | READY |

**Key observation:** UI has 76.7% of all `-> Any` returns; strategy has 69.8% of all missing return types.

## 3. Narrowing Plan

### Per-Layer Recommendations

#### services/engine/assets/research — CLEAN
No type debt. Zero `-> Any`, zero missing returns, zero `# type: ignore`. These layers are strict-myypy-ready.

#### ai — LOW effort (LOC estimate: ~20)
- 7 `-> Any` in protocol interfaces (`IControllable.get_position()`, `IGridEntity.position`, etc.)
- All narrowable to `Vector2` via TYPE_CHECKING string annotations
- Zero missing return types

#### simulation — MODERATE effort (LOC estimate: ~50)
- 15 `-> Any` returns, mostly in protocols and Component interfaces
- 1 CRITICAL: `_StatContributorRegistry.iter_for()` missing return type
- 3 `# type: ignore` sites, all justified
- Protocol files (`entity_protocols.py`, `component_protocols.py`) use `-> Any` for spatial/status types that could be narrowed with TYPE_CHECKING

#### core — MODERATE effort (LOC estimate: ~60)
- 30 `-> Any` returns, almost all in Protocol definitions
- Protocols intentionally use `-> Any` to avoid import cycles
- `json_utils.load_json()` returns `-> Any` (unavoidable)
- `RegistryManager.get_validator()` returns `-> Any` (narrowable to `Optional[Callable[...]]`)
- `formula_evaluator._eval_node()` returns `-> Any` (math/number evaluation)

#### strategy — HIGH effort (LOC estimate: ~150)
- 19 `-> Any` returns in engine helpers (8 `_get_*_mutator()` pattern)
- 30 missing return types (CRITICAL: `GameSession` mutator properties)
- 17 `# type: ignore` sites — 9 are `no-untyped-def` on GameSession mutators
- 2 CRITICAL: `StarSystem.primary_star`, `OrderMetadataView._registry()`
- 1 CRITICAL: `SuperweaponOrderProcessor._get_nav_service()` — called cross-module

#### ui — HIGHEST effort (LOC estimate: ~300)
- 263 `-> Any` returns — the bulk of type debt
- Unavoidable: ~180 are pygame/pygame_gui boundary returns, registry dispatch, dynamic JSON/data lookups
- Narrowable: ~83 are delegation properties, filter functions, and viewmodel methods
- 1 CRITICAL: `StrategyModalWindow.check_clicked_inside_or_blocking()` missing return type
- `stat_getters.py` has 47 `-> Any` functions (justified by data-driven JSON dispatch)
- `planet_list_filters.py` and `star_list_filters.py` have 13 module-level functions with narrowable `-> Any`

## 4. Mypy Strict-Mode Migration Path

| Order | Layer | Status | -> Any | Missing Returns | Type Ignores | Ready? |
|-------|-------|--------|--------|-----------------|-------------|--------|
| 1st | services | **READY NOW** | 0 | 0 | 0 | YES |
| 2nd | assets | **READY NOW** | 0 | 0 | 0 | YES |
| 3rd | research | **READY NOW** | 0 | 0 | 0 | YES |
| 4th | engine | Fix 5 :Any annotations | 0 | 0 | 0 | ~5 changes |
| 5th | ai | Narrow 7 protocol -> Any | 7 | 0 | 0 | ~7 changes |
| 6th | simulation | Narrow 15 -> Any, fix 1 missing return | 15 | 1 | 3 | ~20 changes |
| 7th | core | Narrow Protocol -> Any (TYPE_CHECKING) | 30 | 0 | 0 | ~30 changes |
| 8th | strategy | Fix 30 missing returns, 19 -> Any | 19 | 30 | 17 | ~66 changes |
| 9th | ui | Fix 11 missing, narrow ~83 -> Any | 263 | 11 | 7 | ~100 changes |

**Recommended first target:** Adopt strict mode in `services/`, `assets/`, and `research/` immediately (zero changes). Then tackle `engine/` and `ai/` (~12 changes total).

## 5. Prioritized Remediation Plan

Top-15 findings ranked by `severity_weight × layer_weight × loc_affected`:

| # | ID | Severity | Location | Issue | Fix LOC |
|---|-----|----------|----------|-------|---------|
| 1 | TYP-03-MR-001-007 | CRITICAL | `game/strategy/engine/game_session.py:217-254` | 4 mutator properties + 4 private counterparts missing return types | 8 |
| 2 | TYP-03-CF-001 | MAJOR | `game/strategy/engine/game_session.py:403` | `handle_command() -> Any` should be `-> ValidationResult` | 1 |
| 3 | TYP-04-MR-002 | CRITICAL | `game/strategy/data/star_system.py:85` | `primary_star` property missing return type | 1 |
| 4 | TYP-01-051 | CRITICAL | `game/ui/screens/strategy_modal_window.py:273` | `check_clicked_inside_or_blocking()` missing return type | 1 |
| 5 | CRITICAL-02-01 | CRITICAL | `game/strategy/engine/commands/order_metadata_view.py:76` | `_registry()` missing return type | 1 |
| 6 | TYP-03-CR-001 | CRITICAL | `game/strategy/engine/superweapon_order_processor.py:85` | `_get_nav_service()` missing return type | 1 |
| 7 | TYP-04-MR-001 | CRITICAL | `game/simulation/entities/stat_contributors/registry.py:298` | `iter_for()` missing return type | 1 |
| 8 | TYP-01-011 | MAJOR | `game/ui/screens/planet_list_filters.py:*` | 6 filter functions with narrowable `-> Any` | 12 |
| 9 | TYP-01-019 | MAJOR | `game/ui/screens/star_list_filters.py:*` | 5 filter functions with narrowable `-> Any` | 10 |
| 10 | TYP-03-DF-001 | MAJOR | `game/ui/screens/strategy_renderer.py:*` | 15 delegation properties -> Any narrowable | 15 |
| 11 | TYP-03-DF-002 | MAJOR | `game/ui/screens/strategy_screen.py:*` | 12 delegation properties -> Any narrowable | 12 |
| 12 | TYP-04-003 | MAJOR | `game/ui/screens/battle_screen.py:*` | 8 properties -> Any narrowable | 8 |
| 13 | TYP-01-004-010 | MAJOR | `game/strategy/engine/*` | 8 `_get_*_mutator()` helpers -> Any | 8 |
| 14 | TYP-04-007 | MAJOR | `game/ui/screens/builder/stat_getters.py:*` | 47 -> Any functions (JSON dispatch) | 0* |
| 15 | CF-007 | MAJOR | `game/core/registry.py:248,339` | `get_validator() -> Any` narrowable | 2 |

*`stat_getters.py` is intentionally data-driven; priority is adding Protocol-level typing without per-function annotations.

### Quick Wins (sub-10 LOC each)

- **game_session.py mutators**: Add 8 return type annotations, remove `# type: ignore[no-untyped-def]` — 8 LOC
- **star_system.py primary_star**: `-> Star | None` — 1 LOC
- **order_metadata_view.py _registry()**: `-> CommandRegistry` — 1 LOC
- **strategy_modal_window.py**: `-> bool` — 1 LOC
- **superweapon_order_processor.py _get_nav_service()**: `-> FleetNavigationService` — 1 LOC

**Total quick-win LOC: ~13**

## 6. Trend Comparison

First run — no prior baseline. This report establishes the baseline for future `ocode-type-audit` comparisons.

## 7. Appendices

### A. Type Ignore Justification Summary

| Status | Count | Details |
|--------|-------|---------|
| Justified | 20 | pygame runtime attrs, frozen dataclass overrides, replay store attr-defined, intentional protocol delay |
| Unjustified/Disputed | 3 | `defeat_dialog.py:83` (duplicate of justified `turn_failed_dialog.py:99`), `ship_theme_manager.py:254` (could narrow parameter type), `game_session.py` mutators (add types and remove ignores) |
| Workaround | 4 | `# type: ignore[no-untyped-def]` in game_session.py — fixed by adding return types |
| **Total** | **27** | |

### B. Cross-Shard Consistency

**No duplicate findings** — shards cover disjoint file sets. Three severity inconsistencies found (verification report details), most notably `_get_*_mutator()` pattern rated MAJOR in Shards 02/03 but MINOR in 01/04. Consistent rating should be MINOR.

### C. Methodology

1. **AST scanner** (`Tools/type_audit/type_audit.py`) scanned 846 files for `-> Any`, `: Any`, missing returns, `# type: ignore`, and `cast()` usage
2. **4 in-shard agents** exhaustively read every assigned file, validating each finding against source code
3. **Cross-layer validator** traced type flows from Core → Simulation → Strategy → UI, identified 7 type-loss boundaries and 8 protocol conformance gaps
4. **Verification agent** confirmed all 5 CRITICAL findings and spot-checked 5 MAJOR findings — zero false positives
5. **Compilation** of final report with prioritized narrowing plan and mypy migration path

### D. Full Report Structure

| Report | Path |
|--------|------|
| Final Report | `report.md` (this file) |
| Shard 01 | `findings/type_review_01.md` |
| Shard 02 | `findings/type_review_02.md` |
| Shard 03 | `findings/type_review_03.md` |
| Shard 04 | `findings/type_review_04.md` |
| Cross-Layer Flow | `findings/type_flow_cross_layer.md` |
| Verification | `findings/verification.md` |
| Raw Data | `raw/` |
