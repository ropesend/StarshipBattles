# Strategy Layer Tech Debt Review

**Date:** 2026-05-05  
**Review directory:** `Reviews/results/2026-05-05_strategy-layer-tech-debt-review`  
**Scope:** `game/strategy/` production code, with targeted checks against `tests/` coverage and project documentation.  
**Focus:** Tech debt, maintainability, and extensibility.

---

## Executive Summary

The strategy layer is functionally mature and has good recent documentation coverage, but it is accumulating coordination debt around its most important extension points: battles, effects, turn phases, commands, orders, navigation, and persistence. The layer boundary is mostly intact: no obvious `game.ui`, `game.ai`, or `game.research` imports were found inside `game/strategy`. The issue is more internal: many systems are partly decomposed, but still rely on central switchboards, hardcoded ability/order maps, global defaults, and compatibility fallbacks.

Overall score: **WARNING**.

The highest-priority remediation is to fix the battle registry bypass, then split and data-drive strategic effects aggregation. After that, the next best leverage is to make turn phases and command/order behavior declarative enough that adding one gameplay action no longer requires edits across 5-7 files.

## Review Method

Context read:

- `AGENTS.md`
- `.agents/CODEX.md`
- `docs/README.md`
- `docs/01_ARCHITECTURE.md`
- `docs/02_PATTERNS.md`
- `docs/03_CONVENTIONS.md`
- `docs/05_ERROR_HANDLING.md`
- `docs/systems/strategy_layer.md`

Deterministic checks run:

- `git status --short`
- Strategy file inventory and line counts
- `python -m radon cc game/strategy -s -a`
- Broad-catch scan for `except Exception`
- Global/default lookup scan for `get_default_*`, `ResourceCatalog.from_json`
- Direct JSON/open scan
- Hardcoded ability/order-name scan
- `python -m vulture game/strategy tests --min-confidence 100`

Coverage notes:

- `game/strategy` contains **197 Python files** and about **34,735 lines**.
- **12 production files** exceed the 500-line project ceiling.
- **33 production files** exceed 300 lines.
- `radon` average complexity is **A (3.54)**, but several important functions are high-risk hotspots.
- `vulture` found no 100%-confidence unused production code under `game/strategy`; its output was test-fixture noise.

## Top Ten Findings

### 1. Battle Resolver Bypasses Injected Registries

**Severity:** P1  
**Files:** `game/strategy/adapters/simulation_adapter.py:245-258`  
**Category:** Dependency injection / correctness / extensibility

`SimulationBattleResolver.resolve_battle(...)` accepts a `registries` argument and passes it into spec building and replay capture, but `_run_simulated_battle(...)` calls `run_battle(..., registry_provider=get_default_registry_provider())`.

That means the battle spec can be built from one registry set while simulation materialization uses the global default registry provider. This weakens mod support, test isolation, and any future per-session registry work.

**Impact:**

- Strategy battles can silently ignore session-specific registries.
- Tests that inject custom `GameRegistries` may pass through setup but fail or behave differently at battle runtime.
- Mods or scenario-specific registries become unreliable at the exact strategy/simulation boundary that should be strict.

**Recommended fix:**

Create an `IRegistryProvider` adapter over the supplied `GameRegistries` and pass that to `run_battle`. Add a regression test that injects a non-default registry and asserts materialized ships use it.

**Suggested project:** small targeted bug ticket, independent of broader cleanup.

### 2. Effects Aggregation Is a 193-Line Complexity Hotspot

**Severity:** P1  
**Files:** `game/strategy/services/system_effects_collector.py:62-75`, `game/strategy/services/system_effects_collector.py:281-430`  
**Category:** Complexity / extensibility

`system_effects_collector._aggregate` is a 193-line function with `radon` CC **47 (F)**. It owns source iteration, source error tolerance, ownership filtering, scope validation, activation-state lookup, provider DTO construction, legacy provider compatibility, mixed-kind validation, and final aggregation.

The supported ability set is also hardcoded in `SYSTEM_EFFECT_ABILITIES`, so a new strategic effect requires editing the collector instead of registering metadata.

**Impact:**

- Adding one new strategic effect is likely to require changes in collector internals and tests.
- Bugs in ownership or scope routing are hard to isolate.
- UI-facing effect rows, combat modifier emission, and data rules are coupled.

**Recommended fix:**

Split the collector into small units:

- `EffectAbilityRegistry` or metadata table for display name, kind, group key, scope rules, and value extraction.
- `EffectProviderBuilder` for per-provider row construction.
- `EffectAggregator` for active-status and aggregate-value computation.
- A deletion plan for `_legacy_provider_fields`.

Backfill characterization tests before extraction, especially for ownerful vs ownerless providers, activation state, mixed-kind validation, and combat-relevant effects.

### 3. TurnEngine Remains a Phase God Object

