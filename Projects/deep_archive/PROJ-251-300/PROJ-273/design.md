# PROJ-273: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

The combat system review (2026-04-16) surfaced duplicate ability→stat_key mapping between two spec compilers:

**Battle Setup** (`game/ui/screens/battle_setup/spec_compiler.py:70-74`):
```python
_ABILITY_TO_STAT_KEY = {
    "ShieldProjection": ("shield_bonus_add", "add"),
    "ShieldModifier":   ("shield_capacity_mult", "multiply"),
    "DamageModifier":   ("damage_mult", "multiply"),
}
```

**Strategy** (`game/strategy/combat/spec_compiler.py`): Same three stat_keys emitted via hand-rolled function bodies — `_entries_from_environmental_effects` (L336) for storm hex shield interference, `_entries_from_fleet_combat_modifiers` (L363) for per-team fleet modifiers. Five separate hardcoded `stat_key="..."` calls at lines 353, 385, 400, 412, 444.

The duplication is **unenforced** by any test. When a fourth ability (say `ThrustModifier` → `thrust_mult`) is added, the author must touch three places: the registry, the ability class, AND every compiler that emits it. Nothing alerts you if you miss one.

A skeptic review already flagged the weakness of the existing guard test: `tests/unit/simulation/test_unified_entry_guard.py` iterates a **hardcoded list** of 10 `qs_*_complex` designs. New complex files aren't auto-covered. A content author can add `qs_sector_thrust_booster_complex.json` with an unmapped `ThrustModifier` and the survey check passes vacuously.

## Swarm Findings Summary

Combined from the four Explore agents run during the review:

### Architecture
- Both compilers live at the UI/strategy layer — the shared module must sit below them. `game/simulation/combat/` is the natural home.
- `ModifierEntry` is the emitted DTO (`game/simulation/combat/modifier_stack.py`). Registry produces these directly.
- `FleetAuraManager._apply_bonuses` is the consumer. Today it aggregates ALL entries into `ship.external_stats` keyed by `effect.stat_key` and silently ignores any key it doesn't recognize downstream (abilities never read it).

### Key Patterns to Reuse
- **Frozen-dataclass DTO** (`docs/02_PATTERNS.md` pattern 3): new `AbilityStatMapping` dataclass should be frozen + typed.
- **Protocol-driven emission**: one helper function `emit_entries_for_ability(ability_name, ability_data, scope, owner_team, num_teams, source)` imported by both compilers. Future: plug into N-team routing in PROJ-275.
- **Once-per-source WARN logging** (already used in `FleetAuraManager`): when unknown stat_key appears, warn once per (stat_key, source) pair.

### Dependencies & Risks
1. **Risk: breaking existing stat_key strings.** Registry must preserve the exact three strings — `shield_bonus_add`, `shield_capacity_mult`, `damage_mult` — because ship_stats.py and individual abilities read them directly. Mitigation: registry values are literal strings, tested against current ship_stats.py assumptions.
2. **Dependency blocker for PROJ-275:** N-team routing needs `_route_team_for_scope` to return `List[int]` instead of `int`. This project preserves the current `int` return; PROJ-275 changes it after this lands.
3. **Risk: registry-driven emission changes entry ordering.** Tests that assert specific `modifier_stack` entry order may break. Mitigation: registry iteration order is deterministic (dict preserves insertion order in Python 3.7+).

### Opportunities Discovered
- Unknown-stat_key warning in `FleetAuraManager` is a small add that catches a whole class of silent bugs — worth landing even without the wider refactor.
- Glob-driven design survey is reusable beyond this project; PROJ-275 will want the same iteration pattern.

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.

## Interface Sketch

```python
# game/simulation/combat/ability_stat_registry.py

from dataclasses import dataclass
from typing import Literal, Dict, List, Optional

@dataclass(frozen=True)
class AbilityStatMapping:
    ability_class_name: str
    stat_key: str
    operation: Literal["add", "multiply"]
    value_field: str  # "multiplier" for modifiers, "value" for ShieldProjection

ABILITY_STAT_REGISTRY: Dict[str, AbilityStatMapping] = {
    "ShieldProjection": AbilityStatMapping("ShieldProjection", "shield_bonus_add", "add", "value"),
    "ShieldModifier":   AbilityStatMapping("ShieldModifier", "shield_capacity_mult", "multiply", "multiplier"),
    "DamageModifier":   AbilityStatMapping("DamageModifier", "damage_mult", "multiply", "multiplier"),
}

def emit_entries_for_ability(
    ability_name: str,
    ability_data: dict | float,
    *,
    scope: str,
    owner_team: int,
    num_teams: int,
    source: str,
    stack_group: Optional[str] = None,
) -> List[ModifierEntry]:
    """Emit zero or more ModifierEntry objects for a single ability.

    Scope routing: 'enemy_*' scopes fan out to all non-owner teams (one
    entry per opponent). Own-team scopes emit one entry for owner_team.

    Returns [] if ability is not in the registry.
    """
    ...
```

Both compilers import `ABILITY_STAT_REGISTRY` (or, more typically, just call `emit_entries_for_ability`). The strategy compiler's `_entries_from_fleet_combat_modifiers` becomes a thin mapper: `FleetCombatModifiers.shield_mult` → `emit_entries_for_ability("ShieldModifier", ...)`.
