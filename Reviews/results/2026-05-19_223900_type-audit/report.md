# Type Safety Audit — Final Report

**Date:** 2026-05-19  
**Review Directory:** `Reviews/results/2026-05-19_223900_type-audit`  
**Phase 1 Scanner:** `Tools/type_audit/type_audit.py`  
**Mypy version:** 2.1.0 (strict mode)  
**Files scanned:** 846 production files under `game/`

---

## 1. Executive Summary

| Metric | Count |
|--------|-------|
| `-> Any` returns | 343 |
| `: Any` annotations | 561 |
| Missing return types (public API) | 43 |
| `# type: ignore` sites | 27 |
| `cast()` usages | 0 |
| Mypy strict-mode errors | 2,423 (2,108 real errors + 273 notes + 42 combat_lab) |
| **Overall type safety score** | **D+ (54/100)** |

**Mypy strict-mode readiness:** NOT ready. The codebase has 2,108 real mypy errors in strict mode. Research and Services layers are closest to strict-ready (0-1 errors). The UI layer accounts for 51% of all errors (1,084), largely from untyped `pygame_gui` library calls.

---

## 2. Any Density Heatmap by Layer

| Layer | `-> Any` | `: Any` | Missing Returns | Type Ignores | Cast | Density Score |
|-------|----------|---------|-----------------|--------------|------|--------------|
| ui | 263 | 143 | 11 | 7 | 0 | ⚠️ Very High |
| strategy | 19 | 168 | 30 | 17 | 0 | ⚠️ High |
| core | 30 | 55 | 0 | 0 | 0 | ⚠️ Medium |
| simulation | 15 | 106 | 1 | 3 | 0 | ⚠️ Medium |
| ai | 7 | 47 | 0 | 0 | 0 | ✅ Low |
| unknown/top-level | 9 | 37 | 1 | 0 | 0 | ✅ Low |
| assets | 0 | 0 | 0 | 0 | 0 | ✅ Clean |
| engine | 0 | 5 | 0 | 0 | 0 | ✅ Clean |
| research | 0 | 0 | 0 | 0 | 0 | ✅ Clean |
| services | 0 | 0 | 0 | 0 | 0 | ✅ Clean |

### Any Density by Component

- **UI layer (263 `-> Any` returns):** The heaviest concentration. 15 properties in `StrategyScreen`, 13 in `StrategyRenderer`, ~35 formatting/stat-getter functions in `stat_getters.py` and `stat_rows_dynamic.py`, and multiple filter/sort helpers across list windows.
- **Strategy layer (168 `: Any` annotations):** Primarily in data classes (star systems, planets, fleets) and protocol implementations.
- **Core layer (30 `-> Any` + 55 `: Any`):** Root cause — 30 protocol methods return `-> Any` in the foundational type contracts.
- **Simulation layer (106 `: Any`):** Concentrated in ship components, ability managers, and entity protocols.

---

## 3. Cross-Layer Type Flow — Critical Losses

### Top 3 Type-Loss Cascades

| Rank | Flow | Loss Sites | Impact |
|------|------|-----------|--------|
| 1 | **Vector2 `has-type` → 4 layers** | `core/math.py:22` | ~130 mypy errors (1 root cause) |
| 2 | **GameSession mutator properties → engines → UI** | `engine/game_session.py` (10 props) | Every engine that reads `session.fleet_mutator` loses type info |
| 3 | **Strategy engine lazy-default mutators → order handlers** | 9 sites across 6 files | Bridges untyped GameSession to typed sub-engines |

---

## 4. MyPy Strict-Mode Migration Path

### Recommended Adoption Order

| Rank | Layer | Errors/File | Files | Readiness |
|------|-------|-------------|-------|-----------|
| **1** | **research** | 0.0 | 4 | Adopt strict now |
| **2** | **services** | 0.1 | 7 | Adopt strict now (1 `import-untyped`) |
| **3** | **assets** | 5.0 | 2 | Quick win — only 2 files |
| **4** | **engine** | 3.7 | 3 | Quick win — only 3 files |
| **5** | **core** | 2.2 | 35 | Foundation — fixes benefit ALL higher layers |
| **6** | **ai** | 2.0 | 20 | Moderate effort |
| **7** | **simulation** | 3.5 | 120 | Significant — mostly `Ship` mixin attr-defined |
| **8** | **strategy** | 1.7 | 264 | GameSession properties account for ~30% |
| **9** | **unknown/top-level** | 2.7 | 6 | `app.py` scene accessors |
| **10** | **ui** | 3.5 | 308 | `pygame_gui` untyped — majority external |

### Error Type Distribution by Layer (Top 3)

