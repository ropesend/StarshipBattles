# PROJ-269: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to [decisions.md](decisions.md).

---

## 1. Initial Analysis

The three entry paths into the battle simulator were audited in detail before this project started. Reports archived in `findings/`.

### 1.1 Current entry paths (summary)

| Path | Factory | BattleConfig? | Mode handler? | How ships enter | Exit |
|------|---------|---------------|---------------|-----------------|------|
| Battle Setup | `create_manual_battle` | yes (MANUAL) | yes | `controller.add_ships(team_id=)` | `_on_battle_ended` → results → `app._return_to(BATTLE_SETUP)` |
| Strategy | `create_strategy_battle` (half-factory — returns unconfigured controller) | yes (STRATEGY) | yes (query only; `apply_results` no-op) | `controller.add_ships` after adapter-level ship mutation | `_on_battle_ended` → results → `_return_to(STRATEGY)`; **fleet update via `FleetBattleAdapter.update_from_battle_results`, bypassing mode handler** |
| Combat Lab CLI | none — raw `BattleEngine(...)` | **no** | **no** | `scenario.setup()` calls `engine.start([...], [...], seed=)` | bespoke: `scenario.passed = X` + `log_test_execution` |
| Combat Lab UI visual | `BattleController` constructed | yes (TEST) | **partial** — `_is_started=True` forced; `handler.configure` not called | scenario.setup on raw engine from service | via `BattleResultsScreen` |
| Combat Lab UI headless | raw engine via callback | **no** | **no** | scenario.setup | bespoke: registry + test_history |
| Combat Lab UI run-all | raw engine via callback | **no** | **no** | scenario.setup | bespoke: registry + test_history |
| `ComparisonScenario._run_baseline_battle` | raw `BattleEngine(...)` inline | **no** | **no** | engine.start | `_run_validation` |

### 1.2 Irregularities (ranked)

1. **Combat Lab CLI and headless paths bypass the whole controller/service stack.** Raw `BattleEngine(...)` at `combat_lab/runner.py::run_scenario` and in two paths of `test_executor.py`.
2. **`ComparisonScenario` constructs a throwaway engine** inline at `templates.py::_run_baseline_battle`.
3. **`SimulationBattleResolver` applies modifiers by mutating ship attributes** before the engine sees them, bypassing `BattleConfig.team_modifiers`/`global_modifiers`/`environmental_effects`.
4. **Strategy `apply_results` is routed via the adapter, not the mode handler.** `BattleController.apply_results_to_fleets` exists but is never called.
5. **`create_strategy_battle` is a half-factory** — returns an unconfigured controller; caller must add ships separately.
6. **Battle Setup mutates ships in-place with complex modifiers** via `_apply_complex_modifiers()` before passing them to the factory.
7. **Two ship-deserialization paths:** `ShipInstance.to_ship(registries)` vs `ShipSerializer.from_dict(dict, registries)`. Same purpose, different routes.
8. **Seed routing inconsistency:** `BattleConfig.seed` for Battle Setup; `scenario.metadata.seed` + `scenario._override_seed` side-channel attribute for Combat Lab visual.

### 1.3 Target architecture (one-line)

All three contexts produce a `BattleSpec` via a context-specific **compiler**, hand it to `battle_runner.run_battle(spec)`, and consume the resulting `BattleOutcome` through their own logic. The engine is context-blind.

---

## 2. DTO Schemas

### 2.1 `BattleSpec` (frozen dataclass)

```python
@dataclass(frozen=True)
class BattleSpec:
    # Identity
    seed: int
    telemetry_level: TelemetryLevel  # MINIMAL | NORMAL | DETAILED

    # Arena
    boundary: Optional[BoundaryRegion]  # None = unbounded

    # Termination
    end_condition: IEndCondition  # composable, as today
    absolute_max_ticks: int  # engine safety ceiling

    # Teams (N supported; order of list = team_id)
    teams: Tuple[TeamSpec, ...]

    # Modifier stack (species/empire/system/sector)
    modifier_stack: ModifierStack

    # Post-battle hook (Strategy uses this to update fleets; Combat Lab / Setup pass None)
    post_battle_hook: Optional[PostBattleHook]
```

