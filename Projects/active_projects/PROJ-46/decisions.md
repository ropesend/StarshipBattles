# PROJ-46: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-28 | Project initialized | Starting point for Naming Consistency Standardization |
| 2026-01-28 | Address ALL 30+ issues | User explicitly chose "All Issues (30+)" over subset options |
| 2026-01-28 | Consolidate ui/ into game/ui/ | User chose "Consolidate to game/ui/" for cleaner architecture |
| 2026-01-28 | Use "Screen" naming convention | User chose "Screen (Recommended)" as canonical UI class naming |
| 2026-01-28 | Canonical validator: ship_validator.py | Analysis showed this is Phase 12 refactored version with 9+ tests |
| 2026-01-28 | Delete legacy systems/validator.py | Only 3 importers, older monolithic design without template pattern |
| 2026-01-28 | Standardize on Optional[str] | 99% prevalence (113 uses) vs 1 use of str \| None |
| 2026-01-28 | FleetMobilityService → FleetSpeedCalculator | Only calculates speed, not full mobility management |
| 2026-01-28 | ShipStatsService → ShipStatsCalculator | Pure calculation pattern, not service behavior |
| 2026-01-28 | Defer NS-02 (multi-class files) | test_lab_scene.py has 11 classes in 4096 lines - too disruptive |
| 2026-01-28 | Defer NS-03/NS-04 (import order) | Use isort tool separately - not core to naming consistency |
| 2026-01-28 | Defer service directory moves | SaveGameService/ResearchService location is low priority |
| 2026-01-28 | 7-phase implementation order | Dependencies: Quick wins → Validator → filepath → Services → AssetManager → UI consolidation → Screen naming |
