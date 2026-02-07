# PROJ-54: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-05 | Project initialized | Starting point for Combat Lab Quality Cleanup and Expansion |
| 2026-02-05 | Phase 0 (quality cleanup) before expansion | User explicitly requested code quality focus before adding new features |
| 2026-02-05 | All 5 priorities in scope | User chose all: _resolve_path dedup, extraction generalization, verify dedup, defense tests, modifier tests |
| 2026-02-05 | Add defense stats to extraction | User chose to include defense stats (total_defense_score, emissive_armor, max_shields, current_shields) |
| 2026-02-05 | Test modifiers are single-effect only | User specified: "test modifiers should only modify a single variable" - isolates the variable being tested |
| 2026-02-05 | Test modifiers have no restrictions | Unlike game modifiers which have `allow_abilities`/`deny_abilities`, test modifiers are unrestricted for flexibility |
| 2026-02-05 | Maintain backward compat for `data['weapon']` | Existing beam scenarios use `attacker.weapon.damage` paths - these must continue working after extraction generalization |
| 2026-02-05 | 6-phase structure (3 cleanup + 3 expansion) | Phases 1-3 clean foundation, Phases 4-6 add new features. Run full test suite after each phase. |
