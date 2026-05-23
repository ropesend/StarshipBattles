# Phase 2: Major Foundation narrowings

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-483 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Narrow ~5 MAJOR `-> Any` returns in simulation systems, core registry, and the component-stats calculator.

---

## Tasks

### Task 2.1: simulation attack_processor + fighter_reboard narrowings [Medium]
**Files:** `game/simulation/systems/attack_processor.py`, `fighter_reboard.py`
**Tests:** `pytest tests/ -k 'attack_processor or fighter_reboard'` then `mypy` on files

- [x] Narrow `_spawn_from_carried_vehicle` (`attack_processor.py:142`) to `-> Ship | None`. Confirms via return paths at L149/L158/L220
- [x] Narrow `_ensure_overflow_fighter_group` (`fighter_reboard.py:294`) to `-> FighterWing | SatelliteConstellation`
- [x] Narrow `_ensure_overflow_group` (`fighter_reboard.py:301`) to `-> FighterWing | SatelliteConstellation`
- [x] Verify: tests pass; `mypy` clean

### Task 2.2: core registry `get_validator` narrowing [Simple]
**File:** `game/core/registry.py`
**Tests:** `pytest tests/ -k 'core_registry or registry_manager'` then `mypy game/core/registry.py`

- [x] Narrow `RegistryManager.get_validator` (line 248) to `-> Optional[Callable[..., Any]]` (or a typed `ValidatorProtocol` if you choose to define one)
- [x] Narrow module-level `get_validator()` (line 339) to match
- [x] Verify: tests pass; `mypy` clean

### Task 2.3: component_stats_calculator.evaluate_recursive narrowing [Medium]
**File:** `game/simulation/components/component_stats_calculator.py`
**Tests:** `pytest tests/ -k component_stats_calculator` then `mypy` on file

- [x] Narrow `evaluate_recursive` (line 305) to `-> str | dict[str, Any] | list[Any] | float | int`. This is a nested function returning polymorphic values across formula evaluation branches
- [x] Verify: tests pass; `mypy` clean

### Task 2.4: Phase verification [Simple]
- [x] Verify: `python Tools/test_sharded/test_sharded.py` passes
- [x] Verify: `mypy` clean across all touched files

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-20_210540_type-audit/`. See `findings/source_audit.md` for the link._
