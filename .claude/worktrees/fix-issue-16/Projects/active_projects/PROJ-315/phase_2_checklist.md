# Phase 2: Widget rewrite (COMPONENT STATUS section)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-315 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Replace the existing damage section in
`ship_detail_panel.py` with a new always-rendering COMPONENT STATUS
section. Add module-level grouping helpers and the strikethrough
overlay utility. Add ~15 widget tests.

---

## Tasks

### Task 2.1: Add module-level grouping helpers [Medium]
**File:** `game/ui/panels/ship_detail_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_ship_detail_panel.py -k group_components_by_id`

- [x] At the top of the file (above the `class ShipDetailPanel`),
  add three frozen dataclasses + one pure function:
  ```python
  @dataclass(frozen=True)
  class InstanceDamage:
      instance_index: int
      damage_pct: float
      is_active: bool
      is_damage_induced_inactive: bool

  @dataclass(frozen=True)
  class ComponentGroup:
      component_id: str
      display_name: str
      total: int
      functional: int
      avg_damage_pct: float
      instances: tuple[InstanceDamage, ...]

  def group_components_by_id(
      instances: list[ComponentInstanceView],
      damage_threshold_lookup: Callable[[str], float],
  ) -> list[ComponentGroup]: ...
  ```
- [x] Implementation rules:
  - Group by `component_id`. Preserve first-seen order across the input list.
  - `damage_pct = 0.0 if max_hp == 0 else (1.0 - current_hp / max_hp)`.
  - `is_damage_induced_inactive = (not is_active) and (current_hp < max_hp * threshold)`. False for healthy or fully-destroyed views (the destroyed case is covered by `current_hp == 0` separately).
  - `avg_damage_pct = mean(inst.damage_pct for inst in instances)`.
  - `functional = sum(1 for inst in instances if inst.is_active)`.
  - `display_name = display_name(component_id)` from `game.core.string_utils`.
- [x] Pure-function tests in
  `tests/unit/ui/panels/test_ship_detail_panel.py` under a new
  `TestGroupComponentsById` class:
  1. Empty input → empty output.
  2. Single component, single instance, full HP → group with `total=1`, `functional=1`, `avg_damage_pct=0.0`.
  3. 4 engines at 75/75/25/25 with `is_active=True` for the first two and `False` for the second two (assume threshold 0.5) → `avg_damage_pct == 0.50`, `functional == 2`, `is_damage_induced_inactive == True` for the second two.
  4. All-destroyed group (current_hp=0) → `functional == 0`, `avg_damage_pct == 1.0`.
  5. Manually-disabled instance (`is_active=False`, `current_hp=max_hp`) → `is_damage_induced_inactive == False`, `functional == 0` (counts toward non-functional).
  6. Mixed: a registry stub returning thresholds per component_id is honoured.
  7. Division-by-zero guard: max_hp == 0 → `damage_pct == 0.0`, no exception.
  8. Group ordering: components arrive interleaved (engine, weapon, engine, weapon) → grouped output preserves first-seen order (engine first).
- [x] Verify: targeted test runs green.

**Notes:**

---

