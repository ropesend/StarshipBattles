# Phase 1: Correctness fixes (R1 + R2 + R3 + R4)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-317 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Eliminate the four functional defects (R1 cross-layer
collision, R2 colour not rendered, R3 threshold lookup wired wrong, R4
missing-state fallback emits 0/0). Each defect ships with a regression
test that fails pre-fix and passes post-fix. Block on full sharded
suite green before flipping to Phase 2.

---

## Tasks

### Task 1.1: R1 — lift `per_id_index` out of the layer loop [Simple]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/test_ship_instance_damage.py tests/unit/strategy/test_ship_instance.py`

- [x] In `iter_all_components_by_layer` (line ~573), move
  `per_id_index: Dict[str, int] = {}` from line 577 (inside the
  `for layer_name, components in self.design_data.get('layers', {}).items():`
  loop) to immediately after `result: Dict[str, List[ComponentInstanceView]] = {}`
  at line 573, **before** the layer loop. The counter must persist
  across all layer iterations.
- [x] Add a regression test in
  `tests/unit/strategy/test_ship_instance_damage.py`
  (`TestIterAllComponentsByLayerCrossLayer` or similar):
  ```python
  def test_iter_keys_match_build_full_hp_keys_for_cross_layer_design():
      """R1: cross-layer instance_index counter must be ship-wide,
      matching `_build_full_hp_components_from_design`."""
  ```
  Use `ship_factory` against a real shared-component design (e.g.
  `qs_battleship`) where `battery` appears in CORE+INNER. Assert:
  `iter_keys = {(iv.component_id, iv.instance_index) for layer in iterator_result.values() for iv in layer}`
  equals
  `built_keys = {(s.component_id, s.instance_index) for s in built_components.values()}`.
- [x] Verify the existing 7 `TestIterAllComponentsByLayer` tests still
  pass.
- [x] Verify: `pytest tests/unit/strategy/test_ship_instance_damage.py`
  green.

**Notes:** Added a direct `qs_battleship` parity test against
`_build_full_hp_components_from_design`; the comparison filters the
implicit materialized hull component because `iter_all_components_by_layer`
intentionally excludes HULL from the panel surface. The checklist named
`tests/unit/strategy/test_ship_instance.py`, which does not exist; used
`tests/unit/strategy/test_ship_instance_damage.py`.

---

### Task 1.2: R2 — apply damage-tier colour to rendered label [Medium]
**File:** `game/ui/panels/ship_detail_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_ship_detail_panel.py`

- [x] **Spike:** confirm pygame_gui's `UILabel` parses `<font color>`
  rich-text in this codebase's version. Find another `UILabel` in
  `game/ui/` that wraps text in `<font color='...'>`, OR test in
  isolation via a small fixture. Document the result in **Notes**
  below.
- [x] In `_build_instance_row` (line ~556), after computing `color`
  and `strike`, format the colour as a `#rrggbb` hex string and wrap
  the text:
  ```python
  hex_color = "#{:02x}{:02x}{:02x}".format(*color[:3])
  display_text = (
      f"      • {group.display_name} #{inst.instance_index + 1}  "
      f"{int(round(hp_pct * 100))}%"
  )
  text = f"<font color='{hex_color}'>{display_text}</font>"
  label = UILabel(
      relative_rect=pygame.Rect(x + 25, y, width - 40, 22),
      text=text,
      manager=self.manager,
      container=self.scroll_container,
  )
  ```
  If the spike showed `<font color>` doesn't render, fall back to
  `label.set_text_colour(color)` after construction. If neither path
  works, escalate to a `UITextBox` swap (heavier; document in
  decisions.md).
- [x] In `_apply_strikethrough` (line ~598), accept the colour as a
  parameter and use it for the line colour. Replace the hard-coded
  `(220, 220, 220)`. Update call site at line ~594:
  ```python
  if strike:
      self._apply_strikethrough(label, color)
  ```
- [x] Keep `label._proj315_color = color` and
  `label._proj315_strike = strike` for now — Phase 3 retires them.
  (The legacy widget tests assert against these.)
- [x] Add a new regression test in
  `tests/unit/ui/panels/test_ship_detail_panel.py`
  (`TestInstanceRowColorRendered` or similar):
  ```python
  def test_instance_row_label_renders_in_chosen_colour():
      """R2: colour tier must reach the rendered label, not just sit
      on the test attribute."""
  ```
  Build a fixture ship with one healthy and one destroyed component.
  Render the panel, expand the relevant layer + group, retrieve the
  destroyed instance's label. Assert the label's rendered text or
  styling tree contains the `HP_DESTROYED` colour. **Do not read
  `_proj315_color`.** Approach options in priority:
  1. Inspect `label.text_box_layout` (or equivalent in this
     pygame_gui version) for the parsed text run's colour attribute.
  2. Render the label to a surface and pixel-sample at a known glyph
     position; assert the pixel is in the expected colour band
     (allowing 8-bit anti-alias slop).
  3. Hybrid: assert `<font color='#hexcolor'>` substring is in the
     label's `text` attribute (shallow but ensures colour reached
     pygame_gui's text-parser layer).
  Pick the deepest that's stable in this version.
- [x] Verify: targeted test runs green; new R2 test passes; existing
  widget tests still pass.

**Notes:** `UILabel.set_text()` explicitly does not support HTML markup in
this pygame_gui version, and the element has no `set_text_colour()` method.
The stable rendered path is assigning `label.text_colour = pygame.Color(*color)`
and calling `label.rebuild()`. The new regression asserts `UILabel.text_colour`
for the rendered label and does not read `_proj315_color`; existing PROJ-315
tests still read the private attributes pending the deferred Phase 3 seam
cleanup.

