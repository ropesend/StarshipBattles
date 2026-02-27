# PROJ-190: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Problem Statement
The `game/simulation/` layer has ~97 `hasattr()`/`getattr()` calls across 30 files. These implicit duck-typed contracts:
- Obscure dependency boundaries from developers and static type checkers
- Hide missing attributes from IDE intelligence
- Make refactoring dangerous and brittle
- Block portability to statically-typed languages (C#, C++, Rust)

### Baseline
- **12,705 tests passing**, 1 skipped
- **97 duck-typed calls** in `game/simulation/` across 30 files
- **655 total** across the entire codebase (this project covers simulation only)

### Duck Typing Categories in game/simulation/

| Category | Count | % | Description |
|----------|-------|---|-------------|
| Default Value Fallbacks | 44 | 45% | `getattr(obj, 'attr', default)` with sensible defaults |
| Intentional Duck Typing | 35 | 36% | Ability property extraction, resource type detection, PDC tag detection |
| Lazy Init / Self-Guards | 15 | 15% | `hasattr(self, '_private_attr')` for deferred creation |
| Introspection | 3 | 3% | formula_system.py builtins check |

### Files Most Affected
1. `game/simulation/entities/ship_stats.py` - 13 calls
2. `game/simulation/components/abilities/base.py` - 9 calls
3. `game/simulation/combat/targeting_system.py` - 6 calls
4. `game/simulation/components/modifier_introspection.py` - 6 calls
5. `game/simulation/entities/combat_endurance.py` - 5 calls

### Existing Protocol Infrastructure
The codebase already has well-established protocol patterns:
- `game/core/protocols.py` — IRegistryProvider, IFleet, IPlanet, IScene, IPostBattleShip, IResourceReader, IResourceHolder + TypeGuard functions
- `game/simulation/interfaces/ai_controller.py` — IAIController, IAIControllerFactory
- `game/simulation/interfaces/battle_resolver.py` — IBattleResolver
- All use `@runtime_checkable` and `TYPE_CHECKING` imports

---

## Swarm Findings Summary

### Architecture Analysis

**Layer Separation: CLEAN**
- Simulation layer imports only from `game/core/` — no upward imports
- `TYPE_CHECKING` imports used consistently for cross-layer type hints
- No circular dependencies detected — safe to introduce new protocols

**Entity Hierarchy:**
```
PhysicsBody (game/engine/physics.py)
├── Ship + ShipPhysicsMixin (game/simulation/entities/)
│   layers: Dict[LayerType, LayerData]
│   components: List[Component]
│   resources: ResourceRegistry
└── Projectile (game/simulation/entities/projectile.py)

Component (game/simulation/components/component.py)
└── ability_instances: List[Ability]
    └── modifiers: List[ApplicationModifier]

Ability (game/simulation/components/abilities/base.py)
├── WeaponAbility → ProjectileWeaponAbility, BeamWeaponAbility, SeekerWeaponAbility
├── Propulsion → CombatPropulsion, ManeuveringThruster, StrategicMovement, WarpJump
├── Defense → ShieldProjection, ShieldRegeneration, EmissiveArmor
├── Resources → ResourceConsumption, ResourceStorage, ResourceGeneration
└── 20+ specialized ability types
```

### Key Patterns to Reuse

- **Protocol + TypeGuard pattern**: `game/core/protocols.py:1-19` — Every protocol has a matching `is_X()` TypeGuard function
- **@runtime_checkable**: All existing protocols use this decorator
- **TYPE_CHECKING imports**: Prevents circular dependencies at runtime
- **Minimal interfaces**: `IAIController` only includes methods BattleEngine actually calls

### Dependencies & Risks

1. **Test Mock Specs (~50-80 failures expected)**: 18-22 test files create mocks with `MagicMock(spec=[...])` that don't include all attributes. After Protocol typing makes attribute access direct, these mocks will fail. Mitigation: Update mock specs in dedicated Phase 5.

2. **Lazy Init Pattern (Low Risk)**: `ship.py:228` uses `hasattr(self, '_combat_engine')`. Mitigation: Initialize to None in `__init__`, use `is None` check.

3. **formula_system.py Builtins Check (Exempt)**: `hasattr(builtins, name)` is legitimate Python introspection that has no equivalent in C#/Rust. Leave as-is.

4. **Simulation Test Framework**: `simulation_tests/scenarios/base.py` uses `getattr` for optional stat extraction from ships. These are read-only extraction and should remain defensive since scenarios deal with variable ship configurations.

### Opportunities Discovered

- **Ability typing will enable IDE autocomplete** for the entire ability system — currently invisible to type checkers
- **Protocol hierarchy maps 1:1 to C# interfaces / Rust traits** — direct portability path
- **isinstance() checks replace fragile string-based type detection** (e.g., PDC tag checking, resource type detection via `__class__.__name__`)

---

## Protocol Hierarchy Design

### File Organization
```
game/simulation/interfaces/
    __init__.py              — Updated exports
    ai_controller.py         — EXISTING (no changes)
    battle_resolver.py       — EXISTING (no changes)
    ability_protocols.py     — NEW: 9 ability protocols
    component_protocols.py   — NEW: IComponent
    entity_protocols.py      — NEW: 5 entity protocols
```

### ability_protocols.py (9 protocols)

| Protocol | Extends | Key Members | Implemented By |
|----------|---------|-------------|----------------|
| `IAbility` | Protocol | `trigger`, `stack_group`, `tags`, `get_ui_rows()`, `get_effect_summary()`, `sync_data()` | Ability base class |
| `IResourceConsumptionAbility` | IAbility | `resource_type`, `amount`, `check_available()` | ResourceConsumption |
| `IResourceStorageAbility` | IAbility | `resource_type`, `max_amount` | ResourceStorage |
| `IResourceGenerationAbility` | IAbility | `resource_type`, `rate` | ResourceGeneration |
| `IWeaponAbility` | IAbility | `damage`, `range`, `reload_time`, `firing_arc`, `get_damage()` | WeaponAbility |
| `IBeamWeaponAbility` | IWeaponAbility | `base_accuracy`, `accuracy_falloff` | BeamWeaponAbility |
| `ISeekerWeaponAbility` | IWeaponAbility | `projectile_speed`, `endurance`, `turn_rate`, `projectile_damage`, `projectile_hp` | SeekerWeaponAbility |
| `IProjectileWeaponAbility` | IWeaponAbility | `projectile_speed` | ProjectileWeaponAbility |
| `IWarpJumpAbility` | IAbility | `max_tonnage`, `energy_cost` | WarpJump |

### component_protocols.py (1 protocol)

| Protocol | Key Members | Implemented By |
|----------|-------------|----------------|
| `IComponent` | `ability_instances`, `abilities`, `modifiers`, `stats`, `ability_stats`, `ship`, `shots_fired`, `cost`, `status`, `has_ability()`, `get_abilities()`, `get_ability()`, `has_pdc_ability()` | Component |

### entity_protocols.py (5 protocols)

| Protocol | Key Members | Implemented By |
|----------|-------------|----------------|
| `ICombatShip` | `is_alive`, `team_id`, `position`, `velocity`, `current_shields`, `emissive_armor`, `current_target`, `layers`, `resources`, `combat_engine`, `recalculate_stats()` | Ship |
| `IProjectile` | `owner`, `team_id`, `type`, `target`, `source_weapon`, `endurance`, `hp`, `max_hp`, `turn_rate`, `max_speed`, `distance_traveled`, `status` | Projectile |
| `IPhysicsShip` | `is_thrusting`, `engine_throttle`, `turn_throttle` | Ship (via ShipPhysicsMixin) |
| `IFormationHost` | `formation` | Ship |
| `ISerializableShip` | `total_strategic_movement`, `warp_max_tonnage`, `warp_energy_cost`, `vehicle_type`, `theme_id` | Ship |

### Lazy Init Handling (Not Protocols)

| Pattern | File:Line | Resolution |
|---------|-----------|------------|
| `hasattr(self, '_ability_index')` | `component.py:207,216,226` | Initialize `{}` in `__init__` — already done; remove redundant guards |
| `hasattr(self, '_combat_engine')` | `ship.py:228` | Initialize `None` in `__init__`, use `is None` check |
| `getattr(ship, '_prev_max_*', 0)` | `ship_stats.py:496-499` | Already initialized in `Ship.__init__` — use direct access |
| `getattr(ship, '_resources_initialized', False)` | `ship_stats.py:506` | Already initialized — use direct access |
| `getattr(component, 'evaluated_resource_cost', None)` | `component_resource_manager.py:96` | Initialize `None` in `Component.__init__` |

### C#/Rust Portability Mapping

| Python Pattern | C# Equivalent | Rust Equivalent |
|---|---|---|
| `@runtime_checkable Protocol` | `interface IAbility` | `trait Ability` |
| `isinstance(ab, IWeaponAbility)` | `ab is IWeaponAbility` | `ab.downcast_ref::<dyn WeaponAbility>()` |
| `getattr(x, 'foo', default)` | `(x as IFoo)?.Foo ?? default` | `x.foo().unwrap_or(default)` |
| `hasattr(x, 'foo')` | `x is IFoo` | Pattern matching on trait objects |
| Protocol composition | Interface inheritance | Trait bounds |

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
