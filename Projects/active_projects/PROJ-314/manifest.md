# PROJ-314 File Manifest

> Generated during /claude-proj-start. Used by /claude-proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| `game/ui/assets/ship_theme_manager.py` | Production | Phase 3 — full rewrite. Read `assets:` schema from theme.json; delete `_load_portrait_image()` hardcoded convention; delete `_ship_class_to_portrait_name()`; unify `get_portrait_image()` return contract; use `Paths.SHIP_THEMES_DIR`. |
| `game/core/ship_classes.py` | Production (NEW) | Phase 1 — `SHIP_CLASSES_WITH_VISUAL_THEMES` frozenset (19 entries) as canonical key set. |
| `game/core/paths.py` | Production | Phase 1 — add `SHIP_THEMES_TARGET_SIZE = 2048`. |
| `game/ui/screens/design_image_helper.py` | Production | Phase 5 — delete hardcoded portrait-path construction at lines 72-74; route through `ShipThemeManager.get_portrait_image()`. |
| `game/ui/screens/builder/right_panel.py` | Production | Phase 5 — delete hardcoded portrait-path construction at lines 262-263; route through `ShipThemeManager`. |
| `game/ui/utils/portraits.py` | Production | Phase 5 — delete hardcoded fallback-search-path construction at lines 98-114; route through `ShipThemeManager`. |
| `.agents/skills/codex-ship-theme-creator/scripts/theme_common.py` | Production (external skill) | Phase 5 — update `load_manifest` at line 31 to read new `assets:` schema. |
| `game/ui/services/image/__init__.py` | Production (NEW) | Phase 2 — new image-generation service package. |
| `game/ui/services/image/provider.py` | Production (NEW) | Phase 2 — `ImageProvider` Protocol + `ImageResult` dataclass + `ImageException` hierarchy. |
| `game/ui/services/image/openai_provider.py` | Production (NEW) | Phase 2 — `OpenAIImageProvider` (gpt-image-2). Reads `OPENAI_API_KEY` env-var per-request. Retry-on-5xx with exponential backoff. |
| `game/ui/services/image/null_provider.py` | Production (NEW) | Phase 2 — `NullImageProvider` raises on `generate_image()`. Default in tests; default in prod when `OPENAI_API_KEY` absent. |
| `game/ui/services/image/factory.py` | Production (NEW) | Phase 2 — `ImageProviderFactory` with `register_image_provider()` + env-var dispatch (`IMAGE_PROVIDER`, default "openai"). |
| `game/ui/services/image/defaults.py` | Production (NEW) | Phase 2 — `get_default_image_provider()` / `set_default_image_provider()` module-level singleton accessors. |
| `game/ui/services/image/types.py` | Production (NEW) | Phase 2 — `ImageResult`, `ImageException` codes. |
| `game/ui/services/image/background.py` | Production (NEW) | Phase 2 — `ImageBackgroundCall` threaded wrapper, mirrors `LLMBackgroundCall`. |
| `game/context.py` | Production | Phase 2 — wire `ImageProvider` into `ApplicationContext.create_production()` and `create_test()`. |
| `Tools/regenerate_ship_portraits/cli.py` | Tool (NEW) | Phase 4 — CLI driver with `--theme`, `--ship-class`, `--dry-run`, `--force`, `--cost-cap`, `--model`, `--size`, `--batch`, `--list-themes`, `--list-classes`, `--verbose`. |
| `Tools/regenerate_ship_portraits/audit.py` | Tool (NEW) | Phase 4 — audit script reporting per-theme schema/coverage/casing/size. |
| `Tools/regenerate_ship_portraits/prompts/` | Tool (NEW) | Phase 4 — prompt templates for AI portrait generation, parametrised by theme+ship class. |
| `Tools/regenerate_ship_portraits/last_run.json` | Tool (NEW; gitignored) | Phase 4 — manifest of generation requests/responses for traceability. |
| `assets/ShipThemes/Aetherwake/theme.json` | Data | Phase 5 — migrate to new schema; declare 19 portraits (to be generated in Phase 4). |
| `assets/ShipThemes/Aetherwake/Portraits/*.png` (19) | Data (NEW) | Phase 4 — AI-generated via `gpt-image-2`. |
| `assets/ShipThemes/Aetherwake/Skins/*.png` | Data | Phase 5 — already lowercase_with_underscores; verify only. |
| `assets/ShipThemes/Atlantians/theme.json` | Data | Phase 5 — migrate to new schema; fix `heavey cruiser.png` typo. |
| `assets/ShipThemes/Atlantians/Skins/*.png` | Data | Phase 5 — normalise filenames; rename typo. |
| `assets/ShipThemes/Atlantians/Portraits/*.png` | Data | Phase 4 — re-encode existing 18 `.jpg` to `.png`; generate Light Cruiser portrait. |
| `assets/ShipThemes/Federation/theme.json` | Data | Phase 5 — migrate to new schema with display-form keys; declare portraits. |
| `assets/ShipThemes/Federation/Skins/*.png` | Data | Phase 5 — normalise filenames to lowercase_with_underscores. |
| `assets/ShipThemes/Federation/Portraits/*.png` | Data | Phase 4 — re-encode all 19 `.jpg` to `.png`; rename to lowercase. |
| `assets/ShipThemes/Klingons/theme.json` | Data | Phase 5 — migrate to new schema. |
| `assets/ShipThemes/Klingons/Skins/*.png` | Data | Phase 5 — normalise filenames. |
| `assets/ShipThemes/Klingons/Portraits/*.png` | Data | Phase 4 — re-encode 19 `.jpg` to `.png`; rename. |
| `assets/ShipThemes/Ossivine/theme.json` | Data | Phase 5 — migrate to new schema. |
| `assets/ShipThemes/Ossivine/Portraits/*.png` | Data | Phase 4 — re-encode 19 `.jpg` to `.png`; rename. |
| `assets/ShipThemes/Prismsteel/theme.json` | Data | Phase 5 — migrate to new schema. |
| `assets/ShipThemes/Prismsteel/Portraits/*.png` | Data | Phase 4 — re-encode 19 `.jpg` to `.png`; rename. |
| `assets/ShipThemes/Romulans/theme.json` | Data | Phase 5 — migrate to new schema. |
| `assets/ShipThemes/Romulans/Skins/*.png` | Data | Phase 5 — normalise filenames. |
| `assets/ShipThemes/Romulans/Portraits/*.png` | Data | Phase 4 — re-encode 19 `.jpg` to `.png`; rename. |
| `assets/ShipThemes/Voidforged/theme.json` | Data | Phase 5 — migrate to new schema. |
| `assets/ShipThemes/Voidforged/Portraits/*.png` | Data | Phase 4 — re-encode 19 `.jpg` to `.png`; rename. |
| `assets/ShipThemes/Thoraliens/theme.json` | Data | Phase 5 — migrate from CamelCase to display-form keys; fix `super_dread_naught.png` mismatch. |
| `tests/unit/ui/test_ship_theme_logic.py` | Test | Phase 3 — delete `TestShipClassToPortraitName` (4 tests); rewrite `TestGetPortraitImage` (4 tests) for new schema; update mocks. |
| `tests/unit/ui/test_theme_discovery.py` | Test | Phase 3 — update for new `assets:` schema; remove `theme_data['<class>']['path']` assertions in favour of `'skin_path'` / `'portrait_path'`. |
| `tests/unit/ui/services/image/__init__.py` | Test (NEW) | Phase 2 — package marker. |
| `tests/unit/ui/services/image/test_provider.py` | Test (NEW) | Phase 2 — `ImageProvider` Protocol contract test. |
| `tests/unit/ui/services/image/test_factory.py` | Test (NEW) | Phase 2 — registration + dispatch + unknown-provider error. |
| `tests/unit/ui/services/image/test_defaults.py` | Test (NEW) | Phase 2 — module-level singleton accessors. |
| `tests/unit/ui/services/image/test_null_provider.py` | Test (NEW) | Phase 2 — `NullImageProvider` raises on `generate_image()`. |
| `tests/unit/ui/services/image/test_openai_provider.py` | Test (NEW) | Phase 2 — `OpenAIImageProvider` mocked-network behaviour; real-network test marked `@pytest.mark.slow`. |
| `tests/unit/core/test_ship_classes.py` | Test (NEW) | Phase 1 — pin `SHIP_CLASSES_WITH_VISUAL_THEMES` to exactly 19 entries; assert all expected names present. |
| `tests/unit/core/test_paths.py` | Test (existing, extend) | Phase 1 — assert `SHIP_THEMES_TARGET_SIZE == 2048`. |
| `tests/integration/ui/test_race_setup_ships_smoke.py` | Test (NEW) | Phase 5 — every theme renders all 19 ship slots with both skin and portrait surfaces, no fallbacks. |
| `tests/conftest.py` (or similar) | Test | Phase 2 — autouse fixture: assert default image provider is `NullImageProvider` unless explicitly replaced; reset image-provider singleton between tests. |
| `docs/01_ARCHITECTURE.md` | Doc | Phase 6 — add `game/ui/services/image/` to UI services subpackage section + Package Directory Map. |
| `docs/03_CONVENTIONS.md` | Doc | Phase 6 — add canonical `theme.json` schema, naming convention, 2048×2048 standard, lowercase-with-underscores filename rule. |
| `Projects/active_projects/PROJ-314/findings/ship_themes_unified_schema_migration.md` | Findings | Already created in Phase 0. |
| `Projects/active_projects/PROJ-314/findings/assets/*.png` (3) | Findings | Already created in Phase 0 — QA screenshots. |
| `Projects/projects_index.md` | Tracking | Phase C — index entry already added by `create_project.py` script. |
