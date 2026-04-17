# PROJ-272: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

## Locked Architectural Decisions (from round-2 audit)

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-13 | Project initialized | Successor to PROJ-269/270/271 round-2 audit findings. |
| 2026-04-13 | **PROJ-272 created as SEPARATE project, not PROJ-271 re-open.** | PROJ-271 was properly archived after manual smoke passed. Round-2 findings are new scope — cleaner history to file as successor than un-archive. |
| 2026-04-13 | **Phase 7 stack_group cross-source claim is being SCALED BACK, not re-delivered.** Provider auras bucket by `type(ab).__name__` ("ShieldModifier"); external entries bucket by `effect.stat_key` ("shield_capacity_mult"). These are semantically different keys and should stay separate. Phase 2 documents within-source-only composition + threads `stack_group` through the strategy compiler (currently hardcoded to None at `_real_entry`). | Unifying key schemes would require a class-name → stat_key registry + larger refactor. The production case that motivated Phase 7 (two same-source complexes stacking additively) IS fixed by Phase 7 as landed. The "provider × external same-group MAX" claim in commits/docs was overstated and needs retraction, not more code. |
| 2026-04-13 | **Phase 6 reverts PROJ-271 Phase 12.1's `capacity_mult` read.** Phase 12.1 added `capacity_mult` to flat-bonus scaling to mirror `ShieldProjection.recalculate`. But `capacity_mult` isn't populated by any fleet aura today — the read is a latent double-multiply the moment any future aura populates it. Revert to `shield_capacity_mult` only. | Over-eager symmetry created a silent future-bug. User-clarified intent ("virtual extra shield component") is honored by `shield_capacity_mult` alone for current aura inventory. Revisit if a real `capacity_mult` team aura ever appears. |
| 2026-04-13 | **Pattern 26 (Spec Compiler → run_battle) is a DUPLICATE of pre-existing Pattern 13.** Round-1 docs pass added Pattern 26 without noticing Pattern 13 existed. Phase 9 deletes 26, merges acceptance-guard reference into Pattern 13, rolls count 26 → 25 across all docs. | Honest accounting: round-1 missed the pre-existing pattern because I pattern-matched on the PROJ-269 commit message rather than re-reading the file. Round-2 docs skeptic caught it. |
| 2026-04-13 | **3+ team behavior: LOUD NotImplementedError, not silent misroute.** Battle Setup `_NUM_TEAMS = 2` + `_route_team_for_scope` assume 2 teams. Strategy compiler supports N teams but Resolver takes 2 fleets. Phase 10 adds explicit guard that raises `NotImplementedError` with a clear message when >2 teams reach either compiler. | "Silent misroute" is the most dangerous bug class. Explicit failure surface documents the limitation and forces future multi-team work to address it deliberately. |
| 2026-04-13 | **`_apply_bonuses` `if v` filter → `if v is not None`.** Current filter drops legitimate 0.0 values. A `damage_mult=0.0` suppressor = "enemy ships deal 0 damage" is a valid game-state effect, semantically different from "no modifier applied". | Silently conflating these values is a correctness bug even though no current aura populates 0.0. |
| 2026-04-13 | **Phase 1 `_extract_scope` fix resolves `default_scope` from ability class.** Compiler returns `"self"` on missing scope; runtime uses class-level `default_scope` (e.g., `ALLIED_SYSTEM`). Fix: look up ability class in registry, read `cls.default_scope.value`. Same fix in `combat_modifier_collector.py:88`. | Compiler/runtime disagreement is the most insidious bug class. Fix both. |

## Future Decisions

(Record new decisions below as implementation proceeds.)

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-13 | **Phase 5 scope CORRECTED mid-phase — SHIM RETAINED, not deleted.** Initial audit claimed "zero callers" of `BattleScreen.start(team0, team1)` + `_build_fallback_outcome`. Full regression after deletion surfaced ~46 test callers across `test_battle_screen.py`, `test_battle_screen_simulation.py`, `test_visual_run.py`. Restored both methods as documented legacy shims; marked `BattleScreen.start` docstring `DEPRECATED`; regression guard now enforces "docstring contains deprecation marker" instead of "method absent". Full deletion deferred until those ~46 tests are migrated — separate scope. | The "zero callers" audit used an insufficient grep that missed `self.scene.start([...])` callers with indentation. Restoration is honest: the shim is genuinely test-only today, and eradicating it requires test migration that's outside PROJ-272's risk budget. The guard enforces deprecation visibility instead of absence — contributors can't use it by accident. |
