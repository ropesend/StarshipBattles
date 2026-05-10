# Phase 4: Extract Star Rendering & Verify

**Objective:** Extract per-star rendering to a helper method and verify final CC is below 20.

**Target:** `game/ui/screens/strategy_renderer.py` lines 340-373 (star loop body)

---

## Implementation

- [x] **4.1** Add new method `_draw_star` to `StrategyRenderer` class
  - Location: After `_draw_colony_marker` (from Phase 3)
  - Signature: `def _draw_star(self, screen, star, system_center, system_name, is_primary, is_selected_system):`
  ```python
  def _draw_star(self, screen, star, system_center, system_name, is_primary, is_selected_system):
      """Render a single star with image, selection highlight, and label.

      Args:
          screen: pygame.Surface to draw on
          star: Star object to render
          system_center: (hx, hy) tuple - system center in world pixels
          system_name: str - name of the parent system (for primary star label)
          is_primary: bool - whether this is the primary star
          is_selected_system: bool - whether the parent system is selected
      """
      hx, hy = system_center
      local_pixel_x, local_pixel_y = hex_to_pixel(star.location, self.hex_size)
      star_screen_pos = self.camera.world_to_screen(
          pygame.math.Vector2(hx + local_pixel_x, hy + local_pixel_y)
      )

      asset_key = self._get_star_asset_key(star.color)
      star_img = self._asset_manager.load_image('stars', asset_key)
      screen_star_r = max(3, int(star.diameter_hexes * self.hex_size * self.camera.zoom))

      # Selection highlight (before star image)
      if is_selected_system and is_primary:
          pygame.draw.circle(screen, WHITE, star_screen_pos, screen_star_r + 4, 1)

      # Star image or fallback
      if star_img:
          scaled_img = pygame.transform.smoothscale(star_img, (screen_star_r * 2, screen_star_r * 2))
          dest_rect = scaled_img.get_rect(center=(int(star_screen_pos.x), int(star_screen_pos.y)))
          screen.blit(scaled_img, dest_rect)
      else:
          pygame.draw.circle(screen, star.color, star_screen_pos, screen_star_r)

      # Label at high zoom
      if self.camera.zoom >= 0.5:
          font_size = 12 if is_primary else 10
          font = self._get_font(font_size)
          label_text = system_name if is_primary else star.name
          text = font.render(label_text, True, STAR_LABEL)
          screen.blit(text, (star_screen_pos.x + 10, star_screen_pos.y))
  ```

- [x] **4.2** Replace star loop body in `_draw_systems` with method call
  - Keep the `for star in sys.stars:` loop
  - Replace loop body (lines 341-373) with:
  ```python
  for star in sys.stars:
      is_primary = star == primary
      is_selected_system = self.scene.selected_object == sys
      self._draw_star(screen, star, (hx, hy), sys.name, is_primary, is_selected_system)
  ```

---

## Final `_draw_systems` Structure

After all extractions, `_draw_systems` should look like:
```python
def _draw_systems(self, screen):
    """Draw all star systems with stars, planets, and warp points."""
    tl = self.camera.screen_to_world((0, 0))
    br = self.camera.screen_to_world((self.screen_width, self.screen_height))

    margin = 600
    min_x, max_x = min(tl.x, br.x) - margin, max(tl.x, br.x) + margin
    min_y, max_y = min(tl.y, br.y) - margin, max(tl.y, br.y) + margin

    for sys in self.galaxy.systems.values():
        hx, hy = hex_to_pixel(sys.global_location, self.hex_size)
        world_pos = pygame.math.Vector2(hx, hy)

        if not (min_x < world_pos.x < max_x and min_y < world_pos.y < max_y):
            continue

        # Colony marker at low zoom
        self._draw_colony_marker(screen, sys, world_pos)

        # Stars
        primary = sys.primary_star
        if primary:
            for star in sys.stars:
                is_primary = star == primary
                is_selected = self.scene.selected_object == sys
                self._draw_star(screen, star, (hx, hy), sys.name, is_primary, is_selected)

        # System details at high zoom
        if self.camera.zoom >= 0.5:
            self._draw_system_details(screen, sys, world_pos)
```

---

## Verification

- [x] **4.3** Run star tests: `pytest tests/unit/ui/screens/test_strategy_renderer.py -v -k "star"` (3 passed)
- [x] **4.4** Run full renderer tests: `pytest tests/unit/ui/screens/test_strategy_renderer.py -v` (47 passed)
- [x] **4.5** Run full test suite: `pytest tests/ -n 12` (12743 passed, 1 skipped)
- [x] **4.6** Measure final complexity: CC 7 (target was <20)
  - **Required:** `_draw_systems` CC below 20
  - Expected: CC 16-18

---

## Final Verification

- [x] **4.7** Verify all new methods have correct signatures
- [x] **4.8** Verify no behavioral changes (same render output) - all tests pass
- [x] **4.9** Commit with message: `[PROJ-203] Phase 4: Extract _draw_star() helper - CC 29 -> 7` (b07b7c8f)

---

## Completion Criteria

- `_draw_star` method added and called
- `_draw_systems` CC below 20
- All tests pass
- Changes committed
