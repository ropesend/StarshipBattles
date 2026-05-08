# Pattern Documentation Validation Report

## Summary
- Patterns Documented: 35 (from patterns_toc.json)
- Patterns Verified: 35
- Accurate: 29 | Minor Diff: 4 | Stale: 2 | Wrong: 0
- Undocumented Patterns Found: 2 (significant)

## Pattern Accuracy Assessment

| # | Pattern Name | Accuracy | Issues |
|---|-------------|----------|--------|
| 1 | ApplicationContext | ACCURATE | |
| 2 | Protocol + TypeGuard | ACCURATE | |
| 3 | Registry DI | ACCURATE | |
| 4 | Registry Pattern | ACCURATE | |
| 5 | Facade / Delegate | ACCURATE | |
| 6 | CQRS-lite Strategy Session | ACCURATE | |
| 7 | CommandHandlerRegistry | MINOR_DIFF | Doc says registry class is at `game/strategy/engine/command_handlers.py` — that file is now a re-export shim (PROJ-309 Phase 3.5). The canonical `CommandHandlerRegistry` class lives at `game/strategy/engine/handlers/base.py:399`. The shim preserves backward compatibility, but the doc should list `handlers/base.py` as the canonical location. |
| 8 | MVVM | ACCURATE | |
| 9 | Template Method Validation | ACCURATE | |
| 10 | Event Bus | ACCURATE | |
| 11 | Surface Caching | ACCURATE | |
| 12 | Configuration Classes | MINOR_DIFF | (1) Doc lists `BattleConfig` as a core plain class. It was renamed to `BattleTuning` in `game/core/config.py:111` (PROJ-224 DUP-SYS-003). The name `BattleConfig` now refers to `game/simulation/battle_config.py:18` — a `@dataclass`, which violates the "plain classes" contract. (2) `LLMConfig` and `ImageConfig` plain classes exist in `game/core/config.py` but are not listed in the pattern's primary-contract summary. |
| 13 | Spec Compiler + `run_battle` | ACCURATE | |
| 14 | Two-Phase Ability Aggregation | ACCURATE | |
| 15 | Factory | ACCURATE | |
| 16 | ScrollState | ACCURATE | |
| 17 | Serializable Protocol | ACCURATE | |
| 18 | Per-Battle RNG | ACCURATE | |
| 19 | Error Boundary | ACCURATE | |
| 20 | Precondition Validation | ACCURATE | |
| 21 | Screen State Machine | ACCURATE | |
| 22 | TurnEngineConfig | ACCURATE | |
| 23 | Tick Phase Registry | ACCURATE | |
| 24 | External-Stats Bridge | ACCURATE | |
| 25 | Scope-Driven Team Routing | ACCURATE | |
| 26 | Ability-Stat Registry | ACCURATE | |
| 27 | Budget-Aware Randomization | ACCURATE | |
| 28 | Background Service Call | ACCURATE | |
| 29 | Universal Ability Source | ACCURATE | |
| 30 | Registrar Close-Callback | STALE | Documented as "legacy slot cleanup only" and superseded by #31 — correct status. However, the pattern description still presents a full contract and how-to, which could mislead readers into implementing new windows against this pattern. Should be shortened to a "see #31" pointer. |
| 31 | Strategy Modal Window Base Class | ACCURATE | |
| 32 | Compositional Construction | ACCURATE | |
| 33 | UI Widget Test Factory | ACCURATE | |
| 34 | Weapon Family Registry | ACCURATE | |
| 35 | Stat Contributor Registry | ACCURATE | |

## Detailed Discrepancy Notes

### Pattern 7 — CommandHandlerRegistry (MINOR_DIFF)

**Doc location claim:** `game/strategy/engine/command_handlers.py`

**Reality:** That file is a transitional re-export shim (PROJ-309 sub-phase 3.5, 2026-04-27). The canonical `CommandHandlerRegistry` class is at `game/strategy/engine/handlers/base.py:399`. The shim re-exports all symbols so existing callers keep working, but the doc's "Where:" list should cite `game/strategy/engine/handlers/base.py` as the authoritative location.

**Recommendation:** Replace `game/strategy/engine/command_handlers.py` with `game/strategy/engine/handlers/base.py` (or list both with the shim noted as transitional).

### Pattern 12 — Configuration Classes (MINOR_DIFF)

**Doc says (line 260):** "Core config classes (`DisplayConfig`, `AIConfig`, `PhysicsConfig`, `BattleConfig`) are plain classes with class-level attributes."

**Reality:**
- `BattleConfig` was renamed to `BattleTuning` at `game/core/config.py:111` (PROJ-224 DUP-SYS-003).
- The name `BattleConfig` now points to `game/simulation/battle_config.py::BattleConfig` — a `@dataclass`, not a plain class. This directly conflicts with the doc's "Do not add `@dataclass` decorators" contract.
- `LLMConfig` (line 140) and `ImageConfig` (line 173) are plain config classes in the same file but are not listed in the pattern's summary line.

**Recommendation:** Change `BattleConfig` to `BattleTuning` in the doc. Add `LLMConfig` and `ImageConfig` to the list (or add "(and others)" qualifier). Note that `game/simulation/battle_config.py::BattleConfig` is a `@dataclass` and is NOT a core config class.

### Pattern 30 — Registrar Close-Callback (STALE)

