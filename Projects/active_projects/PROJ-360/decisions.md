# PROJ-360: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-04 | Project ID = PROJ-360 | User-directed sequence start at 356; this is #5 of 5. |
| 2026-05-04 | Project created from realtime-combat tech-debt review | Review finding #5 (P2 maintainability): `ShipStatsCalculator` is monolithic and over the 500 LOC convention. |
| 2026-05-04 | Manual scaffolding (not via `create_project.py`) | Folder pre-existed with `plan.md`. Mirrored canonical templates. |
| 2026-05-04 | Opted into 03c phase-aware execution | Per `.claude/skills/claude-proj-start/SKILL.md` Phase D. |
| 2026-05-04 | Three-phase split (golden / extract behind API / replace hardcoded checks) | Strict TDD; preserve mutation-order semantics; mechanical extraction first, semantic replacement second. |
| 2026-05-04 | Sequence AFTER PROJ-359 | PROJ-359 introduces typed weapon contracts that some weapon/defense contributors will want to consume. |
| 2026-05-04 | `ship_design_stats.py` and `combat_endurance.py` excluded | Each has its own complexity score; not the immediate target. Surface as follow-ups if PROJ-360 reveals natural extraction points. |
| 2026-05-04 | Contributor module location TBD | Likely `game/simulation/entities/stat_contributors/` to mirror `combat/families/` from PROJ-359; finalize in Phase 2 once the first split lands. |
| 2026-05-05 | Phase 1: 7 golden designs (`qs_escort`, `qs_general_purpose`, `qs_frigate_gc`, `qs_heavy_cruiser`, `qs_battleship`, `qs_missile_cruiser`, `qs_warp_gate_opener`) | Cover small/medium/large/capital, with/without armor pool, with/without shields, with/without warp drive, with/without weapons, with/without colony pod (passenger). No fighter-bay design exists in `data/designs/` so launch contributor is exercised through code coverage of `_aggregate_hangar_abilities` (zero-path) plus the unit tests added in Phase 2. |
| 2026-05-05 | Snapshot stored as sibling JSON, not inline literals | 7 designs × ~30 fields × resource maps would be unreadable as a Python literal. JSON file gives clean diff visibility on any future drift. Floats normalized to 12 sig figures via `_round_for_snapshot` to dodge platform float-print noise. |
| 2026-05-05 | Phase 1 sharded baseline: 17665 tests, 17661 passed, 0 failed, 4 skipped | Post-Phase-1 baseline. Phases 2 + 3 must preserve this exactly (will add new domain unit tests on top). |
| 2026-05-05 | Phase 2: contributor split into `stat_contributors/{movement,defense,weapons,command,launch}.py` | Mirror naming from PROJ-359's `combat/families/`. ship_stats.py drops from 643 → 486 LOC under the 500 ceiling. Public `ShipStatsCalculator.calculate()` API unchanged — golden tests bit-identical. |
| 2026-05-05 | Phase 2: `_priority_sort_key` kept as instance method (passthrough to module fn) | Hedge against any hidden caller — the underscore prefix is private but the method has been stable for years. Cheap to remove later if grep confirms no callers (we checked, none, but kept the passthrough). |
| 2026-05-05 | Phase 2: PROJ-359 typed contract NOT consumed in `weapons.py` | The typed `AttackRequest`/`AttackResolution` contract from PROJ-359 covers per-shot resolution, not stat aggregation. ECM/sensor scores are pre-fire *inputs*, not outputs of a fire event — no field on the typed contract maps cleanly. Documented in `weapons.py` module docstring; revisit only if Phase 3 registry surfaces a natural seam. |
| 2026-05-05 | Phase 2 sharded: 17702 tests, 17698 passed, 0 failed, 4 skipped (+37 contributor tests over Phase 1) | Bit-identical preservation confirmed via golden snapshot. |
| 2026-05-05 | Phase 3: sibling registry `stat_contributors/registry.py`, NOT extension of `combat.ability_stat_registry` | The PROJ-273 registry is shaped for the modifier-emission pipeline (compiler → ModifierEntry → external_stats). Per-component stat aggregation has different semantics (read once at recalculate time, no team routing, no scope fan-out). Mixing them would warp both contracts; sibling keeps each focused. |
| 2026-05-05 | Phase 3: Replaced two extension points only — `priority_sort_key` and a generic stat contributor hook | Other "hardcoded" strings (`get_abilities('CombatPropulsion')`, etc.) are TYPED accumulator paths reading typed attributes (`thrust_force`, `turn_rate`) — they are not gating CHECKS. Removing the names would break accumulation. The plan's intent ("registered contributor") is satisfied by the two real extension points: priority sort + the generic hook used by the acceptance test. |
| 2026-05-05 | Phase 3 final: `ship_stats.py` = 495 LOC, sharded 17717/17713 passed (+15 over Phase 2) | Goal met (under 500). Acceptance test codifies extensibility. Pattern documented in `docs/02_PATTERNS.md` §35. |
