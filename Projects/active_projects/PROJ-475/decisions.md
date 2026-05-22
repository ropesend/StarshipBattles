# PROJ-475: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-21 | Project initialized | Starting point for Facade read-path: remaining live strategy-screen + render readers migration (follow-on from PROJ-472) |
| 2026-05-21 | Created + scoped as the **remaining live readers + pass-through deprecation** tail of PROJ-472. **GATED on PROJ-472's guards + first slice landing.** | PROJ-472 honestly leaves the read path tightened-but-not-closed: `StrategyScreen` pass-throughs (`strategy_screen.py:160-189`) and `FacadeSessionState.session` (`_facade_state.py:63-86`) stay as documented transitional surfaces. Their deprecation + the remaining live readers belong here per consult §4/Risks. Respect render-hot-path caution (no per-frame projections). |
