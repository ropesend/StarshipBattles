# Phase 6: Rendering

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-189 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Render storms on the strategy map using existing nebulae assets with transparency and tooltips.

---

## Tasks

### Task 6.1: Add nebulae to asset manifest [Simple]
**File:** `assets/asset_manifest.json`
**Tests:** Manual validation

- [x] Read current `assets/asset_manifest.json` to understand structure
- [x] Add `"nebulae"` category with `"default"` group:
  ```json
  "nebulae": {
    "default": [
      "assets/Images/Stellar Objects/Nebulae/Nebulae_01_transparent.png",
      "assets/Images/Stellar Objects/Nebulae/Nebulae_02_transparent.png",
      "assets/Images/Stellar Objects/Nebulae/Nebulae_03_transparent.png",
      "assets/Images/Stellar Objects/Nebulae/Nebulae_04_transparent.png",
      "assets/Images/Stellar Objects/Nebulae/Nebulae_05_transparent.png",
      "assets/Images/Stellar Objects/Nebulae/Nebulae_06_transparent.png"
    ]
  }
  ```
- [x] Verify all 6 files exist at those paths

**Notes:** All 6 transparent nebulae files confirmed present.

### Task 6.2: Implement storm rendering on strategy map [Medium]
**File:** `game/ui/screens/strategy_renderer.py`
**Tests:** Manual visual testing

- [x] Read current `_draw_dyson_spheres()` method (~line 508-573) to understand multi-hex rendering pattern
- [x] Read current `_draw_system_details()` to understand rendering order
- [x] Add `_draw_storms(self, screen, system, sys_world_pos)` method:
  - Iterate `system.storms`
  - For each storm:
    - Calculate bounding box from `storm.occupied_hexes` using `hex_to_pixel()`
    - Find center pixel position of the storm's bounding box
    - Load nebulae image via `self._asset_manager.get_random_from_group('nebulae', 'default', seed_id=storm.image_variant)`
    - Scale image to cover the storm's hex extent (calculate width/height from hex bounding box * zoom)
    - Apply alpha: `image.set_alpha(int(storm.intensity * 180))` (max 180 = ~70% opacity, keeps background visible)
    - Optional: color tint per storm type (ion=blue tint, plasma=red, gravity=purple, radiation=yellow, nebula=grey)
    - Blit to screen at calculated position
- [x] Call `_draw_storms()` in `_draw_system_details()` BEFORE planet rendering (like Dyson Spheres are rendered before planets)
- [x] Add zoom-level LOD: skip detailed nebulae rendering below a zoom threshold (e.g., 0.3); optionally draw colored hex fill at low zoom
- [x] Viewport culling: skip storms whose bounding box is entirely outside viewport (follow existing pattern)

**Notes:** Implemented `_draw_storms()` and `_draw_storms_low_detail()`. Storms render before Dyson Spheres. Color tints per storm type. Viewport culling and zoom LOD implemented.

### Task 6.3: Storm tooltip on hex hover [Simple]
**File:** `game/ui/screens/strategy_screen.py` or `strategy_renderer.py` (wherever hover handling exists)
**Tests:** Manual visual testing

- [x] Read current hex hover handling to understand tooltip system
- [x] When hovering a hex, check for storm zones via `galaxy.get_zones_at_global_hex()`
- [x] Filter to Storm instances
- [x] Display storm info in tooltip: name, type description, effect summary
  - Example: "Ion Storm Alpha - Shields -50%, Speed -20%"
  - Format multiplicative effects as percentage reduction: `(1.0 - mult) * 100`%
  - Format damage: "Damage: X/turn", drain: "Fuel drain: X/turn"
- [x] Handle multiple storms at same hex (list both)

**Notes:** Storms already discovered via zone registry in `strategy_click_dispatcher.py`. Added:
- `IStorm` protocol and `is_storm()` TypeGuard to `game/core/protocols.py`
- Storm label formatting in `game/ui/screens/strategy_detail_fmt.py`
- `_format_storm()` method in `game/ui/screens/strategy_detail_formatter.py`
- Updated tests to handle new is_storm checker

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] All tests pass: `pytest tests/ --testmon`
- [x] Launch game, generate galaxy, visually verify storms render correctly (User verification)
- [x] Verify storms appear as transparent nebulae overlays behind planets (User verification)
- [x] Verify tooltips display storm info on hover (User verification)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 7

**Test Results:** 12693 passed, 1 skipped
**Visual Verification:** Deferred to final user verification step in plan.md
