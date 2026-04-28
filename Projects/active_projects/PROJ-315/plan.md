# PROJ-315: Fleet Report Component Damage Panel

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-315` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-315 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Strategy data helper (`iter_all_components_by_layer`) | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Widget rewrite (COMPONENT STATUS section) | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Documentation + closeout | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-04-28 — protocol-01 planning complete
**Active Phase:** Plan complete, awaiting user approval before implementation
**Last Action:** Detailed plan written; baseline test suite established at **15893 / 15893 passing**.
**Next Action:** User approval → begin Phase 1.
**Blockers:** None. Two spec ambiguities resolved with the user during Phase C: (a) damage-induced inactive components render in red with strikethrough; manually-disabled components render in muted grey without strike; (b) layer auto-expand re-fires on every ship selection (no manual-collapse persistence).

## Overview

The Fleet Report's right-side ship-detail panel currently shows a
"COMPONENT DAMAGE" section that **only renders when the ship has at
least one damaged component** (`ship_detail_panel.py:273`). On a
healthy ship the section vanishes entirely, leaving the user with the
false impression that no per-component information exists in the game.
This was reported in QA Session 20260428_052952 [05:49–05:51] —
[findings/fleet_report_component_damage_view.md](findings/fleet_report_component_damage_view.md).

This project rewrites that section into a "COMPONENT STATUS" section
that **always renders**, lists **every component** on the ship grouped
by layer, with collapsible groups for identical components showing
average damage % and a `<functional>/<total>` fraction.

## Goals

- Show every component on the selected ship, layer-grouped, regardless
  of damage state — eliminate the "panel hides on healthy ships" bug.
- Group identical components into a single collapsible row with
  `<name> × <count>` showing **average** damage % and
  `<functional>/<total>` fraction (functional = `is_active`).
- Per-instance damage % colour-tiered; damage-induced inactive
  components rendered red + strikethrough; manually-disabled
  components rendered muted grey; destroyed components render with
  HP_DESTROYED grey + strikethrough.
- Visually mirror the Workshop component palette aesthetic.
- Layer order matches Workshop: `[CORE, INNER, OUTER, ARMOR]`. HULL
  is excluded.
- Default everything collapsed; auto-expand layers containing
  destroyed components on every ship-selection event.
- Read-only — no mutation buttons inside the new content.

## Scope

**In:**
- New `ShipInstance.iter_all_components_by_layer()` helper.
- New `ComponentInstanceView` frozen dataclass at
  `game/core/component_state.py` (sibling of `ComponentState`).
- Module-level pure function `group_components_by_id()` colocated at
  the top of `ship_detail_panel.py` (mirrors the
  `planet_report_panel.py` colocation precedent).
- Module-level frozen dataclasses `ComponentGroup` and
  `InstanceDamage` colocated in the same panel file.
- Rewrite of `_build_damage_section` → `_build_component_section` and
  removal of the `if damage_count > 0` gate.
- Strikethrough rendering helper (manual `pygame.draw.line()` overlay
  matching the `test_lab/dialogs.py` pattern).
- New tests covering the iterator, group computation, and widget
  rendering.
- Doc updates in `docs/06_UI_STYLE_GUIDE.md`.

**Out:**
- Facade DTO + slice query for per-ship component breakdown. Panel
  reads `ShipInstance` directly per its existing accepted "Cross-layer
  imports (acceptable for UI display)" pattern. Adding facade
  indirection here is out of scope.
- "Repair component" mutation actions.
- Component-level ability tooltips (would require simulation-Component
  registry lookups).
- Mass / cost / power consumption columns.
- Sorting beyond layer grouping.
- Performance optimisation of the rebuild-on-toggle pattern (current
  ~30-component-per-ship cost is acceptable).

## Key Files

| Component | File Path | Notes |
|-----------|-----------|-------|
| Panel under redesign | [game/ui/panels/ship_detail_panel.py](../../../game/ui/panels/ship_detail_panel.py) | Existing damage section at 271–276 (entry) and 322–390 (`_build_damage_section`); toggle at 392–398. |
| Strategy data helper home | [game/strategy/data/ship_instance.py](../../../game/strategy/data/ship_instance.py) | Add `iter_all_components_by_layer()` alongside existing `get_components_by_layer()` (~541) and `get_damaged_components_by_layer()` (~551–588). |
| Component state | [game/core/component_state.py](../../../game/core/component_state.py) | Add `ComponentInstanceView` frozen dataclass; existing `ComponentState` unchanged. |
| Visual reference (read item) | [game/ui/screens/builder/components.py](../../../game/ui/screens/builder/components.py) | `ComponentListItem` — row 40 px, icon 32 px. |
| Visual reference (layer panel) | [game/ui/screens/builder/layer_panel.py](../../../game/ui/screens/builder/layer_panel.py) | Layer order `[CORE, INNER, OUTER, ARMOR]` confirmed at line 128. HULL prepended conditionally at line 132 — **excluded from our panel**. |
| Layer / item structural reference | [game/ui/screens/builder/structure_list_items.py](../../../game/ui/screens/builder/structure_list_items.py) | `LayerHeaderItem` / `LayerComponentItem` / `IndividualComponentItem` — visual prior art. **Strip mutations; do not reuse classes** (mutation handlers tightly integrated). Match layout & chevron. |
| Colour tokens | [game/ui/colors.py](../../../game/ui/colors.py) | `HP_HEALTHY` / `HP_DAMAGED` / `HP_CRITICAL` / `HP_DESTROYED`. May add `MUTED_GREY` for manual-disable. |
| Damage colour helper | [game/ui/utils/formatters.py](../../../game/ui/utils/formatters.py) | `get_damage_color(hp_pct)` — reuse for tier mapping. |
| Display name helper | [game/core/string_utils.py](../../../game/core/string_utils.py) | `display_name(raw)` — snake_case → "Title Case". |
| Manual strikethrough precedent | [game/ui/screens/test_lab/dialogs.py](../../../game/ui/screens/test_lab/dialogs.py) | `pygame.draw.line()` overlay pattern; copy approach for the strikethrough overlay helper. |
| Module-level pure-function precedent | [game/ui/panels/planet_report_panel.py](../../../game/ui/panels/planet_report_panel.py) | Module-level `_projection_grid_rows`, `_qty_cell`, etc. above the panel class — pin for `group_components_by_id()` colocation. |
| Triage source | [findings/fleet_report_component_damage_view.md](findings/fleet_report_component_damage_view.md) | Origin doc with QA screenshots. |

## Related Documents
- [design.md](design.md) — Architecture analysis and design rationale.
- [decisions.md](decisions.md) — Full decisions log including
  the Phase C clarification answers.

## Initial Analysis (Phase A)

### Existing implementation
The current "COMPONENT DAMAGE" section uses a working pattern:
collapsible layers, `▼` / `▶` chevrons, layer headers as `UIButton`s,
state in `expanded_layers: Dict[str, bool]`, full-rebuild on toggle.
But it has four critical defects vs. the target spec:
1. **Hidden on healthy ships** — `if damage_count > 0:` gate at line
   273 means a fully operational ship shows no component info at all.
2. **Damaged-only listing** — `_build_damage_section` walks
   `get_damaged_components_by_layer()`, never enumerates pristine
   components.
3. **No grouping for identical components** — every damaged instance
   gets its own row even when 4 identical engines all share the same
   damage state.
4. **Latent ID-parsing bug** at lines 367–375: splits component id on
   `_` to derive base id, but the canonical `component_state_key`
   uses `#` separator. A `reactor_mark_2` id would parse incorrectly.

