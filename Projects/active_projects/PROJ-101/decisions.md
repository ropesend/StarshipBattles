# PROJ-101: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-10 | Project initialized | Starting point for Fleet Report Screen Enhancements |
| 2026-02-10 | Replace ShipDetailPanel with DesignReportPanel | User explicitly chose this. DesignReportPanel is the shared panel used in Build Queue and Design Workshop. Needs 750px width (vs 350px for ShipDetailPanel). At 2560px min resolution with 90% window, list still gets 1244px. |
| 2026-02-10 | Use DesignLoaderAdapter to convert ShipInstance→Ship | DesignReportPanel.update_design() takes a Ship (simulation entity). Same pattern used in build_queue_controller.py:578. Create Ship from ship_instance.design_data via DesignLoaderAdapter.load_ship_from_design_data(). |
| 2026-02-10 | All new columns hidden by default | Current 7 columns total 634px. Adding 7 more would overflow. New columns default to visible=False, togglable from sidebar COLUMNS section. |
| 2026-02-10 | Per-ship spaceyard check as static method on FleetCapabilityCalculator | Reuse existing logic. New static `ship_has_spaceyard(ship)` checks design_data layers for SpaceShipyard ability. Existing fleet-level `has_space_shipyard` property refactored to call this. |
| 2026-02-10 | Multi-select follows Build Queue pattern | Ctrl+click toggle with Set-based index tracking. Proven pattern from empire_build_queue_window.py:304-337. |
| 2026-02-10 | Bulk removal → one new fleet | User chose: selecting multiple ships and removing them creates one new fleet containing all removed ships (not individual fleets per ship). |
| 2026-02-10 | Thread empire reference through FleetReportWindow | Need Empire.get_next_fleet_id() and Empire.add_fleet() for ship removal. Pass from strategy_window_manager.py via self.scene.current_empire. |
| 2026-02-10 | Fix _update_sidebar bug | Line 778 calls self._update_sidebar() but method was renamed to _update_summary() in PROJ-44. Latent bug to fix in Phase 1. |
