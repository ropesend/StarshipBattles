# PROJ-351 File Manifest

## Files

| File | Type | Notes |
|------|------|-------|
| `game/strategy/engine/action_execution_engine.py` | Production (refactor) | T6.3 — execution path consults `self._action_time_resolver` if non-None instead of always-static. Lines 55-68 (DI declaration unchanged), 165-168 (consumer). |
| `tests/unit/strategy/engine/test_action_execution_engine_gaps.py` | Test (rewrite) | T6.3 — flip the test at lines 128-156 from "asserts injected instance is never consulted" to "asserts injected instance IS consulted". Possibly add a regression test for the no-injection (default) path. |
| `game/ui/screens/planet_abilities_controller.py` | Production (refactor) | T6.4 — replace hardcoded ability-name lists at lines 29-48 with registry/data scan per `docs/03_CONVENTIONS.md:500-512`. |
| `tests/unit/ui/screens/test_planet_abilities_controller*.py` (locate via grep) | Test (update) | T6.4 — update or replace tests pinning the hardcoded lists. |
| `Projects/active_projects/PROJ-351/plan.md` | Project artifact | Updates per phase |
| `Projects/projects_index.md` | Project index | Status update at end of Phase 2 |

## Verification commands

| Phase | Command |
|-------|---------|
| 1 (T6.3) | `pytest tests/unit/strategy/engine/test_action_execution_engine* -x -q` |
| 2 (T6.4) | `pytest tests/unit/ui/screens/test_planet_abilities_controller* -x -q` |
| Final | `pytest tests/unit/ -q` then `python Tools/lint_test_files.py` |
