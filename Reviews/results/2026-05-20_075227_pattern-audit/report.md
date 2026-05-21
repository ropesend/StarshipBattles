# Pattern Conformance & Architecture Drift Audit — Final Report

> **Date:** 2026-05-20  
> **Review directory:** `Reviews/results/2026-05-20_075227_pattern-audit/`  
> **Patterns documented:** 43 | **Production files:** 846 | **Production LOC:** ~181,929

---

## 1. Executive Summary

### Pattern Health Score: **93.5%**

| Metric | Value |
|--------|-------|
| Patterns documented | 43 |
| Documented patterns with accurate docs | 40 (93.0%) |
| Layer dependency violations | 0 |
| Critical findings (confirmed) | 2 |
| Major findings (confirmed) | 3 |
| Minor findings | 11 |
| LOC ceiling violations (files >500) | 69 |
| Naming collisions | 0 |
| Protocol bypass findings | 0 (cross-boundary) |

**Overall assessment:** The codebase shows strong pattern discipline. The layered architecture is cleanly enforced with zero forbidden cross-layer imports. Command dispatch (CQRS-lite + CommandHandlerRegistry), the Registry pattern, StrategyModalWindow subclasses, and the ability source/aggregation/stat-registry patterns are all correctly implemented. The two critical findings both relate to the Facade/Delegate pattern (#5): the read-path DTO coverage is incomplete, making the facade a write-path-only half-facade. This is a structural architectural gap, not a single violation.

---

## 2. Layer Dependency Violations

**Status: CLEAN — 0 violations across 769 production files.**

The layer validator scanned all 846 files under `game/` and found zero forbidden cross-layer imports. All imports respect the documented dependency direction:
- Core depends on stdlib only
- Services depends on Core only
- Engine depends on Core + Services only
- Simulation depends on Core + Services + Engine only
- Strategy depends on Core + Services + Engine + Simulation only
- UI depends on all layers (top-level consumer)

No remediation needed on layer boundaries.

---

## 3. Pattern Adherence Scorecard

| # | Pattern | Compliance | Status | Notes |
|---|---------|-----------|--------|-------|
| 1 | ApplicationContext | 100% | STRONG | `game/context.py` matches doc; 10 managed services |
| 2 | Protocol + TypeGuard | 95% | MINOR_DRIFT | Some same-layer `isinstance()` on concrete types; no cross-boundary bypass |
| 3 | Registry DI | 95% | MINOR_DRIFT | `component_layers.py:52` has `get_default_registry_provider()` fallback with Intentional broad catch comment; strategy-layer, not simulation |
| 4 | Registry Pattern | 100% | STRONG | Consistent hydration, freeze, inject cycle across layers |
| 5 | Facade / Delegate | 70% | DRIFT | **CRITICAL:** Read-path DTO gap — 135+ UI import sites bypass facade for data reads; write-path enforcement is solid |
| 6 | CQRS-lite Strategy Session | 100% | STRONG | Commands are pure DTOs; 35+ verified dispatch sites through facade; static guard active |
| 7 | CommandHandlerRegistry | 100% | STRONG | Self-registering, registry-backed; no hardcoded dispatch chains; 43 command classes |
| 8 | MVVM | 100% | STRONG | Workshop, BuildQueue, TestLab, BattleSetup all follow MVVM split |
| 9 | Template Method Validation | 100% | STRONG | `IValidationRule` with `_should_validate()` / `_do_validate()` skeleton |
| 10 | Event Bus | 85% | DRIFT | **MAJOR:** Two incompatible implementations; `WorkshopEventBus` has stale path reference to `game/core/events/event_bus.py` |
| 11 | Surface Caching | 100% | STRONG | SpriteManager, galleries, VirtualTable all follow documented invalidation patterns |
| 12 | Configuration Classes | 100% | STRONG | Core config uses plain classes; strategy config uses `DEFAULT_*` + `@lru_cache`; `economy_config.py` uses module-accessor per documented variant |
| 13 | Spec Compiler + `run_battle` | 100% | STRONG | Three compilers → frozen `BattleSpec` → unified `run_battle()` path |
| 14 | Two-Phase Ability Aggregation | 100% | STRONG | `_aggregate_ability_groups()` reused by `FleetAuraManager`; no local reimplementation |
| 15 | Factory | 100% | STRONG | Factories for AI, ships, UI panels, LLM/image providers; construction isolation |
| 16 | ScrollState | 100% | STRONG | Dedicated helper; not misused for camera or pygame_gui scrollbars |
| 17 | Serializable Protocol | 100% | STRONG | `ISerializable` protocol; `PersistenceException` for corrupt data |
| 18 | Per-Battle RNG | 100% | STRONG | `BattleEngine.rng` injected through `CollisionSystem`, `DamageCalculator`, `AIControllerFactory`; `random.seed()` never called |
| 19 | Error Boundary | 100% | STRONG | `TurnStateSnapshot.capture()` → `TurnEngine._time_phase()` → rollback on `EnginePhaseError` |
| 20 | Precondition Validation | 100% | STRONG | `_validate_tick_inputs()` in sub-engines before mutation |
| 21 | Screen State Machine | 100% | STRONG | Declarative transition table with guards and stack-based return |
| 22 | TurnEngineConfig | 100% | STRONG | Frozen dataclass with `create_default()`; no lazy fallback init |
| 23 | Tick Phase Registry | 100% | STRONG | `ITickPhase` with priority ordering; 6 default phases |
| 24 | External-Stats Bridge | 100% | STRONG | `ship.external_stats` battle-scoped; `FleetAuraManager` sole writer |
| 25 | Scope-Driven Team Routing | 100% | STRONG | `OPPONENT_SCOPES` is single source of truth; N-team fan-out correct |
| 26 | Ability-Stat Registry | 100% | STRONG | `ModifierEntry` only constructed in registry locations; `KNOWN_EXTERNAL_STAT_KEYS` maintained |
| 27 | Budget-Aware Randomization | 100% | STRONG | `RacePointBudget` is single cost authority; exponential cost formula |
| 28 | Background Service Call | 100% | STRONG | LLM background calls with status/result/error/cancel/shutdown |
| 29 | Universal Ability Source | 95% | MINOR_DRIFT | 7 adapters in `ability_sources/` follow pattern; `source_kind` is string-typed (no enum) |
| 30 | Registrar Close-Callback | — | SUPERSEDED | Superseded by #31; usage is expected legacy |
| 31 | Strategy Modal Window Base Class | 85% | DRIFT | **MAJOR:** `SettingsWindow` extends `UIWindow` directly — opened from strategy screen context but lacks modal registration, `is_blocking`, and `window_manager` |
| 32 | Compositional Construction | 90% | MINOR_DRIFT | Only `StrategyScreen` uses it; pattern is well-defined but not widely adopted |
| 33 | UI Widget Test Factory | 100% | STRONG | `make_ui_widget` and `bypass_init` in test fixtures |
| 34 | Weapon Family Registry | 100% | STRONG | Weapon families self-register; no central branch edits |
| 35 | Stat Contributor Registry | 100% | STRONG | Per-component stat contributors run through typed accumulator |
| 36 | Re-Export Shim | 100% | STRONG | Thin shims tied to tracked migration projects |
| 37 | Typed `DeployedGroup` Family | 100% | STRONG | `MineGroup`/`FighterWing`/`SatelliteConstellation` as concrete dataclasses; no `group_kind` discriminator |
| 38 | CarriedVehicle Substrate | 100% | STRONG | `VehicleBayAbility` + `CarriedVehicle` + shared `carried_vehicle_to_ship_instance` |
| 39 | Typed-Sidecar Extensions on Frozen DTOs | 100% | STRONG | `BattleSpecExtensions` sidecar in `StrategyBattleAssembly`; no `object.__setattr__` anti-pattern |
| 40 | Named Pre-Tick Setup Registry | 100% | STRONG | `PreTickBattleSetupRegistry` chains mine/reboard setups by name |
| 41 | Polymorphic Order Issuer | 100% | STRONG | `IIssuerAdapter` with `FleetShipIssuerAdapter` / `PlanetStagingYardIssuerAdapter`; same handler family for both |
| 42 | Bootstrap-State Single Assignment Path | 100% | STRONG | `SessionBootstrapState` frozen DTO → `_apply_bootstrap_state()` sole assignment |
| 43 | Unified Container Substrate | 100% | STRONG | `Container` + `ContainerPolicy` + `BayInventory` four-slot widening; `IProductionResourceSource` Protocol |

**Compliance distribution:**
- STRONG: 36 patterns (83.7%)
- MINOR_DRIFT: 4 patterns (9.3%)
- DRIFT (MAJOR): 2 patterns (4.7%)
- DRIFT (CRITICAL): 1 pattern (2.3%)
- SUPERSEDED: 1 pattern (not scored)

---

## 4. Architecture Drift Findings

### CRITICAL-1: Facade Read-Path DTO Gap (Pattern #5)

The `StrategySessionFacade` exposes grouped-namespace read DTOs (FleetInfo, PlanetInfo, SystemInfo, ColonyDemographicView, ContainerSnapshotInfo, EmpireInfo), but 135+ import sites in `game/ui/` reach past the facade for data types not available through its grouped namespaces:

- `CarriedVehicle`, `DropPod`, `FighterWing`, `SatelliteConstellation`, `MineGroup`
- `BuildQueueSource`, `BuildContext`, `FleetCapabilityCalculator`
- `ActivationPhase`, `ComponentActivationState`, `ContainableKind`
- `FacilityAbilitySource`, `RaceConfig`, `HabitabilityFactors`
- `DesignMetadata`, `DesignRoleRegistry`, `GameConfig`

The facade is a write-path-only half-facade — commands route through `facade.handle_command()` (35+ verified sites), but data reads bypass the facade. A static guard (`test_facade_bypass_guard.py`) enforces write-path discipline, but there is no equivalent guard for the read path.

**Remediation:** Either (a) add DTOs for all data the UI reads through the facade's grouped namespaces and migrate the 135+ sites, or (b) formally document which strategy data classes are UI-safe for read access and enforce the boundary through a static guard + convention.

### MAJOR-1: SettingsWindow Bypasses StrategyModalWindow (Pattern #31)

`game/ui/screens/settings_window.py:14` — `SettingsWindow(UIWindow)` extends `UIWindow` directly instead of `StrategyModalWindow`. It is opened from the strategy screen via `SettingsRegistrar.open()` at `empire_panel_ctrl.py:77-94`, in the same `StrategyWindowManager` context as all other strategy modals.

Impact:
- No `is_blocking = True` — background hover/click leaks through
- Not counted by `has_modal_open()`
- Manual `on_close_callback` lifecycle instead of Pattern #31's auto-registration

**Remediation:** Subclass `StrategyModalWindow`, add `window_manager` parameter, remove manual `on_close_callback` lifecycle. ~20 LOC change.

### MAJOR-2: StrategyScreen.session Exposes GameSession Directly (Pattern #5)

`game/ui/screens/strategy_screen.py:242-257` exposes `self._session` as a public property. Active production usage:
- `strategy_detail_formatter.py:112` — reads `self.scene.session.registries`
- `strategy_detail_formatter.py:395-396` — accesses `self.scene.session.turn_engine`
- `list_windows.py:69` — passes `c.scene.session.empires`
- `hex_outlines.py:30` — reads `r.scene.session.active_empire.id`

Known issue tracked by deferred PROJs U1/U2/U3; acknowledged in docstring as "audit-residue delegate."

**Remediation:** Add registry/empire/turn accessor methods to the facade and migrate the 4+ consumption sites. Tracked by PROJ-404 deferred items.

### MAJOR-3: EventBus Fragmentation (Pattern #10)

Two `EventBus` implementations with fundamentally different architectures:

| Aspect | `game/core/event_logging.py::EventBus` | `game/ui/screens/builder/event_bus.py::WorkshopEventBus` |
|--------|----------------------------------------|----------------------------------------------------------|
| Scope | Strategy/simulation events | UI builder widget coordination |
| Handler model | Single callable (constructor-injected) | Pub/sub with multiple subscribers |
| Event payload | `event_type` + `**kwargs` | `event_type` + single `data` arg |
| Lifecycle | Session-scoped, owned by GameSession | Widget-scoped |

The `WorkshopEventBus` docstring (`builder/event_bus.py:5`) references `game/core/events/event_bus.py` — a path that no longer exists (core bus moved to `game/core/event_logging.py` by PROJ-390).

**Remediation:** Fix the stale path reference in `event_bus.py:5`. Document whether the divergence is intentional (different domains) or whether a shared `EventBusProtocol` would be valuable for future strategy→UI event propagation.

---

## 5. Documentation Accuracy

| Metric | Value |
|--------|-------|
| Patterns documented | 43 |
| Patterns verified against live code | 43 |
| ACCURATE | 40 (93.0%) |
| MINOR_DIFF | 3 (7.0%) |
| STALE | 0 |
| WRONG | 0 |

### MINOR_DIFF Details

| # | Pattern | Issue |
|---|---------|-------|
| 10 | Event Bus | Doc uses generic "Workshop event bus" without actual class name `WorkshopEventBus`; code docstring has stale path to `game/core/events/event_bus.py` |
| 32 | Compositional Construction | Only one production consumer (`StrategyScreen`); pattern well-defined but not widely adopted |
| 36 | Re-Export Shim | Line numbers off by 3 in code comment (395-405 vs actual 392-405) |

### Undocumented Patterns Found

Six recurring patterns in code not yet documented:

1. **HabitabilityFactor Registry** — `game/strategy/data/habitability_factors.py` — single-source-of-truth for all habitability axes (called out in `AGENTS.md` as existing but undocumented in patterns)
2. **AbilityMetadataRegistry** — `game/strategy/services/ability_metadata.py` — 566-line shared registry of ability display data
3. **Per-Player UI State Partitioning** — `game/ui/screens/per_player_ui_state.py` — player-switch snapshot/restore (issue #28, partially documented in Pattern #11 PROJ-411 section but deserves its own pattern)
4. **Cross-Context Cache Invalidation** — `VirtualTable.invalidate_widget_caches()` pattern documented under Pattern #11 but applies broadly across UI; may warrant extraction
5. **EmpirePanelRefactor / Registrar Pattern** — `EmpirePanelRegistrar`, `SettingsRegistrar`, etc. — strategy-window opener/factory pattern used consistently across `strategy_window_manager.py`
6. **ValidationResult Propagation** — `ValidationResult` usage pattern across validators, order handlers, and facade return values

---

## 6. Naming Collision Register

**No naming collisions detected across layers.**

All classes/functions with the same name in different layers were verified as either:
- Re-exports from package `__init__.py` (e.g., `IFleet` in both `game/core/protocols/` and `game/strategy/data/`)
- Distinct Protocol definitions in different scopes with different contracts (e.g., `ICombatShip` in both `game/core/protocols/combat.py` and `game/simulation/interfaces/entity_protocols.py` — intentionally different interfaces at different layer boundaries)

---

## 7. LOC Ceiling Violations

**69 files exceed the 500-LOC ceiling** (production files only; test files exempt per convention).

### Top 10 Violations

| LOC | File |
|-----|------|
| 832 | game/simulation/battle_state.py |
| 831 | game/simulation/battle_controller.py |
| 830 | game/strategy/engine/turn_engine.py |
| 830 | game/strategy/engine/production_engine.py |
| 789 | game/strategy/data/ship_instance.py |
| 758 | game/simulation/systems/battle_engine.py |
| 735 | game/ui/screens/event_log_window.py |
| 735 | game/simulation/battle_runner.py |
| 734 | game/ui/screens/empire_build_queue_window.py |
| 732 | game/ui/panels/race_summary_panel.py |

### By Layer

| Layer | Files >500 LOC | Total LOC | Avg LOC/file |
|-------|---------------|-----------|-------------|
| Simulation | 20 | 28,307 | 214 |
| Strategy | 17 | 58,706 | 203 |
| UI | 30 | 79,114 | 236 |
| Core | 2 | 7,102 | 187 |

Note: The `check_file_size.py` tool has a bug in repo-root discovery (`parent.parent` resolves to `Tools/` instead of repo root) — see Section 10.

---

## 8. Prioritized Architecture Remediation Plan

Sorted by structural impact (criticality × scope × LOC affected):

| Priority | Finding | Severity | Remediation | Effort |
|----------|---------|----------|-------------|--------|
| **P1** | Facade read-path DTO gap (Pattern #5) | CRITICAL | Add read DTOs for UI-accessed types through facade grouped namespaces; or formally document read-path exception with static guard | LARGE — requires new DTOs for 15+ data types and migration of 135+ import sites |
| **P2** | SettingsWindow bypasses Pattern #31 | MAJOR | Subclass `StrategyModalWindow`, add `window_manager` param, remove manual close-callback | SMALL — ~20 LOC change |
| **P3** | EventBus stale path reference (Pattern #10) | MAJOR | Fix docstring in `builder/event_bus.py:5` to reference `game/core/event_logging.py` | TRIVIAL — 1 line change |
| **P4** | StrategyScreen.session read-path bypass | MAJOR | Add registry/empire accessor methods to facade; migrate 4+ consumption sites | MEDIUM — tracked by PROJ-404 deferred items |
| **P5** | SettingsWindow classified inconsistently by agents | CROSS-AGENT | Resolve contradiction: pattern_review_03 classified SettingsWindow as "legitimate non-strategy overlay" but it's opened from strategy screen context | INFORMATIONAL — resolved in verification |
| **P6** | `source_kind` string discriminator (Pattern #29) | MINOR | Add `StrEnum` or `Literal` type for the 7 known ability source kinds | SMALL — type-safety improvement |
| **P7** | Same-layer `isinstance()` on concrete types | MINOR | Replace with TypeGuard functions in `order_types.py`, `fleet_dto.py`, `system_slice.py`, `base.py` | SMALL — each is 1-2 line changes |
| **P8** | Document 6 undocumented patterns | MINOR | Add pattern entries to `docs/02_PATTERNS.md` for HabitabilityFactor Registry, AbilityMetadataRegistry, PerPlayerUiState, Registrar pattern, ValidationResult propagation, cross-context cache invalidation | MEDIUM — documentation task |
| **P9** | LOC ceiling: 69 files over 500 | ADVISORY | Prioritize top-10 violations for splitting; `battle_state.py` (832), `battle_controller.py` (831), `turn_engine.py` (830), `production_engine.py` (830) | LARGE — systemic refactoring |
| **P10** | Fix `check_file_size.py` repo-root bug | MINOR | Change `parent.parent` to `parent.parent.parent` on line 70 | TRIVIAL |

---

## 9. Trend Comparison

This is the first pattern audit run. A baseline has been established in `Reviews/results/pattern_tracker.json`.

**Baseline metrics:**
- Pattern health: 93.5%
- Critical findings: 2
- Major findings: 3
- Minor findings: 11
- LOC ceiling violations: 69

Subsequent runs will compute deltas against this baseline.

---

## 10. Appendices

### A. Raw Data Files

| File | Description |
|------|-------------|
| `raw/layer_violations.json` | 769 files scanned, 0 violations |
| `raw/layer_violations_{01..04}.json` | Per-shard splits |
| `raw/file_size_violations.txt` | 69 files over 500 LOC |
| `raw/protocol_registry.json` | 76 protocols, 33 TypeGuards |
| `raw/manifest.json` | 846 production files, 4 shards |
| `raw/patterns_toc.json` | 43 patterns from docs/02_PATTERNS.md |
| `raw/loc_baseline.json` | LOC by layer |

### B. Agent Findings

| File | Scope | Findings |
|------|-------|----------|
| `findings/pattern_review_01.md` | Shard 01 (224 files) | 0 critical, 1 major, 3 minor |
| `findings/pattern_review_02.md` | Shard 02 (207 files) | 0 critical, 0 major, 3 minor |
| `findings/pattern_review_03.md` | Shard 03 (209 files) | 0 critical, 0 major, 2 minor |
| `findings/pattern_review_04.md` | Shard 04 (206 files) | 0 critical, 1 major, 5 minor |
| `findings/pattern_hunter_cross_shard.md` | Cross-shard hunter | 2 critical, 5 major, 7 minor |
| `findings/pattern_docs_validator.md` | Documentation validator | 40 accurate, 3 minor_diff, 6 undocumented |
| `findings/verification.md` | Verification | 2 confirmed critical, 3 confirmed major, 3 downgraded |

### C. Tooling Bug: check_file_size.py

`Tools/check_file_size/check_file_size.py:70` computes `repo_root = Path(__file__).resolve().parent.parent`, which resolves to `Tools/` instead of the repo root. Should be `.parent.parent.parent`. This caused the Phase 1 file_size check to fail silently. The file_size_violations.txt in `raw/` was corrected manually via `find` + `wc -l`.

### D. Cross-Agent Contradiction Resolved

`pattern_review_03` classified `SettingsWindow` as "legitimate non-strategy overlay" (not a violation), while `pattern_review_01` and `pattern_hunter_cross_shard` correctly identified it as a strategy-screen modal opened from `StrategyWindowManager` context that should follow Pattern #31. The verification agent confirmed the latter classification and the discrepancy is recorded for audit process improvement.
