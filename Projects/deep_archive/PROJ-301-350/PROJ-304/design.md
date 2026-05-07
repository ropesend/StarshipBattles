# PROJ-304: Design Document

> **PRECONDITION:** PROJ-300 (ships `roll_intrinsic_abilities` + `format_intrinsic_source_label` per D15). PROJ-301 is no longer required for the helpers. Read [`Projects/active_projects/PROJ-300/design.md`](../PROJ-300/design.md) first.

---

## Initial Analysis

Phase A reading at kickoff:
- `StarSystem` dataclass at `game/strategy/data/galaxy.py`. Confirm fields and serialization.
- Galaxy generator entry point — `game/strategy/generation/`. Confirm where archetype assignment can be inserted.
- A new generator config field for archetype percentage (likely `data/galaxy_generation_config.json` or similar).

## Architecture

### `data/system_archetypes.json` — schema

```json
{
  "version": "1.0",
  "description": "System archetype templates. Registered as IAbilitySource via SystemAbilitySource (PROJ-304).",
  "archetypes": {
    "nebula": {
      "name": "Nebula System",
      "description": "Diffuse gas clouds shroud the system; sensors and shields are degraded throughout.",
      "abilities": {
        "ShieldModifier": {"multiplier": {"min": 0.7, "max": 0.9}, "scope": "system"},
        "StrategicSpeedModifier": {"multiplier": {"min": 0.8, "max": 0.95}, "scope": "system"}
      }
    },
    "ancient_battlefield": {
      "name": "Ancient Battlefield",
      "description": "Debris from a long-ago war pollutes the system; minor radiation hazard system-wide.",
      "abilities": {
        "EnvironmentalDamage": {"rate": {"min": 0.05, "max": 0.15}, "damage_type": "radiation", "scope": "system"}
      }
    },
    "precursor_ruins": {
      "name": "Precursor Ruins",
      "description": "Fragments of ancient technology disturb local spacetime.",
      "abilities": {
        "ThrustModifier": {"multiplier": {"min": 0.85, "max": 0.95}, "scope": "system"}
      }
    },
    "ion_field": {
      "name": "Ion Field",
      "description": "Charged particles permeate the system, disrupting shielding.",
      "abilities": {
        "ShieldModifier": {"multiplier": {"min": 0.6, "max": 0.85}, "scope": "system"}
      }
    },
    "void": {
      "name": "Void System",
      "description": "Empty, unremarkable space. No system-wide effects.",
      "abilities": {}
    }
  }
}
```

(Final archetype set decided in Phase 1.)

### `StarSystem` field additions

```python
@dataclass
class StarSystem:
    ...existing fields...
    archetype: Optional[str] = None
    intrinsic_abilities: Dict[str, Any] = field(default_factory=dict)
```

### Galaxy generator integration

A new generation knob: `archetype_chance: float = 0.15` (configurable). For each generated system, with probability `archetype_chance`, choose a non-`void` archetype uniformly at random and apply `roll_intrinsic_abilities` to populate `system.intrinsic_abilities`. Otherwise, archetype stays `None` and `intrinsic_abilities` is `{}`.

### `SystemAbilitySource` adapter

```python
@dataclass(frozen=True)
class SystemAbilitySource:
    system: StarSystem

    @property
    def source_kind(self) -> str:
        return 'system'

    @property
    def source_label(self) -> str:
        archetype_label = self.system.archetype.replace('_', ' ').title() if self.system.archetype else "System"
        return f"{self.system.name} ({archetype_label})"

    @property
    def source_id(self) -> str:
        return f"system:{self.system.id}"

    @property
    def owner_id(self) -> Optional[int]:
        return None

    def get_abilities(self) -> Dict[str, Any]:
        return self.system.intrinsic_abilities

    def affects_hex(self, hex_coord) -> bool:
        # System archetype effects use system scope. The collector's scope
        # filter handles whether a sector query at hex_coord picks this up;
        # but the source itself "affects" any hex within the system in the
        # affects_hex sense.
        return self._system_contains_hex(hex_coord)

    def affects_system(self, system) -> bool:
        return system is self.system

    def get_activation_state(self, ability_name: str) -> Optional[Any]:
        return None
```

### Iterator registration

```python
def _system_archetype_provider_in_system(system):
    if not system.intrinsic_abilities:
        return  # archetype is None or void
    yield SystemAbilitySource(system)

def _system_archetype_provider_at_hex(system, hex_coord):
    # Same source — only contributes via system-scope abilities.
    if not system.intrinsic_abilities:
        return
    yield SystemAbilitySource(system)
```

## Swarm Findings Summary

To be filled at kickoff.

### Dependencies & Risks
1. **Galaxy generator surgery** — adding archetype assignment touches a hot path of generation. Verify no test relies on deterministic system attributes; if tests break, add the new generator behavior behind a default-off flag and seed for tests.
2. **Save format** — adding two fields to `StarSystem`. Per CLAUDE.md System Migration Policy, old saves are disposable; defaulting `from_dict` is fine.
3. **Combat impact at scale** — a nebula system's `ShieldModifier scope: system` affects every battle in that system. Ensure this stacks correctly with storms in the system (each provider is its own ungrouped entry → MULTIPLY) and isn't double-counted.

## Design Decisions

See [decisions.md](decisions.md).