**Status in doc:** Explicitly marked as "legacy slot cleanup pattern only. Modal tracking is superseded by pattern #31."

**Issue:** Despite the status banner, this pattern has a full section with contract, usage rules, and where-to-use guidance. It is the same length as active patterns. This invites new code to follow the legacy path.

**Recommendation:** Collapse to 2-3 lines stating "Superseded by #31. Only touch legacy code paths that still use slot cleanup."

### ALL TEST ANCHORS VERIFIED

The following guard/documentation test anchors all exist at their documented paths:
- `tests/unit/strategy/data/test_mutator_boundary_ast_guard.py` — exists
- `tests/unit/strategy/data/test_no_method_body_over_5_loc.py` — exists
- `tests/unit/strategy/engine/test_no_specs_tuple_literal.py` — exists
- `tests/unit/quality/test_no_unseeded_random.py` — exists
- `tests/integration/fleet_combat/test_battle_determinism.py` — exists
- `tests/unit/ui/widgets/test_scroll_state.py` — exists
- `tests/unit/core/test_serializable_protocol.py` — exists
- `tests/unit/ui/screens/test_strategy_modal_window.py` — exists
- `tests/integration/ui/test_editor_click_blocking.py` — exists
- `tests/unit/simulation/combat/test_weapon_registry.py::TestExtensibilityAcceptance` — exists
- `tests/unit/simulation/entities/stat_contributors/test_registry_pipeline.py` — exists
- `tests/unit/simulation/entities/test_stat_contributor_extension.py` — exists
- `tests/unit/strategy/turn_engine/test_no_lazy_fallback_init.py` — exists

## Retired Pattern Verification

The following retired/deleted patterns were verified as genuinely absent from production code:
- **SingletonMeta**: No `game/core/singleton.py` file exists. Remaining references are PROJ-258 migration comments only.
- **`.instance()` service access**: Not found in production code.
- **`BattleModeHandler` / `BattleMode` enum**: Deleted. Remaining references are in comments and test docstrings only.
- **`ShipCombatMixin`**: Not found. `Ship` correctly inherits `(PhysicsBody, ShipPhysicsMixin)`.
- **`ShipBuilderService`**: Renamed to `VehicleDesignService`. Old name appears only in a docstring at `game/simulation/services/vehicle_design_service.py`.

## Undocumented Patterns

### 1. HabitabilityFactor Registry (SIGNIFICANT)

**Where:** `game/strategy/data/habitability_factors.py`

**What:** A data-driven registry of `HabitabilityFactor` frozen dataclass objects for 17+ habitability axes (gravity, temperature, water, pressure, tectonic, magnetic, radiation, 10 atmospheric gases). Exposes `FACTOR_REGISTRY: Dict[str, HabitabilityFactor]`, `get_factor()`, `iter_scalar_factors()`, and `iter_gas_factors()`. Each factor carries display metadata, weight, tolerance, setpoint defaults, and a `step` constant. This is the single source of truth for all race habitability — the AGENTS.md references it as "Habitability Factor Registry (single-source-of-truth for all habitability axes)" but 02_PATTERNS.md has no numbered entry.

**Why it qualifies as a pattern:** Adding a new habitability axis means one data entry edit; both the habitability formula and the race setup UI iterate this registry. This is architecturally analogous to the Weapon Family Registry (#34) and Ability-Stat Registry (#26).

**Recommendation:** Add as pattern #36, or fold into #4 (Registry Pattern) as a notable example.

### 2. BuildContext Protocol (MODERATE)

**Where:** `game/strategy/data/build_context.py`

**What:** A `@runtime_checkable` Protocol enabling polymorphic build queue handling between `Planet` and `Fleet` contexts. Used by `BuildQueueScreen` and `BuildQueueController` to operate on either entity type without knowing the concrete class. Follows the Protocol+TypeGuard pattern (#2) but has no specific doc entry.

**Recommendation:** Add as a concrete example under pattern #2 (Protocol + TypeGuard) or note in the extension checklist.

## Documentation Update Recommendations

Priority-ordered list of doc changes needed:

1. **[HIGH] Pattern 12 — fix `BattleConfig` → `BattleTuning`**: The stale class name is misleading. `BattleConfig` now refers to a completely different class (`@dataclass` in `game/simulation/battle_config.py`). Also add `LLMConfig` and `ImageConfig` to the list (or expand "etc.").

2. **[HIGH] Pattern 30 — collapse to pointer**: Reduce the legacy Registrar Close-Callback section to 2-3 lines directing readers to Pattern #31. The current full-contract format invites misuse.

3. **[MEDIUM] Pattern 7 — update canonical file path**: Change "Legacy/runtime command handler registry: `game/strategy/engine/command_handlers.py`" to reference `game/strategy/engine/handlers/base.py` as the canonical location, noting the shim exists at `command_handlers.py`.

4. **[MEDIUM] Add HabitabilityFactor Registry**: Add as pattern #36 or fold as a notable example under #4 (Registry Pattern). The AGENTS.md already references it as a standalone pattern.

5. **[LOW] Add BuildContext Protocol as example**: Add a brief mention under pattern #2 or the extension checklist for polymorphic build queue handling.

6. **[LOW] doc header self-reference**: Line 3 says "Balanced compact derivative of `docs/02_PATTERNS.md`" — this is a circular self-reference. Remove or change to "Compact derivative of the full 02_PATTERNS.md (prior version)."
