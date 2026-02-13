# PROJ-89: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-09 | Project initialized | Starting point for God Class Decomposition - Remaining UI Tier |
| 2026-02-09 | Only 2 files worth decomposing in remaining UI tier | RaceSetupScreen, FleetReportWindow, FormationEditor, StrategyScreen are already well-decomposed with existing helper modules or offer only marginal gains. Focus effort where it matters. |
| 2026-02-09 | Image helper extracted as module-level functions, not a class | Portrait and top-down thumbnail loading are pure functions with no shared state. Module-level functions are simpler and more Pythonic than a utility class. |
| 2026-02-09 | Image helper is reusable across FleetReportWindow and other screens | The design_image_helper.py module takes DesignMetadata as input and returns pygame.Surface - no coupling to DesignSelectorWindow. Any screen showing design previews can import it. |
| 2026-02-09 | Formatter extracted as static methods for easy testing | All formatting methods (_get_queue_summary, _get_first_item_text, etc.) are pure data transforms. Static methods require no mocking of pygame or UIWindow infrastructure. |
| 2026-02-09 | _get_system_name stays as instance-level function accepting galaxy parameter | Unlike the other formatters, _get_system_name needs a galaxy reference for system lookups. It will be a standalone function that accepts galaxy as an explicit parameter rather than a static method. |
| 2026-02-09 | Facade pattern: original classes remain the public API | DesignSelectorWindow and EmpireBuildQueueWindow keep their existing method signatures. Internal methods delegate to new helper modules. All existing tests pass without modification. |
| 2026-02-09 | Filter manager follows fleet_report_filters.py pattern | EmpireBuildQueueWindow filter extraction mirrors the existing FleetReportWindow decomposition for consistency across the codebase. |
