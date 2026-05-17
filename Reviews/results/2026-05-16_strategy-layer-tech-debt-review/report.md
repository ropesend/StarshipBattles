# Strategy Layer Tech Debt Review

**Date:** 2026-05-16  
**Review directory:** `Reviews/results/2026-05-16_strategy-layer-tech-debt-review`  
**Scope:** `game/strategy/` production code, with targeted cross-checks against strategy docs and adjacent extension seams.  
**Focus:** Maintainability, extensibility, and tech-debt payoff priority.

---

## Executive Summary

The strategy layer is better structured than it was in the previous audit, but it still carries a few high-interest debt clusters that will slow any major feature work:

- battle integration remains centered on one oversized translation module
- session/bootstrap/persistence concerns are still tangled into runtime objects
- command/order metadata is declarative in some places but still duplicated or snapshotted in others
- several newer subsystems are implemented by overloading existing abstractions instead of introducing narrower domain models

Overall debt level: **HIGH**.

If the goal is to reduce tech debt before major strategy work, the best payoff is:

1. break apart battle spec compilation and runtime production/persistence coupling
2. finish consolidating command/order metadata into one live source of truth
3. stop letting registry/config modules accumulate business hooks and UI-era compatibility surfaces

## What Improved Since The 2026-05-05 Review

Several items from the earlier strategy-layer review are clearly in better shape now:

- The battle-registry threading problem appears remediated: `SimulationBattleResolver` now forwards resolved registries into the simulator path instead of silently falling back inside `run_battle` (`game/strategy/adapters/simulation_adapter.py:147-155`, `game/strategy/adapters/simulation_adapter.py:280-287`).
- Strategic effect display metadata is no longer hardcoded inside `system_effects_collector`; it now has a dedicated metadata registry (`game/strategy/services/effect_ability_metadata.py:108-141`).
- Turn processing is no longer encoded only as one imperative `_process_tick` body; the live turn loop now executes descriptor lists through `_run_phases(...)` (`game/strategy/engine/turn_engine.py:339-370`, `game/strategy/engine/turn_engine.py:747-757`).

This report therefore focuses on the debt that still remains after those improvements.

## Review Method

Context read:

- `AGENTS.md`
- `.agents/CODEX.md`
- `docs/README.md`
- `docs/01_ARCHITECTURE.md`
- `docs/02_PATTERNS.md`
- `docs/03_CONVENTIONS.md`
- `docs/systems/strategy_layer.md`
- `Reviews/protocols/07_technical_debt_review.md`
- prior strategy-layer review artifact for historical comparison only

Deterministic checks run:

- `git status --short`
- `python -m radon cc game/strategy -s -a`
- `python -m radon raw game/strategy`
- targeted `rg` scans for defaults, fallbacks, compatibility markers, hardcoded ability tables, and order metadata
- targeted file inspection of the largest and most central strategy modules

This was a static architecture/maintainability review. I did **not** run the full test suite.

## Strategy Layer Snapshot

- `game/strategy` currently contains **251 Python files** and about **43,322 lines**.
- **10** production files exceed the project’s 500-line ceiling.
- **42** production files exceed 300 lines.
- `radon` average complexity is **A (3.46)**, but the important hotspots are concentrated in extension seams rather than broad average complexity.
- A simple marker scan found **294** occurrences of `legacy`, `fallback`, or `compat` inside `game/strategy`, which is a strong signal that migration residue is still shaping the live architecture.
- `StrategySessionFacade` still exposes **53** methods.
- `game/strategy/engine/commands/__init__.py` defines **41** command dataclasses.
- `game/strategy/interfaces/engines.py` currently holds **17** engine ABCs in one file.

### Heat Map

| Area | Current signal | Why it matters |
|------|----------------|----------------|
| Battle integration | `spec_compiler.py` 857 LOC, `simulation_adapter.py` 553 LOC | New combat-adjacent strategy features still converge on one translation path |
| Session / commands | `game_session.py` 513 LOC, command DTO catalog + registry + order constants | New actions still fan out across multiple metadata surfaces |
| Runtime persistence | `production_spawner.py` 552 LOC, `design_library.py` 437 LOC, `save_game_service.py` 414 LOC | Turn processing depends directly on disk layout and persistence conventions |
| Entity surface | `ship_instance.py` 695 LOC, `fleet.py` 570 LOC | Domain objects still absorb bridge/persistence/substrate concerns |
| Turn loop | `turn_engine.py` 663 LOC, `turn_phase_registry.py` 418 LOC, `interfaces/engines.py` 625 LOC | Descriptor-driven orchestration exists, but behavior is still spread across central control files |

## Top 10 Debt Items

