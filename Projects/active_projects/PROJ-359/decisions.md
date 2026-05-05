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
| 2026-05-05 | Phase 3: per-family migration commits | Beam (3.1), Projectile (3.2), Seeker (3.3), PDC (3.4) each landed as separate commits. Each kept the legacy fallback branch in place so the previous family's failure mode would be visible in shard output before the next migration. |
| 2026-05-05 | Phase 3.4: introduced FAMILY_METADATA | The plan called for "PDC's distinguishing semantics move into family metadata." Implemented as a frozen-dataclass map `FAMILY_METADATA: dict[WeaponFamily, WeaponFamilyMetadata]` co-located with the contract. Two flags today (`targets_missiles`, `consumes_pdc_missile_context`); the structure scales to additional per-family policy. Mirrors PROJ-273 ABILITY_STAT_REGISTRY shape. |
| 2026-05-05 | Phase 4: BeamResolution gained `type=AttackType.BEAM` discriminator field | Required so `battle_engine._process_attacks` can discriminate by `attack.type` for both legacy Projectile/Missile objects and new BeamResolution dataclasses without an `isinstance` cascade. |
| 2026-05-05 | Phase 4 baseline locked: 17649 tests / 17645 passed / 4 skipped | Same shape as Phase 1 (17621 / 17617 / 4) plus 28 new tests across the project (registry contract + extensibility acceptance + golden test additions in concurrent-agent commits). |
| 2026-05-05 | Concurrent-agent commit attribution: Phase 2 commit absorbed PROJ-364 + superweapon files | A parallel agent staged files between my `git add` and `git commit`. Subsequent commits used `git commit --only <files>` to constrain commit contents. PROJ-364 + superweapon work is preserved (their earlier commit landed first), but the Phase 2 commit `a8a2fc10b` shows additional files that were not part of PROJ-359 scope. Future per-phase commits use `git commit --only` to prevent recurrence. |

## Audit Remediation

OpenCode review `req_20260505_070825_cfa324` reported 0 CRIT, 3 MAJ, 5 MIN, 2 NIT for PROJ-359. Major findings remediated below; minor and nit items deferred (no correctness impact, follow-up tickets at the team's discretion).

| Finding | Verdict | Resolution |
|---------|---------|-----------|
| MAJ-001: Redundant `has_ability('BeamWeaponAbility')` lookup in `TargetingSystem._get_pdc_valid_targets` | Fix | Refactored helper to take an already-resolved `beam_ab` parameter. The PDC branch in `find_valid_target` now resolves `BeamWeaponAbility` once via `comp.get_ability(...)` (no `has_ability` re-lookup) and passes the result. The last family-string lookup in targeting is gone — `weapon_registry.detect_family` is now the only owner of those strings in the dispatch path. |
| MAJ-002: `BeamHandler` and `PDCHandler` carried byte-identical `.fire()` bodies with no shared base, risking silent drift if `BeamResolution` gains a field | Fix | Extracted `families/_beam_common.build_beam_resolution(request)`. Both handlers delegate to it, so the resolution shape stays in sync by construction. The two-handler distinction (per-family targeting policy via `FAMILY_METADATA`) is preserved. |
| MAJ-003: `detect_family → None` graceful skip path had no golden test | Fix | Added `TestTargetingGolden::test_unrecognized_weapon_family_no_attack_emitted` in `tests/unit/simulation/combat/test_weapon_dispatch_golden.py`. Pins the silent-no-op contract for components that have `WeaponAbility` but no recognized family ability — guarantees `fire_weapons` returns `[]` rather than raising `UnregisteredWeaponFamilyError`. |

Test posture: combat unit suite (`tests/unit/simulation/combat/test_weapon_dispatch_golden.py`, `test_weapon_registry.py`, `test_targeting_system.py`, `test_weapon_firing_system.py`) — 95/95 passing. Full sharded-suite failures observed are attributable to concurrent-agent modifications outside PROJ-359 scope (`game/simulation/entities/ship_serialization.py`, `game/simulation/entities/stat_contributors/registry.py`, `game/strategy/engine/superweapon_order_processor.py`); reproducible by stashing only the PROJ-359 audit files.

Deferred (MIN / NIT): seeker arc-check edge-case tests (MIN-001), extensibility-acceptance new-enum scenario (MIN-002), beam-visualization dict (MIN-003), LAUNCH dict path (MIN-004 — explicitly out of scope per `decisions.md` 2026-05-04 row), `process_beam_attack` null-guard (MIN-005), `AttackRequest` `Any` typing (NIT-001), `FAMILY_METADATA` silent-default policy (NIT-002). None affect correctness; capture as follow-ups if PROJ-359 hardening continues.
