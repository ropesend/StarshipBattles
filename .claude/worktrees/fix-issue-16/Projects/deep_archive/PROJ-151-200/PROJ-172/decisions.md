# PROJ-172: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-23 | Project initialized from god class decomposition review | 7-agent review analyzed 16 files, produced actionable plans |
| 2026-02-23 | MVVM pattern for ALL UI extractions | User preference. MVVM provides architectural barrier against regrowth. Facade/delegate alone failed (re-offender evidence). |
| 2026-02-23 | Use existing EventBus (`game/ui/screens/builder/event_bus.py`) | Already proven in WorkshopViewModel. No need to create new infrastructure. |
| 2026-02-23 | ViewModel convention: same directory as screen, named `XxxViewModel` | Follows WorkshopViewModel and FleetListViewModel precedent. |
| 2026-02-23 | Scope: 6 files in Wave 1, user can rewind for remainder | Keeps project focused. Remaining files (Galaxy, Strategy cluster) are separate projects. |
| 2026-02-23 | Phase order: quick wins first, then increasing complexity | BattleStateViewer (1 dep) and FormationEditor (already decomposed) build confidence before tackling re-offenders. |
| 2026-02-23 | Target sub-600 lines, prioritize 800+ files | User preference. 600 is aspirational; practical focus is on the biggest offenders first. |
| 2026-02-23 | EmpireBuildQueueWindow sidebar: extract as COMPLETE subsystem | Root cause of regrowth was extracting only data layer. Sidebar must own both filter logic AND filter UI. |
| 2026-02-23 | TestLabScreen: extract renderer + input handler (not just ViewModel) | Screen has 74 methods. ViewModel alone insufficient — need to extract the 19 draw methods and 12 input handlers. |
| 2026-02-23 | BattleStateViewer: component extraction not MVVM | This is a widget/component, not a screen. Extract reusable parts (json_diff, scrollable_panel), don't force MVVM on it. |
| 2026-02-23 | Test baseline: 12,023 passed, 1 skipped, 0 failures | Established before planning. All phases must maintain this baseline. |
