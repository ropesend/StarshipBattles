# Phase 4: Formation System

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-269 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Formations become a first-class property of `TaskForce`. `FormationResolver` deterministically converts `(formation, entry_vector, boundary, ships)` → per-ship `(position, angle)`. Each context's spec compiler calls the resolver while building `ShipSpec.position`/`angle`, replacing today's ad-hoc positioning. Defaults are chosen by the dominant `design_role` in a task force when `TaskForce.formation` is `None`. Player UI for authoring is out of scope; the resolver + defaults + round-trip through saves land here.

---

### Task 4.1: Add `TaskForce.formation: Optional[FormationSpec]` field [Simple]
**File:** `game/strategy/fleets/task_force.py`

**Tests:** `pytest tests/unit/strategy/fleets/test_task_force.py --testmon`

- [ ] Write failing tests:
  - `TaskForce.formation` field exists, defaults `None`
  - Serialization round-trip (`to_dict` / `from_dict`) preserves the formation
  - A `TaskForce` with an explicit `FormationSpec(shape=WEDGE, spacing=100)` round-trips
- [ ] Implement: add `formation: Optional[FormationSpec] = None` field to `TaskForce` dataclass
- [ ] Update `TaskForce.to_dict()` / `from_dict()` to serialize the formation
- [ ] Verify: tests pass; existing task-force tests still pass

**Notes:**

---

### Task 4.2: Implement `FormationResolver` [Complex]
**File:** `game/simulation/combat/formation.py` (extend — types already exist from Phase 1)

**Tests:** `pytest tests/unit/simulation/combat/test_formation_resolver.py --testmon`

- [ ] Write failing tests for each formation shape (origin=(0,0), facing=0 = east):
  - `LINE_ABREAST`: N ships, all at x=0, y spread symmetrically around 0 with `spacing` between adjacent
  - `LINE_ASTERN`: N ships along +x axis, first at (0, 0), each subsequent at +spacing on x
  - `WEDGE`: 1 leader at (0,0), 2 wingmen at (-spacing, ±spacing), 2 outer at (-2*spacing, ±2*spacing), etc. — arrowhead pointing in +x
  - `ECHELON_LEFT`: N ships on a diagonal, each offset (-spacing, +spacing) from previous
  - `ECHELON_RIGHT`: analogous with (-spacing, -spacing)
  - `SCREEN`: large-hull ships at x=0 column, smaller/scout ships ahead at +x column (determined by mass or design_role)
  - `CARRIER_PROTECTED`: carriers at (0,0); escorts in a ring around carriers
  - `CUSTOM`: uses `formation.custom_positions` verbatim
- [ ] Test: rotation invariance — a formation resolved with `entry_vector.facing=math.pi/2` equals the facing=0 result rotated by 90°
- [ ] Test: each ship's `angle` is set to `entry_vector.facing` (ships face the direction they entered from)
- [ ] Implement `FormationResolver.resolve(formation, entry_vector, boundary, ships, registries) -> Dict[instance_id, (Vector2, float)]`:
  - For each shape: compute local (facing=0) positions, then rotate by `entry_vector.facing`, then translate by `entry_vector.origin`
  - Assertion: no ship is placed outside the `boundary` (warn and clamp to `boundary.closest_inside_point(pos)` if needed)
- [ ] Verify: all shape-specific tests pass
- [ ] Verify: rotation-invariance tests pass

**Notes:** Keep the resolver stateless + deterministic. No AI, no ship-property-dependent magic except `design_role` → shape-default (handled in Task 4.3, not here).

---

### Task 4.3: Design-role → default-formation resolution [Medium]
**File:** `game/simulation/combat/formation.py` (add `resolve_default_for_task_force` helper)

**Tests:** `pytest tests/unit/simulation/combat/test_formation_defaults.py --testmon`

- [ ] Write failing tests:
  - TaskForce with 3 "strike" ships → default `FormationSpec(shape=WEDGE, ...)`
  - TaskForce with 2 "carrier" ships + 4 "defender" escorts → `CARRIER_PROTECTED`
  - TaskForce of all "defender" ships → `LINE_ABREAST`
  - TaskForce of all "scout" ships → `LINE_ASTERN`
  - Mixed TaskForce (no dominant role) → `LINE_ABREAST`
