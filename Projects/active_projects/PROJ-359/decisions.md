# PROJ-359: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-04 | Project ID = PROJ-359 | User-directed sequence start at 356; this is #4 of 5 (largest). |
| 2026-05-04 | Project created from realtime-combat tech-debt review | Review finding #4 (P2 extensibility, largest leverage). |
| 2026-05-04 | Manual scaffolding (not via `create_project.py`) | Folder pre-existed with `plan.md`. Mirrored canonical templates. |
| 2026-05-04 | Opted into 03c phase-aware execution | Per `.claude/skills/claude-proj-start/SKILL.md` Phase D. Phase dependencies captured in each checklist. |
| 2026-05-04 | Four-phase split (golden / contract / migrate / delete) | Strict TDD; cross-cutting refactor risk; per-family migration enables one-file rollback. |
| 2026-05-04 | Sequence AFTER PROJ-356 / 357 / 358 | Smaller correctness fixes first; this is the only structural refactor in the batch and benefits from the test infrastructure those projects build out. |
| 2026-05-04 | Sequence BEFORE PROJ-360 | ShipStatsCalculator decomposition (PROJ-360) may want to consume the typed contract once it lands. |
| 2026-05-04 | Defer specific contract shape | `AttackRequest` / `AttackResolution` field set is best decided in Phase 2 against the actual call sites; do not over-specify in plan.md. |
| 2026-05-04 | Phase 1 baseline locked: 17621 tests (17617 passed, 4 skipped) | After adding 10 golden dispatch tests in `tests/unit/simulation/combat/test_weapon_dispatch_golden.py`. This is the reference count Phases 2-4 must preserve. |
| 2026-05-04 | Phase 1 inventory of existing combat tests | `test_weapon_firing_system.py` (1298 LOC) and `test_targeting_system.py` (1110 LOC) lock per-method behavior with MagicMock-driven scenarios; gaps were end-to-end family-shape contracts (dict vs Projectile constructor kwargs) and beam→collision telemetry chain. Golden tests added to fill those gaps. |
| 2026-05-04 | Phase 2: BeamResolution as 1:1 typed mirror of legacy beam dict | Eases Phase 3 migration: collision.py can switch from `attack['origin']` to `resolution.origin` mechanically. Phase 4 will collapse this further if telemetry convergence allows. |
| 2026-05-04 | Phase 2: PDC detected before BEAM in `detect_family` | A PDC weapon is a Beam weapon with the 'pdc' tag; without PDC-first ordering all PDC dispatches would route through the Beam family. |
| 2026-05-04 | Phase 2: WeaponRegistry as a class with module-level singleton | Lets tests build local registries (`WeaponRegistry()`) without leaking state across tests, while production code uses `WEAPON_REGISTRY`. Mirrors common DI patterns. |
| 2026-05-04 | Phase 2: dict-carrier audit | Beam dict shape consumed by `game/engine/collision.py:76-111`; `AttackType` discriminator consumed by `game/simulation/systems/battle_engine.py:583`; launch dict shape consumed by `_process_launch_attack`. Launch is a *hangar* path, not a weapon family — out of scope for PROJ-359 (this project covers BEAM/PROJECTILE/SEEKER/PDC only). |
