# PROJ-301: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

> **PRECONDITION:** PROJ-300 (Universal IAbilitySource Framework). Read [`Projects/active_projects/PROJ-300/design.md`](../PROJ-300/design.md) before this document.

---

## Initial Analysis

Phase A reading (to be performed at project kickoff):

- Confirm the `Planet` dataclass shape — fields, generation entry point.
- Confirm the existing planet-type taxonomy (`planet_type` enum or string set in `data/`).
- Confirm where planet generation happens (`game/strategy/generation/`) and how rolled per-instance attributes (e.g. resource deposits) are currently produced — reuse the same RNG / pattern for intrinsic ability rolls.
- Confirm how Planet is serialized for save/load to extend the field.

## Architecture

### `data/planet_types.json` — schema

Mirror the `data/storm_types.json` v2.0 shape from PROJ-300. Each planet type declares its `abilities` block. Where a value is rolled at generation, the registry holds `{"min": x, "max": y}` instead of a fixed value:

```json
{
  "version": "1.0",
  "description": "Planet type intrinsic ability templates. Registered as IAbilitySource via PlanetIntrinsicAbilitySource (PROJ-301).",
  "planet_types": {
    "desert": {
      "name": "Desert",
      "description": "Arid world; stellar heat radiates into nearby space.",
      "abilities": {
        "EnvironmentalDamage": {"rate": {"min": 0.1, "max": 0.3}, "damage_type": "thermal", "scope": "sector"}
      }
    },
    "volcanic": {
      "name": "Volcanic",
      "description": "Plasma plumes from active volcanism reach orbital sectors.",
      "abilities": {
        "EnvironmentalDamage": {"rate": {"min": 0.2, "max": 0.5}, "damage_type": "plasma", "scope": "sector"}
      }
    },
    "gas_giant": {
      "name": "Gas Giant",
      "description": "Massive gravity well slows nearby vessels.",
      "abilities": {
        "ThrustModifier":         {"multiplier": {"min": 0.7, "max": 0.9}, "scope": "sector"},
        "StrategicSpeedModifier": {"multiplier": {"min": 0.7, "max": 0.9}, "scope": "sector"}
      }
    },
    "ice": {
      "name": "Ice",
      "description": "Cold planetoid; minimal effects on transiting fleets.",
      "abilities": {}
    },
    "oceanic": {
      "abilities": {}
    },
    "terrestrial": {
      "abilities": {}
    },
    "barren": {
      "abilities": {}
    },
    "lava": {
      "abilities": {
        "EnvironmentalDamage": {"rate": {"min": 0.3, "max": 0.7}, "damage_type": "plasma", "scope": "sector"}
      }
    }
  }
}
```

### Generation-time roll mechanism

A small helper in `game/strategy/services/ability_sources/intrinsic_roll.py` (or co-located with the adapter) takes a registry `abilities` block and produces a "rolled" abilities dict where `{"min": x, "max": y}` values become a single rolled scalar:

```python
def roll_intrinsic_abilities(template: Dict[str, Any], rng: random.Random) -> Dict[str, Any]:
    """Convert a registry abilities template into a rolled instance dict.

    For each ability_data field whose value is {"min": x, "max": y}, replace
    with a uniform sample in [x, y]. Other values pass through unchanged.
    """
```

This helper is reusable across PROJ-302 (stars), PROJ-303 (warp points), PROJ-304 (system archetypes) — promote it to a shared module if all four projects use it.

### `Planet.intrinsic_abilities` field

```python
@dataclass
class Planet:
    ...existing fields...
    intrinsic_abilities: Dict[str, Any] = field(default_factory=dict)
```

Populated in the planet generator from `data/planet_types.json` + roll helper. Carried through `to_dict`/`from_dict`.

### `PlanetIntrinsicAbilitySource` adapter

```python
@dataclass(frozen=True)
class PlanetIntrinsicAbilitySource:
    planet: Planet

    @property
    def source_kind(self) -> str:
        return 'planet'

    @property
    def source_label(self) -> str:
        return f"{self.planet.name} ({self.planet.planet_type.capitalize()})"

    @property
    def source_id(self) -> str:
        return f"planet_intrinsic:{self.planet.id}"

    @property
    def owner_id(self) -> Optional[int]:
        return None  # Intrinsic effects are ownerless (the volcano damages everyone)

    def get_abilities(self) -> Dict[str, Any]:
        return self.planet.intrinsic_abilities

    def affects_hex(self, hex_coord) -> bool:
        return hex_coord == (self.planet.system.global_location + self.planet.location)

    def affects_system(self, system) -> bool:
        return self.planet in system.planets

    def get_activation_state(self, ability_name: str) -> Optional[Any]:
        return None  # Always-on
```

**Owner_id semantics**: ownerless. A volcanic world damages friend and foe equally. If a future design requires "this planet's effect only applies to its owner" semantics, declare that with a scope keyword like `allied_sector` on the ability — not by toggling owner_id. Keeps the adapter rule simple: intrinsic = ownerless.

### Iterator registration

Add to `game/strategy/services/ability_iterator.py`:

```python
def _planet_intrinsic_provider(system, hex_coord):
    for planet in system.planets:
        source = PlanetIntrinsicAbilitySource(planet)
        if source.get_abilities():  # skip if empty (most planet types)
            yield source

register_source_provider(_planet_intrinsic_provider)
```

Registration happens at module import — same pattern PROJ-300 uses for facilities and storms.

## Swarm Findings Summary

To be filled in at project kickoff after Phase A code review.

### Architecture
TBD — confirmed at kickoff against PROJ-300's framework.

### Key Patterns to Reuse
- **`IAbilitySource` adapter pattern** — `game/strategy/services/ability_sources/storm.py` (PROJ-300 reference) — copy-paste-modify.
- **JSON registry loading** — `game/strategy/generation/storm_generator.py` (PROJ-300 reference) shows the load + per-instance population pattern.
- **Generation-time rolls** — existing planet generation already rolls deposits and similar; reuse the same RNG.
- **Save/load roundtrip** — pattern from `Storm.to_dict`/`from_dict` (PROJ-300).

### Dependencies & Risks
1. **`planet_type` consistency** — registry must list every planet_type the generator produces; missing entries should default to empty `abilities`. Add a validation test.
2. **Save format change** — `Planet.intrinsic_abilities` is a new field. Old saves missing the field default to empty dict — acceptable per the "old saves disposable" policy, but a defaulting `from_dict` is cheap insurance.
3. **Ownerless aggregation** — confirm PROJ-300's `_aggregate` correctly handles ownerless sources contributing to empire-scoped queries; the test in PROJ-300 Phase 4 should already cover this.

### Opportunities Discovered
- Same generation-time-roll helper will be used in PROJ-302/303/304. Promote to shared module immediately or wait for the third user — judgment call at the time.

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.