### 2.2 `TeamSpec`

```python
@dataclass(frozen=True)
class TeamSpec:
    team_id: int
    name: str  # "Terran Federation", "Test Team A", "Red Side", ...
    entry_vector: EntryVector  # (origin: Vector2, facing: float) — where the team enters the arena
    fleet_hierarchy: Tuple[TaskForceSpec, ...]
    ai_policy: AIPolicy  # empire-level AI behavior flags
```

### 2.3 `TaskForceSpec` / `SquadronSpec` / `ShipSpec`

```python
@dataclass(frozen=True)
class TaskForceSpec:
    task_force_id: str
    formation: FormationSpec  # default chosen from dominant design_role
    policies: CombatPolicies  # existing TaskForce-level policy bag
    squadrons: Tuple[SquadronSpec, ...]

@dataclass(frozen=True)
class SquadronSpec:
    squadron_id: str
    policies: CombatPolicies  # squadron-level overrides (existing)
    ships: Tuple[ShipSpec, ...]

@dataclass(frozen=True)
class ShipSpec:
    instance_id: str  # stable across battles — allows round-trip to ShipInstance
    design_id: str
    theme_id: str
    name: str
    # Pose at battle start (resolved by FormationResolver from entry_vector + formation)
    position: Vector2
    angle: float
    velocity: Vector2  # usually zero; strategy may carry momentum from the hex approach

    # Persistent per-component HP (enables damage carry-over)
    components: Tuple[ComponentStateSpec, ...]

@dataclass(frozen=True)
class ComponentStateSpec:
    component_id: str
    instance_index: int  # which of the N identical components on this ship
    current_hp: float
    is_active: bool  # player toggle (e.g., offline weapon)
```

### 2.4 `BattleOutcome` (frozen dataclass)

```python
@dataclass(frozen=True)
class BattleOutcome:
    end_reason: EndReason  # which end condition fired
    duration_ticks: int
    seed: int  # echoed for reproducibility
    teams: Tuple[TeamOutcome, ...]  # same team_ids as spec
    telemetry_level: TelemetryLevel  # echoed

@dataclass(frozen=True)
class TeamOutcome:
    team_id: int
    name: str
    fleet_hierarchy: Tuple[TaskForceOutcome, ...]  # mirrors spec, annotated
    ships: Tuple[ShipOutcome, ...]

@dataclass(frozen=True)
class ShipOutcome:
    instance_id: str
    status: ShipStatus  # SURVIVED | DESTROYED | DERELICT | RETREATED
    final_position: Vector2
    final_angle: float
    final_velocity: Vector2
    components: Tuple[ComponentStateSpec, ...]  # same shape as input; reports final HP
    weapons: Tuple[WeaponSummary, ...]  # shots, hits, resolved; always populated (NORMAL+)
    hits_taken: Tuple[HitRecord, ...]  # empty unless telemetry_level=DETAILED
    stats: ShipStats  # total_damage_taken, peak_speed, ticks_derelict, ticks_alive

@dataclass(frozen=True)
class HitRecord:
    tick: int
    attacker_ship_id: str
    weapon_component_id: str
    weapon_ability_class: str  # BeamWeaponAbility | ProjectileWeaponAbility | SeekerWeaponAbility
    damage: float
    modifiers_applied: Tuple[ModifierApplication, ...]  # traceable source of each modifier
```

**Key invariants:**
- `BattleOutcome.teams[i].team_id == BattleSpec.teams[i].team_id` (order preserved).
- Every `ShipSpec` in `BattleSpec` corresponds to exactly one `ShipOutcome` in `BattleOutcome`, matched by `instance_id`. Missing = engine bug.
- `ComponentStateSpec` round-trip: for every component in the input, an entry in the output with updated `current_hp`.

### 2.5 `BoundaryRegion` (abstract + concrete)