| Layer | #1 Error | Count | #2 Error | Count | #3 Error | Count |
|-------|----------|-------|----------|-------|----------|-------|
| core | `has-type` (Vector2) | 50 | `no-any-return` | 16 | `assignment` | 8 |
| simulation | `attr-defined` (Ship) | 130 | `has-type` | 65 | `union-attr` | 63 |
| strategy | `no-any-return` | 131 | `arg-type` | 77 | `union-attr` | 65 |
| ui | `attr-defined` (pygame_gui) | 491 | `assignment` | 181 | `arg-type` | 144 |

---

## 5. Prioritized Remediation Plan

### Tier 1 — Foundation (fixing these benefits the entire codebase)

| # | Finding | Location | Severity | Effort | Impact |
|---|---------|----------|----------|--------|--------|
| 1 | `Vector2.__init__` implicit Optional cascades 130 `has-type` errors | `core/math.py:22` | CRITICAL | Medium | **Resolves ~130 errors across 4 layers** |
| 2 | 10 `GameSession` properties with `# type: ignore[no-untyped-def]` | `engine/game_session.py:202-258` | CRITICAL | Low | **Resolves ~30% of strategy errors, unblocks type flow** |
| 3 | 9 engine `_get_*_mutator()` methods returning `-> Any` | 6 engine files | MAJOR | Low | Bridges typed GameSession to sub-engines |
| 4 | `validate_enum` returns `-> T` but mypy can't verify subscript on `type[T]` | `core/validation_helpers.py:69,86` | MAJOR | Medium | Core public API, blocks strict core |
| 5 | `DesignCatalog.load_design_data` missing return type | `strategy/systems/design_catalog.py:236` | MAJOR | Trivial | One annotation |

### Tier 2 — Strategy Layer

| # | Finding | Location | Severity | Effort |
|---|---------|----------|----------|--------|
| 6 | 9 `GameSession` mutator properties + `handle_command` | `engine/game_session.py` | MAJOR | Low |
| 7 | `TurnEngine._time_phase` returns `-> Any` | `engine/turn_engine.py:286` | MAJOR | Low |
| 8 | `issuer_adapter.py` `# type: ignore[no-any-return]` on `getattr` | `engine/issuer_adapter.py:303` | MAJOR | Low |
| 9 | `BaseCommandHandler._resolve_build_entity`, `_resolve_queue_owner` return `-> Any` | `engine/handlers/base.py:323,377` | MAJOR | Medium |
| 10 | Superweapon handlers missing return types (`_precheck`, `_effect`) | 5 files under `engine/superweapon_handlers/` | MAJOR | Low |

### Tier 3 — Simulation + Collision

| # | Finding | Location | Severity | Effort |
|---|---------|----------|----------|--------|
| 11 | `seeker_ab` / `beam_ab` accessed without None guard on `Ability | None` (3 sites) | `seeker.py`, `targeting_system.py`, `collision.py` | CRITICAL | Low |
| 12 | `Ability.get_effective_stat` returns `-> Any` | `simulation/components/abilities/base.py:258` | MAJOR | Medium |
| 13 | `ICombatShip`, `IProjectile` protocol methods return `-> Any` | `simulation/interfaces/entity_protocols.py` | MAJOR | Low |
| 14 | `component_resource_manager.py` accesses `ability.trigger` on `list[Ability]` not `list[ResourceConsumption]` | `simulation/components/component_resource_manager.py:50` | MAJOR | Medium |

### Tier 4 — Core Protocols

| # | Finding | Location | Severity | Effort |
|---|---------|----------|----------|--------|
| 15 | 18 Core protocol methods return `-> Any` (`IStarSystem.global_location`, `IPlanet.location`, `IFleet.location`, etc.) | `core/protocols/strategy_entities.py` | MAJOR | Medium |
| 16 | `IPlanetMutator` methods use `Any` for known types (`owner_id`, `atmosphere`, etc.) | `core/protocols/strategy_mutators.py` | MAJOR | Low |
| 17 | `IFleetMutator.add_ship(ship: Any)` — should be `ShipInstance` | `core/protocols/strategy_mutators.py` | MAJOR | Low |

### Tier 5 — UI Layer

| # | Finding | Location | Severity | Effort |
|---|---------|----------|----------|--------|
| 18 | 15 `StrategyScreen` properties return `-> Any` (galaxy, empires, systems, facade, etc.) | `ui/screens/strategy_screen.py` | MAJOR | Low |
| 19 | 13 `StrategyRenderer` properties return `-> Any` | `ui/screens/strategy_renderer.py` | MAJOR | Low |
| 20 | 9 `Game` scene accessor properties return `-> Any` | `app.py` | MINOR | Trivial |
| 21 | `ShipControllableAdapter` 16 methods returning `-> Any` | `ai/interfaces/controllable.py` | MAJOR | Low |

