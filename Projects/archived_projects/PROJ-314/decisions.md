# PROJ-314: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-28 | Project initialized | Starting point for Unify Ship Theme Loader Schema, converted from triage `ship_themes_unified_schema_migration.md`. |
| 2026-04-28 | Project title: "Unify Ship Theme Loader Schema" | User-selected from 4 options during interactive setup. |
| 2026-04-28 | Image generation model: `gpt-image-2` | User direction. Confirmed real model via OpenAI developer docs. Supports both text→image (`v1/images/generations`) and image→image edits (`v1/images/edits`). |
| 2026-04-28 | Ship-class key naming: display-form (`"Battleship"`, `"Fighter (Medium)"`, `"Satellite (Heavy)"`) | 8 of 9 themes already use it; only Thoraliens (CamelCase) needs migration. Easier path. User-selected. |
| 2026-04-28 | Image size: 2048×2048 standardised, both skin and portrait | User direction. Validated at load via PIL; loader logs warning on mismatch but does not reject. |
| 2026-04-28 | Image format: PNG only | `docs/03_CONVENTIONS.md` §285–288 mandates PNG; existing `.jpg` files must transition to `.png` when touched. Federation/Atlantians/Klingons/Ossivine/Prismsteel/Romulans/Voidforged portraits (151 `.jpg` files) are converted in Phase 4. |
| 2026-04-28 | Caption sidecar generation: out of scope | User direction. `theme.caption.json` files for newly generated portraits are not produced; that work is handled separately. |
| 2026-04-28 | Schema migration: atomic, no shim | CLAUDE.md Rule 3 (Clean-Sheet Design) + System Migration Policy explicitly forbid backward-compat shims. All 9 `theme.json` files migrate in one commit alongside the loader rewrite. Mitigated by feature-branch development. (API Reviewer agreed; Risk Assessor's "temporary shim" recommendation rejected on policy grounds.) |
| 2026-04-28 | Image service location: `game/ui/services/image/`, NOT `game/services/image/` | Architecture Analyst: all 11 importers of `get_default_ship_theme_manager()` are UI-layer. The "2+ layer" criterion in `docs/01_ARCHITECTURE.md` for top-level `game/services/` is not met. Belongs in the consuming layer's services subpackage. |
| 2026-04-28 | Filename normalisation: `lowercase_with_underscores.png` | Mixed-case filenames in 4 themes work on Windows but break on Linux CI. Phase 5 normalises every filename. CI lint script verifies. |
| 2026-04-28 | `get_portrait_image()` return contract: always `Surface`, never `None` | Long-standing inconsistency with `load_image()` which returns Surface with fallback. Phase 3 unifies both with synthetic fallback for missing portraits. |
| 2026-04-28 | `ImageResult.size`: actual returned size, never silent upscale | API Reviewer: gpt-image-2 may not support every requested size. Returning the actual size (not silently resizing) makes the failure mode visible to callers, who can decide to upscale or accept. |
| 2026-04-28 | Ship-class constant location: `game/core/ship_classes.py::SHIP_CLASSES_WITH_VISUAL_THEMES` | Single source of truth for theme.json schema validation. Frozenset of 19 entries. New file added in Phase 1. |
| 2026-04-28 | Test isolation default: `NullImageProvider` raises on `generate_image()` | Prevents accidental real-OpenAI-API calls during tests when `OPENAI_API_KEY` is set in the developer's environment. `ApplicationContext.create_test()` injects it by default; tests opt-in to a canned-response mock. |
| 2026-04-28 | Out of scope: moving `ShipThemeManager` to `game/assets/` | Architecture Analyst flagged that current placement at `game/ui/assets/` is a code-organisation artifact and should move. Defer to a follow-up project — too much scope creep here. |
| 2026-04-28 | Out of scope: cache invalidation hook for live game development | Watchdog/inotify listener for live PNG file changes was suggested but not added. Regenerator CLI documents that a game restart is needed to pick up new portraits. |
| 2026-04-28 | Test baseline at plan time | 15893 / 15893 passing (sharded suite, 65.8s wall). Net delta after PROJ-314: +6 tests (~15899). |
