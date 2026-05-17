# PROJ-423: GameSession lifecycle extraction (TD-02)

**Execution Protocol:** 03c-phase-aware-execution

> **WORKING ON THIS PROJECT:**
> - Read [`design.md`](design.md) for the verification findings and the target shape of `SessionRuntimeServices` / `SessionBootstrap` / `SessionPersistenceAdapter`
> - Read the source plan [`TD-02_game_session_lifecycle.md`](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/TD-02_game_session_lifecycle.md) for the full specification
> - Open the phase checklist for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 0. Preflight and contract freeze | Complete | [phase_0_checklist.md](phase_0_checklist.md) |
| 1. Add `SessionRuntimeServices` + `SessionBootstrapState` | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Extract canonical service construction into `SessionBootstrap` | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Extract `SessionPersistenceAdapter` | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Collapse `GameSession` to a thin shell | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Docs update | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-05-17
**Active Phase:** Phase 4 — Collapse `GameSession` to a thin shell
**Last Action:** Phase 3 complete — `SessionPersistenceAdapter.serialize/rehydrate_state` live at `game/strategy/engine/session/persistence_adapter.py`; `to_dict` / `from_dict` are thin delegates. Save schema byte-for-byte preserved; `human_player_ids` `[0, 1]` fallback preserved. Sharded suite: 20885/20885 green.
**Next Action:** Phase 4 — introduce canonical `_apply_bootstrap_state(...)`, retarget `__init__` / `from_dict` through it, forward service properties through `self._services`, drop dead imports
**Blockers:** None

## Overview
Split `GameSession` into a thin owned-state shell with a small behavior surface, backed by three internal collaborators (`SessionRuntimeServices`, `SessionBootstrap`, `SessionPersistenceAdapter`) that absorb the composition-root and rehydration responsibilities. This eliminates the documented `__init__` / `from_dict` drift (PROJ-396 CRIT-002) by routing both fresh construction and load through one internal `SessionBootstrapState` payload, without touching the public API (`GameSession(...)`, `GameSession.from_dict(...)`, `GameSession.to_dict()`) or the on-disk save schema.

## Goals
- Introduce `game/strategy/engine/session/` package with `runtime_services.py`, `bootstrap.py`, and `persistence_adapter.py`.
- Route both `__init__` and `from_dict` through a single internal `SessionBootstrapState` payload via a private `_apply_bootstrap_state(...)` method.
- Eliminate the duplicated mutator-service / turn-engine / event-bus construction currently mirrored by hand between `__init__` (lines 104-147) and `from_dict` (lines 498-536).
- Preserve the existing save schema byte-for-byte and preserve current load semantics (including the `human_player_ids` `[0, 1]` fallback).
- Keep `race_registry` lazy on `GameSession` — it is intentionally outside the runtime-services bag.
- Remove inline service / turn-engine / `GameInitializer` imports from `game_session.py` once the extraction is complete.

## Scope
**In:**
- The four-file split inside `game/strategy/engine/session/`.
- `GameSession` refactor to a thin shell with `_apply_bootstrap_state(...)` as the single assignment path.
- New focused unit tests for runtime services, bootstrap, persistence adapter, and the resulting `game_session.py` shape.
- Docs refresh under `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`, `docs/systems/strategy_layer.md`, `docs/systems/save_load.md`.

**Out:**
- Mass-migration of `GameSession(...)` / `GameSession.from_dict(...)` call sites to a new factory.
- Save-schema changes, migrations, or compatibility shims.
- Behavioral cleanup of the `human_player_ids` load fallback or the existing load-path exception handling.
- Changing `race_registry` lifetime (it stays lazy).
- Any TD-05 or TD-08 work that is not strictly required by this extraction.

## Dependencies
Hard predecessors: none. Soft predecessors: none. Soft sequencing preference: run before PROJ-427 (TD-05) and PROJ-430 (TD-08). If TD-05 has already shipped, `SessionRuntimeServices` must absorb its design repository/catalog ownership — see the cross-plan note in the source plan.