```python
class ExitPolicy(Enum):
    DESTROY = "destroy"    # ship removed, status = DESTROYED (warp-out-to-void)
    RETREAT = "retreat"    # ship removed, status = RETREATED
    BOUNCE = "bounce"      # ship bounces back elastically
    NONE = "none"          # ship may exit freely (for unrestricted combat lab scenarios)

class BoundaryRegion(Protocol):
    exit_policy: ExitPolicy
    def contains(self, pos: Vector2) -> bool: ...
    def closest_inside_point(self, pos: Vector2) -> Vector2: ...  # for BOUNCE

@dataclass(frozen=True)
class RectBoundary(BoundaryRegion):
    width: float
    height: float  # centered on (0,0)
    exit_policy: ExitPolicy

@dataclass(frozen=True)
class CircleBoundary(BoundaryRegion):
    radius: float  # centered on (0,0)
    exit_policy: ExitPolicy

@dataclass(frozen=True)
class UnboundedRegion(BoundaryRegion):
    # Always contains every point; exit_policy fixed at NONE.
    exit_policy: ExitPolicy = ExitPolicy.NONE
    def contains(self, pos) -> bool: return True
```

The engine calls `boundary.contains(ship.position)` once per tick per ship. Misses trigger `_apply_exit_policy(ship, boundary.exit_policy)` — either marking the ship (DESTROYED/RETREATED) + removing it, or reflecting its velocity (BOUNCE).

`BattleSpec.boundary: Optional[BoundaryRegion]`. `None` or `UnboundedRegion` = unbounded combat. Strategy pulls a default from game settings; Battle Setup exposes it to the user; Combat Lab scenarios specify it per test.

### 2.6 `ModifierStack`

```python
@dataclass(frozen=True)
class ModifierStack:
    per_team: Mapping[int, Tuple[ModifierEntry, ...]]  # team_id -> modifiers
    global_: Tuple[ModifierEntry, ...]  # applies to all teams

@dataclass(frozen=True)
class ModifierEntry:
    source: str  # "species:Terran", "system:nebula", "sector:ion_storm", "empire:research_xyz"
    stack_group: Optional[str]  # uses existing intra-group MAX, inter-group SUM aggregation
    effect: ModifierEffect  # same shape as existing data/modifiers.json effects
```

Applied by the engine at init — each team/ship has the modifiers attached as ability-like entries in the existing two-phase aggregation. `HitRecord.modifiers_applied` can trace back to `source` for forensic UI.

### 2.7 `FormationSpec`

```python
class FormationShape(Enum):
    LINE_ABREAST = "line_abreast"       # spread perpendicular to entry_vector.facing
    LINE_ASTERN = "line_astern"         # single file along entry_vector.facing
    WEDGE = "wedge"                     # arrowhead pointing in facing direction
    ECHELON_LEFT = "echelon_left"       # diagonal left
    ECHELON_RIGHT = "echelon_right"     # diagonal right
    SCREEN = "screen"                   # heavier ships behind a light-ship screen
    CARRIER_PROTECTED = "carrier_protected"  # carriers center, escorts around
    CUSTOM = "custom"                   # explicit positions provided

@dataclass(frozen=True)
class FormationSpec:
    shape: FormationShape
    spacing: float  # inter-ship distance in pixels
    custom_positions: Tuple[Vector2, ...] = ()  # used only if shape == CUSTOM
```

**Defaults by design_role** (chosen by `FormationResolver` if TaskForce has no explicit formation):
- Dominant Strike → WEDGE
- Dominant Carrier → CARRIER_PROTECTED
- Dominant Defender → LINE_ABREAST
- Dominant Scout/Skirmisher → LINE_ASTERN
- Mixed → LINE_ABREAST

### 2.8 `FormationResolver`

Resolves `(formation, entry_vector, boundary, ship_list, design_roles) → Dict[ship_instance_id, (position, angle)]`. Applied by each compiler while building `ShipSpec.position`/`angle`. Deterministic given same inputs.

### 2.9 `TelemetryLevel`

```python
class TelemetryLevel(Enum):
    MINIMAL = 1   # only end_reason + duration_ticks + team SURVIVED/DEAD summary
    NORMAL = 2    # + per-ship WeaponSummary + ShipStats (no per-hit log)
    DETAILED = 3  # + per-ship HitRecord list (full forensic trail)
```

