# Review Scope: PROJ-389 — score_planet_for_race wrapper migration

**Type:** code (delegated by Claude Code)
**Request ID:** req_20260509_022338_167258
**Review Mode:** quick verification (single commit, single phase, smallest Stage 3 project)

## Scope

Project directory: `Projects/active_projects/PROJ-389/`
Single commit: `f8a396655`

### Production migrations (6 callers + wrapper deletion)
- `game/strategy/engine/population_engine.py:139`
- `game/strategy/engine/happiness_engine.py:117`
- `game/strategy/facade/slices/economy_slice.py:157`
- `game/strategy/formulas/colony_output.py:47, 95, 152`
- `game/ui/screens/strategy_detail_fmt.py:129`
- `game/strategy/formulas/habitability.py` — wrapper deleted
- `game/strategy/formulas/__init__.py` — `score_planet_for_race` removed from public re-export

### Test migrations (4 files)
- `tests/unit/strategy/engine/test_happiness_engine.py`
- `tests/unit/strategy/formulas/test_colony_output.py`
- `tests/unit/strategy/engine/test_harvesting_engine_habitability.py`
- `tests/unit/ui/screens/test_strategy_detail_fmt.py`

### Doc migrations (3 files)
- `game/strategy/facade/dto/colony_demographic_view.py` (docstring)
- `docs/04_SERVICES.md` (2 refs)
- `docs/systems/strategy_layer.md` (1 ref)

## Instructions

1. Final grep verification — confirm zero remaining references to `score_planet_for_race`
2. Semantic equivalence of `calculate_habitability` migration at each of the 6 caller sites
3. Audit-vs-actual call-site delta — verify test/doc migrations were needed and correct
4. Re-export update — verify only `calculate_habitability` remains in `__init__.py`
5. Test-side coverage — spot-check 2 test files for dropped assertions or preserved intent
6. CLAUDE.md Rule 3 compliance — no replacement shim introduced

## Context

Eighth of 11 sequential PROJ runs. Stage 3 lead-off. The smallest of the Stage 3 projects (single phase, single commit, 16 files). The old wrapper `score_planet_for_race` was a 1-line delegate to `calculate_habitability`.

Reference:
- `Reviews/results/2026-05-07_220621_legacy-audit/`
- `Projects/active_projects/PROJ-389/findings/verification_report.md`
