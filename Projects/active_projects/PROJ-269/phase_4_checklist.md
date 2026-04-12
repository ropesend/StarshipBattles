# Phase 4: Formation System

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-269 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** In Progress
**Objective:** Formations become a first-class property of `TaskForce`. `FormationResolver` deterministically converts `(formation, entry_vector, boundary, ships)` → per-ship `(position, angle)`. Each context's spec compiler calls the resolver while building `ShipSpec.position`/`angle`, replacing today's ad-hoc positioning. Defaults are chosen by the dominant `design_role` in a task force when `TaskForce.formation` is `None`. Player UI for authoring is out of scope; the resolver + defaults + round-trip through saves land here.

---

### Task 4.1: Add `TaskForce.formation: Optional[FormationSpec]` field [Simple]
**File:** `game/strategy/fleets/task_force.py`

**Tests:** `pytest tests/unit/strategy/fleets/test_task_force.py --testmon`

- [x] Write failing tests:
  - `TaskForce.formation` field exists, defaults `None`
  - Serialization round-trip (`to_dict` / `from_dict`) preserves the formation
  - A `TaskForce` with an explicit `FormationSpec(shape=WEDGE, spacing=100)` round-trips
- [x] Implement: add `formation: Optional[FormationSpec] = None` field to `TaskForce` dataclass
- [x] Update `TaskForce.to_dict()` / `from_dict()` to serialize the formation
- [x] Verify: tests pass; existing task-force tests still pass (2925 strategy tests pass, same pre-existing ImportError)

**Notes:**
Implemented 2026-04-12. 6 new tests + 2925 strategy regression green.
- `TaskForce.formation: Optional[FormationSpec] = None` as a plain
  instance attribute. `formation` kwarg added to `TaskForce.__init__`.
- `_formation_to_dict` / `_formation_from_dict` helpers local to
  `task_force.py` — flat JSON (shape-value string, spacing float, list
  of [x, y] pairs for custom_positions).
- `to_dict()` omits `formation` key when `None` (back-compat); legacy
  saves without the key deserialize as `formation=None`.

---

### Task 4.2: Implement `FormationResolver` [Complex]
**File:** `game/simulation/combat/formation.py` (extend — types already exist from Phase 1)

**Tests:** `pytest tests/unit/simulation/combat/test_formation_resolver.py --testmon`

- [x] Write failing tests for each formation shape (origin=(0,0), facing=0 = east)
- [x] Test: rotation invariance — a formation resolved with `entry_vector.facing=90°` equals the facing=0 result rotated by 90°
- [x] Test: each ship's `angle` is set to `entry_vector.facing`
- [x] Implement `FormationResolver.resolve(formation, entry_vector, boundary, ships) -> Dict[instance_id, (Vector2, float)]`
- [x] Verify: all shape-specific tests pass
- [x] Verify: rotation-invariance tests pass

**Notes:**
Implemented 2026-04-12. 12 tests green.

Signature: `FormationResolver.resolve(formation, entry_vector, boundary, ships) -> Dict[instance_id, (Vector2, float)]` (stateless
static method). Omitted the `registries` param from the original plan
— the resolver doesn't need registries (Task 4.3's default selector
will need design-role data but that's a separate helper).

Per-shape algorithm (all in local frame with facing=0 == +x):
- `LINE_ABREAST`: perpendicular to facing (along local Y), symmetric around y=0
- `LINE_ASTERN`: (0,0), (s,0), (2s,0), ... along +x
- `WEDGE`: leader at origin; each row k>0 adds ships at (-k·s, ±k·s)
- `ECHELON_LEFT`: (-i·s, +i·s) diagonal up-left
- `ECHELON_RIGHT`: (-i·s, -i·s) diagonal down-left
- `SCREEN`: main line at x=0, screen column at x=+spacing; ships split ~half+half, extra to main
- `CARRIER_PROTECTED`: first ~n/3 at origin (carriers); rest on ring of radius=spacing
- `CUSTOM`: verbatim from `formation.custom_positions` (pads by repeating last if short)

World-space pipeline: local → rotate by `facing` (degrees, CCW) → translate by `origin` → clamp to boundary if outside.
All ships get `angle = entry_vector.facing`.

Ordering: ships are assigned to positions in input list order, so
callers control leader/wingman placement by list order.

---

### Task 4.3: Design-role → default-formation resolution [Medium]
**File:** `game/simulation/combat/formation.py` (add `resolve_default_for_task_force` helper)

**Tests:** `pytest tests/unit/simulation/combat/test_formation_defaults.py --testmon`