Implemented as opt-in `CombatEventBus` subscribers. MINIMAL attaches nothing. NORMAL attaches a `WeaponSummary` aggregator + `ShipStats` aggregator. DETAILED additionally attaches a `HitLogRecorder` that appends `HitRecord` entries.

Default per context: Strategy=NORMAL, Battle Setup=NORMAL, Combat Lab=DETAILED (individual scenarios can override).

---

## 3. Engine Entry Point

```python
# game/simulation/battle_runner.py
def run_battle(
    spec: BattleSpec,
    *,
    ai_factory: IAIControllerFactory,
    headless: bool = True,
    per_tick_callback: Optional[Callable[[BattleEngine], None]] = None,
) -> BattleOutcome:
    """Single entry point into the simulator.

    Consumes a fully-specified BattleSpec and returns a BattleOutcome.
    Engine construction, ship instantiation, modifier application, telemetry
    subscription, tick loop, and outcome extraction all live here.

    The `headless`/`per_tick_callback` parameters are operational concerns
    (do we render?) not battle-spec concerns — they stay as function arguments.
    """
```

The existing `BattleController` / `BattleService` keep their lifecycle role for **running** a battle interactively (pause/resume, frame-by-frame for UI). They become an internal implementation detail of `run_battle`. Visual battles pass `headless=False` and a `per_tick_callback` that the UI uses for rendering.

---

## 4. Spec Compilers

### 4.1 Contract

Each compiler is a pure-ish function: `compile(context_inputs) -> BattleSpec`. It knows nothing about the engine; it only translates its own domain state into the common spec shape.

### 4.2 Strategy compiler

`game/strategy/combat/spec_compiler.py`

```python
def build_strategy_battle_spec(
    fleets_on_hex: List[Fleet],
    hex_entries: Dict[str, HexEdge],  # fleet_id -> edge they entered from
    sector: Sector,
    system: System,
    empires: Dict[str, Empire],
    game_settings: GameSettings,
    registries: GameRegistries,
) -> BattleSpec:
    ...
```

Walks fleets → task forces → squadrons → ship instances, reading `ShipInstance.components` for persistent HP. Derives `EntryVector` from each fleet's hex edge of entry (edge centerline + facing toward hex center). Builds `ModifierStack` by walking system/sector/empire/species. Pulls `boundary` from `game_settings.combat_boundary_default`. Sets `telemetry_level=NORMAL`. Attaches a `PostBattleHook` that writes outcomes back to `ShipInstance.components` and updates fleet/empire state.

### 4.3 Battle Setup compiler

`game/ui/screens/battle_setup/spec_compiler.py`

```python
def build_manual_battle_spec(
    ui_state: BattleSetupState,
    registries: GameRegistries,
) -> BattleSpec:
    ...
```

Reads UI state: selected ships per team, selected toggles (species abilities / sector effects / system auras), entry vectors (UI sliders or defaults), boundary choice (UI dropdown: "small / medium / large / unbounded"), end condition (UI checkboxes). Builds `ModifierStack` from the toggles — NOT by mutating ships. Sets `telemetry_level=NORMAL`. No `post_battle_hook` (results shown in UI, not written back anywhere).

### 4.4 Combat Lab compiler

`combat_lab/spec_compiler.py`

```python
def build_test_battle_spec(
    scenario: TestScenario,
    registries: GameRegistries,
) -> BattleSpec:
    ...
```

Each `TestScenario` exposes what it needs (ship files, positions, modifiers, boundary, end condition, telemetry) either via direct attributes or via a `to_spec()` method on the scenario. Template scenarios (`StaticTargetScenario`, `DuelScenario`, `ComparisonScenario`, etc.) implement `to_spec()` once. The compiler just invokes it. `ComparisonScenario` produces two specs (baseline + variant); both go through `run_battle` — no throwaway engine construction.

---

## 5. Strategic Layer Changes

### 5.1 `ShipInstance.components`

```python
@dataclass
class ShipInstance:
    instance_id: str
    design_id: str
    # ...existing fields...
    components: Dict[str, ComponentState] = field(default_factory=dict)
    # Key format: f"{component_id}#{instance_index}"
    # instance_index disambiguates multiple identical components on the same ship.
```

