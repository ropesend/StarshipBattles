# PROJ-244: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-05 | Project initialized | Starting point for Team Naming Standardization |
| 2026-04-10 | Project review (Protocol 09) conducted | 11 tasks already done (marked complete), 5 new tasks added: test_battle_determinism.py rename, setup_screen→app.py kwargs chain, battle_factories ships1/ships2 + fleet1/fleet2, docs/combat_simulation.md + fixtures/README.md updates. Expanded scope to include all off-by-one naming patterns, not just `team1_ships`/`team2_ships`. |
| 2026-04-10 | Include setup_screen→app.py kwargs chain | Callback kwargs `team1`/`team2` carry ships with `team_id=0`/`team_id=1` — same confusion. Rename to `team0`/`team1`. Keep log "Team 1"/"Team 2" display labels. |
| 2026-04-10 | Include battle_factories ships1/ships2, fleet1/fleet2 | `ships1` = team 0 with docstring "Ships for team 0" — same off-by-one pattern. Rename to `ships0`/`ships1` and `fleet0`/`fleet1`. |
| 2026-04-10 | Documentation needs updating | Original plan said no docs needed — wrong. `combat_simulation.md` code example and `fixtures/README.md` have old naming. |
