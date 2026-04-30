# PROJ-318 File Manifest

> Generated during /claude-proj-start. Used by /claude-proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| `Projects/active_projects/PROJ-314/phase_1_checklist.md` | Tracking | Phase 1 — set Status to `Complete`; check all 34 boxes retroactively documenting that the work shipped via PROJ-314 commit `0ec916cae`. |
| `Projects/active_projects/PROJ-314/phase_2_checklist.md` | Tracking (NEW) | Phase 1 — create file documenting Phase 2 work that shipped via commit `62a7c05af` (image service + DI wiring). |
| `Projects/active_projects/PROJ-314/phase_3_checklist.md` | Tracking (NEW) | Phase 1 — create file documenting Phase 3 work that shipped via commit `48de788da` (loader rewrite). |
| `Projects/active_projects/PROJ-314/phase_4_checklist.md` | Tracking (NEW) | Phase 1 — create file documenting Phase 4 work that shipped via commit `d000acc5a` (regenerate tool + asset prep). |
| `Projects/active_projects/PROJ-314/phase_5_checklist.md` | Tracking (NEW) | Phase 1 — create file documenting Phase 5 work that shipped via commit `0bbf9c36d` (atomic schema migration). |
| `Projects/active_projects/PROJ-314/phase_6_checklist.md` | Tracking (NEW) | Phase 1 — create file documenting Phase 6 work that shipped via commit `e26f00f74` (docs + plan close-out). |
| `Projects/active_projects/PROJ-314/plan.md` | Tracking | Phase 1 — Quick Status table can drop the "(TBD)" annotations on phase_2..6 once the files exist; Current State should note that closeout was completed by PROJ-318. |
| `docs/02_PATTERNS.md` | Doc | Phase 2 — bump "9 services" → "10 services" in the Singleton-Free DI section (lines 83-95). Add `ImageProvider` row to the table. Update the `# all 9 services` comment in the code example. Bump `Last verified:` date. |
| `docs/README.md` | Doc | Phase 2 — bump "9 services" → "10 services" on line 4. Bump `Last verified:` date. |
| `AGENTS.md` | Doc | Phase 2 — bump "9 services" → "10 services" on line 51 (or wherever it appears). |
| `docs/01_ARCHITECTURE.md` | Doc | Phase 2 — implementation found the `ApplicationContext` row still described new services as outside constructor wiring; update it to mention the context-owned `ImageProvider`. |
| `game/ui/utils/portraits.py` | Production | Phase 3 — delete `get_portrait_filename()` (lines 83-97). Delete legacy fallback in `get_portrait_search_paths()` (lines 98-114) or delete the whole function if its sole purpose was the legacy lookup. Update production callers (`build_queue_portraits.py:23`, `design_report_panel.py:18-20`) to use `ShipThemeManager.get_portrait_image()` directly. |
| `tests/unit/ui/utils/test_portraits.py` | Test | Phase 3 — delete `TestGetPortraitFilename` class (3 tests). Verify no other test depends on `get_portrait_filename`. |
| `game/ui/panels/build_queue_portraits.py` | Production | Phase 3 — line 23 caller of `get_portrait_search_paths()`; replace with `ShipThemeManager.get_portrait_image()`. |
| `game/ui/panels/design_report_panel.py` | Production | Phase 3 — lines 18-20 imports of `portraits.py` helpers; replace with `ShipThemeManager.get_portrait_image()` where applicable. |
| `Tools/regenerate_ship_portraits/README.md` | Tool (NEW) | Phase 4 — create README mirroring `Tools/process_components/README.md` shape: Purpose, Usage, Flags, Output, Cost, Examples. |
| `Tools/regenerate_ship_portraits/cli.py` | Tool | Phase 4 — add project-root bootstrap (mirror `Tools/process_components/check_orphans.py:8-19`) BEFORE any `from game.X import` line. Currently lines 45-53 import directly. |
| `Tools/regenerate_ship_portraits/audit.py` | Tool | Phase 4 — same bootstrap as cli.py. Phase 5 — fix the portrait-key gating bug (lines 129-131); add per-theme missing-portrait detection; differentiate exit codes (0 / 2 / 3). |
| `Tools/README.md` | Tool catalog | Phase 4 — add catalog entry for `regenerate_ship_portraits` under appropriate category (Asset Processing or new "Generative" section). |
| `tests/integration/ui/test_race_setup_ships_smoke.py` | Test | Phase 5 — add dimension assertion (`size == (2048, 2048)`); add fallback-discrimination assertion (`surf is not synthetic_fallback`); add `EXPECTED_PORTRAIT_GAPS` allowlist constant + skip-with-allowlist logic. |
| `tests/unit/tools/test_regenerate_ship_portraits.py` | Test | Phase 5 — extend with tests for the new audit behaviour: exit-code assertions, missing-portrait detection per theme, idempotency. |
| `.agents/skills/codex-ship-theme-creator/scripts/create_manifest.py` | Skill (external) | Phase 6 — rewrite `theme.json` writer to emit new `assets:` schema with `schema_version: 1`, display-form keys, top-level `image_sizes`, optional `description`. Mirror `assets/ShipThemes/Federation/theme.json` shape. |
| `.agents/skills/codex-ship-theme-creator/scripts/validate_theme.py` | Skill (external) | Phase 6 — update validator: read `assets:` (not `images:`), accept `.png` 2048×2048 (not `.jpg` 1024×1024), use `SHIP_CLASSES_WITH_VISUAL_THEMES` from `game.core.ship_classes` as the canonical key set. |
| `.agents/skills/codex-ship-theme-creator/scripts/theme_common.py` | Skill (external; READ-ONLY) | Phase 6 — already updated by PROJ-314 commit `0bbf9c36d`. Use as reference for the migrated shape. |
| `tests/unit/tools/test_codex_ship_theme_creator_skill.py` | Test (NEW) | Phase 6 - TDD coverage for the repo-local skill scripts: manifest schema generation, validator acceptance of new schema, and validator rejection of legacy `images:` schema. |
| `Projects/active_projects/PROJ-318/plan.md` | Tracking | Phase 6 closeout — flip Current State to `Complete`. |
| `Projects/projects_index.md` | Tracking | Phase 6 closeout — bump status to `Complete`. |
