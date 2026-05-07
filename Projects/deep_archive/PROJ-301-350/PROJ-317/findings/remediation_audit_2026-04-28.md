# PROJ-315 Remediation Plan

> Five post-merge audit findings against the PROJ-315 implementation.
> All five claims independently verified against source on 2026-04-28.
> This plan is a **follow-up to PROJ-315** — its phases can be appended
> to the existing project (Phase 4–6) or spun out as PROJ-317. The user
> chooses the container.

## Severity Table

| # | Severity | Defect | Fix file(s) | Effort |
|---|---|---|---|---|
| R1 | **High** | Cross-layer `instance_index` collision corrupts per-component HP/active for ships using same `component_id` in multiple layers | `game/strategy/data/ship_instance.py` | Small |
| R2 | **High** | Damage-tier colour computed but never rendered to the label — every instance row shows in default theme colour | `game/ui/panels/ship_detail_panel.py` | Small |
| R3 | **Medium** | Threshold lookup imports from wrong module + calls non-existent method; broad-catch silently falls back to default for all components | `game/ui/panels/ship_detail_panel.py` | Small |
| R4 | **Medium** | Missing-state fallback emits `current_hp = max_hp = 0` (renders "100% of 0 HP" — misleading) instead of registry-derived full HP | `game/strategy/data/ship_instance.py` | Small |
| R5 | **Medium** | `validate_audit_ready.py PROJ-315` fails: phase-section bodies in `plan.md` still say "Not Started"; `Blockers:` field misparses | `Projects/active_projects/PROJ-315/plan.md` | Trivial |
| R6 | **Low** | Two trailing blank lines at EOF in test file | `tests/unit/ui/panels/test_ship_detail_panel.py` | Trivial |
| R7 | **Low** (optional) | Test seam asserts on `_proj315_*` private attrs rather than rendered output — let R2 ship undetected | `tests/unit/ui/panels/test_ship_detail_panel.py` | Medium |
| R8 | **Low** (deferred) | `ship_detail_panel.py` at 681 LOC over the 500-LOC convention | follow-up split | Medium |

R1, R2, R3, R4 are correctness bugs. R5, R6 are cleanliness. R7 is an
audit-strength upgrade. R8 is the original PROJ-309-style decomposition
already on the docket.

---

## R1: Fix cross-layer `instance_index` collision

### Root cause

