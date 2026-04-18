# PROJ-254: Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-06 | Add `query_radius_exact()` as a new method rather than changing existing `query_radius()` | Existing callers may rely on the broad-phase behavior for performance-tolerant uses. New method is opt-in. |
| 2026-04-06 | Thread instance_id through IPostBattleShip protocol, not Ship metadata dict | Protocol property is type-safe and discoverable. Metadata dict would be stringly-typed. |
| 2026-04-06 | Remove expected_stats fallback entirely, not make it opt-in | Per CLAUDE.md "Clean-Sheet Design" rule: if Ship.from_dict() fails, that's a real error. Silencing it with stale data hides bugs. |
| 2026-04-06 | Lightweight index dicts on Galaxy, not a separate index service | The indices are simple dicts maintained at mutation points. A separate service would be overengineering for the current scale. |
