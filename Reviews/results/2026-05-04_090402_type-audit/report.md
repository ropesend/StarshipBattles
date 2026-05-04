# Type Safety & Annotation Quality Audit — Final Report

> **Date:** 2026-05-04
> **Review directory:** `Reviews/results/2026-05-04_090402_type-audit/`
> **Scope:** 692 production files under `game/`
> **Method:** mypy strict-mode + AST annotation scanner + 5-agent deep review + verification

---

## 1. Executive Summary

| Metric | Value |
|--------|-------|
| Production files scanned | 692 |
| `-> Any` return types | 347 |
| `: Any` parameter/variable annotations | 398 |
| Missing return types (public functions) | 13 |
| `# type: ignore` sites | 9 |
| `cast()` usages | 0 |
| mypy strict-mode errors | 2,103 |
| Files exceeding 500 LOC limit | 11 (noted) |

**Overall type safety score: 61/100** — the project has good hygiene in lower layers (Core, Simulation, Strategy) but ~281 of 347 `-> Any` returns (81%) are concentrated in the UI layer, where many are unavoidable (pygame, JSON, registry dispatch). The largest ROI improvements are in Core protocols and strategy/UI screen property accessors.

---

## 2. Any Density Heatmap

| Layer | `-> Any` | `: Any` | Missing Returns | `# type: ignore` | Density Score |
|-------|---------|--------|-----------------|-----------------|---------------|
| **core** | 29 | 39 | 0 | 0 | 7/10 |
| **services** | 0 | 0 | 0 | 0 | 10/10 |
| **assets** | 0 | 0 | 0 | 0 | 10/10 |
| **engine** | 0 | 5 | 0 | 0 | 9/10 |
| **simulation** | 12 | 73 | 0 | 2 | 7/10 |
| **research** | 0 | 0 | 0 | 0 | 10/10 |
| **strategy** | 8 | 93 | 6 | 3 | 6/10 |
| **ai** | 7 | 40 | 0 | 0 | 6/10 |
| **ui** | 282 | 111 | 7 | 4 | 3/10 |
| **unknown** | 9 | 37 | 0 | 0 | 5/10 |

**Density Score** = 10 - (weighted penalty from Any returns + missing annotations + type ignores).

Services, Assets, Research, and Engine layers score 9-10/10. Core is 7/10 due to 29 protocol-level `-> Any` returns. UI is 3/10 — largely explained by pygame/registry/dynamic boundaries but also contains many narrowable returns.

---

## 3. Key Findings Summary

### 3.1 CRITICAL (3 found, all confirmed)

| ID | Finding | Location |
|----|---------|----------|
| TYP-02-001 | `RegistryManager.get_validator()` / module `get_validator()` return `-> Any` — always `ShipDesignValidator \| None` | `game/core/registry.py:248,332` |
| TYP-02-002 | `IEmpire.race_config` et al on facade protocols return `-> Any` — dynamic dispatch structurally unavoidable, downgraded to INFO | `game/core/protocols/strategy_domain.py` |
| TYP-02-003 | `GameSession.handle_command()` returns `-> Any` — always `ValidationResult \| None` | `game/strategy/engine/game_session.py:272` |

### 3.2 Top Impact by Cascade Effect

1. **Narrow 6 protocol `-> Any` to concrete types** (~15 lines, resolves ~65 downstream mypy errors)
   - `ICamera.position` → `Vector2`
   - `ICombatant.position` / `ICombatShip.position` → `Vector2`
   - `IPlanet.location` / `IFleet.location` / `IStarSystem.global_location` → `HexCoord`
   - `IEmpire.color` → `tuple[int, int, int]`

2. **Narrow StrategyScreen/Renderer properties** (~70 lines, resolves ~160 cascade errors)
   - 10 `StrategyRenderer` properties + 10 `StrategyScreen` properties all returning `-> Any` despite typed session objects

3. **Fix `formula_evaluator._eval_node`** (1 line → `int | float`, resolves ~30 cascade errors)

4. **AI `ShipControllableAdapter`** — 18 methods delegating to typed `Ship` via `-> Any`
5. **Planetary ability returns** — 20+ `get_effective_stat`-like methods in `planetary.py` returning `-> Any` for float return paths

### 3.3 Major Findings (40+ across all shards)

