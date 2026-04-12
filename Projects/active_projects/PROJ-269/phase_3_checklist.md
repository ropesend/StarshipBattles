# Phase 3: Boundary + N-Team Engine Support

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-269 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** `BattleEngine` accepts `BoundaryRegion` and enforces it every tick with the configured `ExitPolicy` (DESTROY / RETREAT / BOUNCE / NONE). `BattleSpec.teams` is a tuple of N `TeamSpec`s — the engine internally generalizes from 2-team to N-team. AI targeting treats every non-self team as equally hostile. `TeamEliminatedCondition` becomes "only one team with non-derelict/destroyed ships remaining." Retreat = boundary exit with RETREAT policy; no separate retreat mechanic.

---

### Task 3.1: BattleEngine enforces `BoundaryRegion.contains` per tick [Medium]
**Files:**
- `game/simulation/systems/battle_engine.py`
- `game/simulation/battle_runner.py` (wire boundary from spec)

**Tests:** `pytest tests/unit/simulation/systems/test_battle_engine_boundary.py --testmon`

- [ ] Write failing tests:
  - Engine with a `RectBoundary(width=1000, height=1000, ExitPolicy.NONE)` — ship at (2000, 0) remains in battle (NONE policy = no action)
  - Engine with `UnboundedRegion` — ship far outside remains in battle
  - Per-tick check is O(1) per ship (call `boundary.contains(ship.position)` once per ship per tick)
- [ ] Implement: `BattleEngine` accepts `boundary: BoundaryRegion` at construction (default `UnboundedRegion()`)
- [ ] In `BattleEngine.update()`, after movement phase: for each alive ship, call `self.boundary.contains(ship.position)` — if False, dispatch to `_apply_exit_policy(ship, self.boundary.exit_policy)` (stubbed for Task 3.2)
- [ ] Wire: `run_battle` passes `spec.boundary` to `BattleEngine`
- [ ] Verify: tests pass

**Notes:**

---

### Task 3.2: Implement `ExitPolicy` application [Medium]
**Files:**
- `game/simulation/systems/battle_engine.py` (extend `_apply_exit_policy`)
- `game/simulation/combat/boundary.py` (add `closest_inside_point` for BOUNCE)
- `game/simulation/battle_outcome.py` (possibly extend `ShipStatus`)

**Tests:** `pytest tests/unit/simulation/systems/test_exit_policy.py --testmon`

- [ ] Write failing tests:
  - `ExitPolicy.DESTROY`: ship exiting boundary gets `is_alive=False`, final `ShipOutcome.status == DESTROYED`, recorded damage as if destroyed by boundary
  - `ExitPolicy.RETREAT`: ship gets removed from engine, `ShipOutcome.status == RETREATED`, no damage recorded, final pose = position at boundary crossing
  - `ExitPolicy.BOUNCE`: ship's position is set to `boundary.closest_inside_point(ship.position)` and velocity is reflected along the boundary normal (for RectBoundary: flip X or Y; for CircleBoundary: reflect along radial vector)
  - `ExitPolicy.NONE`: ship continues unchanged
- [ ] Implement:
  - `_apply_exit_policy(ship, ExitPolicy.DESTROY)` — mark ship destroyed via existing damage-application path
  - `_apply_exit_policy(ship, ExitPolicy.RETREAT)` — set `ship.retreated = True`, remove from engine's alive-ships list; engine tracks retreated ships separately
  - `_apply_exit_policy(ship, ExitPolicy.BOUNCE)` — update ship.position + reflect velocity
  - `_apply_exit_policy(ship, ExitPolicy.NONE)` — no-op
- [ ] Add `RETREATED` to `ShipStatus` enum if not already present (Phase 1)
- [ ] Extend `extract_outcome` to emit `status=RETREATED` for retreated ships
- [ ] Verify: all four policies tested and passing

**Notes:**

---

### Task 3.3: Generalize engine from fixed-2-teams to N-teams [Complex]
**File:** `game/simulation/systems/battle_engine.py`

**Tests:** `pytest tests/unit/simulation/systems/test_battle_engine_n_teams.py --testmon`

- [ ] Write failing tests:
  - `BattleEngine` accepts ships with `team_id` in range [0, N-1]
  - `engine.add_ship_mid_battle(ship, team_id=3)` works for team_id beyond the initial 2
  - `engine.get_ships_by_team(team_id)` returns the right ships
  - `engine.get_enemies_of(team_id)` returns every ship whose team_id != argument (no alliances)
  - End condition "only one team with alive ships remains" fires correctly with 3 teams
- [ ] Audit current engine for fixed-2-team assumptions:
  - `engine.teams` field shape (list-of-2 or dict?)
  - `engine.get_winner()` currently returns 0, 1, or -1 (draw)
  - AI controller targeting (per controller; see Task 3.4)
  - End conditions (`TeamEliminatedCondition`, `TeamIncapacitatedCondition`)
