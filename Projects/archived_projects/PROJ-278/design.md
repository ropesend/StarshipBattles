# PROJ-278: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Two existing "role" concepts in the codebase

**1. `design_role` (gameplay)** — file [game/strategy/data/design_role.py](../../../game/strategy/data/design_role.py)
- 28 roles loaded from [data/design_roles.json](../../../data/design_roles.json) at startup via `DesignRoleRegistry`
- Each role has: `id`, `display_name`, `description`, `vehicle_type_filter` (which hull classes can take this role)
- Used by:
  - AI behavior dispatch ([game/ai/policy_manager.py](../../../game/ai/policy_manager.py)) — picks targeting/movement policies based on role
  - Formation defaults ([game/simulation/combat/formation.py](../../../game/simulation/combat/formation.py)) — `resolve_default_for_task_force(ships)` buckets by dominant `design_role`
  - Design library filtering ([game/strategy/systems/design_library.py](../../../game/strategy/systems/design_library.py))
- Currently load-once-at-startup, no runtime mutation
- Already moddable in the trivial sense: a modder edits the base JSON file

**2. Combat Lab `role` (scenario wiring labels)** — encoded in `ShipSpec.instance_id`
- Format: `"{test_id}:{role}"` (e.g. `"BEAM-001:attacker"`)
- Roles seen in current templates: `attacker`, `target`, `ship1`, `ship2`
- Used by [combat_lab/runner.py](../../../combat_lab/runner.py)'s `_role_from_instance_id` substring split, fed into `wire_ships(ships_by_role, engine, initial_state)`
- Pure scenario-author wiring concept — players never see these
- Typo in `"attacker"` vs `"attacer"` in a scenario file breaks silently (the runner's lookup just misses)

### Why unification is worth it

- Both currently encode "string label that identifies a Role within a context"
- Both want validation (vehicle_type filtering for design_role; spelling correctness for both)
- Both want documentation (display_name, description) so editors/UI can render them sensibly
- Sharing one `Role` schema and one `RoleRegistry` class lets each context get type safety, runtime add (where it makes sense), and consistent documentation/validation behaviour from one piece of well-tested machinery

### Why instances must remain separate

- A ship's `design_role` is intrinsic ("this is a Carrier")
- A ship's `scenario_role` is positional ("in this test, this ship plays the attacker")
- Same ship can be a `Carrier` design_role AND an `attacker` scenario_role — two orthogonal axes
- One unified `role` field on `ShipSpec` would force a choice between conflating the two or arbitrarily privileging one

## Architecture

### Shared schema and registry

```python
# game/core/roles.py (NEW)

@dataclass(frozen=True)
class Role:
    id: str                              # canonical lookup key
    display_name: str
    description: str
    vehicle_type_filter: Tuple[str, ...] = ()   # empty = no filter

class RoleRegistry:
    """Generic role registry. Two instances exist in the running app:
    one for design_role (gameplay), one for combat_lab scenario_role.
    """
    def __init__(self, *, allow_runtime_add: bool):
        self._roles: Dict[str, Role] = {}
        self._allow_runtime_add = allow_runtime_add
        self._invalidation_callbacks: List[Callable[[], None]] = []

    def load_from_file(self, path: Path, source_tag: str) -> None: ...
    def get(self, role_id: str) -> Role: ...
    def all(self) -> List[Role]: ...
    def add_user_role(self, role: Role) -> None:        # raises if not allow_runtime_add
        ...
        for cb in self._invalidation_callbacks: cb()
    def register_invalidation_callback(self, cb: Callable[[], None]) -> None: ...
```

### Two registry instances

- `design_role_registry = RoleRegistry(allow_runtime_add=True)` — loaded by `ApplicationContext`
  - Sources in priority order (later overrides earlier):
    1. `data/design_roles.json` (base — modders edit this)
    2. `mods/*/design_roles.json` (mod overlays — directory may not exist; iterate if it does)
    3. `user_data/design_roles.json` (player runtime additions, persisted)
  - `add_user_role` writes to `user_data/design_roles.json` and fires invalidation callbacks
- `combat_lab_role_registry = RoleRegistry(allow_runtime_add=False)` — loaded by `TestRunner`
  - Single source: `combat_lab/data/scenario_roles.json`
  - `add_user_role` raises `RoleRegistryReadOnlyError`

### ShipSpec changes

```python
@dataclass(frozen=True)
class ShipSpec:
    # ... existing fields ...
    design_role: Optional[str] = None      # NEW — references design_role_registry
    scenario_role: Optional[str] = None    # NEW — references combat_lab_role_registry
```

### Combat Lab compiler/runner changes

- `combat_lab/spec_compiler.py` populates `scenario_role` directly on each `ShipSpec` instead of encoding it in `instance_id`
- `combat_lab/runner.py` builds `ships_by_role: Dict[str, Ship]` from `engine.ships` by reading `ship_spec.scenario_role` (looked up via spec→ship matching by `instance_id`)
- Delete `_role_from_instance_id` and any `":"` parsing of `instance_id` for role purposes (`instance_id` becomes purely an opaque identifier)

### Cache invalidation contract

- Subsystems that cache `design_role` lookups (`PolicyManager`, formation default tables) call `design_role_registry.register_invalidation_callback(self._invalidate_role_cache)` at construction
- When `add_user_role` is called, every registered callback fires → caches are dropped → next lookup rebuilds

## Key Patterns to Reuse
- **Registry Pattern** — see existing `GameRegistries` ([game/core/registry.py](../../../game/core/registry.py)) for the shape
- **ApplicationContext DI** — register `design_role_registry` here ([game/context.py](../../../game/context.py))
- **Layered config loading** — similar to how mod-style overlays are sometimes structured; document the precedence rules

## Dependencies & Risks
1. **Cache invalidation correctness** — any subsystem that caches role-derived data must register a callback. **Mitigation:** dedicated phase, audit grep for `design_role` lookups, test that runtime add flushes all caches
2. **`user_data/` directory may not exist** — first runtime add creates it. **Mitigation:** loader tolerates missing file; saver creates the directory
3. **Persistence atomicity for `user_data/design_roles.json`** — already covered by `save_json()` atomic write (per memory)
4. **Backwards compatibility for save files containing old design_role string values** — values that no longer exist in the registry. **Mitigation:** lookup returns a sentinel "unknown role" with a WARN log rather than crashing
5. **Combat Lab tests that hard-code `instance_id` substrings** — there may be tests asserting on `"BEAM-001:attacker"` form. **Mitigation:** grep + migrate as part of Phase 3

## Opportunities Discovered
- The same `RoleRegistry` could later host other "named, classified, optionally-typed" concepts (research disciplines, fleet doctrines, etc.) — keep the schema general
- Cache-invalidation pattern can be extracted to a `MutableRegistry` mixin if other registries need runtime add later

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
