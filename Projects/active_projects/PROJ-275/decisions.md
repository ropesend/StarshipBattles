# PROJ-275: Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-16 | Project initialized | User explicitly confirmed N-team as a real goal; sequential 2-team decomposition was "a mistake." |
| 2026-04-16 | Sequential 2-fleet decomposition in `ConflictResolutionEngine` is DELETED, not kept as fallback | Rule 3 (Clean-Sheet) + user's explicit framing ("was a mistake"). System Migration Policy forbids keeping legacy behind flags. |
| 2026-04-16 | N-team is functional for 2-8 sides; UI polish for >4 sides is follow-up | Ship engine support + reasonable UI. 5+ cosmetic polish can be a later project. |
| 2026-04-16 | Everyone-hostile — no alliances, no team relationships | Explicit in `docs/systems/combat_simulation.md` §9 ("No alliances" comment on `get_enemies_of`). |
| 2026-04-16 | Max teams = 8 | Practical UI + ring layout cap. Engine has no hard cap; the 8 limit lives in UI + spec validation. |
| 2026-04-16 | Ring-based entry vectors; preserve 2-team legacy layout | For N=2, keep west/east (player expectations). For N≥3, equally-spaced points on a ring. Prevents visual regression for the common case. |
| 2026-04-16 | Project depends on PROJ-273 AND PROJ-274 | Registry helper needs `num_teams` kwarg; materializer must be team-agnostic. Cannot start Phase 2 until both complete. |
| 2026-04-16 | `BattleSetupState` uses `List[BattleSetupSide]` with `side_0`/`side_1` backcompat properties | Landing the state change before UI migration reduces blast radius. Delete shims after UI migrates. |
| 2026-04-16 | `_route_team_for_scope` returns `List[int]` | Enemy-scope fan-out is the whole point. Single-int return was the 2-team assumption. |
| 2026-04-16 | No mid-battle team addition | Teams are fixed at battle start. Mid-battle reinforcements join an existing team. |
| 2026-04-16 | Save compatibility is NOT preserved | Per `CLAUDE.md` — saves are disposable. |
