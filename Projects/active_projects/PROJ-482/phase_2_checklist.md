# Phase 2: Major Strategy narrowings

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-482 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Narrow ~13 MAJOR `-> Any` returns including the 8 `_get_*_mutator` cluster, `GameSession.handle_command`, three handler resolvers, two game_initializer generators, the strategic-ability walker generator, and the combat-lab fallback. Drives a coordinated tightening of the Strategy → Engine mutator surface.

---

## Tasks

### Task 2.1: GameSession.handle_command [Simple]
**File:** `game/strategy/engine/game_session.py`
**Tests:** `pytest tests/ -k game_session` then `mypy game/strategy/engine/game_session.py`

- [ ] Narrow `handle_command` (line 403) from `-> Any` to `-> ValidationResult` (TYPE_CHECKING import of `Command`). Docstring already states "Returns: ValidationResult"
- [ ] Verify: tests pass; `mypy` clean

### Task 2.2: harvesting_engine mutator helpers [Simple]
**File:** `game/strategy/engine/harvesting_engine.py`
**Tests:** `pytest tests/ -k harvesting` then `mypy` on file

- [ ] Narrow `_get_planet_mutator` (line 196) to `-> PlanetWriteService`
- [ ] Narrow `_get_empire_mutator` (line 205) to `-> EmpireWriteService`
- [ ] Verify: tests pass; `mypy` clean

### Task 2.3: order_handlers/base mutator helpers [Simple]
**File:** `game/strategy/engine/order_handlers/base.py`
**Tests:** `pytest tests/ -k order_handler` then `mypy` on file

- [ ] Narrow `_get_planet_mutator` (line 143) to `-> PlanetWriteService`
- [ ] Narrow `_get_ship_mutator` (line 152) to `-> ShipInstanceWriteService`
- [ ] Verify: tests pass; `mypy` clean

### Task 2.4: environmental_hazard_engine mutator helper [Simple]
**File:** `game/strategy/engine/environmental_hazard_engine.py`
**Tests:** `pytest tests/ -k environmental_hazard` then `mypy` on file

- [ ] Narrow `_get_ship_mutator` (line 65) to `-> IShipInstanceMutator`
- [ ] Verify: tests pass; `mypy` clean

### Task 2.5: planet_modifier_effect_engine mutator helper [Simple]
**File:** `game/strategy/engine/planet_modifier_effect_engine.py`
**Tests:** `pytest tests/ -k modifier_effect` then `mypy` on file

- [ ] Narrow `_get_planet_mutator` (line 34) to `-> IPlanetMutator`
- [ ] Verify: tests pass; `mypy` clean

### Task 2.6: production_spawner mutator helper [Simple]
**File:** `game/strategy/engine/production_spawner.py`
**Tests:** `pytest tests/ -k production_spawner` then `mypy` on file

- [ ] Narrow `_get_planet_mutator` (line 103) to `-> IPlanetMutator` (or `-> PlanetWriteService` — match concrete return)
- [ ] Verify: tests pass; `mypy` clean

### Task 2.7: superweapon_order_processor._get_empire_mutator [Simple]
**File:** `game/strategy/engine/superweapon_order_processor.py`
**Tests:** `pytest tests/ -k superweapon_order` then `mypy` on file

- [ ] Narrow `_get_empire_mutator` (line 77) to `-> IEmpireMutator`
- [ ] Verify: tests pass; `mypy` clean

### Task 2.8: handlers/base resolvers + colonize target [Medium]
**File:** `game/strategy/engine/handlers/base.py`
**Tests:** `pytest tests/ -k 'handlers and base'` then `mypy` on file

- [ ] Narrow `_resolve_build_entity` (line 323 / current ~336) to `-> Planet | Fleet | None`
- [ ] Narrow `_resolve_queue_owner` (line 377 / current ~390) to `-> Planet | Fleet | PlanetaryFacility | None`
- [ ] Narrow `_build_colonize_target` (line 419 / current ~432) to `-> Planet | dict[str, Any]`
- [ ] Verify: tests pass; `mypy` clean

### Task 2.9: game_initializer generator annotations [Simple]
**File:** `game/strategy/engine/game_initializer.py`
**Tests:** `pytest tests/ -k game_initializer` then `mypy` on file

- [ ] Add `-> Iterator[Fleet]` to `_at_hex` nested generator (line 157)
- [ ] Add `-> Iterator[Fleet]` to `_in_system` nested generator (line 163)
- [ ] Verify: tests pass; `mypy` clean

### Task 2.10: strategic abilities walker generator [Simple]
**File:** `game/strategy/services/ability_sources/fleet.py`
**Tests:** `pytest tests/ -k ability_sources` then `mypy` on file

- [ ] Add `-> Generator[tuple[str, dict[str, Any]], None, None]` to `_walk_strategic_abilities` (line 128) — generator yielding `(ability_name, ability_data)` tuples
- [ ] Verify: tests pass; `mypy` clean

### Task 2.11: app_bootstrap fallback closure [Simple]
**File:** `game/app_bootstrap.py`
**Tests:** `pytest tests/ -k 'app_bootstrap or combat_lab'` then `mypy` on file

- [ ] Add `-> Ship` to nested closure `_replay_combat_lab_fallback` (line 310)
- [ ] Verify: tests pass; `mypy` clean

### Task 2.12: radiation_shield_editor (cross-cuts with PROJ-481) — coordination check [Simple]
**File:** `game/ui/screens/radiation_shield_editor.py`

> Note: this finding (audit Shard 03) is filed under UI in PROJ-481 Task 3.12. No action here; just a coordination marker — if PROJ-481 picks it up, this task is a no-op.

- [ ] Verify PROJ-481 owns the `_button_handlers` annotation; remove this task if confirmed

### Task 2.13: Phase verification [Simple]
- [ ] Verify: `python Tools/test_sharded/test_sharded.py` passes
- [ ] Verify: `mypy` clean across all touched files

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-20_210540_type-audit/`. See `findings/source_audit.md` for the link._
