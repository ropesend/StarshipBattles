# Phase 1: Define Protocols (Pure Additions)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-190 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Create all 15 protocol definitions in 3 new files. No behavioral changes — purely additive.

---

## Tasks

### Task 1.1: Create ability_protocols.py [Medium]
**File:** `game/simulation/interfaces/ability_protocols.py` (NEW)
**Tests:** `pytest tests/unit/simulation/ -n 12` (sanity check — no changes expected)

- [x] Create file with module docstring explaining purpose and portability goals
- [x] Import: `typing.Protocol`, `runtime_checkable`, `TYPE_CHECKING`, `TypeGuard`, `Optional`, `List`, `Dict`, `Any`, `Set`
- [x] Define `IAbility` protocol:
  - `trigger: str` (property)
  - `stack_group: Optional[str]` (property)
  - `tags: Set[str]` (property)
  - `get_ui_rows() -> List[Dict[str, str]]` (method)
  - `get_effect_summary() -> List[Dict[str, Any]]` (method)
  - `sync_data() -> None` (method)
- [x] Define `IResourceConsumptionAbility(IAbility)` protocol:
  - `resource_type: str` (property)
  - `amount: float` (property)
  - `check_available() -> bool` (method)
- [x] Define `IResourceStorageAbility(IAbility)` protocol:
  - `resource_type: str` (property)
  - `max_amount: float` (property)
- [x] Define `IResourceGenerationAbility(IAbility)` protocol:
  - `resource_type: str` (property)
  - `rate: float` (property)
- [x] Define `IWeaponAbility(IAbility)` protocol:
  - `damage: float`, `range: float`, `reload_time: float`, `firing_arc: float` (properties)
  - `get_damage(range_to_target: float = 0) -> float` (method)
- [x] Define `IBeamWeaponAbility(IWeaponAbility)` protocol:
  - `base_accuracy: float`, `accuracy_falloff: float` (properties)
- [x] Define `ISeekerWeaponAbility(IWeaponAbility)` protocol:
  - `projectile_speed: float`, `endurance: float`, `turn_rate: float`, `projectile_damage: float`, `projectile_hp: float` (properties)
- [x] Define `IProjectileWeaponAbility(IWeaponAbility)` protocol:
  - `projectile_speed: float` (property)
- [x] Define `IWarpJumpAbility(IAbility)` protocol:
  - `max_tonnage: float`, `energy_cost: float` (properties)
- [x] Add TypeGuard helper functions: `is_resource_consumption()`, `is_resource_storage()`, `is_resource_generation()`, `is_weapon()`, `is_beam_weapon()`, `is_seeker_weapon()`, `is_projectile_weapon()`, `is_warp_jump()`
- [x] Verify: `python -c "from game.simulation.interfaces.ability_protocols import IAbility"` succeeds

**Notes:** Created with 9 ability protocols + is_ability TypeGuard. All imports verified.

---

### Task 1.2: Create component_protocols.py [Simple]
**File:** `game/simulation/interfaces/component_protocols.py` (NEW)
**Tests:** `pytest tests/unit/simulation/ -n 12`

- [x] Create file with module docstring
- [x] Define `IComponent` protocol:
  - Properties: `id: str`, `name: str`, `is_active: bool`, `current_hp: int`, `max_hp: int`, `status: Any` (ComponentStatus), `ability_instances: List[Any]`, `abilities: Dict[str, Any]`, `modifiers: List[Any]`, `stats: Dict[str, Any]`, `ability_stats: Dict[str, Dict[str, Any]]`, `ship: Optional[Any]`, `shots_fired: int`, `shots_hit: int`, `cost: int`, `layer_assigned: Optional[Any]`
  - Methods: `get_abilities(name: str) -> List[Any]`, `get_ability(name: str) -> Optional[Any]`, `has_ability(name: str) -> bool`, `has_pdc_ability() -> bool`, `can_afford_activation() -> bool`
- [x] Add `is_component()` TypeGuard function
- [x] Verify: `python -c "from game.simulation.interfaces.component_protocols import IComponent"` succeeds

**Notes:** Created with IComponent protocol covering all documented members.

---

### Task 1.3: Create entity_protocols.py [Medium]
**File:** `game/simulation/interfaces/entity_protocols.py` (NEW)
**Tests:** `pytest tests/unit/simulation/ -n 12`

- [x] Create file with module docstring
- [x] Import Vector2 type under TYPE_CHECKING
- [x] Define `ICombatShip` protocol:
  - Identity: `name: str`, `team_id: int`, `angle: float`
  - Physics: `position: Any`, `velocity: Any`, `radius: float`, `mass: float`
  - Health: `hp: int`, `max_hp: int`, `is_alive: bool`, `is_derelict: bool`
  - Defense: `current_shields: float`, `max_shields: int`, `emissive_armor: int`, `crystalline_armor: int`, `shield_regen_rate: float`, `repair_rate: float`
  - Targeting: `current_target: Optional[Any]`, `secondary_targets: List[Any]`, `max_targets: int`, `total_defense_score: float`
  - Structure: `layers: Dict[Any, Any]`, `resources: Any`, `combat_engine: Any`
  - Methods: `get_all_components() -> List[Any]`, `iter_components() -> Any`, `get_components_by_ability(name: str) -> List[Any]`, `recalculate_stats() -> None`
- [x] Define `IProjectile` protocol:
  - `owner: Optional[Any]`, `team_id: int`, `position: Any`, `velocity: Any`
  - `damage: float`, `max_range: float`, `endurance: Optional[float]`, `max_endurance: float`
  - `type: Any` (AttackType), `is_alive: bool`, `status: str`
  - `source_weapon: Optional[Any]`, `target: Optional[Any]`
  - `turn_rate: float`, `max_speed: float`, `hp: int`, `max_hp: int`
  - `distance_traveled: float`, `radius: float`
- [x] Define `IPhysicsShip` protocol:
  - `is_thrusting: bool`, `engine_throttle: float`, `turn_throttle: float`
  - `mass: float`, `turn_speed: float`, `acceleration_rate: float`
- [x] Define `IFormationHost` protocol:
  - `formation: Any`
- [x] Define `ISerializableShip` protocol:
  - `total_strategic_movement: float`, `warp_max_tonnage: float`, `warp_energy_cost: float`
  - `ship_class: str`, `vehicle_type: str`, `theme_id: str`
- [x] Add TypeGuard helpers: `is_combat_ship()`, `is_projectile()`, `is_physics_ship()`, `is_formation_host()`, `is_serializable_ship()`
- [x] Verify: `python -c "from game.simulation.interfaces.entity_protocols import ICombatShip"` succeeds

**Notes:** Created with 5 entity protocols + TypeGuards.

---

### Task 1.4: Update interfaces/__init__.py [Simple]
**File:** `game/simulation/interfaces/__init__.py`
**Tests:** `pytest tests/unit/simulation/ -n 12`

- [x] Import and re-export all protocols from `ability_protocols`, `component_protocols`, `entity_protocols`
- [x] Import and re-export all TypeGuard functions
- [x] Update `__all__` list
- [x] Verify: `python -c "from game.simulation.interfaces import ICombatShip, IComponent, IAbility"` succeeds
- [x] Run full simulation unit tests: `pytest tests/unit/simulation/ -n 12` — all pass

**Notes:** All 15 protocols + 14 TypeGuards exported. 2594 simulation unit tests passing.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/unit/simulation/ -n 12` — all pass (no regressions)
- [x] All 15 protocols importable from `game.simulation.interfaces`
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
