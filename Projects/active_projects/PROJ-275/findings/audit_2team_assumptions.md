# PROJ-275 Phase 1 — Audit of 2-Team Assumptions

## Summary

| Category | Sites | Severity | Phase addressing |
|----------|-------|----------|------------------|
| `_NUM_TEAMS = 2` hardcode + usage | 7 (battle_setup/spec_compiler.py) | **Load-bearing** | Phase 3 + 4 |
| `team_modifiers[0]/[1]` indexing | 2 (simulation_adapter.py:187,189) | Load-bearing | Phase 7 |
| `side_0`/`side_1` state fields | 7 (battle_setup_state.py) | Load-bearing | Phase 5 |
| `side_0`/`side_1` UI reads | ~10 (battle_setup_screen.py) | Load-bearing | Phase 5 |
| `side_0`/`side_1` compiler reads | 3 (battle_setup/spec_compiler.py) | Load-bearing | Phase 4 |
| `fleet1/fleet2` `SimulationBattleResolver.resolve_battle` | ~10 (simulation_adapter.py) | **Load-bearing** | Phase 7 |
| `fleet1/fleet2` `IBattleResolver` interface | 5 (battle_resolver.py) | Load-bearing | Phase 7 |
| Sequential 2-fleet decomposition in conflict resolver | 1 function (`_resolve_combat_at_hex`) | **Critical (user explicitly called this a mistake)** | Phase 7 |

## Load-Bearing Findings

### 1. `game/ui/screens/battle_setup/spec_compiler.py`
```
L83:  _NUM_TEAMS = 2  # module-level constant
L362: num_teams=_NUM_TEAMS (passed to emit_entries_for_ability)
L432: "Battle Setup is 2-sided (`_NUM_TEAMS == 2`)" (docstring)
L433: "(_NUM_TEAMS - 1) - owner is the single opponent"  (docstring)
L440: ""
L442: if owner_team < 0 or owner_team >= _NUM_TEAMS: raise NotImplementedError(...)
L445: f"(_NUM_TEAMS={_NUM_TEAMS})"
L451: return (_NUM_TEAMS - 1) - owner_team
```
**Lift strategy (Phase 3 + 4):** delete `_NUM_TEAMS` constant. Compute `num_teams = len(state.sides)` inside `build_manual_battle_spec`. Widen `_route_team_for_scope` signature to take `num_teams` and return `List[int]` (see Phase 3).

### 2. `game/strategy/adapters/simulation_adapter.py`
```
L63-75:   def resolve_battle(self, fleet1: 'Fleet', fleet2: 'Fleet', ...)
L94:      f"Fleet {fleet1.id} vs Fleet {fleet2.id}"
L96-97:   team0_combat from fleet1 / team1_combat from fleet2
L123:     self._build_spec(fleet1, fleet2, ...)
L143-44:  team0_survivors from fleet1 / team1_survivors from fleet2
L174-192: _build_spec(self, fleet1, fleet2, ...): [fleet1, fleet2] list-built
L187-189: team_modifiers[0] = team0_modifiers; team_modifiers[1] = team1_modifiers
```
**Lift strategy (Phase 7):** widen `resolve_battle(fleets: Sequence[Fleet], ...)`; build `team_modifiers: Dict[int, Any]` by iterating; ship the per-team survivor lists the same way.

### 3. `game/strategy/interfaces/battle_resolver.py`
```
L58-82:  docstring + signature for IBattleResolver.resolve_battle
         — still 2-fleet
```
**Lift strategy (Phase 7):** update the protocol signature + docstring; the protocol is small (one method).

### 4. `game/strategy/engine/conflict_resolution_engine.py`
```
L215-256: _resolve_combat_at_hex — this is THE SEQUENTIAL 2-FLEET LOOP
         the user flagged as "a mistake":

         while len(fleets_by_emp) > 1:
             id1, id2 = self._rng.sample(emp_ids, 2)
             survivor = self._resolve_combat(f1, f2)  # single pair
             # remove loser, loop

L258-277: _resolve_combat(f1, f2) — single-pair dispatcher
L279-361: _resolve_combat_simulated(f1, f2, ...) — pair → battle_resolver
```
**Lift strategy (Phase 7):** replace with single N-team battle:
- collect all fleets at hex → `fleets: List[Fleet]`
- one call: `self._battle_resolver.resolve_battle(fleets, seed=..., registries=..., ...)`
- process N-team outcome (mark all losing fleets as destroyed)

