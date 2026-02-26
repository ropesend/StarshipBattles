# PROJ-194: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Baseline
- **12,718 tests passing**, 1 skipped, 0 failures

### Scope: ~90 instances across ~21 files

| Area | Files | Instances |
|------|-------|-----------|
| `game/ui/screens/builder/` | 12 | 57 |
| `game/ui/screens/workshop_*.py` | 5 | 18 |
| `game/ui/panels/` (builder-related) | 5 | ~15 |

**Heaviest files:** stats_config.py (20), weapons_viewmodel.py (11), workshop_event_router.py (9), right_panel.py (7), design_report_panel.py (7)

### Pattern Categories

1. **Ship Stat Access** (~35) — `getattr(ship, 'attr', 0)` for stat display
2. **Weapon Ability Access** (~12) — `getattr(ab, 'base_accuracy', 2.0)` etc.
3. **Component Property Checks** (~10) — `hasattr(comp, 'ability_instances')`
4. **GUI Panel Existence** (~15) — `hasattr(gui, 'panel_name')` init-order defense
5. **Pygame Event Checks** (~5) — `hasattr(event, 'ui_element')` (out of scope)
6. **Self-Attribute Checks** (~13) — `hasattr(self, ...)` defensive patterns

### Existing Protocol Infrastructure
- 21+ `@runtime_checkable` Protocols in `game/core/protocols.py`
- Convention: `IProtocolName` + `is_protocol_name()` TypeGuard pattern
- Layer interfaces in `game/*/interfaces/`
- Boundary protocols (IPostBattleShip, IResourceReader) already solved this for strategy-simulation

### Opportunities
- WeaponAbility has well-defined properties — Protocol is a clean fit
- Component.ability_instances always exists — hasattr is unnecessary
- Ship.resources always exists (Optional) — hasattr is unnecessary

### Risks
- Ship class is massive — IBuilderShip could become a god interface
- Dynamic attribute names (`f'{res}{attr_suffix}'`) resist static typing
- GUI panel hasattr checks are init-order issues, not type issues

## Swarm Findings Summary
Combined analysis from individual agent reports in `findings/`.

### Architecture

| Category | Count | Fix Strategy |
|----------|-------|-------------|
| Unnecessary getattr (attr always exists) | ~35 | Direct attribute access |
| Unnecessary hasattr (method always exists) | ~20 | Remove check, call directly |
| Mode-dependent button init-order | ~9 | Declare Optional attrs in __init__ |
| Self-attribute init-order checks | ~8 | Ensure all attrs in __init__ |
| Dynamic resource attributes | ~8 | Typed accessor method on Ship |
| Legitimate subtype checks | ~5 | isinstance or Protocol |
| StatDefinition.get_value() generic dispatch | 2 | Keep (intentional design) |

~65 of ~87 in-scope instances are pure deletions (attr always exists).

### Key Patterns to Reuse
- **IPostBattleShip**: `game/core/protocols.py:444-490` — Boundary protocol pattern
- **StatDefinition dispatch**: `stats_config.py:25-30` — Generic getattr is intentional (keep)
- **Component.has_ability()**: Proper interface already, no Protocol needed

### Dependencies & Risks
1. `workshop_screen.py:286` setattr pattern — must pre-declare button attrs
2. `stats_config.py` dynamic resources — need typed accessor on Ship
3. `components.py:123` BeamWeaponAbility subtype check — use isinstance
4. `modifier_impact_grid.py:172` STAT_BINDINGS check — legitimate class feature check

### Opportunities Discovered
1. ~35 pure deletions (getattr where attr always present)
2. Pre-declaring Optional button attrs eliminates 5-6 hasattr checks
3. Single `ship.get_resource_stat()` replaces ~8 dynamic getattr calls, portable to C#/C++/Rust
4. No IBuilderShip/IBuilderComponent Protocols needed — Ship/Component APIs are stable

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
