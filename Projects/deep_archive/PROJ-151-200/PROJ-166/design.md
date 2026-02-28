# PROJ-166: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Current State
BaseGallery was extracted in PROJ-108 Phase 6 from RacePortraitGallery and RaceFlagGallery. RaceThemeGallery was missed and remains a standalone class with 4 duplicated methods.

### Gallery Inheritance Tree (Before)
```
BaseGallery (ABC)                     RaceThemeGallery (standalone)
├── RacePortraitGallery ✓             ├── _sanitize_object_id (DUPLICATE)
└── RaceFlagGallery ✓                 ├── handle_button_click (DUPLICATE)
                                      ├── set_from_config (DUPLICATE)
                                      └── on_theme_selected (DUPLICATE of on_asset_selected)
```

### Gallery Inheritance Tree (After)
```
BaseGallery (ABC)
├── RacePortraitGallery ✓
├── RaceFlagGallery ✓
└── RaceThemeGallery ✓ (NEW)
    ├── overrides _create_content (no label, no preview panel)
    ├── overrides _populate_gallery (vertical list, not image grid)
    └── overrides _discover_assets (ShipThemeManager, not filesystem)
```

### Key Incompatibilities Identified
1. **Layout:** BaseGallery hardcodes Label + PreviewPanel + ScrollContainer. Theme gallery only needs ScrollContainer.
2. **Button style:** BaseGallery uses image-overlay grid buttons. Theme gallery uses text-labeled list buttons.
3. **Data structure:** BaseGallery stores 3-tuples `(btn, img, id)`. Theme gallery uses 2-tuples `(btn, id)`.
4. **Asset discovery:** BaseGallery expects `List[Tuple[str, Surface]]`. Theme gallery returns `List[Tuple[str, Dict[str, Surface]]]`.

## Swarm Findings Summary

### Architecture
- `_create_content()` is a concrete method, not abstract — can be overridden by subclasses
- `_populate_gallery()` is also concrete and overridable
- The `img` element in the 3-tuple is **write-only**: created during `_populate_gallery`, never read by any code anywhere. Tests confirm with `MagicMock()` placeholders that are never asserted.
- RaceSetupScreen never directly accesses `theme_buttons`, `theme_scroll`, or calls `on_theme_selected` — it only uses the public API (`handle_button_click`, `set_from_config`, constructor callback).

### Key Patterns to Reuse
- **RacePortraitGallery**: `game/ui/panels/race_portrait_gallery.py` — exemplar for "extend BaseGallery" pattern. ~150 lines. Sets up subclass-specific state before `super().__init__()`.
- **RaceFlagGallery**: `game/ui/panels/race_flag_gallery.py` — same pattern, 163 lines.

### Dependencies & Risks
1. **2-tuple normalization touches 3 files**: base_gallery.py + 2 test files. LOW risk — purely structural, no behavioral change.
2. **_discover_assets return type mismatch**: RaceThemeGallery returns `Dict[str, Surface]` per theme instead of a single Surface. Since `_populate_gallery` is also overridden, the type mismatch never reaches BaseGallery code. Acceptable.
3. **Test mock setup**: Tests bypass `__init__` with `patch.object`. After refactoring, tests may need additional attributes set up (e.g., `_asset_loader`, `preview_panel`) since `on_asset_selected` now comes from BaseGallery. RaceThemeGallery's `_update_preview` is a no-op, so this is low risk.

### Opportunities Discovered
- After this project, ALL gallery panels follow the same BaseGallery contract, making future gallery types trivial to add.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.

### Key Decision: Normalize to 2-Tuples (Option B)
The UIImage overlay stored in `asset_buttons` 3-tuples is write-only. No code ever reads it after creation. The image is a rendering artifact of `_populate_gallery`, not part of the selection contract. Clean-sheet design stores only what the selection logic needs: `(button, asset_id)`.

### Key Decision: Override _create_content, Don't Modify It
Rather than adding flags/conditionals to BaseGallery's `_create_content` for "no label" or "no preview", RaceThemeGallery simply overrides the entire method. This is cleaner — BaseGallery's default layout is correct for image-grid galleries, and theme gallery's override provides its own layout. No base class changes needed for layout flexibility.