### TD-01: Battle spec compilation is still a central integration knot

**Interest:** Very High  
**Size:** Large  
**Locations:** `game/strategy/combat/spec_compiler.py:78-260`, `game/strategy/combat/spec_compiler.py:225-260`, `game/strategy/adapters/simulation_adapter.py:309-340`

**Problem:**  
`spec_compiler.py` is still the place where strategy fleets become battle teams, environmental and team modifiers become combat modifier stacks, mine groups get split out, post-battle writeback gets attached, and pre-tick tactical setup gets smuggled through spec side channels like `_mine_groups`, `_owner_to_team_id`, and `_engine_ref`.

**Why it hurts:**  
This is one of the highest-change extension seams in the whole layer. Adding any new “strategy affects battle” feature still means touching a large translator plus the adapter that interprets its private side-channel attributes. The architecture has moved away from pre-mutation, but not yet to explicit extension objects.

**Payoff approach:**  
Split this into explicit builders:

- `TeamSpecBuilder`
- `StrategyModifierStackBuilder`
- `PostBattleHookBuilder`
- `PreTickBattleSetupRegistry`

The goal is to replace side-channel spec attributes with typed extension slots or a dedicated strategy-battle assembly DTO.

### TD-02: `GameSession` is still both session model and composition root

**Interest:** Very High  
**Size:** Large  
**Locations:** `game/strategy/engine/game_session.py:77-198`, `game/strategy/engine/game_session.py:202-216`, `game/strategy/engine/game_session.py:299-430`, `game/strategy/engine/game_session.py:432-520`

**Problem:**  
`GameSession` still owns runtime state, command dispatch, preview helpers, registry resolution, mutator/service wiring, turn-engine construction, event-bus creation, and save rehydration. `from_dict()` bypasses `__init__` and then replays a large amount of bootstrapping manually.

**Why it hurts:**  
Any new dependency or lifecycle rule has to be added in at least two places: fresh construction and rehydration. That creates drift risk and makes the session harder to reason about as a pure domain object.

**Payoff approach:**  
Introduce one shared bootstrap/rehydration path, for example:

- `SessionBootstrap` or `GameSessionFactory`
- `SessionRuntimeServices`
- `SessionPersistenceAdapter`

`GameSession` should become the owned state plus small runtime behaviors, not the place where the whole strategy world gets composed.

### TD-03: Command and order metadata still lives in multiple truth surfaces

**Interest:** Very High  
**Size:** Large  
**Locations:** `game/strategy/engine/commands/__init__.py:1-520`, `game/strategy/engine/commands/registry.py:70-426`, `game/strategy/data/order_types.py:52-108`, `game/strategy/services/action_time_resolver.py:35-50`, `game/strategy/services/action_time_resolver.py:101-106`

**Problem:**  
The command registry is a real improvement, but the order system still has at least four important metadata surfaces:

- the 41-command DTO catalog in `commands/__init__.py`
- `CommandRegistry` specs
- duplicated `MOVEMENT_ORDER_TYPES` / `ACTION_ORDER_TYPES` / `PLANET_ACTION_ORDER_TYPES` constants in `order_types.py`
- `ActionTimeResolver.ORDER_TO_ABILITY_MAP`, which is built once at import time

`order_types.py` explicitly documents that the duplication exists because deriving those sets live would create cycles. `CommandRegistry` explicitly supports `replace=True` for overlays, but `ActionTimeResolver` snapshots its map at import and does not refresh when the registry changes.

**Why it hurts:**  
This is the clearest remaining example of “mostly declarative, but not fully.” Adding or overlaying commands is still fragile because some consumers use the live registry and some use duplicated or frozen derivatives.

**Payoff approach:**  
Create one cycle-safe, lazily derived `OrderMetadataView` object and make all consumers read through it. That removes the import-time cache and the duplicated category constants without reintroducing the original tuple-literal design.

### TD-04: The phase registry is only partly declarative

**Interest:** High  
**Size:** Medium-Large  
**Locations:** `game/strategy/engine/turn_phase_registry.py:124-253`, `game/strategy/engine/turn_phase_registry.py:273-395`

**Problem:**  
The turn loop now reads a phase descriptor list, but the registry module also owns substantial business behavior in hook helpers:

- logging and turn-start side effects
- environment event accumulation
- movement diffing
- direct mutation of `emp._booster_dirty`
- construction and invocation of `MinefieldResolver`
- fleet pruning after mine resolution
- lazy local construction of `PlanetModifierEffectEngine`

**Why it hurts:**  
The code now looks data-driven, but important gameplay behavior still hides in hook functions attached to the data. That makes phase work harder to audit because the registry is no longer just ordering metadata.

