# PROJ-392: Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-08 | Project initialized | Starting point for Legacy removal — Misc orphan wrappers + zero-call-site placeholders (2026-05-07) |
| 2026-05-08 | Bundled findings from `2026-05-07_220621_legacy-audit` by removal cluster `misc_orphan_wrappers` per user direction | Catch-all bundle for legacy artifacts that don't belong to other clusters but are too small to warrant their own projects. UNCERTAIN-included: LEG-02-015 (`_menu_scene` rename). INFO-included: LEG-03-010 (`get_asset_manager` alias), LEG-03-016 (`get_crew_required` wrapper). UNCERTAIN-excluded: LEG-01-008 (`find_metadata` intentional API), LEG-03-012 (`Ship.to_dict/from_dict` Facade pattern), LEG-03-013 (`to_roman` 1-LOC convenience). Full bundling discussion in `findings/bundling_decisions.md`. |
