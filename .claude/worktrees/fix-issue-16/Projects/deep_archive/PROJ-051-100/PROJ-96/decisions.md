# PROJ-96: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-10 | Project initialized | Starting point for Species Setup Ships View Layout Redesign |
| 2026-02-10 | Baseline: 7595 tests passing, 0 failures | Established before any changes |
| 2026-02-10 | Theme list on left (~200px), preview grid on right | User requirement: themes as scrollable list on left side |
| 2026-02-10 | 3 columns, 9 ships per theme | User requirement: 3 per line, 9 total (up from 2 per line, 6 total) |
| 2026-02-10 | Ship selection: Fighter(Med), Satellite(Med), Escort, Frigate, Cruiser, Heavy Cruiser, Battleship, Dreadnought, Superdreadnought | User approved this set of 9 representative classes |
| 2026-02-10 | Use visible bounding rect for top-down scaling | Top-down images have large transparent areas; using `get_image_metrics()` to scale based on visible pixels makes ships appear at comparable size to portraits |
| 2026-02-10 | Portrait size: 160px (down from 180px) | Slightly smaller to fit 3 columns comfortably with centered image pairs |
| 2026-02-10 | Delete `_load_ship_portrait` method | Duplicates `ShipThemeManager.get_portrait_image()` which has proper caching and thread safety |
| 2026-02-10 | Remove preview label/panel from RaceThemeGallery | Redundant - button highlighting already shows selection; parent screen has title |
| 2026-02-10 | Cap top-down scale factor at 3.0 | Prevents absurdly large images for very small sprites with lots of transparency |