---

## 6. Verification Results

| Total CRITICAL findings | 7 |
|--------------------------|----|
| Confirmed | 6 |
| Disputed | 0 |
| Inconclusive | 1 (reporting artifact — no actual CRITICAL in Shard 04) |
| MAJOR spot-checks | 9 confirmed |

### CRITICAL Findings Status

| ID | Finding | Rating |
|----|---------|--------|
| A01 | `seeker.py` — `seeker_ab` accessed without None guard on `Ability | None` | ✅ CONFIRMED |
| R01 | `design_catalog.py:236` — `load_design_data` missing return type | ✅ CONFIRMED |
| S02#1 | `app_bootstrap.py:310` — `_replay_combat_lab_fallback` missing return type | ✅ CONFIRMED (severity→MAJOR) |
| S02#2 | `pygame_gui_patch.py:90` — `_to_tuple` missing return type | ✅ CONFIRMED (severity→MINOR) |
| S03#1 | `validation_helpers.py:69,86` — `validate_enum` subscript access on `type[T]` | ✅ CONFIRMED |
| S03#2 | `game_session.py` — 10 properties with `# type: ignore[no-untyped-def]` | ✅ CONFIRMED |
| S04 | Shard 04 report claims 1 CRITICAL but no CRITICAL section | ⚠️ INCONCLUSIVE |

---

## 7. Trend Comparison

No prior type audit run found — this is the baseline. Future runs will show deltas against these numbers:
- `-> Any` returns: 343
- `: Any` annotations: 561
- Missing returns: 43
- `# type: ignore`: 27
- `cast()`: 0
- Mypy errors: 2,423

---

## 8. Single Highest-Impact Fix

**Fix `Vector2` typing in `game/core/math.py:22`:**

Change `y: float = None` → `y: float | None = None` (or refactor to `@dataclass`)

This single change resolves approximately **130 mypy `has-type` errors** across 4 layers (core, engine, simulation, AI) because `Vector2` is the primary coordinate type used throughout the codebase. Every function that creates or manipulates a `Vector2` currently suffers from `Cannot determine type of "x"` / `Cannot determine type of "y"` errors.

---

## 9. Appendices

### Appendix A: Type Ignore Audit Summary

| File | Sites | Justified? |
|------|-------|-----------|
| `game_session.py` | 10 | ❌ No — actively harmful, suppresses `no-untyped-def` |
| `battle_runner.py` | 2 | ⚠️ Partial — `replay_id` should be declared attribute |
| `controllable.py` | 0 | ✅ Clean |
| `save_game_service.py` | 2 | ❌ No — bypass for private attribute access |
| `attack_processor.py` | 1 | ⚠️ Marginal — `launched_in_battle_id` dynamic attr |
| `defeat_dialog.py` / `turn_failed_dialog.py` | 2 | ⚠️ Marginal — `_dismiss_button = None` override |
| `ship_detail_panel.py` | 2 | ⚠️ Marginal — dynamic `_proj315_*` attrs |
| `pygame_gui_patch.py` | 1 | ✅ Likely justified — monkey-patching pygame_gui |
| `simulation_adapter.py` | 1 | ⚠️ Marginal — `no-redef` for inner function |

### Appendix B: cast() Usage

**Zero `cast()` calls found in the entire production codebase.** Clean.

### Appendix C: Agent Findings Breakdown

| Report | Files | Findings | Critical | Major | Minor |
|--------|-------|----------|----------|-------|-------|
| `type_review_01.md` | 194 | 42 | 2 | 21 | 19 |
| `type_review_02.md` | 215 | 52 | 2 | 25 | 22 (+3 INFO) |
| `type_review_03.md` | 220 | 86 | 3 | 29 | 54 |
| `type_review_04.md` | 217 | 27 | 0 | 15 | 11 |
| `type_flow_cross_layer.md` | global | 44 type-loss | — | — | — |
| **Total** | **846** | **~250** | **7** | **90** | **106** |

### Appendix D: Full Report Links

- [Shard 01 Detailed Review](findings/type_review_01.md)
- [Shard 02 Detailed Review](findings/type_review_02.md)
- [Shard 03 Detailed Review](findings/type_review_03.md)
- [Shard 04 Detailed Review](findings/type_review_04.md)
- [Cross-Layer Type Flow](findings/type_flow_cross_layer.md)
- [Verification Report](findings/verification.md)
- [Raw mypy output](raw/mypy_report.json)
- [Raw Any heatmap](raw/any_heatmap.json)
