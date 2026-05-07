# PROJ-365: Design Document

## Initial Analysis

`_process_tick` (`turn_engine.py:703-782`) is imperative — every phase is a hand-written `self._time_phase('name', engine.method, args...)` call. The 14 phases (0a/0b/0c/0c1/0d/0e/0f/1/1.5/1.6/1.7/1.8/2/3/4 — see findings/01) are encoded as code, not data. Two cross-phase state issues:
- Phase 1.8 lazily imports `PlanetModifierEffectEngine` (line 751)
- Phase 2 → 3 → 4 needs a pre/post-movement diff (`pre_movement_locations` then `moved_fleet_ids`) — PROJ-320

Documentation does NOT describe a phase registry pattern (per findings/01). PROJ-365 is greenfield.

## Swarm Findings Summary

### Architecture (findings/01_architecture.md)

```python
@dataclass(frozen=True)
class TickPhase:
    phase_key: str                                    # Identity, timing bucket
    callable_target: Callable[[TurnEngine], Callable] # Engine method resolver (e.g. lambda e: e.harvesting_engine.process_harvesting_tick)
    args_resolver: Callable[[TickContext], tuple]
    error_policy: str = 'wrap'                        # 'wrap' | 'barrier'
    tick_gating: str | None = None                    # 'only_tick_1' | None
    timing_bucket: str | None = None                  # Defaults to phase_key
    post_exec_hook: Callable[[TickContext, Any], None] | None = None

@dataclass
class TickContext:
    tick: int
    empires: list
    galaxy: object
    component_registry: dict | None = None
    save_path: str | None = None
    pre_movement_locations: dict[int, HexCoord] | None = None
    moved_fleet_ids: set[int] | None = None
    last_environmental_events: list = field(default_factory=list)
```

The `callable_target` is a **resolver** (lambda taking the engine instance) rather than a bound method, because TurnEngine engines are lazily resolved via properties. This avoids forcing eager engine construction at descriptor-definition time.

### Dependencies (findings/02_dependencies.md)

- `process_turn` is called from `game_session.py:226` (production) + ~24 integration test sites.
- `create_default_turn_engine` is the construction factory.
- 15 engine interfaces (`IMovementEngine`, etc.) — all live; no consolidation in this project.
- `_time_phase` is internal-only (22 sites, all in `_process_tick`). Refactor preserves it.
- `last_environmental_events` has no external consumer beyond test assertions; preserved as-is in `TickContext`.

### Test Impact (findings/03_test_impact.md)

- Existing phase-ordering test (`test_turn_processing.py:69-108`) uses `call_order` mock tracking. Will need migration to assert against the descriptor list rather than internal mocks.
- PROJ-320 `moved_fleet_ids` characterization (`test_turn_engine_phase_320_movement_diff.py`) is a hard invariant — must stay green.
- `test_turn_engine_phase_timing.py` pins `_time_phase` accumulator semantics — preserved.
- Golden-list test does not exist yet — Phase 1 introduces it.

### Risks

| Risk | Mitigation |
|------|------------|
| Phase-order regression | Phase 1 golden-list test pins the order. Any reordering requires explicit test update. |
| `moved_fleet_ids` derivation | `TickContext.pre_movement_locations` snapshot before phase 3, `moved_fleet_ids` derived after — encoded as `post_exec_hook` on phase 3, `args_resolver` for phase 4 reads it. |
| Mid-phase logging | Lines 705 and 723-724 (`_log_empire_state`) become `post_exec_hook` with `tick_gating='only_tick_1'`. |
| PlanetModifierEffectEngine lazy import (line 751) | Move to module-level import after confirming no circular deps; or instantiate via descriptor's `callable_target` resolver lambda. |
| Tests mocking individual engines | Most tests use `mock_engines.py` IXxx fakes — orthogonal to descriptor list. Should not need changes. |
| End-of-turn engines (lines 571-602) | OUT OF SCOPE; keep imperative. |

### Key Patterns to Reuse
- Frozen dataclass + tuple registry (StabilizerRegistry, EffectAbilityMetadata, SuperweaponSpec).
- Cross-phase context object (Pythonic alternative to barrier phases).

## Design Decisions
See [decisions.md](decisions.md).
