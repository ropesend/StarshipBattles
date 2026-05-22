# PROJ-476: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-21 | Project initialized | Starting point for Facade read-path: tooling/editor screens (battle_setup, galaxy_test, race_setup) reader migration (follow-on from PROJ-472) |
| 2026-05-21 | Created + scoped as the **tooling/editor screens** tail of PROJ-472. **GATED on PROJ-472's guards; informed by PROJ-475.** | Tooling/sandbox surfaces (`battle_setup` x4, `galaxy_test` x3, `race_setup` x4, `builder` x3 — verified 2026-05-21) are not live strategy screens and likely need broader/file-scoped exemptions than the main strategy UI (consult §4 + Open Question 1). Migrated last so the live-UI policy is settled first; exemptions must be file+reason scoped, not blanket waivers. |
