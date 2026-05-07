# PROJ-303: Design Document

> **PRECONDITION:** PROJ-300 (Universal IAbilitySource Framework). Read [`Projects/active_projects/PROJ-300/design.md`](../PROJ-300/design.md) before this document.

---

## Initial Analysis

Phase A reading at kickoff:
- Confirm the `WarpPoint` dataclass (likely `game/strategy/data/warp_point.py` or inside `galaxy.py`).
- Confirm the warp_point type taxonomy. If the codebase currently has only one warp_point type ("stable"), this project may need to introduce additional types — coordinate with the user.
- Confirm warp_point save/load.

## Architecture

### `data/warp_point_types.json` — schema

```json
{
  "version": "1.0",
  "warp_point_types": {
    "stable": {
      "name": "Stable Warp Point",
      "description": "A reliable transit point. No intrinsic effects.",
      "abilities": {}
    },
    "unstable": {
      "name": "Unstable Warp Point",
      "description": "Warp shear stresses ship hulls passing through.",
      "abilities": {
        "EnvironmentalDamage": {"rate": {"min": 0.1, "max": 0.3}, "damage_type": "warp", "scope": "sector"}
      }
    },
    "dimensional_rift": {
      "name": "Dimensional Rift",
      "description": "Tears in spacetime that disrupt shields and sensors.",
      "abilities": {
        "ShieldModifier":      {"multiplier": {"min": 0.6, "max": 0.85}, "scope": "sector"},
        "EnvironmentalDamage": {"rate": {"min": 0.05, "max": 0.2}, "damage_type": "warp", "scope": "sector"}
      }
    },
    "precursor_gateway": {
      "name": "Precursor Gateway",
      "description": "Ancient warp gate; ambient EM disturbance.",
      "abilities": {
        "ShieldModifier": {"multiplier": {"min": 0.85, "max": 0.95}, "scope": "sector"}
      }
    }
  }
}
```

### `WarpPoint.intrinsic_abilities` field

Added as a `Dict[str, Any] = field(default_factory=dict)`. Standard pattern from PROJ-301/302.

### `WarpPointAbilitySource` adapter

```python
@dataclass(frozen=True)
class WarpPointAbilitySource:
    warp_point: WarpPoint
    system: StarSystem  # captured at adapter construction for global location

    @property
    def source_kind(self) -> str:
        return 'warp_point'

    @property
    def source_label(self) -> str:
        return f"{self._descriptive_name} ({self.warp_point.warp_point_type})"

    @property
    def source_id(self) -> str:
        return f"warp_point:{self.warp_point.id}"

    @property
    def owner_id(self) -> Optional[int]:
        return None

    def get_abilities(self) -> Dict[str, Any]:
        return self.warp_point.intrinsic_abilities

    def affects_hex(self, hex_coord) -> bool:
        wp_global = self.system.global_location + self.warp_point.location
        return hex_coord == wp_global

    def affects_system(self, system) -> bool:
        return self.warp_point in system.warp_points

    def get_activation_state(self, ability_name: str) -> Optional[Any]:
        return None
```

### Iterator registration

Standard pattern — register a `_warp_point_provider_at_hex` that walks `system.warp_points`, yielding sources whose `affects_hex` matches and whose `get_abilities` is non-empty.

## Swarm Findings Summary

To be filled at kickoff. Patterns from PROJ-301/302 carry over.

### Dependencies & Risks
1. **Existing warp_point taxonomy may be flat** — if today only "stable" warp points are generated, the project must introduce new types and add generation logic for them. Coordinate with the user before adding new types.
2. **Warp travel interaction** — sailing a fleet through an unstable warp point should apply the damage as a one-tick environmental effect (the fleet briefly occupies the warp point's hex). Verify this works through the existing environmental_hazard_engine path. May need a small adjustment if traversal doesn't tick.

## Design Decisions

See [decisions.md](decisions.md).
