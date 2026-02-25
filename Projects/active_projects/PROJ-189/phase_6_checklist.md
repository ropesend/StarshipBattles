# Phase 6: Rendering

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-189 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Render storms on the strategy map using existing nebulae assets with transparency and tooltips.

---

## Tasks

### Task 6.1: Add nebulae to asset manifest [Simple]
**File:** `assets/asset_manifest.json`
**Tests:** Manual validation

- [ ] Read current `assets/asset_manifest.json` to understand structure
- [ ] Add `"nebulae"` category with `"default"` group:
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
- [ ] Verify all 6 files exist at those paths

**Notes:**

### Task 6.2: Implement storm rendering on strategy map [Medium]
**File:** `game/ui/screens/strategy_renderer.py`
**Tests:** Manual visual testing

- [ ] Read current `_draw_dyson_spheres()` method (~line 508-573) to understand multi-hex rendering pattern
- [ ] Read current `_draw_system_details()` to understand rendering order
- [ ] Add `_draw_storms(self, screen, system, sys_world_pos)` method:
  - Iterate `system.storms`
  - For each storm:
    - Calculate bounding box from `storm.occupied_hexes` using `hex_to_pixel()`
    - Find center pixel position of the storm's bounding box
    - Load nebulae image via `self._asset_manager.get_random_from_group('nebulae', 'default', seed_id=storm.image_variant)`
    - Scale image to cover the storm's hex extent (calculate width/height from hex bounding box * zoom)
    - Apply alpha: `image.set_alpha(int(storm.intensity * 180))` (max 180 = ~70% opacity, keeps background visible)
    - Optional: color tint per storm type (ion=blue tint, plasma=red, gravity=purple, radiation=yellow, nebula=grey)
    - Blit to screen at calculated position
- [ ] Call `_draw_storms()` in `_draw_system_details()` BEFORE planet rendering (like Dyson Spheres are rendered before planets)
- [ ] Add zoom-level LOD: skip detailed nebulae rendering below a zoom threshold (e.g., 0.3); optionally draw colored hex fill at low zoom
- [ ] Viewport culling: skip storms whose bounding box is entirely outside viewport (follow existing pattern)

**Notes:** The rendering should layer: grid -> warp lanes -> storm nebulae -> Dyson Spheres -> planets -> warp points -> fleets. This ensures storms appear behind all entities but in front of the grid.

### Task 6.3: Storm tooltip on hex hover [Simple]
**File:** `game/ui/screens/strategy_screen.py` or `strategy_renderer.py` (wherever hover handling exists)
**Tests:** Manual visual testing

- [ ] Read current hex hover handling to understand tooltip system
- [ ] When hovering a hex, check for storm zones via `galaxy.get_zones_at_global_hex()`
- [ ] Filter to Storm instances
- [ ] Display storm info in tooltip: name, type description, effect summary
  - Example: "Ion Storm Alpha - Shields -50%, Speed -20%"
  - Format multiplicative effects as percentage reduction: `(1.0 - mult) * 100`%
  - Format damage: "Damage: X/turn", drain: "Fuel drain: X/turn"
- [ ] Handle multiple storms at same hex (list both)

**Notes:** The tooltip implementation depends on the existing tooltip/hover system. Read the code first to understand how planet/star tooltips work.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All tests pass: `pytest tests/ --testmon`
- [ ] Launch game, generate galaxy, visually verify storms render correctly
- [ ] Verify storms appear as transparent nebulae overlays behind planets
- [ ] Verify tooltips display storm info on hover
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 7
