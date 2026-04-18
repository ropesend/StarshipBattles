# Phase 3: Migrate Asset Path References

## Goal
Replace all hardcoded `"assets/..."` paths in production code with `Paths` constants.

## Files to Migrate

### Sprites / Component Images
- [ ] `game/ui/renderer/sprites.py:38` — `os.path.join(base_path, "assets", "Images", "Components")` → `Paths.COMPONENTS_IMAGES_DIR`
  - [ ] Write test
  - [ ] Update code
  - [ ] Run tests

### Resource Portraits (2 files, same path)
- [ ] `game/ui/panels/build_queue_portraits.py:200` — `os.path.join("assets", "Images", "Resource Portraits")` → `Paths.RESOURCE_PORTRAITS_DIR`
- [ ] `game/ui/panels/planet_report_panel.py:447` — `os.path.join("assets", "Images", "Resource Portraits")` → `Paths.RESOURCE_PORTRAITS_DIR`
  - [ ] Write tests
  - [ ] Update both files
  - [ ] Run tests

### Ship Theme Portraits & Skins (3 files, same pattern)

These files build paths like `os.path.join("assets", "ShipThemes", theme, "Portraits", filename)`. The fix is to use `Paths.SHIP_THEMES_DIR` as the base:
```python
# Before
os.path.join("assets", "ShipThemes", theme, "Portraits", filename)
# After
os.path.join(Paths.SHIP_THEMES_DIR, theme, "Portraits", filename)
```

- [ ] `game/ui/screens/design_image_helper.py:71-73` — 3 path constructions using `"assets"` base
- [ ] `game/ui/screens/design_image_helper.py:157` — skin path using `"assets"` base
  - [ ] Write tests
  - [ ] Update code
  - [ ] Run tests

- [ ] `game/ui/utils/portraits.py:108-111` — portrait paths using `"assets"` base
  - [ ] Write test
  - [ ] Update code
  - [ ] Run tests

- [ ] `game/ui/screens/builder/right_panel.py:251-260` — 3 path constructions using `"assets"` base
  - [ ] Write test
  - [ ] Update code
  - [ ] Run tests

### Default Ship Portrait
- [ ] `game/ui/screens/design_image_helper.py:73` — `os.path.join("assets", "Images", "Default_Ship_Portrait.png")` → `Paths.DEFAULT_SHIP_PORTRAIT`
- [ ] `game/ui/utils/portraits.py:111` — same path → `Paths.DEFAULT_SHIP_PORTRAIT`
- [ ] `game/ui/screens/builder/right_panel.py:260` — same path → `Paths.DEFAULT_SHIP_PORTRAIT`
  - [ ] Update all 3 files
  - [ ] Run tests

### Game Config
- [ ] `game/strategy/engine/game_config.py:24` — `os.path.join(project_root, "assets", "ShipThemes")` → `Paths.SHIP_THEMES_DIR`
  - [ ] Write test
  - [ ] Update code
  - [ ] Run tests

## Verify
- [ ] Run full test suite
- [ ] Grep for remaining `"assets"` hardcodes in `game/` (excluding test files)
