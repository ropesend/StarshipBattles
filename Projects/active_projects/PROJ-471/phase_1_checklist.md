# Phase 1: Critical + class-shared-state (state-corruption gate)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-471 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Close the state-corruption finding before any tail cleanup: the MAJOR `ShipCombatEngine` class-level subsystems shared across all ship instances. (Task 1.1 `_default_provider` CRITICAL DROPPED as a verified false positive — see decisions.md.) Requires regression + determinism tests that exercise the shared-state path. **This phase is the exit gate.**

---

## Tasks

### Task 1.1: ~~Bind `_default_provider` through ApplicationContext~~ — DROPPED (verified false positive)
**Status:** DROPPED per scope revision 2026-05-20 (see decisions.md).

`DefaultRegistryProvider` (`game/core/registry.py:380-394`) re-calls
`get_default_registry_manager()` on every accessor; it never captures or caches a
`RegistryManager`. The `_default_provider` singleton (`registry.py:466-483`) caches only
the stateless provider wrapper. There is therefore no singleton-divergence bug. No code
change. (The genuinely-dual `_default_manager` at `registry.py:284-315` is a separate real
item handled by Phase 2 Task 2.3.)

### Task 1.2: Convert `ShipCombatEngine` shared subsystems to per-instance [Complex]
**File:** `game/simulation/entities/ship_combat_engine.py`, `game/simulation/systems/battle_setup.py`, `game/simulation/systems/battle_engine.py`
**Tests:** `pytest tests/ -k ship_combat_engine` (add the regression tests below); `pytest tests/unit/simulation/`; then `python -m combat_lab.run_tests`

- [x] Replace the class-level `_targeting_system` / `_damage_calculator` / `_weapon_firing_system` with **per-instance** subsystems. Introduced per-battle `CombatSubsystems` bundle (`game/simulation/combat/combat_subsystems.py`) owned by `BattleEngine` (seeded `DamageCalculator(rng=engine.rng)`, `TargetingSystem`, bus-wired `WeaponFiringSystem`); injected into each ship's `ShipCombatEngine` via constructor (`ShipCombatEngine.__init__(ship, subsystems=None)`). Standalone construction builds a fresh per-instance bundle. Class attributes removed entirely.
- [x] Routed the cross-module write at `battle_setup.py:48-49` into `engine.combat_subsystems` (built in `initialize_start_state` keyed to `engine.rng`), threaded into ships via `Ship.set_combat_subsystems` → `ShipCombatManager.set_combat_subsystems` before `set_event_bus` in `_initialize_ship`.
- [x] Updated the ram/mine resolver damage-calc lookups (`battle_engine.py`) to read `self.combat_subsystems.damage_calculator` (via `getattr` for `__new__`-constructed test engines), and removed the obsolete eager class-level firing-system/event-bus wiring in `__init__` (the bus is now wired into the bundle's `WeaponFiringSystem`).
- [x] **Regression test (class-shared-state):** `tests/unit/simulation/ship_combat_engine/test_subsystem_isolation.py` — two standalone engines have distinct subsystems; no class-level state; injected bundle is used; bundle-sharing within a battle preserved; seeded RNG identity preserved. Inverted the stale `test_multiple_engines_share_subsystems` (which pinned the bug) in `test_cooldowns.py`.
- [x] **Determinism characterization test:** `tests/unit/simulation/systems/test_battle_combat_subsystems.py` — per-battle bundle's `DamageCalculator.rng is engine.rng`; all ships share the bundle; same seed → identical RNG sequence; bundle rebuilt per `start` (no cross-battle leak).
- [x] Verify: pytest passes (3970 simulation unit + combat/replay integration green); combat_lab 168 passed, 2 failed (`TOHIT-ATK-FLEET-003/004` — confirmed PRE-EXISTING on clean tree, unrelated); no class-level mutable subsystem state remains; no new mutable parameter defaults introduced.

**Notes:** Determinism preserved by design — `random.X` draw sequence unchanged (same seeded RNG flows through the bundle's `DamageCalculator`). The class attributes were load-bearing shared-within-battle state; the bundle makes that sharing explicit + per-battle. Files: `combat_subsystems.py` (new), `ship_combat_engine.py`, `ship_combat_manager.py`, `ship.py`, `battle_engine.py`, `battle_setup.py`.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked (Task 1.1 DROPPED; Task 1.2 complete)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-20_082533_state-audit/`. See `findings/source_audit.md` for the link._