- [ ] Refactor:
  - `engine.teams: Dict[int, List[Ship]]` — keyed by team_id, not fixed slots
  - `engine.get_winner() -> Optional[int]` — None when >1 team alive; `team_id` when exactly one alive
  - Add `engine.get_enemies_of(team_id) -> List[Ship]` helper
- [ ] Update `run_battle` + `extract_outcome` to construct and report N-team structure
- [ ] Verify: existing 2-team battles still behave identically (regression gate)
- [ ] Verify: 3-team test runs to correct conclusion

**Notes:**

---

### Task 3.4: Generalize AI targeting — no team preference [Medium]
**File:** `game/ai/controllers/*` (find targeting call sites)

**Tests:** `pytest tests/unit/ai/test_ai_n_team_targeting.py --testmon`

- [ ] Write failing test:
  - Place 3 ships on 3 different teams, each equidistant from a 4th attacker
  - Run AI targeting
  - Attacker selects the closest of the three enemies (determinism via seed); any enemy is a valid choice
  - No team_id preference exists in targeting logic
- [ ] Audit current AI targeting for hardcoded "team 0 / team 1" assumptions
- [ ] Refactor `IsEnemy(self_ship, other_ship)` predicate to `other_ship.team_id != self_ship.team_id` — used uniformly across movement, spatial, targeting behaviors
- [ ] Verify: tests pass; existing 2-team AI tests still green

**Notes:** User confirmed: "Each Team only attacks the enemy players... with no preference for targets." No alliance system yet.

---

### Task 3.5: Generalize end conditions for N teams [Medium]
**Files:**
- `game/simulation/systems/battle_end_conditions.py`

**Tests:** `pytest tests/unit/simulation/systems/test_battle_end_conditions_n_team.py --testmon`

- [ ] Write failing tests:
  - `TeamEliminatedCondition` — in 3-team battle, fires when 2 teams have 0 alive ships
  - `TeamIncapacitatedCondition` — fires when 2 teams have 0 non-derelict ships
  - `AnyCondition` / `AllCondition` still compose correctly
- [ ] Refactor:
  - `TeamEliminatedCondition.is_met(engine)` — returns True when `len([t for t in engine.teams if any(s.is_alive for s in engine.teams[t])]) <= 1`
  - `TeamIncapacitatedCondition` — analogous
- [ ] Rename `TeamEliminatedCondition` → keep the name (backward-compatible); just generalize logic
- [ ] Verify: 2-team existing tests still green
- [ ] Verify: 3-team test scenarios resolve at the correct tick

**Notes:**

---

### Task 3.6: 3-team integration smoke test [Medium]
**File:** `tests/integration/simulation/test_three_team_battle.py` (new)

- [ ] Write integration test:
  - Build `BattleSpec` with 3 teams, each with 1 ship
  - Ships positioned equidistant
  - Run `run_battle(spec, ...)`
  - Assert `BattleOutcome.end_reason == TEAM_ELIMINATED`
  - Assert exactly one team has a surviving ship
  - Assert outcomes for all 3 ships are present
- [ ] Run: test fails before N-team generalization
- [ ] After Tasks 3.3–3.5: test passes

**Notes:**

---

### Task 3.7: Boundary integration smoke test [Medium]
**File:** `tests/integration/simulation/test_boundary_retreat.py` (new)

- [ ] Write integration test:
  - `BattleSpec` with `RectBoundary(width=500, height=500, ExitPolicy.RETREAT)`
  - One ship placed near the edge with velocity pointing outward
  - Run `run_battle`
  - Assert that ship's `ShipOutcome.status == RETREATED`
  - Assert the other team's ships all show `status != RETREATED`
- [ ] Run before/after implementation

**Notes:**

---

### Task 3.8: 2-team regression gate [Simple]
**File:** (reuse existing combat_lab fast suite)

- [ ] Run `python -m combat_lab.run_tests --fast` — all 162+ scenarios pass
- [ ] Run existing 2-team pytest suites — all green
- [ ] Confirm no scenario's pass rate changed >2% vs baseline

**Notes:** This is a regression gate, not new tests. If Combat Lab scenarios start failing, the N-team refactor broke something in the 2-team common path.

---

### Task 3.9: Documentation updates [Simple]
**File:** `docs/systems/combat_simulation.md`

- [ ] Add "Boundary" section describing `BoundaryRegion`, the four `ExitPolicy` values, and how retreat is a special case of RETREAT
- [ ] Update "Battle Orchestration" section to note N-team support (no longer limited to 2)
- [ ] Update the "End conditions" table: `TeamEliminatedCondition` description generalized to N teams
- [ ] Verify: doc renders; no stale "team 0 or team 1" language

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/ --testmon` fully green
- [ ] `python -m combat_lab.run_tests --fast` — 162+ passing (regression gate)
- [ ] Tasks 3.6 + 3.7 integration tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4 Task 4.1