[`iter_all_components_by_layer`](../../../game/strategy/data/ship_instance.py#L573-L604)
at line 577 declares `per_id_index: Dict[str, int] = {}` **inside** the
`for layer_name, components in self.design_data.get('layers', {}).items()`
loop. The counter resets at every layer boundary.

The authoritative scheme used to *create* `ComponentState` entries —
[`_build_full_hp_components_from_design`](../../../game/strategy/data/ship_instance.py#L45-L94)
at line 77 — declares the counter **outside** the layer loop. So
`battery#0` is the first `battery` anywhere on the ship (might be in
CORE), `battery#1` is the second (might be in INNER), and so on,
keyed by the order the ship-serializer materializes them.

The two schemes diverge whenever a `component_id` appears in more than
one layer. `data/designs/qs_battleship.json` has at least `battery` and
`fuel_tank` in both CORE and INNER — these ships render with silent
state aliasing today.

### Fix

Lift `per_id_index` out of the layer loop so it spans the whole ship.

```python
def iter_all_components_by_layer(self) -> Dict[str, List[ComponentInstanceView]]:
    result: Dict[str, List[ComponentInstanceView]] = {}
    per_id_index: Dict[str, int] = {}  # ← MOVED HERE: ship-wide
    for layer_name, components in self.design_data.get('layers', {}).items():
        if layer_name == 'HULL':
            continue
        views: List[ComponentInstanceView] = []
        for entry in components:
            comp_id = entry.get('id') if isinstance(entry, dict) else entry
            if not comp_id:
                continue
            idx = per_id_index.get(comp_id, 0)
            per_id_index[comp_id] = idx + 1
            ...
```

⚠️ **Layer ordering is significant for this fix** — the authoritative
scheme uses `ship.layers.items()` order (Python dict insertion order
post-3.7). The design-data JSON happens to declare layers in
`CORE → INNER → OUTER → ARMOR` order, so iterating
`design_data['layers'].items()` matches the authoritative order. If the
ordering ever drifts, the keys diverge again. Pin this with a test
that asserts the key-set returned by `iter_all_components_by_layer`
equals the key-set of `_build_full_hp_components_from_design` for the
same design, across at least one shared-component design.

### Verification

- New test in `tests/unit/strategy/test_ship_instance_damage.py`:
  `test_iter_keys_match_build_full_hp_keys_for_cross_layer_design`
  using a `qs_battleship`-style fixture (battery in CORE+INNER).
  Assert `set((iv.component_id, iv.instance_index) for layer in result.values() for iv in layer)`
  equals `{(s.component_id, s.instance_index) for s in built_components.values()}`.
- Existing 7 iterator tests must still pass.

---

## R2: Apply damage-tier colour to rendered labels

### Root cause

[`_build_instance_row`](../../../game/ui/panels/ship_detail_panel.py#L556-L596)
chooses the right colour (`HP_DESTROYED` / `HP_CRITICAL` / `MUTED_GREY`
/ `get_damage_color(...)`) and stores it on
`label._proj315_color = color` for the tests. **It never applies it
to the rendered text.** The label uses the default theme colour.

The strikethrough overlay (line 598-625) IS rendered correctly (a
`UIImage` with a hard-coded light-grey line). So strikethrough works;
colour tiering does not.

### Fix options

**Preferred — pygame_gui `<font color>` rich text:**
```python
hex_color = "#%02x%02x%02x" % color
text = (
    f"      • {group.display_name} #{inst.instance_index + 1}  "
    f"{int(round(hp_pct * 100))}%"
)
label = UILabel(
    relative_rect=pygame.Rect(x + 25, y, width - 40, 22),
    text=f"<font color='{hex_color}'>{text}</font>",
    manager=self.manager,
    container=self.scroll_container,
    text_kwargs={...},  # if needed
)
```
Requires the label widget to accept rich text. Confirm the panel's
existing labels can render HTML — search for any other `UILabel` in
the codebase that uses a `<font>` tag, or fall back to the alternate.

**Alternate — `set_text_colour()` on the label after creation:**
```python
label = UILabel(...)
label.set_text_colour(color)  # check pygame_gui API for the actual method
```
Likely cleaner but pygame_gui's API may not expose runtime colour
changes for `UILabel`. The repo's `game/ui/utils/formatters.py` may
have the canonical helper.

**Alternate (worst) — switch to `UITextBox`:** richer text support but
heavier widget. Only if the first two paths fail.

The strikethrough overlay should also adopt the chosen `color` instead
of hard-coded `(220, 220, 220)` — minor cosmetic upgrade.

### Verification

- New widget test:
  `test_instance_row_label_uses_chosen_color_in_text` — instantiate the
  panel against a known-damaged fixture, retrieve the rendered label,
  and assert via either pygame_gui's text-element API (preferred) or
  pixel sampling that the rendered text is in the expected tier
  colour. **Do not rely on `_proj315_color`** — that's the seam that
  hid this bug. The new test must read what's actually shown.
- Update `decisions.md` Decision #31 (the `_proj315_*` test seam) with
  a note that R2's regression test reads rendered output, not the seam.

### Out of scope for R2
- Font weight, typeface, or background tint changes.

---

## R3: Fix the threshold-lookup wiring

### Root cause

[`_resolve_threshold_lookup`](../../../game/ui/panels/ship_detail_panel.py#L443-L461)
does:
```python
from game.context import get_default_registry_provider          # ← wrong module
provider = get_default_registry_provider()
registry = provider.get_component_registry()                    # ← wrong method
```

`get_default_registry_provider` lives in `game.core.registry` (line
456), and `DefaultRegistryProvider` exposes `get_components()` (a dict)
— not `get_component_registry()`.

The broad `except Exception` swallows the `ImportError` (or
`AttributeError` if you fix the import alone) and returns the
default-only lookup. Production therefore uses
`CombatConstants.DEFAULT_DAMAGE_THRESHOLD` (0.5) for every component,
ignoring per-component or modded `damage_threshold` values entirely.

### Fix

```python
def _resolve_threshold_lookup(self) -> Callable[[str], float]:
    default = CombatConstants.DEFAULT_DAMAGE_THRESHOLD
    try:
        from game.core.registry import get_default_registry_provider
        provider = get_default_registry_provider()
        components: Dict[str, Any] = provider.get_components()
    except Exception:  # Intentional broad catch: UI tests run without ApplicationContext
        return lambda _comp_id: default

    def lookup(comp_id: str) -> float:
        comp = components.get(comp_id)
        if comp is None:
            return default
        return float(getattr(comp, 'damage_threshold', default))

    return lookup
```

Two changes: (1) import from `game.core.registry`, (2) call
`get_components()` and treat the result as a dict.

### Verification

- New test:
  `test_resolve_threshold_lookup_uses_per_component_value` — build a
  test registry where component `engine_x` has
  `damage_threshold = 0.7`. Construct a `ShipDetailPanel`, call
  `_resolve_threshold_lookup()`, invoke the returned callable with
  `'engine_x'`, assert `0.7`. With `'unknown_component'`, assert
  `CombatConstants.DEFAULT_DAMAGE_THRESHOLD`.
- The fallback path (no registry available) keeps its existing
  behaviour; add a test that confirms it.

### Bonus narrowing
The bare `except Exception` should narrow if possible. The realistic
failure modes are `ImportError`, `AttributeError`,
`RuntimeError` (ApplicationContext not initialised). Narrow to
`(ImportError, AttributeError, RuntimeError)` per
`docs/05_ERROR_HANDLING.md` if narrowing is feasible. The
`# Intentional broad catch:` comment can stay if a true broad catch is
needed (e.g. for unknown registry-init failures).

---

## R4: Real full-HP fallback for missing component state

### Root cause

[`iter_all_components_by_layer`](../../../game/strategy/data/ship_instance.py#L591-L594)
when `state is None`:
```python
else:
    max_hp = 0
    current_hp = 0
    is_active = True
```
The downstream `damage_pct = 0.0 if max_hp == 0 else 1.0 - current_hp / max_hp`
treats this as "0% damage" (healthy), but the panel renders the
instance as "100% of 0 HP" — a clear UX bug that confuses the player.

The Phase 1 checklist Task 1.2 explicitly required: "fall back to a
registry lookup if available, else `0`". The code took the second
branch unconditionally — registry was never consulted.

### Fix

Look up the component's `max_hp` from the component registry when
`state is None`. If the registry is unavailable or the component is
unknown, **skip the instance entirely** (don't emit a meaningless
default view).

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

Add a small helper:
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

### Verification

- Replace the existing missing-state test (which asserts `current_hp == max_hp`)
  with one that asserts: when `self.components` lacks a key but the
  registry knows the component, the iterator emits `current_hp ==
  max_hp == registry_max_hp` and `is_active == True`.
- Add a test for the dual-miss case (no state AND registry unaware) —
  iterator skips the instance.
- Update `iter_all_components_by_layer`'s docstring to match the new
  behaviour.
- Update `decisions.md` decision row about "fall back to default view"
  to reflect the registry lookup.

---

## R5: Make the audit-readiness gate pass

### Root cause

`validate_audit_ready.py` parses `plan.md`'s **`## Phases`** section
(lines 236+), not the `## Quick Status` table (lines 13-18). The body
sections at lines 241, 248, 254 still say:
```
**Status:** Not Started — see [phase_X_checklist.md].
```

The `Blockers:` line (line 25) starts with `None.` followed by carry-over
narrative; the validator's regex parses everything after `Blockers:` as
a blocker entry.

### Fix

Three trivial edits to `Projects/active_projects/PROJ-315/plan.md`:
1. Lines 241, 248, 254: `**Status:** Not Started …` → `**Status:** Complete`.
2. Line 25 `**Blockers:**` field: trim trailing narrative or replace with `**Blockers:** None`.
3. Re-run `python Projects/scripts/validate_audit_ready.py PROJ-315` —
   expect `RESULT: PASSED`.

### Verification

- `validate_audit_ready.py PROJ-315` exits 0 with no errors.
- Index status in `Projects/projects_index.md` already reads
  `Awaiting User Verification` (warning is informational).

---

## R6: Trim trailing whitespace at EOF

### Fix

Open `tests/unit/ui/panels/test_ship_detail_panel.py`. Strip the two
trailing blank lines so the file ends with exactly one final newline
after the last assertion.

### Verification
- `git diff --check e26f00f74..HEAD` reports no whitespace errors.

---

## R7 (Optional but recommended): Strengthen test seam

### Issue

The widget tests at `tests/unit/ui/panels/test_ship_detail_panel.py`
assert via `_proj315_color` / `_proj315_strike` attributes on the
label objects, not the rendered output. R2 sailed through 15 widget
tests undetected because the choice of colour was tagged on the label
even though the colour was never rendered.

### Fix
After R2 lands, retire the `_proj315_color` / `_proj315_strike`
attributes. Replace the assertions with checks that read what
pygame_gui actually rendered:
- For colour: read the label's text-styling structure (pygame_gui
  exposes a `text_box_layout` / `colours` dict) or pixel-sample the
  rendered surface at a known character cell.
- For strikethrough: assert the overlay `UIImage` exists at the right
  rect; pixel-sample its surface for a non-transparent pixel along the
  baseline row.

This brings the test contract in line with the project goal: *visible*
damage tiers, not *chosen* damage tiers.

### Out of scope for R7
- Refactoring the panel to a different rendering backend.

---

## R8 (Deferred): Decompose `ship_detail_panel.py`

`decisions.md` row 32 records this. Leave for the next PROJ-309-style
sweep. Natural seams:
- Extract `ComponentInstanceView` consumer logic +
  `group_components_by_id` + the dataclasses to
  `game/ui/panels/ship_component_grouping.py`.
- Extract `_build_component_section` / `_build_layer_block` /
  `_build_group_block` / `_build_instance_row` /
  `_apply_strikethrough` / `_resolve_threshold_lookup` to a
  `ship_component_status_renderer.py` collaborator.
After both extractions, `ship_detail_panel.py` should drop back well
under 500 LOC.

---

## Suggested phase grouping

If folded into PROJ-315 as new phases:

- **Phase 4 — Correctness fixes** (R1, R2, R3, R4): one commit per
  defect, each with a regression test that fails pre-fix and passes
  post-fix. **Block on full sharded suite green** before flipping to
  Phase 5.
- **Phase 5 — Hygiene** (R5, R6): single commit. Audit gate must pass.
- **Phase 6 (optional) — Test seam strengthen** (R7): can ship later.

If spawned as PROJ-317:
- Phase 1 = correctness fixes, Phase 2 = hygiene, Phase 3 = test seam.

## Verification checklist (combined)

- [ ] R1: cross-layer iterator key set equals
  `_build_full_hp_components_from_design` key set on a
  shared-component design fixture.
- [ ] R2: damage-tier colour visible in rendered output, asserted by a
  test that does NOT rely on `_proj315_color`.
- [ ] R3: threshold lookup returns a registry value for known
  component, default for unknown.
- [ ] R4: missing-state fallback uses registry-derived `max_hp`;
  dual-miss skips the instance.
- [ ] R5: `validate_audit_ready.py PROJ-315` exits 0.
- [ ] R6: `git diff --check` clean.
- [ ] Full sharded suite passes: 15994 + new R1–R4 tests, 0 failed.
- [ ] Manual smoke: open a `qs_battleship` (battery shared CORE+INNER)
  in the Fleet Report. Inflict damage to the second-layer battery via
  a save-edit or test fixture. Confirm the panel shows damage on the
  *correct* layer's battery only — not aliased to the first-layer
  battery.

## Origin

Post-merge audit findings against PROJ-315 by independent agent on
2026-04-28. All five claims independently re-verified against source
HEAD `348bceef0` before drafting this remediation plan.