### Data layer is complete except for one helper
`ShipInstance.components` (a `Dict[str, ComponentState]` keyed by
`<id>#<index>`) is populated end-to-end by the post-battle bridge
([`ShipInstanceBridge.update_from_ship`](../../../game/strategy/data/ship_instance_bridge.py#L115-L163))
and survives save/load via
[`ShipInstanceSerializer.to_dict` / `from_dict`](../../../game/strategy/data/ship_instance_serializer.py#L24).
There's no auto-repair between turns. The only data-layer gap is the
absence of an "enumerate ALL components per layer" helper.
`get_damaged_components_by_layer()` is damaged-only;
`get_components_by_layer()` returns design entries without joining
state.

### Direct ShipInstance read is the existing accepted pattern
The panel file's own docstring documents:
> "Cross-layer imports (acceptable for UI display): ShipInstance
> (TYPE_CHECKING - used for type hints only)"
Adding a facade DTO + FleetSlice query would be unrelated churn.

## Swarm Findings Summary (Phase B)

### Architecture
- Layer-rule clean: panel already crosses Strategy boundary (accepted
  pattern). New `ComponentInstanceView` belongs in **Core**
  (`game/core/component_state.py`) next to `ComponentState`.
- Layer iteration uses **string keys** in `design_data['layers']`
  (e.g. `"CORE"`, `"INNER"`); `LayerType` enum is sim-layer-only.
  Iterate by string list `['CORE', 'INNER', 'OUTER', 'ARMOR']`.
- Workshop layer order confirmed at
  `game/ui/screens/builder/layer_panel.py:128`
  (`[CORE, INNER, OUTER, ARMOR]`); HULL prepended conditionally at
  line 132 — excluded from our panel.

### Dependency Map
- Sole instantiator of `ShipDetailPanel`: `fleet_report_window.py:143`.
  Sole `update_ship` caller: `fleet_report_window.py:236`. Renaming
  the private method `_build_damage_section` is safe.
- Callers of `get_damaged_components_by_layer`: panel (1) +
  `tests/unit/strategy/test_ship_instance_damage.py` (1). Adding
  `iter_all_components_by_layer` alongside is non-disruptive.
- No wildcard imports of `component_state`. New
  `ComponentInstanceView` adds zero import-conflict risk.
- No reverse `game/strategy/` → `game/ui/` dependency. No
  circular-import risk for the new helper imports.

### Test Impact
- Existing tests for the panel: 31 across 8 classes in
  `tests/unit/ui/panels/test_ship_detail_panel.py`. Heavy mocking;
  most are insulated from the rewrite.
- Existing `test_ship_instance_damage.py` (18 tests) covers
  `get_damaged_components_by_layer`. Adding the new iterator
  alongside leaves these green.
- Canonical pygame_gui fixture: `tests/integration/ui/conftest.py:38–54`
  (autouse `pygame.display.set_mode((1920, 1080))`, cached `ui_manager`
  fixture). Ship factories: `tests/conftest.py` (`ship_factory`).
- Estimated new tests: **18–22**. Distributed across iterator (5–7),
  grouping function (3–5), widget rendering (8–10).

### Pattern Scout
- Module-level pure-function colocation precedent confirmed at
  [planet_report_panel.py](../../../game/ui/panels/planet_report_panel.py)
  (`_projection_grid_rows`, `_qty_cell`, etc.). Pin the same shape for
  `group_components_by_id`, `ComponentGroup`, `InstanceDamage`.
- Workshop component item visual constants: row height 40 px, icon
  32 px, label area starts at x=45.
- Chevron convention has codebase **inconsistency**: builder/
  structure-list uses `▲`/`▼`, while existing
  `ship_detail_panel.py:351` already uses `▼`/`▶`. **Decision: keep
  the existing `▼`/`▶`** within this panel for continuity (changing
  the chevron is out of scope and unrelated to the bug being fixed).
- Strikethrough: pygame_gui has **no native `<s>` rich-text support**.
  Only precedent is manual `pygame.draw.line()` overlay in
  `game/ui/screens/test_lab/dialogs.py`. Adopt that pattern.

### Risks Resolved
1. **Division-by-zero on `max_hp = 0`** — addressed in plan: damage
   helpers must guard with `0% if max_hp == 0`. Render `"N/A"` for
   such instances.
2. **`is_active` semantic conflation (damage vs manual vs resource)**
   — user clarified: distinguish damage-induced inactive (HP < damage
   threshold → red + strike) from manual-disable (HP intact → muted
   grey, no strike). See decisions.md.
3. **Empty / missing `design_data['layers']`** — iterator returns
   empty dict; panel renders "No components" placeholder.
4. **Per-tick rebuild churn on toggle** — accepted as out of scope.
   Documented in code comment.
5. **`component_id` rename across saves** — covered by CLAUDE.md
   "Saves are disposable" policy. Iterator falls back to `display_name`
   on unknown ids; never crashes.
6. **Auto-expand vs manual collapse** — user clarified: re-fire
   auto-expand on every ship selection (no manual-collapse
   persistence). See decisions.md.
7. **Armor "functional" semantics** — `is_active` already follows the
   damage-threshold rule uniformly per
   `ComponentHealthManager.take_damage` at line 73–75. Armor counted
   the same way as everything else; documented for player clarity in
   the UI style guide note.
8. **Per-ship state isolation** — auto-expand re-fires per selection,
   so per-ship state isn't required. `expanded_layers` and
   `expanded_groups` reset on `update_ship` to deterministic defaults
   computed from the new ship.

---

## Phases

### Phase 1: Strategy data helper [Simple]
**Objective:** Add `ShipInstance.iter_all_components_by_layer()` and
the `ComponentInstanceView` dataclass; cover with unit tests.
**Status:** Not Started — see [phase_1_checklist.md](phase_1_checklist.md).

### Phase 2: Widget rewrite [Medium]
**Objective:** Replace `_build_damage_section` with
`_build_component_section`. Add module-level dataclasses + grouping
function. Implement strikethrough overlay helper. Cover with widget
tests.
**Status:** Not Started — see [phase_2_checklist.md](phase_2_checklist.md).

### Phase 3: Documentation + closeout [Simple]
**Objective:** Update `docs/06_UI_STYLE_GUIDE.md` with the new
read-only-component-grouping pattern. Update Work Log; archive triage
findings; update `Tracking/projects_index.md`.
**Status:** Not Started — see [phase_3_checklist.md](phase_3_checklist.md).

---

## Verification Checklist

### Project Start (REQUIRED — done as part of planning)
- [x] Read `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`,
  `docs/03_CONVENTIONS.md`.
- [x] Read task-specific docs: `docs/06_UI_STYLE_GUIDE.md` referenced.
- [x] Run full test suite (sharded). Baseline:
  **15893 passed | 0 failed | 0 errors** in 52.4 s.

### After Each Phase
- [ ] Run `pytest tests/ --testmon` — all affected tests pass.
- [ ] Manual test: open Fleet Report, select healthy + damaged + ship
  with destroyed components — confirm correct rendering per phase
  goals.
- [ ] Update Current State block.

### Final Verification
- [ ] Open Fleet Report on a strategy save.
- [ ] Select a fully healthy ship — `COMPONENT STATUS` section
  renders, every layer collapsed, every group row reads `0% avg
  damage` and `<N>/<N>` functional.
- [ ] Run a battle that destroys 2 components on a ship.
- [ ] Re-select the damaged ship — affected layers auto-expanded;
  group rows show correct average % + `<functional>/<total>`;
  per-instance rows render destroyed instances in HP_DESTROYED grey
  + strike; damage-induced inactive (HP below threshold but not 0)
  rendered HP_CRITICAL red + strike.
- [ ] Manually toggle a healthy component off via design — confirm it
  renders in muted grey **without** strike.
- [ ] Toggle layer collapse manually; switch ships and switch back —
  auto-expand re-fires deterministically.
- [ ] Save → exit → reload — damage state persists; panel rebuilds
  the same view.
- [ ] Run `python Tools/test_sharded/test_sharded.py` — full suite
  green; no regressions on the 15893-test baseline (modulo new tests
  added).
- [ ] Verify `docs/06_UI_STYLE_GUIDE.md` updated with the new pattern
  + bumped `Last verified:` date.

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] Phase 1 complete.
- [ ] Phase 2 complete.
- [ ] Phase 3 complete.
- [ ] All tests passing.
- [ ] User verified.