## Key Files
| Component | File Path | Action |
|-----------|-----------|--------|
| Session model + composition root (today) | `game/strategy/engine/game_session.py` | Edit (shrinks to a shell) |
| Save-game service | `game/strategy/systems/save_game_service.py` | Edit only if delegation surface requires it |
| Session package marker | `game/strategy/engine/session/__init__.py` | Add |
| Runtime services value object | `game/strategy/engine/session/runtime_services.py` | Add |
| Bootstrap (canonical service construction) | `game/strategy/engine/session/bootstrap.py` | Add |
| Persistence adapter (serialize + rehydrate) | `game/strategy/engine/session/persistence_adapter.py` | Add |
| Runtime services unit tests | `tests/unit/strategy/engine/session/test_runtime_services.py` | Add |
| Bootstrap unit tests | `tests/unit/strategy/engine/session/test_bootstrap.py` | Add |
| Persistence adapter unit tests | `tests/unit/strategy/engine/session/test_persistence_adapter.py` | Add |
| `GameSession` shape tests | `tests/unit/strategy/engine/test_game_session_shape.py` | Add |
| Architecture docs | `docs/01_ARCHITECTURE.md` | Edit |
| Patterns docs | `docs/02_PATTERNS.md` | Edit |
| Strategy layer system doc | `docs/systems/strategy_layer.md` | Edit |
| Save/load system doc | `docs/systems/save_load.md` | Edit |

See [`manifest.md`](manifest.md) for the full per-phase touch list including regression-coverage test files that must stay green.

## Phases

### Phase 0: Preflight and contract freeze
Run the two `rg` guardrail commands from the source plan, confirm production callers still go through `GameSession(...)` / `GameSession.from_dict(...)`, and record the current `human_player_ids` load fallback and `race_registry` lazy behavior as behaviors to preserve.

### Phase 1: Add `SessionRuntimeServices` and `SessionBootstrapState`
Introduce the two internal value objects with no caller-visible change. `GameSession.__init__` still uses the existing construction path but assembles `self._services` and exposes a `services` property.

### Phase 2: Extract canonical service construction into `SessionBootstrap`
Move service construction into `SessionBootstrap._build_services(...)` and add `SessionBootstrap.new_game_state(...) -> SessionBootstrapState`. Both fresh and loaded sessions must end up using the same construction function; an anti-drift test compares the service classes produced by both paths.

### Phase 3: Extract `SessionPersistenceAdapter`
Move save/load serialization and rehydration logic out of `GameSession.from_dict`. `serialize(session)` returns the exact current dict shape; `rehydrate_state(data, ai_factory=...)` returns `SessionBootstrapState` (not `GameSession`). `to_dict` / `from_dict` become thin delegates. The `human_player_ids` fallback semantics are preserved exactly as today.

### Phase 4: Collapse `GameSession` to a thin shell
Add `_apply_bootstrap_state(...)` and route both public entry paths through it. Convert service properties to forward through `self._services`. Keep `race_registry` lazy. Remove inline service / turn-engine / bootstrap imports from `game_session.py`. Do **not** migrate external call sites.

### Phase 5: Docs update
Document `SessionRuntimeServices`, `SessionBootstrap`, and `SessionPersistenceAdapter` as internal collaborators. Explicitly state that the public API and save schema are unchanged.

## Related Documents
- Source plan: [`TD-02_game_session_lifecycle.md`](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/TD-02_game_session_lifecycle.md)
- Execution order reference: [`EXECUTION_ORDER.md`](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/EXECUTION_ORDER.md)
- Project design notes: [`design.md`](design.md)
- Decisions log: [`decisions.md`](decisions.md)
- Per-phase file manifest: [`manifest.md`](manifest.md)

## Verification
- [ ] `game/strategy/engine/session/` exists with `runtime_services.py`, `bootstrap.py`, and `persistence_adapter.py`.
- [ ] `GameSession.__init__` and `GameSession.from_dict()` both route through `SessionBootstrapState` + `_apply_bootstrap_state(...)`.
- [ ] `game_session.py` no longer imports `FleetNavigationService`, `FleetWriteService`, `PlanetWriteService`, `EmpireWriteService`, `ShipInstanceWriteService`, `TurnEngineConfig`, `TurnEngine`, `GameInitializer`, `EventBus`, or `create_default_registry`.
- [ ] `race_registry` remains lazy on `GameSession`.
- [ ] `SessionPersistenceAdapter.serialize()` preserves the existing save schema byte-for-byte.
- [ ] `python Tools/test_sharded/test_sharded.py` passes after Phase 3 and again after Phase 4.
- [ ] All phase checklists complete; docs in Phase 5 updated.
