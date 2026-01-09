# Simulation Layer Reorganization Proposal

## 1. Executive Summary
This report analyzes the current flat structure of the "Simulation Layer" (Ship, Components, Physics, Combat) and proposes a modular package structure to separate concerns, improve maintainability, and clarify dependencies.

The proposed structure introduces two main top-level packages:
- **`game.engine`**: Generic, low-level systems (Physics, Spatial, Collision) that are game-agnostic.
- **`game.simulation`**: Starship Battles specific logic (Entities, Components, Systems).

## 2. Proposed Directory Structure

```text
c:\Dev\Starship Battles\
├── game\
│   ├── engine\                 # Generic Systems
│   │   ├── __init__.py
│   │   ├── physics.py          # PhysicsBody, Vector2
│   │   ├── spatial.py          # SpatialGrid
│   │   └── collision.py        # Collision logic (raycast, etc)
│   │
│   └── simulation\             # Game Specific Verification Logic
│       ├── __init__.py
│       ├── components\         # ECS Definitions
│       │   ├── __init__.py
│       │   ├── component.py    # Base Component class
│       │   ├── abilities.py    # Ability definitions & Registry
│       │   ├── modifiers.py    # Modifier definitions
│       │   └── resources.py    # ResourceRegistry & Ability Exports
│       │
│       ├── entities\           # Game Objects
│       │   ├── __init__.py
│       │   ├── ship.py         # Main Ship Class
│       │   └── projectile.py   # Projectile Entity
│       │
│       └── systems\            # Logic Systems & Managers
│           ├── __init__.py
│           ├── combat.py       # ShipCombatMixin
│           ├── movement.py     # ShipPhysicsMixin
│           ├── stats.py        # ShipStatsCalculator
│           ├── validator.py    # ShipDesignValidator
│           ├── persistence.py  # ShipIO
│           └── projectile_manager.py
│
└── main.py (Entry point updates imports)
```

## 3. Detailed File Moves

| Current File | New Namespace/Path | Notes |
| :--- | :--- | :--- |
| `components.py` | `game.simulation.components.component` | Defines `Component`, `LayerType`. |
| `abilities.py` | `game.simulation.components.abilities` | Core Ability logic. |
| `component_modifiers.py` | `game.simulation.components.modifiers` | `apply_modifier_effects`. |
| `resources.py` | `game.simulation.components.resources` | *Note: Also holds AbilityRegistry in current impl.* |
| `ship.py` | `game.simulation.entities.ship` | The God Object (Logic Hub). |
| `projectiles.py` | `game.simulation.entities.projectile` | `Projectile` class. |
| `ship_combat.py` | `game.simulation.systems.combat` | Mixin for Ship. |
| `ship_physics.py` | `game.simulation.systems.movement` | Mixin for Ship. |
| `ship_stats.py` | `game.simulation.systems.stats` | Logic-only calculator. |
| `ship_validator.py` | `game.simulation.systems.validator` | Rules engine. |
| `ship_io.py` | `game.simulation.systems.persistence` | Save/Load logic. |
| `physics.py` | `game.engine.physics` | Base `PhysicsBody`. |
| `spatial.py` | `game.engine.spatial` | `SpatialGrid`. |
| `collision_system.py` | `game.engine.collision` | Stateless collision logic. |
| `projectile_manager.py` | `game.simulation.systems.projectile_manager` | State manager for projectiles. |

## 4. Circular Dependency Analysis & Mitigation

### A. The "Ship" Hub
`Ship` is the central dependency for almost all systems.
- **Risk**: `ship.py` imports `stats`, `validator`, `combat`, `movement`. `stats` and `validator` often need to reference `Ship` for type hints or logic.
- **Mitigation**:
    - **Type Hinting**: Use `if TYPE_CHECKING:` blocks for `Ship` imports in `stats.py` and `validator.py`.
    - **Runtime Imports**: `ShipValidator` already uses lazy imports (inside methods) for `ship.VEHICLE_CLASSES`. *This pattern must be preserved.*

### B. Components <-> Resources <-> Abilities
There is a complex inter-dependency here:
- `components.py` imports `resources` (for `ABILITY_REGISTRY`).
- `resources.py` imports `abilities` (to expose them).
- `abilities.py` is generally clean but references component structure.
- **Mitigation**: Move these files together into `game.simulation.components.*`. Intra-package imports will remain consistent. 
    - *Refactor Note*: Ideally, `ABILITY_REGISTRY` should live in `abilities.py`, and `components.py` should import it from there. `resources.py` currently acts as a strange bridge. For this reorg, we will move them "as is" to avoid code breakage, but future refactoring should decouple `resources.py` from Ability definitions.

### C. Mixins (Combat/Movement)
`ship_combat.py` and `ship_physics.py` are Mixins.
- **Risk**: They rely on `self` having attributes defined in `Ship` (e.g., `self.layers`, `self.mass`).
- **Mitigation**: This is standard Python Mixin behavior. As long as `Ship` inherits from them and they don't try to import `Ship`, it is safe. We moved them to `systems` to separate logic from state, but they could also live in `entities/mixins` if desired. `systems` is preferred for logic definition.

## 5. Implementation Steps
1.  **Create Directories**: `game/engine`, `game/simulation/components`, `game/simulation/entities`, `game/simulation/systems`.
2.  **Move Files**: Execute moves and rename files as specified (e.g., `ship_io.py` -> `persistence.py`).
3.  **Update Imports**: Systematic find-and-replace for imports.
    - `from ship import Ship` -> `from game.simulation.entities.ship import Ship`
    - `from components import Component` -> `from game.simulation.components.component import Component`
    - `from location import ...` updates.
4.  **Verify**: Run `unit_tests/` to ensure import paths resolve correctly.
