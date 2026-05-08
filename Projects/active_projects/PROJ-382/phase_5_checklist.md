# Phase 5: LOC ceiling sweep — 5 oversized files not covered by an active PROJ

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-382 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Bring 5 production files under the 500-LOC ceiling that are currently uncovered by any active PROJ. Files already in active decomposition projects (race_summary_panel.py, battle_screen.py, ship_detail_panel.py, production_engine.py, workshop_event_router.py, build_queue_panel_factory.py, battle_panels.py, registry.py, spec_compiler.py) are explicitly out of scope here.

> Each task in this phase is a structural decomposition. Do not attempt them in parallel — each requires reading the file end-to-end first and choosing extraction boundaries before any edit. Phases 1-4 take precedence.

---

## Tasks

### Task 5.1: Decompose `planetary.py` (913 LOC, +413)
**File:** `game/simulation/components/abilities/planetary.py`
**Pattern:** n/a (LOC ceiling — `docs/03_CONVENTIONS.md` §File Size)
**Tests:** `pytest tests/ -k planetary --testmon`

- [ ] Read the file end-to-end. Confirm the 16 ability classes are independently coherent (audit's recommendation).
- [ ] Split into sub-modules under `game/simulation/components/abilities/planetary/`: e.g. `shield.py` (PlanetaryShield, RadiationShield), `stabilizer.py` (GeologicStabilizer, StellarStabilizer, WarpFieldStabilizer), `modifier.py` (ShieldModifier, DamageModifier, ThrustModifier, etc.), `terraforming.py` (AtmosphereModifier, GravityModifier, WaterModifier, QualityImprovement).
- [ ] Re-export the public surface from the new package `__init__.py` so existing import paths still work.
- [ ] Verify: every ability still resolves through the abilities registry; tests for the affected ability classes still pass.

### Task 5.2: Decompose `battle_engine.py` (775 LOC, +275)
**File:** `game/simulation/systems/battle_engine.py`
**Pattern:** n/a (LOC ceiling)
**Tests:** `pytest tests/ -k battle_engine --testmon`

- [ ] Read end-to-end. Identify extraction candidates: `BattleLogger` (~252 LOC), `_bounce_ship` boundary policy logic (~80 LOC).
- [ ] Extract `BattleLogger` to a sibling `battle_logger.py`.
- [ ] Extract boundary enforcement (`enforce_boundary`, `_apply_exit_policy`, `_bounce_ship`) to `boundary_enforcement.py`.
- [ ] Verify: `BattleEngine` still wires both delegates; combat regression tests pass.

### Task 5.3: Decompose `fleet_navigation_service.py` (773 LOC, +273)
**File:** `game/strategy/services/fleet_navigation_service.py`
**Pattern:** n/a (LOC ceiling)
**Tests:** `pytest tests/ -k fleet_navigation --testmon`

- [ ] Read end-to-end. Identify the natural split — likely projection vs scheduling vs reentrancy guards.
- [ ] Extract responsibility-coherent helpers into sibling modules. Note: `threading.local()` reentrancy guard at lines 121-129 is a candidate to retain in the original service or move to a small dedicated helper.
- [ ] Verify: fleet navigation tests pass; no behavioral change.

### Task 5.4: Decompose `superweapon_order_processor.py` (723 LOC, +223) — DEFERRED

**Status:** Deferred during implementation (PROJ-382 Phase 5, 2026-05-08).

**Reason:** The 5 `process_*` superweapon dispatchers carry per-effect
closures (`_precheck` + `_effect`) closing over `self._get_empire_mutator()`,
`self._event_bus`, `self._registries`.  Extracting them as free functions
either threads the engine reference through every closure or requires a
state-bag type — neither has a clean single-responsibility payoff.  The
audit's "register effect closures on SuperweaponSpec" path is a separate
registry-restructuring project.  See
`findings/verification_report.md` "Deferred During Implementation".

**File:** `game/strategy/engine/superweapon_order_processor.py`
**Pattern:** n/a (LOC ceiling)
**Tests:** `pytest tests/ -k superweapon --testmon`

- [ ] Read end-to-end. Likely extraction by superweapon kind (planet imploder, stellerator, warp-point ops, dyson sphere, self-destruct) — match the rows of the `SUPERWEAPONS` registry.
- [ ] Split into a `superweapon_order_processor/` package with one effect closure per kind, registered on the `SuperweaponSpec` row.
- [ ] Verify: every superweapon order processes correctly end-to-end.

### Task 5.5: Decompose `conflict_resolution_engine.py` (567 LOC, +67)
**File:** `game/strategy/engine/conflict_resolution_engine.py`
**Pattern:** n/a (LOC ceiling)
**Tests:** `pytest tests/ -k "conflict or end_turn" --testmon`

- [ ] Read end-to-end. The +67 LOC overage is small — a focused single-responsibility extraction (likely RNG management or per-hex resolution helpers) should suffice.
- [ ] Extract one cohesive helper module; do not over-decompose.
- [ ] Verify: end-turn conflict resolution tests pass; N-team battles (PROJ-275 territory) still resolve cleanly.

### Task 5.6: Phase verification
**File:** N/A
**Pattern:** LOC ceiling
**Tests:** Full suite

- [ ] `pytest tests/ --testmon` passes.
- [ ] `python Tools/test_sharded/test_sharded.py` baseline holds.
- [ ] Each of the five files now < 500 LOC. Confirm by re-running `Tools/check_file_size.py` (the audit notes this tool had a path bug — verify the tool works first or count manually).
- [ ] No new file in the new packages exceeds 500 LOC.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-07_220452_pattern-audit/`. See `findings/source_audit.md` for the link._
