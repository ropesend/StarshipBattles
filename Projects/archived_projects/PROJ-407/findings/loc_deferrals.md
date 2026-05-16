# PROJ-407 D-09: LOC-ceiling audit (read-only)

> Project convention (CLAUDE.md / docs/03_CONVENTIONS.md): production
> files under `game/` should stay under 500 LOC. Split by responsibility
> when a touched file approaches that ceiling.

This audit covers production files that PROJ-380 touched (per
`git log --grep="PROJ-380" --name-only -- 'game/*.py'`). Line counts
are raw `wc -l` taken on `feat/03c-phase-aware-execution` at the
PROJ-407 D-08 commit.

**D-09 is read-only.** Splitting these files is real refactor work
(extracting cohesive responsibilities, threading new constructor
arguments, updating callers and tests). It is out of scope for this
Tier 3 doc + typing sweep and is deferred to dedicated future
projects.

## Files over 500 LOC

| LOC | File | Notes |
|----:|------|-------|
| 831 | `game/simulation/battle_controller.py` | Battle lifecycle controller; touched by PROJ-380 DUP-X-* consolidations. Decomposition would extract phase-runner / outcome-builder responsibilities. |
| 830 | `game/simulation/battle_state.py` | Combined ship/projectile/state container. Strong candidate for splitting alongside `battle_engine.py` in a coordinated refactor. |
| 734 | `game/simulation/battle_runner.py` | Top-level runner orchestration; sits between `BattleSpec` and `BattleController`. |
| 633 | `game/ui/screens/strategy_click_dispatcher.py` | Click-mode dispatch ladder; PROJ-380 phase 3.7 already extracted `_cancel_input_mode` and the related mode handlers, but the dispatcher itself remains over the ceiling. |
| 532 | `game/simulation/systems/battle_end_conditions.py` | End-condition implementations; could split per condition family. |
| 530 | `game/strategy/adapters/simulation_adapter.py` | Strategy↔simulation adapter; PROJ-380 added superweapon-spec wiring here. |
| 520 | `game/simulation/systems/battle_engine.py` | Tick engine; coupled to `battle_state.py`. |

## Recommendation

Open a dedicated future project that batches a coordinated
`battle_controller / battle_runner / battle_state / battle_engine`
decomposition (the four largest, all in `game/simulation/`, all
heavily inter-coupled). Treat the other three (`battle_end_conditions`,
`strategy_click_dispatcher`, `simulation_adapter`) as separate
single-file extractions.

PROJ-407 itself does not perform any of this work. It only documents
the audit so future agents can find the deferred items in one place.