**Severity:** P2  
**Files:** `game/strategy/engine/turn_engine.py:139-218`, `game/strategy/engine/turn_engine.py:703-782`  
**Category:** Orchestration / extensibility

`TurnEngine` has a long constructor wiring 13+ collaborators, then hardcodes the complete per-tick phase sequence directly in `_process_tick`. The docs describe a tick phase registry pattern, but the live code still makes the central engine the mandatory edit point for every phase insertion or phase dependency change.

**Impact:**

- New per-tick systems create constructor growth, property growth, protocol growth, and `_process_tick` edits.
- Phase ordering is encoded as imperative code instead of inspectable data.
- Testing one phase boundary often requires standing up a large `TurnEngine`.

**Recommended fix:**

Introduce a small phase descriptor model:

- phase key
- callable resolver
- arguments resolver
- timing/error behavior
- tick gating

Then have `TurnEngine` own phase registration and execution rather than phase-specific logic. Keep the current order as a characterization baseline.

### 4. Command and Order Extension Requires Too Many Manual Edits

**Severity:** P2  
**Files:** `game/strategy/engine/handlers/registry_factory.py:44-115`, `game/strategy/facade/slices/command_dispatch_slice.py:50-219`, `game/strategy/data/order_types.py:18-67`, `game/strategy/services/action_time_resolver.py:31-49`, `game/strategy/engine/order_processor.py:688-732`  
**Category:** Duplication / command architecture

The strategy command model is spread across dataclasses, `OrderType`, category sets, facade dispatch helper methods, string-based handler registry entries, action-time maps, serializer branches, and processor dispatch tables.

Adding one new action can require touching all of these:

- command DTO
- order enum
- order category set
- handler registration
- facade dispatch helper
- action time map
- order execution dispatch
- serialization target handling
- UI code

**Impact:**

- High chance of partial implementation.
- Reviews must search the whole strategy layer to know whether a command is complete.
- Existing helper methods are very repetitive and difficult to keep consistent.

**Recommended fix:**

Create a declarative command/order registry that describes:

- command class
- order type
- handler
- category: movement/action/planet/build/instant
- action ability and time field
- serializer target codec
- optional facade helper exposure

The existing `CommandHandlerRegistry` can remain the runtime dispatcher, but its contents should be generated from a single command spec source.

### 5. Superweapon Behavior Is Duplicated by Ability

**Severity:** P2  
**Files:** `game/strategy/engine/superweapon_order_processor.py:151-190`, `game/strategy/engine/superweapon_order_processor.py:293-505`, `game/strategy/services/stabilizer_registry.py:54-67`  
**Category:** Duplication / data-driven behavior

Each superweapon method repeats a similar structure: check current order, resolve target/system, check stabilizer, find ship by hardcoded ability name, mutate galaxy state, pop order, maybe consume fleet, log event, and return `SuperweaponResult`.

The stabilizer side has moved toward a declarative registry, but superweapon execution has not.

**Impact:**

- New superweapons require copied control flow.
- Ability names and event behavior are embedded in methods.
- Common invariants are easy to drift, especially order popping and fleet removal.

**Recommended fix:**

Introduce `SuperweaponSpec` entries that define:

- order type
- required ability
- target resolver
- stabilizer scope
- effect executor
- consume-ship policy
- event type and event payload builder

Then rewrite each current method as data plus a small effect function. This should be a focused refactor project because it touches gameplay-critical mutation.

### 6. Navigation Mixes Pure Pathfinding, UI Projection, Intercept Logic, and Mutation

**Severity:** P2  
**Files:** `game/strategy/services/fleet_navigation_service.py:132-732`, `game/strategy/data/pathfinding.py:200-294`  
**Category:** Responsibility boundaries / testability

`FleetNavigationService` advertises itself as a single source of truth, but it spans four different concerns:

- destination resolution
- path calculation
- future path projection for UI
- mutation bridge for fleet execution

The lower-level `find_hybrid_path` is also complex and contains fallback behavior when warp graph data is missing.

**Impact:**

- A change to user-facing path previews can affect turn execution.
- Intercept and mutual-pursuit logic are difficult to reason about independently.
- The thread-local projection guard is a symptom of recursive coupling between projection and intercept.

**Recommended fix:**

Separate into:

- `PathPlanner`: pure path from current to destination.
- `DestinationResolver`: order-to-destination logic.
- `FleetPathProjector`: UI/forecast path simulation.
- `FleetMovementApplier`: mutable fleet bridge.

Keep compatibility wrappers during the refactor only if tests migrate in the same project; do not leave long-term aliases.

### 7. Domain Entities Still Carry Persistence and Compatibility Weight

**Severity:** P2  
**Files:** `game/strategy/data/planet.py:434-623`, `game/strategy/data/fleet.py:461-535`, `game/strategy/data/ship_instance.py:555-585`, `game/strategy/data/stars.py:527-769`  
**Category:** Entity bloat / persistence coupling