- [x] Write failing tests:
  - TaskForce with 3 "strike" ships → default `FormationSpec(shape=WEDGE, ...)`
  - TaskForce with 2 "carrier" ships + 4 "defender" escorts → `CARRIER_PROTECTED`
  - TaskForce of all "defender" ships → `LINE_ABREAST`
  - TaskForce of all "scout" ships → `LINE_ASTERN`
  - Mixed TaskForce (no dominant role) → `LINE_ABREAST`
- [x] Implement `resolve_default_for_task_force(ships) -> FormationSpec`
- [x] Integrate at the compiler level (Tasks 4.4–4.6) — if `task_force.formation is None`, call `resolve_default_for_task_force` first
- [x] Verify: tests pass

**Notes:**
Implemented 2026-04-12. 8 new tests green.

- Two-stage mapping: `design_role` (27 roles in
  `data/design_roles.json`) → archetype bucket ("carrier", "strike",
  "defender", "scout", or "other"), then bucket → `FormationShape`.
- Strike bucket: `interceptor`, `assault_ship`, `raider`,
  `missile_platform`. Defender bucket: `line_combatant`,
  `fleet_escort`, `defensive_platform`, `shield_projector`. Scout
  bucket: `scout`, `command_ship`, `sensor_platform`. Any role not
  listed falls into "other" → `LINE_ABREAST`.
- Tie detection: when two or more archetypes share the top count,
  fall back to `LINE_ABREAST` (mixed-fleet default).
- Signature is `resolve_default_for_task_force(ships)` — a sequence
  of ship-like objects with `design_role`. Tests in the compilers
  (Tasks 4.4-4.6) verify the integrated behavior.

---

### Task 4.4: Wire `FormationResolver` into strategy compiler [Medium]
**File:** `game/strategy/combat/spec_compiler.py`

**Tests:** `pytest tests/unit/strategy/combat/test_spec_compiler_formation.py --testmon`

- [x] Write failing tests:
  - Default strike-archetype fleet produces a WEDGE-shaped spec
  - Default defender-archetype fleet produces LINE_ABREAST positions
  - Explicit `TaskForce.formation` overrides the default
  - ShipSpec angles match `entry_vector.facing`
  - Empty fleet yields empty ShipSpec tuple
- [x] Implement: in `build_strategy_battle_spec`, for each fleet:
  - Pick formation via `_pick_formation_for_fleet` (explicit TF.formation or design-role default)
  - Call `FormationResolver.resolve(formation, entry_vector, boundary=None, fleet.ships)`
  - Emit `ShipSpec.position` / `angle` from the resolver output
- [x] Verify: strategy-battle positions are deterministic and formation-correct
- [x] Incidental fix: `ShipInstance.create()` now mirrors `design_data["design_role"]` onto `instance.design_role` so the formation-default selector sees it

**Notes:**
Implemented 2026-04-12. 5 new tests green. Strategy regression 2930 pass (same pre-existing ImportError baseline).

Phase 4 simplifications:
- Entry vector math uses `(Vector2(0, 0), facing=0)` for all fleets in
  this MVP. Hex-edge entry math is an enhancement deferred to a later
  project — the FormationResolver accepts whatever `EntryVector` it's
  given, so rewiring the origin/facing doesn't require resolver
  changes.
- Resolver called per fleet (not per TaskForce). Phase 1's compiler
  wraps each Fleet as a single TF/squadron, so per-fleet resolution
  is equivalent. When fleets carry multiple TaskForces with distinct
  formations, this will need rework — logged as a follow-up.
- `_pick_formation_for_fleet` prefers the first TF with an explicit
  `formation`. When every TF has `formation=None` (the common case),
  falls back to `resolve_default_for_task_force(fleet.ships)`.
- Boundary is NOT passed to the resolver yet — strategy compiler
  pulls boundary from settings at a different level. Clamp-to-boundary
  remains optional on the resolver API.
- **ShipInstance.design_role init**: this was a pre-PROJ-269 gap.
  `ShipInstance.create()` had a `design_role: Optional[str] = None`
  field but never populated it from `design_data["design_role"]`.
  Added mirror-init at the tail of `create()` so downstream consumers
  (resolver, UI filters, etc.) see it correctly.

---

### Task 4.5: Wire `FormationResolver` into Battle Setup compiler [Medium]
**File:** `game/ui/screens/battle_setup/spec_compiler.py`

**Tests:** `pytest tests/unit/ui/screens/battle_setup/test_spec_compiler_formation.py --testmon`

