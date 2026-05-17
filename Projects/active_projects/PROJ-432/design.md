# PROJ-432: TurnStateSnapshot rehydrate alignment — design

## Source

Codex consult on shipped PROJ-423 work (2026-05-17). Codex reviewed the GameSession lifecycle extraction and identified three follow-ups; the third — flagged as a real risk warranting its own project — is the parallel rehydrate path inside `TurnStateSnapshot.restore()`.

## Finding

There are two rehydrate paths in the strategy layer:

### Reference path — `SessionPersistenceAdapter.rehydrate_state()`

File: `game/strategy/engine/session/persistence_adapter.py:171-198`.

After two-phase deserialization (Galaxy → Empires) the adapter performs four post-load wiring steps:

```python
# game/strategy/engine/session/persistence_adapter.py:171-198 (abridged)

# PROJ-219: galaxy back-references for auto fleet registration.
for empire in empires:
    empire.set_galaxy(galaxy)

# PROJ-219: deserialised fleets bypass add_fleet(); register
# explicitly with galaxy for O(1) lookup.
for empire in empires:
    for fleet in empire.fleets:
        galaxy.register_fleet(fleet)

# PROJ-207: fleet orders targeting other fleets/planets are stored
# as marker dicts during deserialisation; resolve them to live
# object references now that everything is loaded.
for empire in empires:
    for fleet in empire.fleets:
        fleet.resolve_order_references(galaxy, empires)

# PROJ-222: rebuild pursuer tracker from resolved order references.
for empire in empires:
    for fleet in empire.fleets:
        for order in fleet.orders:
            if order.type in (
                OrderType.MOVE_TO_FLEET,
                OrderType.JOIN_FLEET,
            ):
                if hasattr(order.target, "pursuer_tracker"):
                    order.target.pursuer_tracker.add_pursuer(fleet)
```

Four steps: `(1) empire.set_galaxy`, `(2) galaxy.register_fleet`, `(3) fleet.resolve_order_references`, `(4) pursuer_tracker.add_pursuer`.

### Parallel path — `TurnStateSnapshot.restore()`

File: `game/strategy/engine/turn_state_snapshot.py:70-100`.

```python
# game/strategy/engine/turn_state_snapshot.py:84-99 (post-PROJ-423-phase_6)

session.galaxy = Galaxy.from_dict(self.galaxy_dict)
session.empires = [
    Empire.from_dict(
        d, galaxy=session.galaxy, registries=session.services.registries
    )
    for d in self.empire_dicts
]

# Re-register fleets with galaxy
for empire in session.empires:
    for fleet in empire.fleets:
        session.galaxy.register_fleet(fleet)

# Resolve order references (fleet/planet targets)
for empire in session.empires:
    for fleet in empire.fleets:
        fleet.resolve_order_references(session.galaxy, session.empires)
```

**Steps performed:** `(2) galaxy.register_fleet`, `(3) fleet.resolve_order_references`.

**Steps missing:**
- `(1) empire.set_galaxy(galaxy)` — empires post-restore have no galaxy back-reference. Any downstream code that walks `empire._galaxy` (PROJ-219 auto-fleet-registration on subsequent `empire.add_fleet(...)`, capability calculators that consult the galaxy through the empire) silently breaks.
- `(4) pursuer_tracker.add_pursuer(fleet)` — every `MOVE_TO_FLEET` / `JOIN_FLEET` order that survived through the snapshot loses its pursuit relationship. The target fleet's `pursuer_tracker` is empty post-restore even though the source fleet still has the order. PROJ-222's invariant — "every live pursuit order is also recorded on the target's pursuer tracker" — is violated.

## Existing test coverage

`tests/unit/strategy/turn_engine/test_turn_state_snapshot.py:89-141` covers three coarse round-trip behaviors:

- `test_restore_resets_empires` — empire name round-trip.
- `test_restore_resets_galaxy` — galaxy systems count round-trip.
- `test_restore_preserves_empire_count` — empire count.

None of these touch the back-reference or pursuer-tracker invariants. The asymmetry is invisible to the current suite.

The reference path is well-covered: `test_rehydrate_wires_galaxy_back_refs` (`tests/unit/strategy/engine/session/test_persistence_adapter.py:77-86`) and `test_rehydrate_rebuilds_pursuer_trackers` (`tests/unit/strategy/engine/session/test_persistence_adapter.py:135-160`) pin both invariants for the save-load path. The new snapshot tests should mirror this assertion shape.

## Target shape

Phase 1 adds two wiring blocks to `TurnStateSnapshot.restore()` so the full ordered sequence becomes:

1. `session.galaxy = Galaxy.from_dict(...)`.
2. `session.empires = [Empire.from_dict(..., registries=session.services.registries) for d in ...]`.
3. **New:** `for empire in session.empires: empire.set_galaxy(session.galaxy)`. Mirrors persistence_adapter.py:171-173.
4. `for empire in session.empires: for fleet in empire.fleets: session.galaxy.register_fleet(fleet)` (unchanged). Mirrors persistence_adapter.py:175-179.
5. `for empire in session.empires: for fleet in empire.fleets: fleet.resolve_order_references(session.galaxy, session.empires)` (unchanged). Mirrors persistence_adapter.py:181-186.
6. **New:** pursuer-tracker rebuild for `MOVE_TO_FLEET` / `JOIN_FLEET` orders. Mirrors persistence_adapter.py:188-197.

The two paths still differ on their **input shape** (snapshot owns the empire_dicts + galaxy_dict; adapter owns the full save dict + `ai_factory` + `turn_number_provider` + `race_registry_provider`) and a unification refactor that has both paths call the same private helper is **explicitly out of scope** — that is a larger structural change and PROJ-423 already concluded that this kind of refactor benefits from being a project of its own.

## Risk register

- **Test fragility around pursuer-tracker membership:** `set` vs `list` semantics differ inside `PursuerTracker`. The new tests should assert `restored_source in restored_target.pursuer_tracker.pursuers` exactly as `test_rehydrate_rebuilds_pursuer_trackers` does.
- **Galaxy back-reference object identity:** `Empire.set_galaxy(galaxy)` stores into `empire._galaxy`. The new test should assert `empire._galaxy is session.galaxy` (identity, not equality), matching `test_rehydrate_wires_galaxy_back_refs`.
- **Order resolution must run before pursuer-tracker rebuild.** This is the ordering invariant the reference path encodes by sequencing steps 5 → 6. The snapshot path's new step must respect the same order, since pursuer rebuild reads `order.target` which is set by `resolve_order_references`.