Core strategy entities continue to handle serialization, deserialization, defaulting for older shapes, derived behavior, and mutable game state. This is visible in the over-500-line files:

- `order_processor.py`: 771 lines
- `turn_engine.py`: 707 lines
- `superweapon_order_processor.py`: 662 lines
- `stars.py`: 649 lines
- `ship_instance.py`: 646 lines
- `fleet_navigation_service.py`: 636 lines
- `spec_compiler.py`: 608 lines
- `interfaces/engines.py`: 577 lines
- `production_engine.py`: 563 lines
- `galaxy.py`: 558 lines
- `planet.py`: 547 lines
- `fleet.py`: 511 lines

**Impact:**

- Entities are hard to understand and unsafe to extend.
- Save/load decisions leak into domain behavior.
- The no-save-migration policy is weakened by old-save defaults and fallback code.

**Recommended fix:**

Move persistence into serializer modules for each major entity, similar to existing `ShipInstanceSerializer`. For old-save defaults, decide explicitly whether they are current schema defaults or migration behavior; remove migration behavior.

### 8. Data-Driven Extensibility Is Incomplete

**Severity:** P2  
**Files:** `game/strategy/data/design_role.py:55-120`, `game/strategy/engine/planet_energy_engine.py:78-88`, `game/strategy/services/action_time_resolver.py:31-49`, `game/strategy/services/system_effects_collector.py:62-75`  
**Category:** Hardcoded gameplay metadata

The strategy layer has several registries, but many behavior decisions still rely on hardcoded ability-name sets:

- design role classification
- activatable strategic abilities
- order-to-ability action-time lookup
- system-effect display and effect kind
- superweapon ability requirements

This conflicts with the project convention against hardcoded type lists and makes modding or new ability families expensive.

**Impact:**

- New abilities require code edits even when component data already has the needed fields.
- Ability naming becomes part of control flow.
- Behavior may diverge between design data, UI display, and engine execution.

**Recommended fix:**

Move strategy ability metadata into data or a single registry:

- tags: `weapon`, `seeker`, `support`, `carrier`, `command`, `activatable`, `superweapon`
- order bindings
- effect display metadata
- activation/deactivation semantics

### 9. Global Default Lookups Weaken Session Isolation

**Severity:** P2  
**Files:** `game/strategy/engine/game_session.py:130-144`, `game/strategy/adapters/simulation_adapter.py:245-258`, `game/strategy/data/ship_instance.py:555-571`, `game/strategy/engine/production_engine.py:212-254`, `game/strategy/config/economy_config.py:103-120`  
**Category:** Dependency injection / testability

Several production paths still resolve global defaults internally. Some are probably acceptable module-level config singletons, but others bypass injected state or hide missing dependencies:

- `GameSession._resolve_registries()` always uses `get_default_registry_provider()`.
- `SimulationBattleResolver` uses `get_default_registry_provider()` during `run_battle`.
- `ShipInstance._lookup_design_max_hp()` falls back to global registry lookup.
- production rates and economy config are default singletons used by engines and services.

**Impact:**

- Session-specific data cannot be trusted end-to-end.
- Tests may need global state setup even when dependencies appear injectable.
- Feature work that introduces scenario/mod-specific registries will have subtle failure points.

**Recommended fix:**

Make `GameSession` accept registries or a registry provider explicitly. Treat module defaults as composition-root conveniences, not internal fallback paths. For config defaults, either inject config objects into engines or formalize them as immutable session settings.

### 10. Error and Compatibility Hygiene Has Drifted

**Severity:** P3  
**Files:** `game/strategy/data/ship_instance.py:67-74`, `game/strategy/services/design_validator.py:71-93`, `game/strategy/engine/turn_state_snapshot.py:53-61`, `game/strategy/data/planet.py:602-622`, `game/strategy/engine/superweapon_order_processor.py:436-438`  
**Category:** Conventions / maintainability

The broad-catch convention is mostly followed, but several strategy broad catches lack the required `# Intentional broad catch:` format. More importantly, some broad catches convert real data or validation problems into empty/default state.

Examples:

- `ShipInstance` catches any simulation materialization failure and creates empty component state.
- `DesignValidator` catches all exceptions around ship materialization and simulation validation.
- `Planet.from_dict` has old-save safe defaults despite the no-save-migration rule.
- `SuperweaponOrderProcessor` still handles legacy plain-string warp targets for in-flight orders.

**Impact:**

- Bugs become degraded behavior rather than explicit failures.
- New developers cannot easily tell which fallbacks are policy and which are leftovers.
- The no-migration convention becomes harder to enforce.

**Recommended fix:**

Audit strategy fallbacks in one cleanup project:

- add missing intentional broad-catch comments where broad catches are truly required
- narrow exception types where possible
- delete old-save and in-flight-order compatibility branches
- update tests to assert strict failures for invalid current schema

## Issue Matrix

| Rank | Finding | Severity | Main Risk | Suggested Track |
|------|---------|----------|-----------|-----------------|
| 1 | Battle resolver bypasses injected registries | P1 | Wrong battle data, broken mods/tests | Bug |
| 2 | Effects aggregation hotspot | P1 | Hard to extend strategic effects safely | Refactor project |
| 3 | TurnEngine phase god object | P2 | Every phase change touches core orchestrator | Refactor project |
| 4 | Command extension manual edits | P2 | Partial command implementation | Architecture project |
| 5 | Superweapon duplication | P2 | Copy-paste gameplay drift | Refactor project |
| 6 | Navigation responsibility mix | P2 | Preview/execution drift | Refactor project |
| 7 | Entity persistence bloat | P2 | Hard-to-change domain model | Serialization project |
| 8 | Hardcoded ability metadata | P2 | Poor mod/extensibility story | Registry/data project |
| 9 | Global default lookups | P2 | Weak session isolation | DI cleanup |
| 10 | Error/fallback hygiene drift | P3 | Hidden failures, convention drift | Cleanup ticket |

## Recommended Remediation Roadmap

### Phase 1: Quick Correctness Wins

1. Fix `SimulationBattleResolver` to pass a provider derived from the injected `GameRegistries`.
2. Add missing broad-catch justification comments or narrow the catches in the strategy sites found by scan.
3. Replace direct file JSON reads in strategy config/generation paths with `game.core.json_utils` where applicable.

Expected effort: 1-2 focused tickets.

### Phase 2: Effects and Ability Metadata

1. Create a strategy-effect metadata registry.
2. Split `_aggregate` into provider collection, provider normalization, aggregation, and row formatting.
3. Move effect display names, grouping, value kind, and scope rules out of the collector.
4. Remove `_legacy_provider_fields` after UI consumers are migrated.

Expected effort: one medium project with characterization tests.

### Phase 3: Commands, Orders, and Superweapons

1. Define a single command/order spec registry.
2. Generate or centralize handler registration, action-time binding, and category membership from the spec.
3. Convert superweapons to `SuperweaponSpec` plus effect executors.
4. Remove duplicated facade helper boilerplate where the public API can safely remain generic.

Expected effort: one larger architecture project, best split into command registry first, then superweapon cleanup.

### Phase 4: Turn and Navigation Decomposition

1. Introduce declarative turn phase descriptors.
2. Split `FleetNavigationService` into pure planning, destination resolution, projection, and mutation bridge.
3. Move entity serialization responsibilities out of large domain objects.

Expected effort: multiple projects; do not combine with feature work.

## Test Strategy

Because this is technical debt in gameplay-critical code, each remediation should follow strict TDD:

- Add characterization tests first for current behavior.
- Confirm failing tests before changing behavior.
- Keep tests narrow for the first DI fix.
- Use broader integration tests for effects, commands, and turn phases.
- Add mod/custom-registry tests anywhere global lookups are removed.

High-value test targets:

- `tests/unit/strategy/adapters/test_simulation_adapter.py`
- `tests/unit/strategy/services/test_system_effects_collector.py`
- `tests/unit/strategy/turn_engine/`
- `tests/unit/strategy/services/test_action_time_resolver.py`
- `tests/unit/strategy/services/test_fleet_navigation_*`
- `tests/integration/strategy/`

## Residual Risks

- This audit did not execute the full test suite.
- The review was static plus targeted tool scans; it did not include runtime profiling.
- The top ten list intentionally prioritizes maintainability/extensibility over gameplay bugs unless the debt directly threatens correctness.
- Some compatibility branches may be intentionally retained by current tests; those should be challenged against the explicit no-save-migration policy before removal.

## Raw Scan Summary

Line budget:

- 197 strategy Python files.
- About 34,735 lines in `game/strategy`.
- 12 files over 500 lines.
- 33 files over 300 lines.

Complexity:

- `radon` average: A (3.54).
- Highest hotspot: `system_effects_collector._aggregate`, CC 47.
- Other large hotspots include `strategic_ability_scanner._resolve_planets_for_scope`, `pathfinding.find_hybrid_path`, `galaxy_warp_generator._should_add_density_edge`, `simulation_adapter.resolve_battle`, and `combat_modifier_collector.collect_combat_modifiers`.

Dead code:

- `vulture game/strategy tests --min-confidence 100` produced no confirmed unused production-code findings for `game/strategy`.
- Output consisted of unused test fixtures/fixture parameters outside the reviewed production scope.

Layer boundary:

- No obvious `game.ui`, `game.ai`, or `game.research` imports found inside `game/strategy`.

