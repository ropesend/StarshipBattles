# PROJ-482: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Audit

- **Audit dir:** `Reviews/results/2026-05-20_210540_type-audit/`
- **Audit verified (5 CRITICAL + 5 MAJOR spot-checks):** zero false positives per `findings/verification.md`
- **Bundle counts:** Audit verified ~28 strategy items / This bundle: 28 verified, 1 uncertain (resolved → included), 3 deferred (formula_evaluator, ability_scanner TypedDict, battle_assembly cast)
- **Project siblings:** [PROJ-481](../PROJ-481/) (UI), [PROJ-483](../PROJ-483/) (Foundation + strict quick wins)
- **Layer coverage:** `game/strategy/` (engine, services, adapters, data, systems, commands, handlers) + `game/app_bootstrap.py` for one fallback closure
- **Severity breakdown:** Phase 1: 4 CRITICAL (incl. GameSession 10-property cluster as one combined task). Phase 2: ~13 MAJOR. Phase 3: ~11 MINOR.

## Initial Analysis
Strategy is the second-largest source of type debt per the heatmap: 19 `-> Any` returns and 30 missing return types (69.8% of all missing returns). The single highest-impact item is the `GameSession` mutator-property cluster — 10 properties at lines 202-258 that each have BOTH a missing return type AND a `# type: ignore[no-untyped-def]` suppression. Fixing them in one combined edit removes 10 ignores and adds 10 protocol-typed accessors — a clean tightening of the Engine→Session→consumer chain.

The 8 `_get_*_mutator` helpers across engine modules are the same pattern (lazy-default + return the configured mutator) and narrow trivially to either `IPlanetMutator` / `IEmpireMutator` / `IShipInstanceMutator` (protocol) or the concrete `PlanetWriteService` / `EmpireWriteService` / `ShipInstanceWriteService`. Audit suggested the protocol where lazy-init is via `self._config.<mutator>` and the concrete where the lazy-default is `self._planet_mutator or PlanetWriteService()`.

## Swarm Findings Summary
Combined analysis from `.agent_reports/2026-05-20_210540_type-audit/`:
- `verification_core_strategy_sim_ai_any.md` — 20 verified items including the 8 mutator helpers, `handle_command`, `_resolve_*` cluster, and `_json_safe`
- `verification_missing_returns.md` — 4 CRITICAL + the GameSession cluster + ~10 MINOR closures
- `verification_type_ignores.md` — GameSession cluster overlap; one cross-shard note (turn_failed_dialog/defeat_dialog) lives in PROJ-481

### Architecture
- **GameSession cluster** at `game/strategy/engine/game_session.py:202-258` — 10 properties delegate to `self._services` (`SessionRuntimeServices`) which already has typed attributes. Adding return annotations exposes that contract through `GameSession`.
- **Mutator helper cluster** — `_get_<x>_mutator()` lazy-init + return pattern. Each is a 1-line body; clean narrowing.
- **Superweapon-handler closures** — `_precheck`/`_effect` defined inside `process_<superweapon>` functions. Return types are stable per handler module.

### Key Patterns to Reuse
- **TYPE_CHECKING-guarded protocol imports** for `IFleetMutator` / `IPlanetMutator` / `IEmpireMutator` / `IShipInstanceMutator` from `game/core/protocols/strategy_mutators.py`
- **`-> Iterator[T]` / `-> Generator[T, None, None]`** for generator methods (game_initializer + `_walk_strategic_abilities`)
- **New type for replay capture context** — `simulation_adapter._build_capture_context` returns an internal dict shape; define a `TypedDict` or small `@dataclass` named `ReplayCaptureContext` in `game/strategy/adapters/`.

### Dependencies & Risks
1. **GameSession cluster import cycles** — protocol imports under `TYPE_CHECKING` are required; runtime imports would cycle through `SessionRuntimeServices` → mutator services → session.
2. **planet_write_service.pop_construction_item** — narrowed here AND in PROJ-483 (Protocol side `IPlanetMutator.pop_construction_item`). Both ends must match (`dict | None`) — Phase 3 Task 3.6 notes the coordination.
3. **production_spawner._get_planet_mutator** — audit suggested both `IPlanetMutator` (interface) and `PlanetWriteService` (concrete). Reading the function determines which: if it lazy-init returns `PlanetWriteService()`, use concrete; if it pulls from config, use protocol.

### Opportunities Discovered
- `GameSession.handle_command -> ValidationResult` rippling through `StrategySessionFacade.handle_command` chain — once narrowed, every command handler return becomes statically verified at the facade boundary.
- The 8 mutator helpers, once narrowed, eliminate Any-leakage in engine subclasses that consume them.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
