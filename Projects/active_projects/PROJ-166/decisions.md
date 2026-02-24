# PROJ-166: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-23 | Project initialized | Starting point for Make RaceThemeGallery Extend BaseGallery |
| 2026-02-23 | Option B: Normalize asset_buttons to 2-tuples | Clean-sheet approach. The UIImage in the 3-tuple is write-only (created during _populate_gallery, never read). Storing it in the shared data structure couples layout concerns to the selection contract. User confirmed clean-sheet preference. |
| 2026-02-23 | Override _create_content entirely | RaceThemeGallery has a fundamentally different layout (vertical list vs image grid). Rather than adding conditionals/flags to BaseGallery, simply override the concrete method. This is the standard template method approach. |
| 2026-02-23 | Keep asset_loader optional | RaceThemeGallery uses ShipThemeManager directly, not RaceAssetLoader. Making asset_loader optional in BaseGallery __init__ preserves this flexibility. |
| 2026-02-23 | Accept _discover_assets return type variance | RaceThemeGallery returns `List[Tuple[str, Dict[str, Surface]]]` while base declares `List[Tuple[str, Surface]]`. Since _populate_gallery is also overridden, the type mismatch never reaches base class code. Pragmatic over dogmatic. |
| 2026-02-23 | No changes to RaceSetupScreen | Verified that RaceSetupScreen only uses public API (constructor, handle_button_click, set_from_config, callback). No direct attribute access. Public API is preserved through inheritance. |
| 2026-02-23 | 3 phases: normalize, refactor, test | Phase 1 normalizes the base (safe, isolated). Phase 2 does the actual refactoring. Phase 3 updates theme tests. Keeps each phase focused and testable. |
