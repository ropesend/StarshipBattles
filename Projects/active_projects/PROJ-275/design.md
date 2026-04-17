# PROJ-275: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation.

## Initial Analysis

The combat engine ALREADY supports N teams:
- `engine.start_teams(teams: Dict[int, List[Ship]])` — N-team entry
- `engine.get_enemies_of(ship)` — filters on `team_id != ship.team_id` (everyone else hostile)
- `TeamEliminatedCondition` — "ends when ≤1 team retains alive ships" (correct for any N)
- `tests/integration/simulation/test_three_team_battle.py` — existing proof

The gap is in **compilers and UI**:

| Layer | 2-team assumption |
|-------|-------------------|
| Battle Setup UI | `BattleSetupState.side_0` / `side_1` — hardcoded two fields |
| Battle Setup compiler | `_NUM_TEAMS = 2` at L92; `_route_team_for_scope` returns single `int` (L452); `raise NotImplementedError` for 3+ at L467-474 |
| Strategy adapter | `SimulationBattleResolver.resolve_battle(fleet1, fleet2, ...)` takes two fleets; `team_modifiers[0]` / `[1]` hardcoded (L184-188) |
| Strategy conflict resolution | `ConflictResolutionEngine` decomposes 3+ empires into sequential 2-fleet battles |
| Strategy spec compiler | Similar — iterates 2 fleets only |

**Per user**: "sequential 2-team system was a mistake." Delete that decomposition; emit N-team battles natively.

## Swarm Findings Summary

### Architecture
- Battle Setup is the largest surface. UI panels parameterize on "side 0" / "side 1" today.
- Strategy resolver (`SimulationBattleResolver`) is one function; the hardcoded team_modifiers indexing is 2 lines.
- Entry-vector resolution today is hardcoded (west→east, east→west). Must generalize to a ring of N equally-spaced points.
- `apply_outcome_to_fleets` post-battle hook iterates fleets today — verify it doesn't assume 2.

### Key Patterns to Reuse
- **N-team engine support**: already proven, don't re-invent. Use `start_teams` directly.
- **ModifierStack + FleetAuraManager**: already N-team internally. Fan-out from compiler to N teams just means emitting N entries.
- **Formation resolver** at `game/simulation/combat/formation.py` — extend with ring-based entry vectors.
- **PROJ-273 `emit_entries_for_ability`** — perfect hook for multi-opponent fan-out; takes `num_teams` kwarg.

### Dependencies & Risks
1. **Dependency: PROJ-273 must land first.** Enemy-scope fan-out needs the registry's `emit_entries_for_ability(num_teams=...)` signature.
2. **Dependency: PROJ-274 must land first.** Ship materialization must be team-agnostic; the InstanceBackedMaterializer must support any team_id without 2-team assumptions leaking through `ShipInstance.to_ship`.
3. **Risk: Battle Setup UI complexity.** Adding dynamic sides to a static 2-side layout may require panel refactoring not yet scoped. Phase 1 audit surfaces this before committing UI structure.
4. **Risk: `apply_outcome_to_fleets` post-battle hook.** Around `game/strategy/combat/post_battle_hook.py:120`, assumes 2 teams today. Phase 6 verifies N-team behavior.
5. **Risk: Save compat.** N-team battles produce outcomes that may not round-trip through saved games built on 2-team assumptions. Per user policy ("saves disposable") accepted.
6. **Risk: AI targeting.** `AIController._find_enemies_in_radius` already filters on `team_id != self.ship.get_team_id()` (per `docs/systems/combat_simulation.md`). No preference between teams — confirms everyone-hostile. Low risk.

### Opportunities Discovered
- UI can model sides as `List[BattleSetupSide]` cleanly; the "Side N" label is dynamic.
- `ConflictResolutionEngine` decomposition removal is a net LOC reduction.
- Sequential 2-fleet battle decomposition had subtle ordering bugs; removing it improves determinism.

## Design Decisions

See [decisions.md](decisions.md).

## Ring-Based Entry Vectors

For N teams around the origin:

```python
def resolve_team_entry_vectors(team_count: int, arena_radius: float = 2000.0) -> Dict[int, EntryVector]:
    """Equally-spaced points on a circle of radius `arena_radius`, facing inward.

    For 2 teams: (west, facing east) + (east, facing west). Preserves current behavior.
    For N teams: angle_step = 360 / N. Team i at angle = i * angle_step.
    """
    if team_count == 2:
        return {
            0: EntryVector(origin=(-arena_radius, 0), facing=0.0),
            1: EntryVector(origin=(+arena_radius, 0), facing=180.0),
        }
    vectors = {}
    for i in range(team_count):
        angle_rad = math.radians(i * (360 / team_count))
        origin = (arena_radius * math.cos(angle_rad), arena_radius * math.sin(angle_rad))
        facing = (math.degrees(angle_rad) + 180) % 360
        vectors[i] = EntryVector(origin=origin, facing=facing)
    return vectors
```

## `_route_team_for_scope` Signature Change

```python
# Before
def _route_team_for_scope(scope_str: str, owner_team: int) -> int:
    if scope_str in _OPPONENT_SCOPES:
        return (_NUM_TEAMS - 1) - owner_team  # 2-team only
    return owner_team

# After
def _route_team_for_scope(scope_str: str, owner_team: int, num_teams: int) -> List[int]:
    if scope_str in _OPPONENT_SCOPES:
        return [t for t in range(num_teams) if t != owner_team]
    return [owner_team]
```

Every caller site in `_complex_to_entries` iterates the returned list:

```python
for target_team in _route_team_for_scope(scope_str, owner_team, num_teams):
    entries.append(ModifierEntry(
        effect=...,
        applies_to_team_id=target_team,
        source=source,
        stack_group=stack_group,
    ))
```

## `BattleSetupState` Evolution

```python
# Before
@dataclass
class BattleSetupState:
    side_0: BattleSetupSide
    side_1: BattleSetupSide

# After
@dataclass
class BattleSetupState:
    sides: List[BattleSetupSide]  # min 2, max 8

    @property
    def side_0(self) -> BattleSetupSide:  # backcompat shim, delete after UI migration
        return self.sides[0]

    @property
    def side_1(self) -> BattleSetupSide:  # backcompat shim, delete after UI migration
        return self.sides[1]
```

Shims let Phase 5 land incrementally. Delete after UI migration in Phase 5.

## `SimulationBattleResolver` Evolution

```python
# Before
def resolve_battle(self, fleet1: Fleet, fleet2: Fleet, modifiers=None, ...):
    team_modifiers = modifiers.team_modifiers or {0: ..., 1: ...}
    # uses team_modifiers[0], team_modifiers[1]

# After
def resolve_battle(self, fleets: Sequence[Fleet], modifiers=None, ...):
    team_modifiers = modifiers.team_modifiers or {i: default for i in range(len(fleets))}
    for team_id, fleet_modifier in team_modifiers.items():
        # fan out to all teams
```

## `ConflictResolutionEngine` Evolution

```python
# Before (pseudocode): for each pair in combinations(empires, 2): resolve_battle(pair)
# After: fleets = [empire.fleets[sector] for empire in empires_at(sector)]
#        resolve_battle(fleets, ...)  # single N-team battle
```

Delete the combinations loop entirely.
