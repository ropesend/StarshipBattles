# PROJ-180: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-24 | Project initialized | Starting point for PROJ-172 Post-Refactor Cleanup |
| 2026-02-24 | Phase order: ghost code → backward-compat → InputHandler | Trivial deletion first, then systematic test updates, then new code last. Each phase is independently valuable. |
| 2026-02-24 | Update tests BEFORE deleting properties | Prevents test breakage window. All tests green at every step. |
| 2026-02-24 | Create WeaponsInputHandler (not move to ViewModel) | Geometry calculations (pixel mapping, rect collision) belong in InputHandler, not ViewModel. Follows FormationInputHandler precedent. |
| 2026-02-24 | TestLabScreen controller delegation is OUT OF SCOPE | Those properties are necessary architectural bridges to controller, not backward-compat shims. Different pattern, different purpose. |
| 2026-02-24 | "Why" comment improvements are OUT OF SCOPE | Documentation polish without structural impact. Can be addressed ad-hoc. |