**Payoff approach:**  
Keep descriptors declarative and move hook bodies into dedicated collaborators or phase classes. If a phase needs post-processing, that should be an explicit engine/phase object, not an opaque hook attached in the registry table.

### TD-05: Runtime production is tightly coupled to the savegame filesystem

**Interest:** High  
**Size:** Large  
**Locations:** `game/strategy/engine/production_spawner.py:157-216`, `game/strategy/engine/production_spawner.py:238-257`, `game/strategy/systems/design_library.py:107-137`, `game/strategy/systems/design_library.py:153-172`, `game/strategy/systems/design_library.py:183-230`, `game/strategy/systems/design_library.py:298-301`, `game/strategy/systems/save_game_service.py:25-61`, `game/strategy/systems/save_game_service.py:81-140`

**Problem:**  
Live production behavior depends directly on savegame folders and on-disk design files. `ProductionSpawner` repeatedly constructs `DesignLibrary(save_path, empire.id)` to load designs during turn execution. `DesignLibrary` chooses between save folders and temp folders, manages directory creation, and optionally depends on `FacadeSessionState` for UI cache invalidation. `SaveGameService` also owns a static `_replay_store` hook.

**Why it hurts:**  
This makes runtime gameplay logic depend on persistence conventions. It also means UI caching rules and filesystem policy are embedded inside the same classes that production uses in the turn loop.

**Payoff approach:**  
Split “design persistence” from “runtime design catalog”:

- a repository/service for disk I/O
- an in-memory runtime catalog for production/spawning
- instance-owned replay-store coordination instead of static hooks

That would make future backends, batch tooling, and headless simulation much cleaner.

### TD-06: `ShipInstance` is still an overloaded entity facade

**Interest:** High  
**Size:** Large  
**Locations:** `game/strategy/data/ship_instance.py:97-176`, `game/strategy/data/ship_instance.py:233-310`, `game/strategy/data/ship_instance.py:338-369`, `game/strategy/data/ship_instance.py:473-537`, `game/strategy/data/ship_instance.py:799-840`

**Problem:**  
`ShipInstance` holds identity, damage state, activation state, resource state, cargo, carried vehicles, pod storage, design-role state, registry DI, stat caching, simulation bridging, serializer forwarding, and display helpers. Delegates exist, but the façade still exposes an extremely broad mixed surface.

**Why it hurts:**  
This class remains the easiest place to “just add one more ship concern,” which is exactly how long-term entity bloat happens. It also knows too much about both runtime behavior and persistence/bridge behavior.

**Payoff approach:**  
Shrink `ShipInstance` to durable state + a small identity API. Move bridge, serializer, display, and advanced cargo/bay concerns behind narrower service boundaries so new ship mechanics stop inflating the core entity.

### TD-07: Strategy ability metadata is only partially registry-driven

**Interest:** High  
**Size:** Medium  
**Locations:** `game/strategy/services/effect_ability_metadata.py:108-141`, `game/strategy/data/design_role.py:55-129`, `game/strategy/engine/planet_energy_engine.py:79-89`, `game/strategy/services/action_time_resolver.py:89-118`

**Problem:**  
The strategy layer now has a good metadata registry for strategic effects, but other strategy behaviors still rely on hardcoded ability-name sets:

- design-role classification
- activatable energy-draining abilities
- action-time lookup special cases

**Why it hurts:**  
The architecture is inconsistent: some ability families are data-driven, while others still require code edits across multiple modules. That makes new ability work slower and encourages name-based control flow.

**Payoff approach:**  
Promote ability metadata to one strategy-facing registry/tag surface that can answer questions like:

- does this ability define a design role hint?
- is it activatable and energy-draining?
- which action-time field does it use?
- is it a strategic effect and of what kind?

### TD-08: The strategy facade boundary is still oversized and legacy-aware

**Interest:** Medium-High  
**Size:** Medium  
**Locations:** `game/strategy/facade/strategy_session_facade.py:7-15`, `game/strategy/facade/strategy_session_facade.py:61`, `game/strategy/facade/strategy_session_facade.py:115-165`, `game/strategy/facade/strategy_session_facade.py:219-226`, `game/strategy/facade/strategy_session_facade.py:434-477`

**Problem:**  
The monolithic facade was split into slices internally, but the public boundary still preserves:

- 53 public methods
- 28 `dispatch_*` helpers
- cache-forwarding properties kept for legacy tests

**Why it hurts:**  
The internal refactor reduced file-level pain, but the boundary itself is still wider than necessary. New UI-strategy features are still incentivized to add one more facade method rather than converging on a smaller stable API.

