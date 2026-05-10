# PROJ-403: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-09 | Project initialized | Starting point for Tier 1 B-04: Migrate stale _MockGalaxy doubles to GalaxyState |
| 2026-05-09 | Use real `GalaxyState(radius=10)` per test (Option A); rename fixture from `galaxy` to `state` | Exercises the production dataclass directly. No shared helper extracted: the fixture is one line and a helper would obscure intent. Per-file fixture keeps each file self-contained. Mock-stub `_MockGalaxy` class deleted entirely (no compat shim). |
| 2026-05-09 | Production caller audit clean | `rg "GalaxyEntityRegistry\(\|GalaxySpatialIndex\("` against `game/` finds only `galaxy.py:63-64` — both pass `self._state`. No production fix needed. |
| 2026-05-09 | No other stale Galaxy stubs found in scope | Per "Don't expand scope" rule, did not search wider for legacy stubs. |
