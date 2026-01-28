# PROJ-40: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-27 | Project initialized | Starting point for Comprehensive Code Quality Remediation |
| 2026-01-27 | Address all 108 new issues plus 3 remaining original findings in single project | Comprehensive approach ensures nothing overlooked; phased structure allows incremental progress |
| 2026-01-27 | Organize into 11 phases following architectural layers | Critical fixes first to unblock other work; layer-by-layer respects dependency direction |
| 2026-01-27 | Create UI-facing service interfaces rather than direct entity access | UI layer should not know about internal entity structure; enables future UI framework changes |
| 2026-01-27 | Plan god class decomposition but implement incrementally | Full decomposition of Ship (793 lines) and AIController (385 lines) too large for one phase |
| 2026-01-28 | RaceSetupScreen (1227 lines) - No further decomposition needed | PROJ-12 Phase 4 already extracted 8 components. Remaining code is primarily coordination logic that belongs in the screen class. See detailed analysis below. |

---

## RaceSetupScreen Decomposition Analysis (Task 12.16)

**File:** `game/ui/screens/race_setup_screen.py`
**Size:** 1,227 lines, 36 methods
**Prior Work:** PROJ-12 Phase 4 extracted 8 components

### Already Extracted Components (PROJ-12 Phase 4)

| Component | Location | Description |
|-----------|----------|-------------|
| RaceEnvironmentPanel | `game/ui/panels/race_environment_panel.py` | Environment sliders/controls |
| RaceDescriptionPanel | `game/ui/panels/race_description_panel.py` | Bio/socio text editing |
| RaceFlagGallery | `game/ui/panels/race_flag_gallery.py` | Flag thumbnail selection |
| RacePortraitGallery | `game/ui/panels/race_portrait_gallery.py` | Portrait thumbnail selection |
| RaceThemeGallery | `game/ui/panels/race_theme_gallery.py` | Ship theme selection |
| RaceBrowserDialog | `game/ui/screens/race_browser_dialog.py` | Save/load dialog |
| RaceValidator | `game/ui/screens/race_validator.py` | Validation logic |
| RaceAssetLoader | `game/ui/screens/race_asset_loader.py` | Asset loading utilities |

### Remaining Code Analysis

| Method Group | Lines | Purpose | Extract? |
|--------------|-------|---------|----------|
| `__init__`, `_create_ui` | ~80 | Window setup | No - coordination |
| `_create_tab_buttons`, `_create_step_panels` | ~70 | Tab structure | No - coordination |
| `_create_summary_panel_content`, `_refresh_summary` | ~200 | Summary UI | Maybe - large |
| `_create_ships_panel_content`, `_refresh_ship_preview` | ~130 | Ship preview | Maybe - large |
| `_create_visuals_panel_content` | ~50 | Visuals setup | No - uses extracted galleries |
| `_create_environment_panel_content` | ~20 | Env setup | No - uses extracted panel |
| `_create_descriptions_panel_content` | ~20 | Desc setup | No - uses extracted panel |
| Tab navigation methods | ~80 | Tab switching | No - coordination |
| Event handling | ~60 | User events | No - coordination |
| Callback handlers | ~50 | Save/load/cancel | No - coordination |

### Candidates for Extraction

1. **`RaceSummaryPanel`** (~200 lines)
   - `_create_summary_panel_content()` (lines 573-767)
   - `_refresh_summary()` (lines 768-975)
   - Self-contained UI for the summary/landing tab

2. **`RaceShipPreview`** (~130 lines)
   - `_create_ships_panel_content()` (lines 318-364)
   - `_refresh_ship_preview()` (lines 365-457)
   - `_load_ship_portrait()` (lines 458-499)

### Recommendation: No Extraction Needed

**Rationale:**
1. Prior decomposition (PROJ-12) already extracted 8 domain-specific components
2. Remaining code is primarily:
   - Tab/panel **coordination** (belongs in screen class)
   - **Glue code** connecting extracted components
   - **Event routing** to child components
3. Summary panel is large but doesn't have complex internal logic - mostly layout
4. Ship preview is self-contained but tightly coupled to RaceConfig state
5. Further extraction would create minimal benefit while adding indirection complexity

**If extraction is desired in future:**
- Extract `RaceSummaryPanel` as lowest-risk option
- Would reduce RaceSetupScreen by ~200 lines
- Benefits: Cleaner separation, easier testing
- Costs: Need to pass RaceConfig changes via events/callbacks
