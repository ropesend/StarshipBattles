# Phase 8: UI integration

**Status:** Complete (2026-04-27)
**Objective:** Make the Sector panel render storm effects identically to facility effects (using the unified `source_label`); add rate-style value formatting for `EnvironmentalDamage` and `FuelDrain`; strip the per-effect breakdown from the storm detail panel (lore only).

---

## Tasks

### Task 8.1: Use unified `source_label` in `_add_effects_group` [Medium]
**File:** `game/ui/panels/system_tree_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_system_tree_panel.py` (or similar)

- [ ] Read current `_add_effects_group` (around lines 412-492) to understand single-vs-multi-provider rendering.
- [ ] Replace `f"{p['facility_name']} ({p['planet_name']})"` constructions with `p['source_label']`.
- [ ] Single-provider branch: `f"{display_name} {value_str} — {status} ({p['source_label']})"`.
- [ ] Multi-provider branch (collapsible group): `f"{p['source_label']} — {p['status']}"` per child row.
- [ ] Add a test:
  - [ ] `test_storm_effect_renders_with_storm_source_label` — fixture with a storm in the hex; assert tree contains `"Ion Storm Alpha"` as the source label.
  - [ ] `test_facility_effect_renders_with_facility_source_label`.
  - [ ] `test_mixed_storm_and_facility_providers_render_under_one_effect_when_same_ability`.

**Notes:**

### Task 8.2: Add rate-style formatter to `_format_effect_value` [Simple]
**File:** `game/ui/panels/system_tree_panel.py`

- [ ] Read `_format_effect_value` (around lines 494-526).
- [ ] Add cases for the new abilities:
  ```python
  if effect.get('kind') == 'rate':
      v = effect.get('aggregate_value', 0.0)
      if v <= 0:
          return ""
      ability = effect.get('ability_name', '')
      if ability == 'EnvironmentalDamage':
          return f"-{v:.1f}/turn"
      if ability == 'FuelDrain':
          return f"-{v:.1f} fuel/turn"
      return f"{v:.1f}/turn"
  ```
- [ ] Multiplier-style abilities `ThrustModifier`, `StrategicSpeedModifier` get their own formatter:
  ```python
  if ability in ('ThrustModifier', 'StrategicSpeedModifier'):
      v = effect.get('aggregate_value', 1.0)
      if v != 1.0:
          pct = (v - 1.0) * 100
          sign = "+" if pct >= 0 else ""
          return f"{sign}{pct:.0f}%"
  ```
- [ ] Add tests for each new format.

**Notes:**

### Task 8.3: Strip storm effect breakdown from detail panel [Simple]
**File:** `game/ui/screens/strategy_detail_formatter.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_detail_formatter.py`

- [ ] Read `_format_storm` (around lines 410-456 per investigation findings).
- [ ] Remove the per-effect breakdown lines (the lines that print "Shields: -50%", "Speed: -30%", etc.).
- [ ] Keep:
  - Storm name
  - Storm type
  - Description (from `data/storm_types.json`)
  - Size in hexes (`len(storm.occupied_hexes)`)
- [ ] Add a one-line note like `"Effects shown in Sector Effects panel"` so users understand where to look.
- [ ] Add a test:
  - [ ] `test_format_storm_shows_lore_only` — assert output contains description but does NOT contain `-50%` / `-30%` / numeric effect strings.

**Notes:**

### Task 8.4: Manual UI smoke test [Manual]
**File:** N/A (manual)

- [ ] Launch the game.
- [ ] Generate a galaxy with at least one of each storm type.
- [ ] Click on a storm hex. Verify Sector Effects panel shows:
  - For ion storm: `Shield Modifier 0.50x — Active (Ion Storm Alpha)` and `Strategic Speed Modifier -20% — Active (Ion Storm Alpha)`.
  - For radiation belt: `Radiation Damage -0.8/turn — Active (Radiation Belt Beta)` and `Fuel Drain -0.1 fuel/turn — Active (Radiation Belt Beta)`.
- [ ] Click on a planet hex with a complex containing `ShieldModifier sector` — verify it shows alongside any storm effects in the same hex.
- [ ] Click on the storm itself in detail panel — verify lore only, no numbers.
- [ ] Move a fleet into a dark nebula — verify slowdown.
- [ ] End-of-turn in radiation belt — verify hull damage and fuel drain.
- [ ] Resolve combat in two overlapping ion storms — verify shields effective at 0.25× (multiplied per decisions.md).

**Notes:** If the game won't launch, capture the traceback and return to the appropriate phase.

---

## Phase Completion Checklist
- [ ] All tasks complete
- [ ] UI tests green
- [ ] Manual smoke test passes for all six bullets in 8.4
- [ ] `pytest tests/ --testmon` clean
- [ ] Update status to `Complete`
- [ ] Update plan.md