**Payoff approach:**  
Treat the next cleanup as an API-reduction project, not another internal split. Deprecate cache forwarders, group read/write surfaces by feature domain, and migrate tests away from private-facade assumptions.

### TD-09: Engine protocols are concentrated in a single 17-interface file

**Interest:** Medium  
**Size:** Medium  
**Locations:** `game/strategy/interfaces/engines.py:53-754`

**Problem:**  
Nearly every turn-engine seam still lives in one large interface module. Today that file contains 17 engine ABCs ranging from movement and production to happiness, water, and component activation.

**Why it hurts:**  
Protocol churn becomes centralized. Small local contract changes create wide diffs and broad import touchpoints, which discourages incremental contract tightening.

**Payoff approach:**  
Split engine contracts by domain or colocate them with their owning subsystems, then re-export only the minimal public seams that `TurnEngineConfig` actually needs.

### TD-10: Deployable small craft and minefields still overload generic fleet/ship cargo abstractions

**Interest:** Medium  
**Size:** Medium-Large  
**Locations:** `game/strategy/engine/minefield_resolver.py:147-163`, `game/strategy/engine/minefield_resolver.py:243-307`, `game/strategy/data/ship_instance.py:135-146`, `game/strategy/data/ship_instance.py:516-529`, `game/strategy/engine/handlers/base.py:209-229`

**Problem:**  
The current deployable-object substrate works, but it bends generic abstractions:

- mine groups are `Fleet` objects whose first ship acts as the mine container
- `ShipInstance.carried_items` stores both legacy drop-pod dicts and typed `CarriedVehicle` entries
- command handlers need `group_kind` guards to stop generic fleet actions on deployed groups

**Why it hurts:**  
This keeps the short-term surface compatible, but every new deployable strategic object will compound the same overload pattern. That is manageable for three kinds of payloads and increasingly awkward after that.

**Payoff approach:**  
Introduce a more explicit deployable-group or strategic-payload model before adding the next family of deployables. If full model separation is too large, at least stop using “first ship’s carried_items” as the storage substrate.

## Priority Order

### Priority 1: Fix the architecture that compounds fastest

1. `TD-01` battle spec compiler knot
2. `TD-03` command/order metadata fragmentation
3. `TD-05` runtime production + filesystem coupling

These are the items most likely to multiply the cost of future strategy work.

### Priority 2: Reduce central object pressure

4. `TD-02` `GameSession` lifecycle/composition sprawl
5. `TD-06` `ShipInstance` overload
6. `TD-08` oversized facade boundary

These are the items that make normal feature work feel heavier than it should.

### Priority 3: Improve extension hygiene

7. `TD-04` partially declarative phase registry
8. `TD-07` partial ability-metadata convergence
9. `TD-09` engine interface monolith
10. `TD-10` deployable-object substrate overload

These are not the first wins, but they will keep generating friction if left in place.

## Suggested Payoff Roadmap

### Wave 1: High-ROI architecture cleanup

- Build an explicit strategy-battle assembly pipeline (`TD-01`)
- Replace duplicated order metadata with one live derived view (`TD-03`)
- Introduce a runtime design repository/catalog split for production (`TD-05`)

Expected outcome: the three most common extension seams become more predictable before new feature work lands on them.

### Wave 2: Lifecycle and entity slimming

- Extract bootstrap/rehydration from `GameSession` (`TD-02`)
- Reduce `ShipInstance` to durable state + a smaller behavioral shell (`TD-06`)
- start shrinking the public facade boundary (`TD-08`)

Expected outcome: lower change blast radius for ordinary strategy work.

### Wave 3: Consistency pass

- move business hooks out of the phase registry (`TD-04`)
- converge hardcoded ability tables into a shared strategy-ability metadata surface (`TD-07`)
- split interface monoliths and revisit deployable-object modeling (`TD-09`, `TD-10`)

Expected outcome: future systems extend existing seams instead of inventing one-off local tables.

## Residual Risks

- This review did not run the full suite; it is a static maintainability audit, not a behavioral verification run.
- Some compatibility/fallback code exists to keep current tests and current save workflows green; removing it will need careful TDD even when the end goal is deletion.
- Several issues are interconnected. For example, `TD-03`, `TD-07`, and `TD-08` will be easier if they are planned as one architecture arc rather than isolated tiny tickets.

## Bottom Line

The strategy layer has made real progress since the previous audit, but the remaining debt is concentrated in central extension seams rather than random code quality noise. That is exactly the kind of debt that slows large feature work.

If only one architecture arc is funded next, make it:

1. battle assembly cleanup
2. command/order metadata convergence
3. runtime production/persistence decoupling

Those three changes would materially reduce the maintenance cost of almost every future strategy feature.
