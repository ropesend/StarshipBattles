# PROJ-297: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-26 | Project initialized | Remediation of confirmed 2026-04-26 code review findings |
| 2026-04-26 | FleetOrder rename split into separate project (PROJ-298) | 726 old-name usages — too broad to bundle into a "quick wins" PR; merits its own checklist and merge-management. User confirmed via AskUserQuestion. |
| 2026-04-26 | `battle_runner.py:191` DI fix is OUT OF SCOPE | Confirmed call site, but it's the documented PROJ-274 transitional fallback. Removal must coordinate with PROJ-274 closure |
| 2026-04-26 | `print()` in `battle_resolver.py:56` is REFUTED | The print is inside a docstring example, not production code |
| 2026-04-26 | "5 TODOs / 2 PROJ-XXX placeholders" claim is REFUTED | Only 2 legitimate TODOs in `game/`; zero placeholders |
| 2026-04-26 | PROJ-296 "empty placeholder" claim is REFUTED | PROJ-296 is the active LLM-services project (committed today) |
| 2026-04-26 | Mock-overuse in `test_command_handlers.py` (267 refs) is OUT OF SCOPE | Mock-density reduction is its own dedicated refactor project, not a "quick win" |
| 2026-04-26 | Priority-3 review items (file bloat, deep nesting, type annotations) are OUT OF SCOPE | Each is a multi-file refactor warranting its own scoped project — bundling them into "review cleanup" would inflate scope |
| 2026-04-26 | Stale tests will be investigated per-file before deletion (user choice) | User selected "Investigate per-file, likely delete" — check git log to see when symbols were removed; verify equivalent coverage exists; only then delete |