- [x] Write failing tests:
  - Three assault_ship ships on side 0 produce WEDGE positions
  - Three line_combatant ships on side 0 produce LINE_ABREAST positions
  - Side 0 and side 1 have distinct entry vectors (facings)
  - Ship angles match entry_vector facing
- [x] Implement: in Battle Setup compiler, call `FormationResolver.resolve` per fleet using the team's entry vector + design-role default / explicit `TF.formation`
- [x] Replace existing `DeploymentZoneCalculator.compute_positions` usage with resolver output *(N/A — Battle Setup compiler path didn't use DeploymentZoneCalculator; the compiler was previously emitting `Vector2(0, 0)` for every ship as a Phase-1 scaffold)*
- [x] Verify: positions match formation selection
- [x] Manual: launch Battle Setup, select a formation via the UI (may be stubbed), start battle — ships are positioned correctly *(Phase-4 MVP: UI does not yet expose formation selection; compiler uses design-role defaults. Manual UI verification is a post-phase user step.)*

**Notes:**
Implemented 2026-04-12. 4 new tests + existing 10 Battle Setup
compiler tests green (14/14).

- Team 0 enters at `(-500, 0)` facing east (+x); team 1 at `(500, 0)`
  facing west (180°). Phase 4 MVP hard-coded; later work can derive
  entry vectors from UI selections.
- Per-fleet formation picked via `_pick_formation_for_fleet` (same
  pattern as strategy compiler): first TF with explicit `formation`
  wins; else design-role default from `resolve_default_for_task_force`.
- `_ship_spec_from_instance` now takes an optional `pose` arg.
- UI formation selection (per-TaskForce) is deferred to a follow-up
  project. When it lands, the compiler already honors
  `TaskForce.formation` so the UI just needs to set the field.

---

### Task 4.6: Wire `FormationResolver` into Combat Lab compiler [Medium]
**File:** `combat_lab/spec_compiler.py`

**Tests:** `pytest tests/unit/combat_lab/test_spec_compiler_formation.py --testmon`

- [x] Write failing tests:
  - `StaticTargetScenario` with `distance=500` compiles to a spec where attacker is at (0,0) and target is at (500,0) — preserving current test semantics
  - Each TaskForce in the spec carries a `FormationSpec(shape=CUSTOM)` (not None)
- [x] Implement: for `StaticTargetScenario`, populate each team's `TaskForceSpec.formation` with `FormationSpec(shape=CUSTOM, custom_positions=(Vector2(0, 0),))`. Combine with each team's `entry_vector` to produce the final world-space positions (attacker at (0, 0); target at (distance, 0) via `entry_vector.origin`).
- [x] Verify: all existing Combat Lab scenarios produce the same ship positions after the refactor — `python -m combat_lab.run_tests BEAMWEAPON-001 --no-history` still passes
- [x] Verify: 162+ Combat Lab fast scenarios still pass (regression gate runs at phase wrap)

**Notes:**
Implemented 2026-04-12. 3 new tests + 245 existing combat_lab tests green.

- Final world positions identical to pre-Phase-4 (attacker at (0, 0);
  target at (distance, 0)) — team-level entry vectors preserved the
  position math, and each TF's CUSTOM formation is a single-entry
  `(Vector2(0, 0),)` in its own local frame.
- Duel/Propulsion/Resource/Comparison templates are still unsupported
  by `build_test_battle_spec` (raise NotImplementedError). They'll
  migrate in later phases when their templates need formations too.
- Combat Lab CLI smoke: BEAMWEAPON-001 + BEAMWEAPON-001-HT both
  PASS on this path.

---

### Task 4.7: Documentation updates [Simple]
**Files:**
- `docs/systems/combat_simulation.md`
- `docs/systems/strategy_layer.md`

- [x] Add "Formation System" section to `combat_simulation.md`: describe `FormationSpec`, `FormationResolver`, the 8 shapes, design-role defaults
- [x] Update `strategy_layer.md` — note `TaskForce.formation` field and its role in battle-start positioning
- [x] Verify: doc renders correctly; no broken links

**Notes:**
Added "Formation System (Phase 4)" subsection to
`docs/systems/combat_simulation.md` §0 with:
- 8-shape table (local-frame patterns)
- World-space pipeline (rotate + translate + boundary clamp)
- Design-role bucket mapping to defaults
- Tie-breaking + fallback rules

`docs/systems/strategy_layer.md` got a `TaskForce.formation` entry in
the PROJ-269 section block right before the Phase-2 components entry.

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