---

### Task 1.3: R3 — fix threshold lookup wiring [Simple]
**File:** `game/ui/panels/ship_detail_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_ship_detail_panel.py -k threshold`

- [x] In `_resolve_threshold_lookup` (line ~443), change the import
  path from `game.context` to `game.core.registry`:
  ```python
  from game.core.registry import get_default_registry_provider
  provider = get_default_registry_provider()
  components: Dict[str, Any] = provider.get_components()
  ```
- [x] Replace `provider.get_component_registry()` (non-existent
  method) with `provider.get_components()` (returns `Dict[str, Any]`
  keyed by component id).
- [x] Update the inner `lookup` callable to read from the dict:
  ```python
  def lookup(comp_id: str) -> float:
      comp = components.get(comp_id)
      if comp is None:
          return default
      return float(getattr(comp, 'damage_threshold', default))
  ```
- [x] (Optional) Narrow `except Exception` to
  `(ImportError, AttributeError, RuntimeError)`. Keep the
  `# Intentional broad catch:` comment if narrowing proves
  insufficient during testing.
- [x] Add a new regression test in
  `tests/unit/ui/panels/test_ship_detail_panel.py`:
  ```python
  def test_resolve_threshold_lookup_uses_per_component_value():
      """R3: production path must surface per-component
      damage_threshold, not always default."""
  ```
  Three sub-assertions:
  1. With a real ApplicationContext + a registry component whose
     `damage_threshold` is e.g. 0.7, the returned callable returns
     0.7 for that component_id.
  2. With an unknown component_id, the callable returns
     `CombatConstants.DEFAULT_DAMAGE_THRESHOLD`.
  3. With no ApplicationContext (fall-back path), every component_id
     returns the default.
- [x] Verify: targeted test runs green.

**Notes:** Kept the existing broad catch with the required justification
comment because UI-only test contexts can fail through multiple registry
startup paths. The lookup handles both dict-backed and object-backed
component definitions.

---

### Task 1.4: R4 — registry-derived missing-state fallback [Medium]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/test_ship_instance_damage.py`

- [x] Add a private helper to `ShipInstance`:
  ```python
  def _lookup_design_max_hp(self, comp_id: str) -> Optional[int]:
      """Look up a component's design max_hp from the global
      registry. Returns None if registry unavailable or component
      unknown.
      """
      try:
          from game.core.registry import get_default_registry_provider
          components = get_default_registry_provider().get_components()
      except Exception:  # Intentional broad catch: registry may be absent in legacy save context
          return None
      comp = components.get(comp_id)
      if comp is None:
          return None
      raw = getattr(comp, 'max_hp', None) or getattr(comp, 'hp', None)
      return int(raw) if raw is not None else None
  ```
- [x] In `iter_all_components_by_layer` (lines ~591–594), replace the
  `else` branch:
  ```python
  else:
      fallback_max_hp = self._lookup_design_max_hp(comp_id)
      if fallback_max_hp is None:
          # No state and no registry — skip rather than show 0/0
          continue
      max_hp = fallback_max_hp
      current_hp = fallback_max_hp
      is_active = True
  ```
- [x] Update the `iter_all_components_by_layer` docstring to reflect
  the new behaviour: "When backing `ComponentState` is missing, the
  iterator looks up `max_hp` from the global component registry. If
  the registry is unavailable or the component is unknown, the
  instance is skipped entirely rather than emitted with zero HP."
- [x] Add regression tests:
  ```python
  def test_missing_state_uses_registry_max_hp_for_full_hp_view():
      """R4: missing ComponentState should not render as 0/0."""

  def test_missing_state_and_unknown_to_registry_skips_instance():
      """R4 dual-miss: skip rather than emit a meaningless view."""
  ```
- [x] Verify the existing missing-state test
  (`test_missing_component_state_defaults_to_full_hp_active` or
  similar) is updated — it currently passes the meaningless 0/0
  assertion. Replace with the registry-derived assertion.
- [x] Verify: targeted tests green.

**Notes:** Missing state now renders full HP when registry metadata provides
numeric `max_hp`/`hp`, and skips the instance when neither state nor registry
metadata is available. Existing synthetic-id tests now seed explicit
`ComponentState` so they keep testing parser/index behavior rather than the
missing-state fallback.

---

### Task 1.5: Validate against full sharded suite [Simple]
**File:** N/A
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Run the full sharded suite from `c:/Dev/Starship Battles` (NOT
  from a worktree path containing `\a` — known runner bug per PROJ-315
  `decisions.md` row 33).
- [x] Baseline: 15994 passing (post-PROJ-315 merge).
- [x] After Phase 1: expected 15994 + ~6–8 new R1–R4 regression tests
  → ~16000–16002 passed, 0 failed.
- [x] If any unrelated tests fail, investigate and document — do not
  proceed to Phase 2 with a broken baseline.

**Notes:** First full sharded run collected 16003 tests and failed only two
sprite tests because the worktree had not yet generated ignored derivative
assets (`assets/Images/Components/Components 64`). The two sprite tests passed
when rerun after generation. After adding the injected-registry regression, the
final full sharded run passed: 16004 passed / 0 failed.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked.
- [x] Update status at top of this file to `Complete`.
- [x] Update plan.md phase table row to `Complete`.
- [x] Update plan.md Current State to point to Phase 2.
- [x] Run `python Projects/scripts/validate_phase.py PROJ-317 1`.