- [ ] Implement `resolve_default_for_task_force(task_force, registries) -> FormationSpec`:
  - Compute mode of `ship.design.design_role` across task_force.ships
  - Map mode → default shape (per [design.md §2.7](design.md))
  - Return `FormationSpec(shape=default, spacing=DEFAULT_SPACING, custom_positions=())`
- [ ] Integrate: `FormationResolver.resolve` — if the passed formation is `None` or `task_force.formation is None`, call `resolve_default_for_task_force` first
- [ ] Verify: tests pass

**Notes:**

---

### Task 4.4: Wire `FormationResolver` into strategy compiler [Medium]
**File:** `game/strategy/combat/spec_compiler.py`

**Tests:** `pytest tests/unit/strategy/combat/test_spec_compiler_formation.py --testmon`

- [ ] Write failing test:
  - Fleet with one TaskForce of 5 strike ships, hex edge = NORTH
  - Compile spec with entry_vector derived from hex edge (point at south edge of hex, facing north)
  - Verify ship positions form a WEDGE pattern facing north
- [ ] Implement: in `build_strategy_battle_spec`, for each TaskForce:
  - Derive `entry_vector` from the hex edge of entry (hex-edge centerpoint, facing into the hex)
  - Call `FormationResolver.resolve(tf.formation, entry_vector, spec.boundary, tf.ships, registries)`
  - Emit `ShipSpec.position` / `angle` from the resolver output
- [ ] Verify: strategy-battle positions are deterministic and formation-correct

**Notes:** Hex-edge math: given a hex with center `(cx, cy)` and an edge vector (one of 6 unit vectors), the entry vector for a fleet entering through that edge is `origin = (cx + edge_vector * hex_radius)` and `facing = -edge_vector.angle()` (pointing into the hex).

---

### Task 4.5: Wire `FormationResolver` into Battle Setup compiler [Medium]
**File:** `game/ui/screens/battle_setup/spec_compiler.py`

**Tests:** `pytest tests/unit/ui/screens/battle_setup/test_spec_compiler_formation.py --testmon`

- [ ] Write failing test:
  - BattleSetupState with 1 task force of 3 ships per side, each side chooses a formation via UI toggle
  - Compile spec
  - Verify positions match the chosen formation, with team 0 entering from "west" and team 1 from "east"
- [ ] Implement: extract formation from `BattleSetupState` (may require UI to set `task_force.formation`); call `FormationResolver.resolve` per task force
- [ ] Replace existing `DeploymentZoneCalculator.compute_positions` usage with resolver output
- [ ] Verify: positions match formation selection
- [ ] Manual: launch Battle Setup, select a formation via the UI (may be stubbed), start battle — ships are positioned correctly

**Notes:** If UI doesn't yet expose formation selection, Phase 4 can default to `None` (design-role default) and user will configure via UI in a future project.

---

### Task 4.6: Wire `FormationResolver` into Combat Lab compiler [Medium]
**File:** `combat_lab/spec_compiler.py`

**Tests:** `pytest tests/unit/combat_lab/test_spec_compiler_formation.py --testmon`

- [ ] Write failing test:
  - `StaticTargetScenario` with `distance=500` compiles to a spec where attacker is at (0,0) and target is at (500,0) — preserving current test semantics
- [ ] Implement: for template scenarios, construct `FormationSpec(shape=CUSTOM, custom_positions=(...))` from the scenario's existing explicit positions (e.g., `StaticTargetScenario.distance`, `DuelScenario.distance`, etc.)
- [ ] Verify: all existing Combat Lab scenarios produce the same ship positions after the refactor — regression by running `python -m combat_lab.run_tests --fast` and checking pass rate
- [ ] Verify: 162+ Combat Lab fast scenarios still pass

**Notes:**

---

### Task 4.7: Documentation updates [Simple]
**Files:**
- `docs/systems/combat_simulation.md`
- `docs/systems/strategy_layer.md`

- [ ] Add "Formation System" section to `combat_simulation.md`: describe `FormationSpec`, `FormationResolver`, the 8 shapes, design-role defaults
- [ ] Update `strategy_layer.md` — note `TaskForce.formation` field and its role in battle-start positioning
- [ ] Verify: doc renders correctly; no broken links

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/ --testmon` fully green
- [ ] `python -m combat_lab.run_tests --fast` — 162+ passing (regression gate)
- [ ] Each formation shape has at least one test with asserted positions
- [ ] Rotation-invariance test passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5 Task 5.1