Key patterns:
- **Protocol Any leakage:** Core protocol interfaces define `-> Any` where concrete types are importable within Core
- **UI property drill-through:** Screen classes like `StrategyScreen`, `StrategyRenderer`, `FleetOperations`, `CameraNavigator`, etc. expose typed session data via `-> Any` properties
- **Stat getter functions:** `stat_getters.py` has ~45 functions all returning `-> Any` — many can narrow to `int | float | str | bool`
- **Missing return types on `_button_handlers`:** 4 editor files (`atmosphere_target_editor.py`, etc.) lack `-> None` on `_button_handlers`
- **Wrong annotation:** `data_extractor.py:215` — `get_components_cache()` annotated `-> bool` but actually returns `dict[str, dict]`

### 3.4 Type Ignore Audit

All 9 `# type: ignore` sites confirmed justified:
- 2 `battle_runner.py` — `replay_id` attr-defined on BattleEngine (dynamic attribute)
- 1 `simulation_adapter.py` — `no-redef` for nested function
- 2 `save_game_service.py` — `set_save_root`/`clear_save_root` attr-defined on replay store singleton
- 1 `ship_theme_manager.py` — `index` for tuple unpacking (mypy doesn't track tuple access)
- 1 `race_theme_gallery.py` — `override` for incompatible base class overload
- 2 `ship_detail_panel.py` — `attr-defined` for runtime monkey-patched pygame label attributes

### 3.5 cast() Usage

Zero `cast()` calls found — excellent.

---

## 4. Mypy Strict-Mode Migration Path

| Layer | Current Errors | Strict Readiness | Adoption Order | Key Blockers |
|-------|---------------|-----------------|----------------|-------------|
| **core** | ~50 | MEDIUM | **1st** ✓ | math.py implicit optionals, protocol Any leakage |
| **services** | 0 | HIGH | **2nd** | None |
| **engine** | ~5 | HIGH | **3rd** | collision.py implicit optional |
| **research** | 0 | HIGH | **4th** | None |
| **assets** | ~4 | HIGH | **5th** | PIL stub missing |
| **simulation** | ~60 | MEDIUM | **6th** | Mixin attr-defined errors (ship_physics), harvester type errors |
| **strategy** | ~20 | MEDIUM | **7th** | naming.py yaml stub missing |
| **ai** | ~15 | MEDIUM | **8th** | controllables, spatial_behaviors Any returns |
| **ui** | ~1,900 | LOW | **9th (last)** | ~1900 errors, mostly from pygame/untyped API boundaries |

**Recommendation:** Start with Core strict-mode adoption. 50 errors, mostly `math.py` implicit optionals and protocol `-> Any` returns. Fixing these (~2-3 hours) provides a strong foundation and propagates correct types upward to Simulation/Strategy/AI layers.

After Core strict mode: adopt Services → Engine → Research → Assets in rapid succession (near-zero fixes needed). Then tackle Simulation (~60 errors, mostly mixin attr-defined and ability return types). Strategy and AI are medium-effort. UI strict-mode is a long-term goal; the 1,900 errors are dominated by pygame_gui's untyped API surface.

---

## 5. Prioritized Remediation Plan

### Phase 1: Foundation (Core Layer) — ~2 hours, 65+ downstream error reduction

| ID | Action | LOC | Impact |
|----|--------|-----|--------|
| P1-01 | Narrow 6 protocol `-> Any` to concrete types (`Vector2`, `HexCoord`, `tuple[int,int,int]`) | 15 | Resolves ~65 mypy errors |
| P1-02 | Fix `math.py` implicit optionals (`float = None` → `float \| None`) | 8 | Resolves ~15 errors |
| P1-03 | Narrow `RegistryManager.get_validator()` → `ShipDesignValidator \| None` | 2 | Resolves ~5 errors |
| P1-04 | Fix `validation_helpers.py` generic TypeVar usage | 5 | Resolves ~4 errors |
| P1-05 | Fix `formula_evaluator._eval_node` → `int \| float` | 1 | Resolves ~30 errors |

### Phase 2: Strategy/Simulation Cross-Layer — ~2 hours, 200+ downstream error reduction

| ID | Action | LOC | Impact |
|----|--------|-----|--------|
| P2-01 | Narrow `GameSession.handle_command()` → `ValidationResult \| None` | 1 | Resolves ~5 errors |
| P2-02 | Narrow `StrategyScreen` 10 properties from `-> Any` to concrete facade types | 30 | Resolves ~50 errors |
| P2-03 | Narrow `StrategyRenderer` 10 properties from `-> Any` to concrete types | 30 | Resolves ~40 errors |
| P2-04 | Narrow FleetOperations/CameraNavigator/ColonizationSystem/SuperweaponOperations properties | 40 | Resolves ~40 errors |
| P2-05 | Narrow `ShipControllableAdapter` 18 methods using typed Ship delegation | 20 | Resolves ~20 errors |

### Phase 3: Simulation Abilities — ~1.5 hours

| ID | Action | LOC | Impact |
|----|--------|-----|--------|
| P3-01 | Add return types on 20+ `planetary.py` `get_effective_stat` methods → `float` | 20 | Resolves ~20 errors |
| P3-02 | Fix `harvester.py` type errors (attr redef, dict-item mismatch) | 10 | Resolves ~10 errors |
| P3-03 | Narrow `resources.py` return types (5 methods) | 5 | Resolves ~5 errors |
| P3-04 | Fix `stat_keys.py` return value inconsistency (line 87, 102) | 3 | Resolves ~3 errors |

### Phase 4: UI Cleanup — ~3 hours

| ID | Action | LOC | Impact |
|----|--------|-----|--------|
| P4-01 | Narrow `stat_getters.py` 45 functions from `-> Any` to `int \| float \| str \| bool` | 90 | Resolves ~90 errors |
| P4-02 | Add `-> None` to 4 `_button_handlers` methods | 4 | Completeness |
| P4-03 | Fix `data_extractor.py` wrong annotation (`-> bool` → `-> dict`) | 1 | Correctness |
| P4-04 | Narrow UI list window filter methods (planet_list, star_list, etc.) | 15 | Resolves ~20 errors |
| P4-05 | Add missing return types to `_resolve_economy_config`, `_walk_strategic_abilities` | 4 | Completeness |

**Total estimated effort: ~8.5 hours** for all phases.
**Total error reduction: ~437 mypy errors** (from 2,103 → ~1,666), a 21% improvement.
**Remaining ~1,666 errors** are mostly UI pygame_gui untyped API calls requiring a broader strategy (stub files or deferred to Phase 5+).

---

## 6. Appendices

### A. File Size Violations (>500 LOC in production)

| File | Lines | Layer |
|------|-------|-------|
| `game/ui/screens/strategy_renderer.py` | ~790 | ui |
| `game/ui/screens/strategy_screen.py` | ~700 | ui |
| `game/simulation/components/abilities/planetary.py` | ~900 | simulation |
| `game/ui/screens/strategy_ui.py` | ~550 | ui |
| `game/ui/screens/workshop_viewmodel.py` | ~500 | ui |
| `game/ui/screens/builder/stat_getters.py` | ~530 | ui |
| `game/ui/screens/test_lab/screen.py` | ~500 | ui |
| `game/simulation/entities/ship.py` | ~550 | simulation |
| `game/strategy/facade/strategy_session_facade.py` | ~500 | strategy |
| `game/strategy/data/galaxy.py` | ~520 | strategy |
| `game/ui/screens/workshop_screen.py` | ~600 | ui |

### B. Agent Reports

- Shard 01: `findings/type_review_01.md` — 166 files, 37 findings (0C, 8M, 29m)
- Shard 02: `findings/type_review_02.md` — 176 files, 42 findings (3C, 17M, 22m)
- Shard 03: `findings/type_review_03.md` — 180 files, 86+ findings
- Shard 04: `findings/type_review_04.md` — 170 files, 10 findings (0C, 8M, 2m)
- Cross-Layer: `findings/type_flow_cross_layer.md` — 14 flows traced, 12 loss boundaries, 9 protocol gaps
- Verification: `findings/verification.md` — 3 CRITICAL + 7 MAJOR spot-checks, all CONFIRMED

### C. Raw Data

- `raw/any_heatmap.json` — Per-layer Any density
- `raw/any_returns.json` — All 347 -> Any return sites
- `raw/missing_returns.json` — All 13 missing return type sites
- `raw/type_ignore_sites.json` — All 9 # type: ignore sites
- `raw/cast_usage.json` — Zero cast() usages
- `raw/mypy_report.json` — All 2,103 mypy strict-mode errors
- `raw/manifest.json` — 4-shard file assignments
