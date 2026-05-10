# PROJ-93: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

PROJ-84 introduced `LayerData` dataclass (`game/simulation/entities/layer_data.py`) to replace raw `Dict[str, Any]` for ship layers. The migration was comprehensive — all ~90 access sites across 29 files use typed attribute access. The only remaining gap is the protocol type annotations.

### Current State of Protocols (Pre-Fix)

```python
# game/core/protocols.py

class IPostBattleShip(Protocol):
    @property
    def layers(self) -> Dict[str, Any]:  # line 416 — WRONG TYPE
        ...

class IResourceHolder(Protocol):
    @property
    def layers(self) -> Dict[str, Any]:  # line 459 — WRONG TYPE
        ...
```

### Actual Implementation (Ship class)

```python
# game/simulation/entities/ship.py line 338
self.layers: Dict[LayerType, LayerData] = {}
```

### Import Layer Analysis

```
game/core/protocols.py  (core layer)
    ├── can import: game.core.constants.LayerType  (same layer — direct import OK)
    └── can import: game.simulation.entities.layer_data.LayerData  (cross-layer — TYPE_CHECKING only)

game/simulation/ does NOT import from game/core/protocols.py → no circular dependency
```

## Key Patterns to Reuse
- **TYPE_CHECKING guard**: Already exists at `protocols.py:39` — just add LayerData import there
- **String forward references**: Used throughout the codebase for cross-layer type annotations

## Dependencies & Risks
1. **Runtime protocol checking** — `@runtime_checkable` protocols use `isinstance()` at runtime. String forward references in property annotations don't affect runtime behavior since Protocol only checks attribute existence, not types. **Risk: None.**
2. **Cross-layer import** — `LayerData` import guarded by TYPE_CHECKING. Only available to type checkers, never at runtime. **Risk: None.**

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
