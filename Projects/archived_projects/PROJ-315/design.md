# PROJ-315: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Architecture

### Layers touched
- **Core** — add `ComponentInstanceView` frozen dataclass alongside
  the existing `ComponentState` in
  `game/core/component_state.py`. Pure data; no behaviour.
- **Strategy** — add `ShipInstance.iter_all_components_by_layer()`
  helper at `game/strategy/data/ship_instance.py`. Joins the ship's
  `design_data['layers']` enumeration with the `self.components`
  state dict.
- **UI** — rewrite the COMPONENT DAMAGE section in
  `game/ui/panels/ship_detail_panel.py` into a COMPONENT STATUS
  section. Add module-level `ComponentGroup`, `InstanceDamage`
  dataclasses and a pure `group_components_by_id()` function above
  the panel class.

No facade layer changes. The panel already takes a direct
`ShipInstance` reference via TYPE_CHECKING and the file's docstring
explicitly documents this as accepted.

### Data shape

```python
# game/core/component_state.py — additive
@dataclass(frozen=True)
class ComponentInstanceView:
    """Read-only snapshot of one component instance for UI display.

    Joins design-data presence with persisted ComponentState. When a
    ComponentState entry is missing for a key (legacy saves, freshly
    materialised ships), defaults to current_hp == max_hp and
    is_active == True.
    """
    component_id: str
    instance_index: int
    current_hp: int
    max_hp: int
    is_active: bool
```

```python
# game/strategy/data/ship_instance.py — new helper
def iter_all_components_by_layer(self) -> Dict[str, List[ComponentInstanceView]]:
    """Return every component grouped by layer. HULL excluded.

    Walks design_data['layers'] in source order. Looks up each
    component in self.components by component_state_key(); falls
    back to a default view (full HP, active) when missing.
    """
```

```python
# game/ui/panels/ship_detail_panel.py — module-level (above class)
@dataclass(frozen=True)
class InstanceDamage:
    instance_index: int
    damage_pct: float           # 0.0 = full HP; 1.0 = destroyed
    is_active: bool
    is_damage_induced_inactive: bool  # current_hp < max_hp * damage_threshold

@dataclass(frozen=True)
class ComponentGroup:
    component_id: str
    display_name: str
    total: int
    functional: int             # sum(is_active for v in instances)
    avg_damage_pct: float
    instances: tuple[InstanceDamage, ...]

def group_components_by_id(
    instances: list[ComponentInstanceView],
    damage_threshold_lookup: Callable[[str], float],
) -> list[ComponentGroup]:
    """Pure function. No pygame deps. Trivially unit-testable."""
```

`damage_threshold_lookup` is injected so the test suite can stub it
without instantiating the registry. Production callers pass
`get_default_registry_provider().get_component_registry().get_component(id).damage_threshold`,
falling back to `CombatConstants.DEFAULT_DAMAGE_THRESHOLD` (0.5) if
the lookup misses.

### Visual rendering rules

| State                                                       | Colour           | Strike-through? |
|-------------------------------------------------------------|------------------|-----------------|
| Healthy (HP == max_hp, is_active)                           | `HP_HEALTHY`     | No              |
| Damaged (0 < damage_pct ≤ 0.5 × threshold, is_active)       | `HP_DAMAGED`     | No              |
| Critical (damage_pct > 0.5 × threshold, is_active)          | `HP_CRITICAL`    | No              |
| Destroyed (current_hp == 0)                                 | `HP_DESTROYED`   | Yes             |
| Damage-induced inactive (HP < threshold, !is_active, HP>0)  | `HP_CRITICAL`    | Yes             |
| Manually disabled (HP ≥ threshold, !is_active)              | `MUTED_GREY` *   | No              |

\* `MUTED_GREY` constant added to `game/ui/colors.py` (e.g.
`(130, 130, 150)`). Distinct from `HP_DESTROYED` grey to convey
"intentionally off, not broken".

Group-row colour is `get_damage_color(1.0 - avg_damage_pct)` from
`game/ui/utils/formatters.py`. Layer-header colour is the worst tier
across all groups in the layer: HP_CRITICAL if any group has a
destroyed instance, HP_DAMAGED if any group has avg_damage_pct > 0,
otherwise neutral text colour.

### Strikethrough rendering

pygame_gui's `UILabel` does not support `<s>` natively. We use the
manual overlay pattern from
`game/ui/screens/test_lab/dialogs.py`: after the label is drawn,
draw a horizontal `pygame.draw.line()` across its rect at the
baseline. Encapsulate as `_apply_strikethrough(label: UILabel)` in
the panel file. Document: "If pygame_gui adds `<s>` support in a
future release, prefer that and remove this helper."

### Auto-expand semantics

`update_ship(ship)` is the sole entry point for switching ships.
Inside, after building the ship's `ComponentGroup` tree, walk the
groups and:

```python
self.expanded_layers = {layer: False for layer in LAYER_ORDER}
for layer, groups in groups_by_layer.items():
    if any(inst.damage_pct >= 1.0 for g in groups for inst in g.instances):
        self.expanded_layers[layer] = True
self.expanded_groups = {}  # always start groups collapsed
```

Per the user's Phase C decision, auto-expand re-fires on every
`update_ship` call. No persistence of manual collapse across
selections.

### Read-only contract

Group rows and instance rows are `UILabel`s. Only the layer-header
chevron and group-header chevron remain `UIButton` (used for toggle
input). The pre-existing `Remove from Fleet` button continues to
exist below the COMPONENT STATUS section and is unaffected.

A regression test asserts that, for a given fixture ship, the count
of `UIButton` instances spawned inside the section equals
`len(layer_buttons) + len(group_buttons)` — no other interactive
widgets.

## Trade-offs Considered

### Iterator location: Core vs Strategy
Considered placing `iter_all_components_by_layer` on a Core helper
module so it could be reused by Workshop / AI / Combat Lab.
Rejected: those layers don't read `ShipInstance.components` (a
Strategy concept). The iterator stays on `ShipInstance` as the
natural owner.

### Grouping function: separate module vs colocated
The triage doc proposed a separate `ship_component_grouping.py`
module. Rejected per the Plan agent — ~40 lines of pure logic
doesn't justify a new file. Module-level colocation in
`ship_detail_panel.py` matches the `planet_report_panel.py`
precedent and keeps the grouping logic trivially testable.

### Facade DTO: introduce vs skip
The original triage suggested a new facade DTO + slice query.
Rejected. The panel already direct-reads `ShipInstance` via
TYPE_CHECKING; the file's docstring documents this as accepted
"Cross-layer imports (acceptable for UI display)". Adding facade
indirection here would be unrelated cleanup.

### Strikethrough: rich-text vs manual draw vs Unicode combining
- pygame_gui `<s>` rich-text: not supported in this version.
- Unicode combining overstrike (U+0336): rendering quality varies
  per font; ugly to embed in source strings.
- Manual `pygame.draw.line()` overlay: matches `dialogs.py`
  precedent; clean to encapsulate. **Chosen.**

### Layer order: inside-out vs outside-in vs Workshop
User chose Workshop order: `[CORE, INNER, OUTER, ARMOR]`. HULL
excluded.

## Risks & Mitigations
See `## Swarm Findings Summary` in `plan.md` for the full risk
register. The eight risks identified by the Risk Assessor are all
either resolved by user decisions in Phase C, addressable in the
phase checklists, or accepted as out of scope (perf optimisation
of the rebuild-on-toggle pattern).

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
