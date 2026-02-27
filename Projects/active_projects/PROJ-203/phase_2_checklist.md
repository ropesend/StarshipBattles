# Phase 2: Extract Star Color Mapping

**Objective:** Extract the 5-branch color classification chain to a pure function.

**Target:** `game/ui/screens/strategy_renderer.py` lines 344-354

---

## Implementation

- [ ] **2.1** Add new method `_get_star_asset_key` to `StrategyRenderer` class
  - Location: After line ~375 (after `_draw_systems`)
  - Signature: `def _get_star_asset_key(self, color: tuple) -> str:`
  - Docstring: Document that evaluation order matters (white before orange)
  ```python
  def _get_star_asset_key(self, color: tuple) -> str:
      """Map star RGB color to asset key for star image loading.

      IMPORTANT: Evaluation order matters - conditions overlap.
      White check must come before orange check.

      Args:
          color: RGB tuple (r, g, b) with values 0-255

      Returns:
          Asset key: 'yellow', 'red', 'blue', 'white', or 'orange'
      """
      r, g, b = color[0], color[1], color[2]
      if r > 200 and g < 100:
          return 'red'
      elif b > 200 and r < 100:
          return 'blue'
      elif r > 200 and g > 200 and b > 200:
          return 'white'
      elif r > 200 and g > 150:
          return 'orange'
      return 'yellow'
  ```

- [ ] **2.2** Replace inline code in `_draw_systems` with method call
  - Remove lines 344-353 (the if/elif chain)
  - Replace with: `asset_key = self._get_star_asset_key(star.color)`
  - Keep the `color = star.color` line for fallback circle usage

---

## Verification

- [ ] **2.3** Run star color tests: `pytest tests/unit/ui/test_star_color_mapping.py -v`
- [ ] **2.4** Run renderer tests: `pytest tests/unit/ui/screens/test_strategy_renderer.py -v`
- [ ] **2.5** Measure complexity: `radon cc game/ui/screens/strategy_renderer.py -s -a`
  - Expected `_draw_systems` CC: ~25 (down from 29)

---

## Completion Criteria

- New `_get_star_asset_key` method added
- `_draw_systems` calls the new method
- All tests pass
- CC reduced by ~4