```python
@dataclass
class ComponentState:
    component_id: str
    instance_index: int
    current_hp: float  # persisted between battles
    is_active: bool  # player toggle; default True
```

**Round-trip contract:**
1. Strategy compiler reads `ShipInstance.components` → `ComponentStateSpec` tuples in `ShipSpec`.
2. Engine initializes `Ship` components with the HP from the spec.
3. After battle, `ShipOutcome.components` carries updated HP.
4. `PostBattleHook` copies outcome HP back to `ShipInstance.components`.

On first migration: for existing saves without `components`, populate from the design at full HP. Per CLAUDE.md ("saves are disposable"), this isn't a save-format migration — just a one-shot "missing field gets default" on load.

### 5.2 `TaskForce.formation`

```python
@dataclass
class TaskForce:
    # ...existing...
    formation: Optional[FormationSpec] = None  # None = use design_role default
```

Settable via UI (future project); default chosen by `FormationResolver` based on dominant design_role in the task force.

### 5.3 `FleetBattleAdapter` replacement

`FleetBattleAdapter.to_battle_ships` and `update_from_battle_results` are replaced by:
- **Spec compiler** handles `Fleet → ShipSpec` via `ShipInstance.components`.
- **`PostBattleHook`** (closure returned by the compiler) handles `BattleOutcome → ShipInstance` via `instance_id` matching.

`SimulationBattleResolver` shrinks to:
```python
def resolve_battle(
    fleets: List[Fleet], sector, system, empires, settings, registries,
) -> BattleOutcome:
    spec = build_strategy_battle_spec(fleets, ..., registries)
    return run_battle(spec, ai_factory=self._ai_factory)
    # The spec's post_battle_hook mutates ShipInstance.components + Fleet as a side effect.
```

---

## 6. Migration Strategy (Phased)

Each phase is independently shippable. The game remains runnable at every commit. Tests remain green. Legacy code paths coexist with new ones until Phase 6.

| # | Phase | Gated behind | Rollback path |
|---|-------|--------------|---------------|
| 1 | DTO boundary + compilers | `run_battle` exists; old factories still work | Delete `battle_runner.py` + compilers; no change to engine |
| 2 | Component HP persistence | `ShipInstance.components` field; default empty | Field stays but is unused; engine reads from `ShipDesign` as today |
| 3 | Boundary + N-team | `BattleSpec.boundary`, `BattleSpec.teams: list` supports any length | Unbounded + 2 teams = identical to today |
| 4 | Formation system | `TaskForce.formation` + `FormationResolver` | Compilers still fall back to today's positioning when formation is None |
| 5 | Telemetry levels | `TelemetryLevel` field; NORMAL is the default that matches today | MINIMAL / DETAILED are opt-in |
| 6 | Delete legacy | After all three contexts go through `run_battle` | Last phase — no rollback, just don't land it |

Between phases, both paths (old factories + `run_battle`) exist. The three compilers are wired up in Phase 1 but Combat Lab / Setup / Strategy still call the old factories. Each subsequent phase migrates one context at a time.

---

## 7. Layer Contracts

```
┌────────────────────────────────────────────────────────────┐
│  UI Layer (game/ui/)                                       │
│    Battle Setup spec_compiler                              │
│    Combat Lab spec_compiler                                │
│    Test Lab screens (unchanged API surface)                │
│    Battle Screen (consumes BattleOutcome for display)      │
└─────────────────────────────┬──────────────────────────────┘
                              │
┌─────────────────────────────▼──────────────────────────────┐
│  Strategy Layer (game/strategy/)                           │
│    Strategy spec_compiler                                  │
│    SimulationBattleResolver (shrunk; calls run_battle)     │
│    ConflictResolutionEngine                                │
│    PostBattleHook implementation (updates ShipInstance)    │
└─────────────────────────────┬──────────────────────────────┘
                              │
┌─────────────────────────────▼──────────────────────────────┐
│  Simulation Layer (game/simulation/) — CONTEXT-BLIND       │
│    run_battle(spec) -> outcome                             │
│    BattleSpec / BattleOutcome DTOs                         │
│    BoundaryRegion / FormationResolver / TelemetryLevel     │
│    BattleEngine (accepts boundary, N teams, telemetry)     │
└────────────────────────────────────────────────────────────┘
```