### 5. `game/ui/screens/battle_setup_state.py`
```
L130-131: __init__: self.side_0 = BattleSetupSide(team_id=0); self.side_1 = ...
L135:     get_side(team_id): side_0 if team_id == 0 else side_1
L166-167: reset(): same pattern
L172-173: to_dict: "side_0": ..., "side_1": ...
L184-187: from_dict: same
```
**Lift strategy (Phase 5):** migrate to `sides: List[BattleSetupSide]`. Keep `side_0` / `side_1` as backcompat @property wrappers during the transition; delete after Phase 5.4.

### 6. `game/ui/screens/battle_setup_screen.py`
```
L151-152: create_fleet on side_0 / side_1 at screen init
L1044:    if _total_ships(self.state.side_0) == 0 or _total_ships(self.state.side_1) == 0
L1112-15: _collect(0,"system"), _collect(0,"sector"), _collect(1,"system"), _collect(1,"sector")
```
**Lift strategy (Phase 5):** iterate `state.sides` by index.

### 7. `game/ui/screens/battle_setup/spec_compiler.py`
```
L117: team0 = _build_team_spec(ui_state.side_0, team_id=0, name="Side 0")
L118: team1 = _build_team_spec(ui_state.side_1, team_id=1, name="Side 1")
L272: for team_id, side in ((0, ui_state.side_0), (1, ui_state.side_1)):
```
**Lift strategy (Phase 4):** replace with `for team_id, side in enumerate(ui_state.sides):`.

## Cosmetic / Low-Severity Findings

- `tests/unit/ui/screens/battle_setup/test_spec_compiler.py:357` comment `# today (_NUM_TEAMS = 2); expansion is a deliberate future project` — update post-Phase 4.
- `simulation_adapter.py:L94` log string "Fleet X vs Fleet Y" — cosmetic log only.

## `apply_outcome_to_fleets` Post-Battle Hook Check

Per Phase 1 audit plan: verify the hook iterates teams rather than indexing 0/1. Deferred verification to Phase 6.4 when strategy compiler N-fleet work lands.

## Battle Setup UI Complexity Estimate (Phase 5)

Panels live directly in `game/ui/screens/battle_setup/` (only `spec_compiler.py` + `__init__.py` there; the screen is `game/ui/screens/battle_setup_screen.py`). State is all threaded through `BattleSetupState.side_0 / side_1`. Screen code reads these in ~10 places, mostly iterating both. Converting the screen to iterate `state.sides` by index is mechanical but touches many call sites.

**Proposed UI cap:** 2-8 sides (as decided). Rendering can stay as horizontally-stacked columns in the current layout for 2-4 sides; for 5+ sides a simpler list view.

## Phase-Order Confirmation

Based on dependency graph:
1. Phase 2 (ring entry vectors — pure function) — unblocks 3+
2. Phase 3 (`_route_team_for_scope` → List[int]) — unblocks 4
3. Phase 4 (Battle Setup compiler N-teams) — needs Phase 2+3
4. Phase 5 (Battle Setup state + UI) — needs Phase 4
5. Phase 6 (Strategy compiler N-fleets)
6. Phase 7 (Strategy adapter + conflict resolution) — needs Phase 6
7. Phase 8 (integration tests)
8. Phase 9 (docs)

Phase 5 and Phase 6 can be swapped; Phase 7 needs Phase 6.

## No User-Sign-Off Surprises

No surprises during audit. Everything matches the plan's expected blast radius. The sequential 2-fleet loop is clearly isolated (one function, one while loop). Battle Setup UI is the largest surface but mechanical. Proceeding to Phase 2.
