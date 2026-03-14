# PROJ-196: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-24 | Project initialized | Starting point for Consolidate Duplicated Code |
| 2026-02-24 | Drop ValidationResult production code refactor | All game/ code already uses factory methods. The duplication report counted factory implementations themselves and 2 unrelated classes in simulation_tests/. |
| 2026-02-24 | Still clean up 7 test ValidationResult constructor calls | User preference for consistency in test mocks. |
| 2026-02-24 | New `game/ui/fonts.py` module (not UIConfig or colors.py) | Dedicated module matches `game/ui/colors.py` pattern. UIConfig is layout-only. Colors module shouldn't own font logic. |
| 2026-02-24 | Two font APIs: `get_font()` + `get_default_font()` | `pygame.font.SysFont("Arial", N)` and `pygame.font.Font(None, N)` produce visually different fonts. Cannot consolidate to single API. |
| 2026-02-24 | Remove FONT_MAIN from colors.py entirely (no re-export) | Per project migration policy: eradicate old patterns completely. |
| 2026-02-24 | TestLabTheme as separate `test_lab/theme.py` module | Test Lab has ~80 colors forming a cohesive dark theme. Too many for colors.py. Creates extensible pattern for other screens. |
| 2026-02-24 | Only 6 new constants in colors.py | TEXT_LIGHT, TEXT_MUTED, TEXT_DIM, PANEL_BG, BORDER_LIGHT, BORDER_DARK — appear in 5+ non-test-lab files. |
| 2026-02-24 | Leave scripts/ fonts/colors as-is | Standalone visual test scripts, not production code. |
| 2026-02-24 | Leave simulation_tests ValidationResult classes untouched | schema_validator.ValidationResult and scenarios/validation.ValidationResult are completely different classes with different interfaces. |
| 2026-02-24 | Preserve research_renderer quantization wrapper | Continuous zoom could create unbounded font entries. Wrapper stays as `_get_font()` but delegates caching to central `get_font()`. |
