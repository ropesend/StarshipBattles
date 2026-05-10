# PROJ-372: Facade-Delegate Template

A 1-page template for downstream phase implementers. The pattern is
already 50% in place on `Galaxy` (PROJ-173 Phase 2's four delegates);
this doc nails it down so the remaining extractions stay consistent.

## Structure

```
Facade (the data class)
  + state (data fields, __eq__, __hash__, serde) ← stays here
  + 1-line method delegations to services         ← thin facade
  + transient cache fields (PROJ-285 pattern)     ← stays here

Service (new module under game/strategy/services/)
  + algorithmic / query / calc methods
  + accepts state by reference (Planet, GalaxyState) — no back-pointer
  + protocol-typed (game/strategy/data/galaxy_protocols.py)
```

## Decision rules

**Move out of the facade when:**

- Method body > 5 LOC OR contains `if/else` branches OR holds
  algorithmic logic.
- Method late-imports a module to dodge circular dependencies (sign of
  a swap point — make it explicit via injected service).
- Method scans collections, computes derived values, or interacts with
  multiple sub-objects.

**Keep on the facade when:**

- Identity (`__eq__`, `__hash__`).
- Serialization (`to_dict`, `from_dict`, `__init__` for dataclasses).
- Direct field accessors / 1-line returns of a stored value.
- Mutation methods that are intrinsically tied to the data class
  (e.g., `add_to_stockpile`) — keep but conform to a protocol.

## Service signatures

```python
# Bad — holds Galaxy back-reference
class _MyService:
    def __init__(self, galaxy: Galaxy): self._galaxy = galaxy
    def lookup(self, x): return self._galaxy._global_hex_planets[x]

# Good — accepts state by reference
class _MyService:
    def __init__(self, state: GalaxyState): self._state = state
    def lookup(self, x): return self._state.global_hex_planets[x]
```

For pure-function services with no state, prefer `@staticmethod`:

```python
class PlanetQueryService:
    @staticmethod
    def occupied_hexes(planet: Planet) -> FrozenSet[HexCoord]: ...
```

## Test pattern

Service tests should not need to construct a real `Galaxy()` (which
loads naming registries from disk). Use stub state objects:

```python
def test_my_service():
    state = GalaxyState(radius=10)
    state.systems[HexCoord(0, 0)] = make_stub_system("Alpha")
    state.systems[HexCoord(5, 0)] = make_stub_system("Beta")
    svc = MyService(state)
    assert svc.find_path("Alpha", "Beta") == [...]
```

Facade tests assert the 1-line delegation works:

```python
def test_galaxy_delegates_to_my_service():
    galaxy = Galaxy(radius=10)
    galaxy._my_service = StubService()  # or monkeypatch
    galaxy.do_thing(...)
    assert galaxy._my_service.do_thing.called
```

## Predecessors

- `GalaxyEntityRegistry` / `GalaxySpatialIndex` (PROJ-173 Phase 2) — the
  in-tree exemplar. Currently hold `_galaxy: Galaxy` back-references; Phase 3
  switches them to `GalaxyState`.
- PROJ-86/87/88/89 — facade-pattern decompositions for adjacent god
  classes (UI screens, Ship, Component, Fleet, GameSession). Verbatim
  pattern: facade preserves public API; logic moves to delegates.
- PROJ-258 — `ApplicationContext` injection pattern. Use this for
  habitability service swap (G4).
- PROJ-370 — mutator protocols. PROJ-372 read protocols compose with
  PROJ-370 write protocols; do not duplicate.