**Layer invariants enforced by this design:**
- Simulation imports only `game.core` and its own sub-packages. No import from strategy / UI / combat_lab.
- Strategy imports simulation (for DTOs + `run_battle`) but not UI.
- UI imports simulation + strategy.
- `combat_lab` imports simulation but not game UI internals.
- `BattleSpec` / `BattleOutcome` live in `game/simulation/` so every layer can import them.

---

## 8. Risks & Mitigations

1. **`BattleOutcome` becomes enormous for long DETAILED battles** — Combat Lab 100k-tick scenarios could produce huge hit logs.
   - *Mitigation:* DETAILED level is opt-in per scenario; MINIMAL for batch runs. Hit log can be segmented by ship (so only affected ships carry it) and stats can be streamed via callback instead of accumulated if we hit real memory issues.

2. **Formation defaults might surprise players** — auto-WEDGE for strike fleets may differ from what Battle Setup does today.
   - *Mitigation:* Phase 4 adds formation with `None` → design_role default; UI authoring is a later project. Battle Setup's existing positioning can be preserved as an explicit `FormationShape.CUSTOM` default until UI lands.

3. **N-team AI targeting** — today's AI assumes two teams. Generalizing "closest enemy" is easy; targeting policies with team bias might need rework.
   - *Mitigation:* User confirmed no target preference. AI treats everyone not on `my team_id` as equally valid. `IsEnemy(ship) = ship.team_id != self.team_id` — straightforward.

4. **Combat Lab scenarios have rich assumptions about the engine** — direct calls to `engine.update()`, peek at `engine.projectiles`, etc.
   - *Mitigation:* `run_battle` still runs the engine; scenarios can still attach per-tick callbacks for observation. What goes away is direct `BattleEngine(...)` construction, not engine inspection.

5. **Save format breakage** — existing saves lack `ShipInstance.components`.
   - *Mitigation:* CLAUDE.md rule: saves are disposable. On load, missing `components` defaults to full-HP from the design. No migration shim for prior saves.

6. **Modifier source tracing** requires every existing modifier entry to carry a `source` string.
   - *Mitigation:* Existing `Modifier` class may not have `source`. Extend it in Phase 1 alongside `ModifierStack`. Legacy modifiers get `source="legacy"` until callers are updated.

---

## 9. Testing Strategy

- **TDD throughout.** Each task's first action is "write a failing test."
- **Phase 1** exercises the DTO shape: round-trip tests (`spec → outcome` preserves `instance_id` / `team_id`), compiler-per-context unit tests with hand-built inputs.
- **Phase 2** exercises persistence: create a damaged ship → compile to spec → run a trivial battle → verify outcome HP → write back → compile again → verify damage carries.
- **Phase 3** exercises boundary: place a ship outside a `RectBoundary`, run 1 tick, verify exit policy applied. N-team: 3-team battle ends when 2 teams eliminated.
- **Phase 4** exercises formation: each shape produces expected relative ship positions; rotation by entry_vector.facing; spacing respected.
- **Phase 5** exercises telemetry levels: MINIMAL outcome has empty hit_log; NORMAL has weapon summaries; DETAILED has full hit log. Per-level memory and performance measured with one reference scenario.
- **Phase 6** is a removal phase: each deletion must be preceded by verifying no caller exists.
- **Combat Lab fast suite** (`python -m combat_lab.run_tests --fast`) must stay green after every phase (162+ passing).

---

## 10. Open Questions / Follow-ups

- Repair mechanic (deferred) — future project.
- Formation authoring UI (deferred) — future UI project.
- Alliance / non-aggression system (deferred) — requires target-selection changes.
- Sector effect library — what sectors offer which modifiers. Out of scope for the plumbing; content comes later.

---

*Last edited: 2026-04-12 — initial project plan.*
