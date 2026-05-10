# PROJ-317: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Architecture

### Layers touched
- **Strategy** — single fix in
  `game/strategy/data/ship_instance.py` to
  `iter_all_components_by_layer` (R1, R4). No public-API change; the
  return type stays `Dict[str, List[ComponentInstanceView]]`. Two
  internal additions: ship-wide `per_id_index` counter, registry-derived
  `max_hp` fallback helper.
- **UI** — fixes in
  `game/ui/panels/ship_detail_panel.py`. Three editing surfaces:
  `_resolve_threshold_lookup` (R3 import + method-name fix),
  `_build_instance_row` (R2 colour application), `_apply_strikethrough`
  (R2 strike-tint match). No new module. No new dataclass.
- **Project tracking** — text edits in
  `Projects/active_projects/PROJ-315/plan.md` (R5).
- **Tests** — additions to
  `tests/unit/strategy/test_ship_instance_damage.py` (R1, R4) and
  `tests/unit/ui/panels/test_ship_detail_panel.py` (R2, R3, plus EOF
  whitespace trim for R6, plus optional R7 seam retirement).

No new files. No facade DTO. No new pattern entries in `docs/02_PATTERNS.md`.

### R1 — cross-layer instance index

**Authoritative scheme** in
[`_build_full_hp_components_from_design`](../../../game/strategy/data/ship_instance.py#L45-L94)
declares `per_id_index: Dict[str, int] = {}` at line 77 — **outside**
the layer loop. Iterates `ship.layers.items()`. Increments globally
across the ship.

**Buggy mirror** in
[`iter_all_components_by_layer`](../../../game/strategy/data/ship_instance.py#L573-L604)
declares the same dict at line 577 — **inside** the layer loop.
Counter resets per layer.

**Fix:** lift the declaration above the `for layer_name` loop. No other
behaviour change; instance ordering within a layer remains source-order.
Cross-layer keys now match the canonical scheme exactly.

**Ordering caveat:** the authoritative path iterates `ship.layers`
(materialised by `ShipSerializer.from_dict`) while the iterator path
walks `design_data.get('layers', {})`. Both rely on dict insertion
order being stable (Python 3.7+). Designs typically declare layers
`CORE → INNER → OUTER → ARMOR`. Pin ordering equivalence with a test
that asserts the key set returned by `iter_all_components_by_layer`
exactly equals
`{(s.component_id, s.instance_index) for s in built_components.values()}`
for a representative shared-component design (`qs_battleship`-style
fixture).

### R2 — colour application path

**Defect:** [_build_instance_row](../../../game/ui/panels/ship_detail_panel.py#L556-L596)
chooses the right colour, stores it on `label._proj315_color = color`,
and never applies it visually. Strikethrough overlay at line 598-625
uses hard-coded `(220, 220, 220)`.

**Fix path (preferred):** wrap the label text in a pygame_gui rich-text
`<font color>` span. Format the colour as `#rrggbb` hex string.
```python
hex_color = "#{:02x}{:02x}{:02x}".format(*color[:3])
text = f"<font color='{hex_color}'>{plain_text}</font>"
```
Confirm pygame_gui's `UILabel` parses `<font color>` in this version
during a Phase-1 spike. If not, fall back to `set_text_colour()`.
If both fail, escalate to `UITextBox` (heavier widget but full
rich-text support).

**Strike overlay:** pass the chosen colour into `_apply_strikethrough`
and use it for the line colour. Drop the hard-coded
`(220, 220, 220)`.

**Test seam tension:** the `_proj315_color` /  `_proj315_strike`
attributes stay in place during Phase 1 (so existing tests keep passing
under the colour-aware code path) but a new test reads rendered output
and asserts the colour is actually visible. Phase 3 retires the
seam after the new tests prove out.

### R3 — threshold lookup wiring

**Defect:** [_resolve_threshold_lookup](../../../game/ui/panels/ship_detail_panel.py#L443-L461)
imports from `game.context` (wrong; `get_default_registry_provider`
lives in `game.core.registry`) and calls `get_component_registry()`
(wrong; the actual method is `get_components()` returning a dict).

**Fix:** correct both the import path and the method call. The new
shape:
```python
from game.core.registry import get_default_registry_provider
provider = get_default_registry_provider()
components: Dict[str, Any] = provider.get_components()

def lookup(comp_id: str) -> float:
    comp = components.get(comp_id)
    if comp is None:
        return CombatConstants.DEFAULT_DAMAGE_THRESHOLD
    return float(getattr(comp, 'damage_threshold',
                        CombatConstants.DEFAULT_DAMAGE_THRESHOLD))
```

**Broad-catch narrowing (optional but encouraged):** narrow
`except Exception` to
`(ImportError, AttributeError, RuntimeError)` per
`docs/05_ERROR_HANDLING.md`. The
`# Intentional broad catch:` justification stays only if the narrowed
form proves insufficient.

### R4 — missing-state fallback

**Defect:** [iter_all_components_by_layer](../../../game/strategy/data/ship_instance.py#L591-L594)
emits `max_hp = 0`, `current_hp = 0` when `state is None`. Renders
"100% of 0 HP" — meaningless and misleading.

**Fix:** consult the component registry for a default `max_hp`. If the
registry is unavailable or the component is unknown, **skip the
instance entirely** (don't emit a meaningless default view).

```python
state = self.components.get(key)
if state is not None:
    max_hp = int(state.max_hp)
    current_hp = int(state.current_hp)
    is_active = bool(state.is_active)
else:
    fallback_max_hp = self._lookup_design_max_hp(comp_id)
    if fallback_max_hp is None:
        # No state and no registry — skip rather than show 0/0
        continue
    max_hp = fallback_max_hp
    current_hp = fallback_max_hp
    is_active = True
```

Helper:
```python
def _lookup_design_max_hp(self, comp_id: str) -> Optional[int]:
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

**Update `iter_all_components_by_layer`'s docstring** to reflect the
new behaviour (registry-derived fallback; skip on dual-miss).

### R5 — audit-readiness gate

`validate_audit_ready.py PROJ-315` parses the `## Phases` section
bodies (lines 236–254 of `plan.md`), not the `## Quick Status` table
at the top. Three lines need editing:
- L241: `**Status:** Not Started — see [phase_1_checklist.md].` →
  `**Status:** Complete`.
- L248: same for Phase 2.
- L254: same for Phase 3.

`Blockers:` field at L25 of `plan.md` starts with `None.` followed by
"Two spec ambiguities resolved with the user…" narrative. The
validator's regex parses everything after `Blockers:` as a blocker.
Trim to `**Blockers:** None`. The narrative belongs in `decisions.md`
(already present there as Decision 12 + 13).

### R6 — EOF whitespace

`tests/unit/ui/panels/test_ship_detail_panel.py` ends with two CRLF
blank lines. Trim to a single trailing newline. The fix is one editor
keystroke; no behaviour change.

### R7 — test seam strengthen (optional)

The widget tests assert via `label._proj315_color` and
`label._proj315_strike` attributes. After R2 lands, those attributes
become redundant — colour is now visible in the rendered output. Phase
3 retires the seam.

**Replacement assertion strategies (in order of preference):**
1. **Read pygame_gui's text-element internals** — pygame_gui's
   `UILabel.text_box_layout` (or equivalent in this version) exposes
   the parsed text-styling tree. Walk it and find the colour applied
   to the text run. This avoids pixel sampling.
2. **Pixel sample** — render the label to a surface, sample at a
   known character cell, assert the pixel is in the expected colour
   range (allowing for anti-aliasing).
3. **Hybrid** — assert intent on a non-private attribute (e.g.
   `_apply_strikethrough` is invoked on the label) plus a single
   pixel sample to confirm visible colour.

If 1 proves brittle in this codebase's pygame_gui version, fall back
to 3.

## Trade-offs Considered

### R7: Phase 3 vs immediate
Phase 1 fixes are correctness work. R7 is test-strength work that's
arguably not blocking. Splitting it into Phase 3 lets Phase 1 ship
independently. If pygame_gui's text-element API is too brittle for
clean tests, R7 can be deferred indefinitely without leaving Phase 1
fixes in limbo.

### R3: narrow vs broad catch
The plan keeps `except Exception` as the safe default but encourages
narrowing. Narrowing fully is risky if a less-common exception
surfaces in production. The broad catch with the comment satisfies
`docs/05_ERROR_HANDLING.md` policy.

### R8: deferred to PROJ-309
`ship_detail_panel.py` is at 681 LOC. The natural seams to extract
were already documented in PROJ-315 `decisions.md` row 32. The
remediation project deliberately doesn't touch the file's structure
to avoid a churn cascade — every PROJ-315 widget test instantiates the
panel directly. Leaving it for a dedicated PROJ-309 sweep keeps the
remediation focused.

## Risks & Mitigations

See `## Risks Identified` in `plan.md` for the full register.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
