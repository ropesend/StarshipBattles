# PROJ-84: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Problem
Ship layers use raw `Dict[str, Any]` with 8 string keys. Every consumer accesses via `layer_data['components']`, `layer_data.get('max_mass_pct', 1.0)` etc. — no IDE support, no type safety, typo-vulnerable.

### Current Layer Dict Schema
```python
{
    'components': List[Component],   # Mutable list, appended/popped frequently
    'radius_pct': float,             # Set at init, recalculated in _initialize_layers()
    'restrictions': List[str],       # Set at init, read-only after
    'max_mass_pct': float,           # Set at init, read-only after
    'mass': float,                   # Recalculated every stats recalc
    'hp_pool': int,                  # ARMOR only — current damage pool
    'max_hp_pool': int,              # ARMOR only — max damage pool
    'hp': int,                       # DEAD CODE — never read/written after init
}
```

### Layer Types
5 types defined in `LayerType` enum (`game/core/constants.py`):
- HULL (0) — structural, radius_pct=0.0, max_mass_pct=100.0, restrictions=['HullOnly']
- CORE (1) — innermost equipment layer
- INNER (2) — middle equipment layer
- OUTER (3) — outer equipment layer
- ARMOR (4) — outermost, uses hp_pool/max_hp_pool for armor damage tracking

### Dual Initialization
`Ship._initialize_layers()` and `ShipComponentManager.initialize_layers()` are near-identical copies. Both create the same dict structure. Decision: consolidate.

## Swarm Findings Summary

### Architecture
- Layer data flows through a clear lifecycle: **Creation** (ship init / change_class / deserialization) → **Mutation** (component add/remove, stats calc, damage) → **Read** (rendering, serialization, validation, AI) → **Replacement** (change_class reinit)
- `ship.layers` is always `Dict[LayerType, layer_data]` — the outer dict structure stays unchanged
- Only the inner `layer_data` values change from `Dict[str, Any]` to `LayerData`

### Key Patterns to Reuse
- **Existing dataclass pattern**: `@dataclass` with `field(default_factory=list)` for collections — used in `Planet`, `ShipInstance`, `RaceConfig`, etc.
- **Factory classmethod pattern**: `@classmethod def from_dict(cls, data)` — standard in this codebase
- **Serialization pattern**: `to_dict()` / `from_dict()` methods on dataclasses

### Dependencies & Risks
1. **Serialization `isinstance` guard** — `ship_serialization.py:83` checks `isinstance(layer_data, dict)`. Must be removed/updated. MEDIUM risk.
2. **Simulation test `isinstance` guards** — 6 files in `simulation_tests/scenarios/` check `isinstance(layer_data, dict) and 'components' in layer_data`. Must be simplified. LOW risk.
3. **Builder UI direct dict mutation** — `builder/main.py` directly sets `layer_data['components'] = []` etc. during clear. Must use `layer_data.clear()` method. LOW risk.
4. **Damage calculator sort** — Sorts layers by `x[1]['radius_pct']`, must become `x[1].radius_pct`. LOW risk.
5. **Test blast radius** — ~50 test files with direct dict construction or key access. HIGH effort but LOW risk per file.

### Opportunities Discovered
- Drop dead `hp` field (never used, confused with `ship.hp` cached property)
- Consolidate duplicated layer init between Ship and ShipComponentManager
- Clean up inconsistent `.get()` vs `['key']` access patterns

## LayerData Dataclass Design

```python
from dataclasses import dataclass, field
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from game.simulation.components.component import Component

@dataclass
class LayerData:
    """Typed representation of a ship layer's data.

    Replaces raw Dict[str, Any] for type safety and IDE support.
    """
    components: List['Component'] = field(default_factory=list)
    radius_pct: float = 0.5
    restrictions: List[str] = field(default_factory=list)
    max_mass_pct: float = 1.0
    mass: float = 0.0
    hp_pool: int = 0
    max_hp_pool: int = 0

    @classmethod
    def create_hull(cls) -> 'LayerData':
        """Create the HULL layer with standard defaults."""
        return cls(
            components=[],
            radius_pct=0.0,
            restrictions=['HullOnly'],
            max_mass_pct=100.0,
        )

    @classmethod
    def from_definition(cls, l_def: dict) -> 'LayerData':
        """Create a layer from a vehicle class layer definition dict."""
        return cls(
            components=[],
            radius_pct=l_def.get('radius_pct', 0.5),
            restrictions=l_def.get('restrictions', []),
            max_mass_pct=l_def.get('max_mass_pct', 1.0),
        )

    def clear(self) -> None:
        """Reset mutable fields to defaults (used by builder clear)."""
        self.components = []
        self.mass = 0.0
        self.hp_pool = 0
        self.max_hp_pool = 0
```

### Conversion Patterns

| Old Pattern | New Pattern |
|-------------|-------------|
| `{'components': [], 'radius_pct': 0.5, ...}` | `LayerData(radius_pct=0.5, ...)` |
| `layer_data['components']` | `layer_data.components` |
| `layer_data['mass'] = 100` | `layer_data.mass = 100` |
| `layer_data.get('max_mass_pct', 1.0)` | `layer_data.max_mass_pct` |
| `isinstance(layer_data, dict)` | Remove check (always LayerData) |
| `key=lambda x: x[1]['radius_pct']` | `key=lambda x: x[1].radius_pct` |

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
