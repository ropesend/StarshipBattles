# PROJ-395: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-08 | Project initialized | Starting point for PROJ-381 remediation — review CRITICAL + MAJOR findings (B-5 modal, ValidationException registry, test assertions, etc.) |
| 2026-05-09 | **MAJ-013 + MAJ-014 closed in PROJ-409** | See `Projects/active_projects/PROJ-409/decisions.md` for rationale. MAJ-013 closure mode: **ratified — already actively closed by PROJ-390** (the module-level `log_event` / `set_event_handler` / `get_event_handler` compatibility shim was deleted; PROJ-395's reviewer flagged the file but did not pick up the PROJ-390 closure). MAJ-014 closure mode: **actively deleted** in commit `c0ff79f92` — defensive raw `EnginePhaseError` catch removed from `game/ui/screens/strategy_game_state_manager.py` per CLAUDE.md Rule 4 now that PROJ-408 C-02 unit-tests the facade conversion directly. |