### Task 2.2: Add `MUTED_GREY` colour constant + strikethrough overlay [Simple]
**Files:** `game/ui/colors.py`, `game/ui/panels/ship_detail_panel.py`
**Tests:** `pytest tests/unit/ui/test_colors.py` (if exists; otherwise no test for the constant — it's pinned by snapshot tests in 2.4)

- [x] In `game/ui/colors.py`, add `MUTED_GREY = (130, 130, 150)` near
  the existing `HP_*` constants. Document: "Manually-disabled
  components — distinct from `HP_DESTROYED` to convey 'off but not
  broken'."
- [x] In `ship_detail_panel.py`, add a private helper:
  ```python
  def _apply_strikethrough(self, label: UILabel) -> None:
      """Overlay a horizontal line across `label` to convey strike.

      pygame_gui has no native <s> rich-text. Pattern mirrors
      game/ui/screens/test_lab/dialogs.py.
      """
  ```
- [x] Keep the `UIImage` overlay pinned to the label's rect so the
  strike scrolls with the scrolling container. Track in
  `self.ui_elements` for `_clear_elements()` cleanup.

**Notes:**

---

### Task 2.3: Replace the section entry + `_build_damage_section` [Medium]
**File:** `game/ui/panels/ship_detail_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_ship_detail_panel.py`

- [x] Remove the `if damage_count > 0:` gate at lines 271–275.
  Replace with an unconditional call to a renamed
  `_build_component_section(ship, 10, y, width)`. Update the
  section header text from `COMPONENT DAMAGE (...)` to
  `COMPONENT STATUS`.
- [x] Rename `_build_damage_section` → `_build_component_section`
  and rewrite the body. Internal flow:
  1. Call `ship.iter_all_components_by_layer()` → `views_by_layer`.
  2. For each layer in `LAYER_ORDER = ['CORE', 'INNER', 'OUTER', 'ARMOR']`:
     - Skip if no entries.
     - Group via `group_components_by_id(views, threshold_lookup)`.
     - Render a layer header (chevron + name + aggregate
       "<functional>/<total> functional · <avg>% avg damage").
     - If `expanded_layers[layer]`, render each `ComponentGroup`:
       - Group row: chevron + `<display_name> × <count>` +
         `<functional>/<total>` + `<avg>%` colour-tinted via
         `get_damage_color(1.0 - avg_damage_pct)`.
       - If `expanded_groups.get((layer, comp_id))`, render
         `len(instances)` instance rows below it.
- [x] Per-instance rendering rules per `design.md`:
  - Healthy/Damaged/Critical: `get_damage_color(hp_pct)` colour, no strike.
  - Destroyed (`current_hp == 0`): `HP_DESTROYED` colour, **strike**.
  - Damage-induced inactive (`is_damage_induced_inactive == True`,
    `current_hp > 0`): `HP_CRITICAL` colour, **strike**.
  - Manually disabled (`!is_active and not is_damage_induced_inactive`):
    `MUTED_GREY` colour, no strike.
- [x] Replace the existing `expanded_layers` initialiser at lines
  57–63 with deterministic-from-ship logic — moved into
  `update_ship` so it re-fires per the user's Phase C decision:
  ```python
  def update_ship(self, ship_instance):
      self.current_ship = ship_instance
      if ship_instance is None:
          self._show_placeholder(); return
      self._compute_initial_expand_state(ship_instance)
      self._clear_elements()
      self._build_ship_display(ship_instance)
  ```
  where `_compute_initial_expand_state` groups the ship's components
  and sets `expanded_layers[layer] = True` iff that layer contains a
  destroyed instance, otherwise `False`. Also resets
  `expanded_groups = {}`.
- [x] Group-row chevron handling: extend `process_event` so clicks on
  group buttons toggle `expanded_groups[(layer, comp_id)]` and
  trigger a rebuild via `self.update_ship(self.current_ship)`. Hold
  group buttons in a parallel `self.group_buttons: dict[tuple[str, str], UIButton]`.
- [x] Wire the threshold lookup. Production path:
  ```python
  from game.core.constants import CombatConstants
  registry_provider = get_default_registry_provider()
  components_registry = registry_provider.get_component_registry()

  def threshold_lookup(comp_id: str) -> float:
      comp = components_registry.get_component(comp_id)
      if comp is None:
          return CombatConstants.DEFAULT_DAMAGE_THRESHOLD
      return getattr(comp, 'damage_threshold', CombatConstants.DEFAULT_DAMAGE_THRESHOLD)
  ```
  Wrap with `# Intentional broad catch: registry may be absent in
  test contexts` only if a try/except is needed.
- [x] Fix the latent `_`-split parser bug at the old lines 367–375
  by removing it entirely. The new view uses
  `ComponentInstanceView.component_id` directly.
- [x] Verify: targeted test run green; manual inspection in a fresh
  game loads cleanly.

**Notes:**

---

### Task 2.4: Widget tests [Medium]
**File:** `tests/unit/ui/panels/test_ship_detail_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_ship_detail_panel.py`

Re-use the canonical fixtures: autouse pygame fixture from
`tests/integration/ui/conftest.py:38-54`, `ui_manager` fixture, and
`ship_factory` from `tests/conftest.py`.

Add a new test class `TestComponentStatusSection` with at least the
following tests (12-15 total):

- [x] Pristine ship: section renders, header "COMPONENT STATUS",
  every layer collapsed by default, every group row reads
  `<N>/<N>` functional and `0%` avg damage in neutral colour.
- [x] Single damaged engine: collapsed group row shows the right avg
  % and `<functional>/<total>`; layer header tinted HP_DAMAGED.
- [x] 4 engines at 75/75/25/25 with the bottom two below threshold:
  collapsed group reads `2 / 4` and `50%`.
- [x] Destroyed instance: containing layer auto-expands on
  `update_ship`. Group row stays collapsed by default. Manually
  expanding the group reveals an instance row that renders in
  `HP_DESTROYED` colour with the strikethrough overlay.
- [x] Damage-induced inactive (HP > 0 but below threshold,
  is_active=False): instance row renders in `HP_CRITICAL` red with
  strikethrough.
- [x] Manually-disabled (is_active=False, HP == max_hp): instance
  row renders in `MUTED_GREY`, no strikethrough.
- [x] Layer ordering deterministic: the rendered layer headers
  always appear in `[CORE, INNER, OUTER, ARMOR]` order.
- [x] HULL layer suppressed even when present in design_data.
- [x] Toggle a layer manually then call `update_ship` with a fresh
  ship → auto-expand re-fires; manual collapse does NOT persist
  across ship reselection (Phase C decision).
- [x] Group-row toggle cycles `expanded_groups` and rebuilds
  correctly.
- [x] Display-name format: group row text matches exactly
  `"Reactor Standard × 4"` (× is U+00D7, single-space padding).
- [x] Read-only contract: assert that the only `UIButton` instances
  spawned inside the section equal the layer-header buttons +
  group-header buttons. No instance-row buttons. The pre-existing
  `Remove from Fleet` button is unaffected.
- [x] Component_id with numeric suffix (`reactor_mark_2`) renders
  with the right display name and the right group count — pins the
  parser-bug fix.
- [x] Save/load round-trip: damage state survives reload, panel
  rebuilds the same view.

**Notes:**

---

### Task 2.5: Validate against full sharded suite [Simple]
**File:** N/A
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Run the full sharded suite. Expected baseline (15893) + new
  Phase 1 + Phase 2 tests (~25-30 added) → ~15918-15923 passed, 0
  failed.
- [x] Manual smoke (in addition to the verification list in plan.md):
  open Fleet Report on a healthy fleet — see all components, all
  collapsed, all 100%. Run a battle that destroys a component;
  re-open Fleet Report and verify the affected layer auto-expanded
  and the destroyed instance is in HP_DESTROYED + strike.

**Notes:**

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked.
- [x] Update status at top of this file to `Complete`.
- [x] Update plan.md phase table row to `Complete`.
- [x] Update plan.md Current State to point to Phase 3.
- [x] Run `python Projects/scripts/validate_phase.py PROJ-315 2`.
