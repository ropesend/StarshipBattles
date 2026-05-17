# PROJ-428: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

`game/strategy/engine/turn_phase_registry.py` should describe phases as
declarative data. The TD-04 review found it does the opposite: it owns
behavior-carrying helpers and even constructs gameplay engines from inside
the module. The fix is to relocate behavior to `TurnEngine` (or a single
named collaborator owned by `TurnEngine`) so the registry becomes pure
descriptor data again.

## Current Hook Inventory (to be relocated)

Six module-level helpers currently live in `turn_phase_registry.py`:

| Helper | Wired to | New home |
|---|---|---|
| `_log_turn_start_tick_1` | `turn_start` hook | Named `TurnEngine` method (Phase 3) |
| `_log_after_construction_tick_1` | post-production hook | Named `TurnEngine` method (Phase 3) |
| `_accumulate_env_events` | env-event hook | Named `TurnEngine` method (Phase 3) |
| `_capture_move_queue` | `movement_calc` hook | `MovementPhaseCollaborator.snapshot_before` (Phase 4) |
| `_derive_moved_fleet_ids` | `movement_apply` hook | `MovementPhaseCollaborator.resolve_after` (Phase 4) |
| `_resolve_planet_modifier_effects` | planet-modifier hook | `TurnEngine.planet_modifier_effect_engine` lazy property + descriptor lambda (Phase 2) |

In addition, the module currently:

- Imports `PlanetModifierEffectEngine` and caches a constructed instance.
- Imports / constructs `MinefieldResolver` inside `_derive_moved_fleet_ids`.

Both imports must disappear from the registry.

## Worst Offender: `_derive_moved_fleet_ids`

This single registry hook currently performs four distinct responsibilities:

1. **Movement diff** — compare pre-movement locations (captured by
   `_capture_move_queue`) against post-movement locations to derive
   `moved_fleet_ids`.
2. **`_booster_dirty` propagation** — flip the dirty flag for every empire
   whose fleets actually moved.
3. **Minefield resolution** — call
   `MinefieldResolver.resolve_minefield_entry(..., registries=engine._registries)`
   for each moved fleet, wrapped in a broad catch so unexpected resolver
   errors do not abort the turn.
4. **Fleet pruning** — remove fleets emptied by minefield damage from the
   owning empire.

The TD-04 plan calls this out as the only hook in the inventory that
warrants its own dedicated object. Hence one new collaborator, not six.

## Target Shape

### `TurnEngine.planet_modifier_effect_engine` lazy property

A read-only property on `TurnEngine` that constructs the
`PlanetModifierEffectEngine` on first access and caches the instance. The
phase descriptor switches from a module-level function reference to a
resolver lambda:

```python
lambda e: e.planet_modifier_effect_engine.process_modifier_effects_tick
```

Important: **do not** add a new `TurnEngineConfig` field. The lazy property
alone is sufficient and avoids unrelated test/doc churn.

### Named `TurnEngine` methods (small hooks)

Three named methods replace the three small registry helpers:

- `TurnEngine._log_turn_start_tick_1(ctx)` (name chosen to match existing
  style; final name is an implementation detail).
- `TurnEngine._log_after_construction_tick_1(ctx)`.
- `TurnEngine._accumulate_env_events(ctx, result)`.

Phase descriptors point at bound methods via resolver lambdas. The TD-04
plan explicitly forbids creating a separate `TurnLogger` class unless
`turn_engine.py` becomes materially less clear — start without it.

### `MovementPhaseCollaborator`

New file (optional but expected):
`game/strategy/engine/movement_phase_collaborator.py`.

Public surface:

- `snapshot_before(ctx, result)` — replaces `_capture_move_queue`. Stores
  both `move_queue` and `pre_movement_locations` on the context exactly as
  before.
- `resolve_after(engine, ctx)` — replaces `_derive_moved_fleet_ids`. Owns
  the four-step pipeline above.

Recommended private split:

- `_diff_moved_fleets(ctx)` — pure diff against `pre_movement_locations`.
- `_mark_boosters_dirty(empires, moved_owner_ids)` — booster flag flip only.
- `_resolve_minefields(engine, ctx, moved_fleets)` — calls
  `MinefieldResolver.resolve_minefield_entry(..., registries=engine._registries)`
  inside the existing broad catch. Call contract is preserved bit-for-bit.
- `_prune_destroyed_fleet_contents(owning_empire, fleet, destroyed_ship_ids)`
  — removes empty fleets from their owning empire.

The collaborator is owned by `TurnEngine` (constructed eagerly or via a
private lazy slot — implementation detail). It is not a global; it never
constructs its own `MinefieldResolver` — it receives `engine` and uses
`engine._registries`.

### Registry-purity AST guard

A new test (or extension of `test_tick_phase_descriptors.py`) that uses the
`ast` module to walk `turn_phase_registry.py`. Assertions:

1. The module has zero top-level `FunctionDef` / `AsyncFunctionDef` nodes.
2. The module has no `import` / `from … import` statements that pull in
   `PlanetModifierEffectEngine`, `MinefieldResolver`, or any other gameplay
   engine.
3. `DEFAULT_TICK_PHASE_LIST` and `DEFAULT_END_OF_TURN_PHASE_LIST` retain
   their existing phase keys, order, and timing buckets (golden lists).

This guard prevents future drift the moment someone reintroduces a hook
helper in the registry module.

## Key Patterns to Reuse

- **Lazy property + cached instance attribute** — already used elsewhere on
  `TurnEngine` for engine subsystems; the planet-modifier engine is the new
  example.
- **Resolver lambdas on phase descriptors** — already supported by the
  phase machinery. We are just moving from a free function to
  `lambda e: e.method`.
- **Collaborator object owned by `TurnEngine`** — pattern used elsewhere in
  the strategy layer for cohesive sub-responsibilities. The movement
  collaborator follows that shape.

## Dependencies & Risks

1. **Phase order / key drift** — mitigated by Phase 1 characterization
   tests against `DEFAULT_TICK_PHASE_LIST` / `DEFAULT_END_OF_TURN_PHASE_LIST`.
2. **Subtle minefield behavior drift** — mitigated by FMS-B integration
   tests run before the sharded suite, and by preserving the exact
   `MinefieldResolver.resolve_minefield_entry(..., registries=engine._registries)`
   call contract.
3. **`engine=None` descriptor tests start evaluating hook bodies** — mitigated
   by keeping resolvers as callables, not eager evaluations.
4. **Collaborator scope creep** — explicit guardrail: the collaborator owns
   movement snapshotting, movement diffing, minefield resolution wiring,
   and fleet pruning. Nothing else.
5. **`_booster_dirty` regression** — Phase 1 tests pin the flip-only-for-moved
   behavior before any code moves.
6. **PROJ-422 (TD-09) interplay** — soft predecessor only. Phase 2 uses a
   lazy property rather than a new ABC, so the engine-interface monolith does
   not block this work.

## Opportunities Discovered

- The `MinefieldResolver` construction in the registry is currently the
  only thing forcing an import cycle risk between the registry and the
  resolver module. Moving the construction to the collaborator removes
  that coupling entirely.
- The AST guard, once in place, makes future "tiny one-line helper added
  to the registry" PRs fail loudly, which is a much higher-leverage win
  than the immediate cleanup.

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.
