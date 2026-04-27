# `component_damage` Call-site Audit — Phase 1

**Date:** 2026-04-16
**Scope:** All production (`game/`) occurrences of `component_damage` —
field definitions, reads, writes, docstrings.

Classification key:
- **DEF** — field definition, parameter default, or docstring
- **READ** — reads `instance.component_damage.get(...)` / `[...]` / `in`
  / passes it to a consumer
- **WRITE** — mutates: assignment, `.clear()`, `.update()`, `[k]=v`

---

## Summary Table

| File | DEFs | READs | WRITEs | Dead? | Notes |
|---|---|---|---|---|---|
| `game/strategy/data/ship_instance.py` | 2 | 5 | 1 | live | field + ctor default + `is_damaged()`, `get_damaged_component_count`, `get_damaged_components_by_layer`, `repair()` clear |
| `game/strategy/services/ship_stats_calculator.py` | 7 | 13 | 0 | **DEAD** | No production importers — see [Dead Module Finding](#dead-module-finding) below |
| `game/strategy/data/ship_instance_bridge.py` | 0 | 2 | 2 | live | `to_ship` legacy-path read, `update_from_ship` mirror write + clear |
| `game/strategy/combat/post_battle_hook.py` | 0 | 1 | 2 | live | L155-162 dual-write ("Mirror legacy"): `= {}` then conditional `[comp_id] = ...` |
| `game/strategy/data/ship_instance_serializer.py` | 0 | 3 | 0 | live | serializer reads ship.component_damage → save dict, reads save → constructs with `component_damage=`, clone reads |
| `game/strategy/data/component_state.py` | 2 | 0 | 0 | DEF | docstring references only |
| `game/simulation/entities/ship_design_stats.py` | 2 | 2 | 0 | **LIVE HOT PATH** | `calculate_design_stats(component_damage=…)` param + `_lookup_damage` — reached from every `ShipInstance.get_calculated_stats()` |
| `tests/fixtures/strategy_entities.py` | 0 | 0 | 1 | fixture | `component_damage={"laser_1": 5}` construction |
| **TOTAL (production)** | **13** | **26** | **6** | | **45 occurrences**. Plan said 47; actual grep = 45 in game/ + 1 fixture = 46. |

---

## Dead Module Finding

**`game/strategy/services/ship_stats_calculator.py` has zero production
importers. Verified via:**

```
grep "from game.strategy.services.ship_stats_calculator" game/   # no hits
grep "ship_stats_calculator" game/ -i                            # no hits outside that file
```

All 37 callers live in `tests/unit/strategy/ship_stats/*.py`. The
static-helper `has_warp_capability` was duplicated into
`game/strategy/services/component_inspector.py:302`, and that is the
function everyone imports.

**Production stat-calculation call graph (verified):**

```
ShipInstance.get_calculated_stats()
    game/strategy/data/ship_instance.py:337
  → calculate_design_stats(design_data, registries, component_damage, component_toggles)
    game/simulation/entities/ship_design_stats.py:16
  → Ship.from_dict() + ship.recalculate_stats()     # per-component HP set at L58-62
    (ship.recalculate_stats uses simulation-layer ShipStatsCalculator,
     NOT the strategy-layer one)
```

So the strategy-layer `ShipStatsCalculator` — the class the design doc
calls "the hardest migration … a stat calculation hot path" — is in
fact never reached in production. The ~13 `component_damage` READ sites
in that file are dead code.

**Implication for Phase 2:** the plan's biggest phase is ~13 live
production reads, all concentrated in `ship_design_stats.py::
calculate_design_stats`+ `_lookup_damage` (4 occurrences total).
Everything else in `ship_stats_calculator.py` should be deleted, not
migrated (Clean-Sheet Rule + System Migration Policy).

**THIS CHANGES PROJECT SCOPE — PAUSED for user sign-off before
proceeding. See session summary.**

---

## Per-file Detail (every production occurrence)

### `game/strategy/data/ship_instance.py`

| Line | Code | Class |
|---|---|---|
| 113 | `component_damage: Dict[str, int] = field(default_factory=dict)` | DEF (field) |
| 122 | `# \`component_damage\` above is kept in sync ...` | DEF (docstring) |
| 300 | `bool(self.component_damage) or` | READ (is_damaged) |
| 350 | `self.component_damage,` passed to `calculate_design_stats` | READ |
| 524 | `return len(self.component_damage)` | READ (get_damaged_component_count) |
| 559 | `if not self.component_damage:` | READ (get_damaged_components_by_layer) |
| 577 | `for comp_id, current_hp in self.component_damage.items():` | READ (same) |
| 635 | `self.component_damage.clear()` | WRITE (repair full-heal) |

### `game/strategy/services/ship_stats_calculator.py` — DEAD

All uses are within the module's own `calculate_stats` /
`get_component_effectiveness` / `_get_warp_effectiveness` /
`_accumulate_warp_stats` / `_get_current_hp` methods. 13 READ references
to the parameter + 7 DEFs (param types & docstrings). 0 WRITEs.

Lines: 89, 96, 113, 114, 181, 228, 257, 272, 277, 278, 296, 316, 328,
340, 355, 367, 616, 625, 626, 629. Not enumerated individually since
this module is proposed for **deletion**.

### `game/strategy/data/ship_instance_bridge.py`

| Line | Code | Class |
|---|---|---|
| 88 | `# legacy \`component_damage\` dict (single-instance granularity)` | DEF (doc) |
| 106 | `for comp_id, target_hp in self._ship.component_damage.items():` | READ (to_ship legacy fallback — reached only when `components` is empty) |
| 146 | `self._ship.component_damage.clear()` | WRITE (update_from_ship) |
| 154 | `# Legacy \`component_damage\` mirror (first instance wins, ...)` | DEF (doc) |
| 156 | `if comp.current_hp < comp.max_hp and comp.id not in self._ship.component_damage:` | READ |
| 157 | `self._ship.component_damage[comp.id] = comp.current_hp` | WRITE |

### `game/strategy/combat/post_battle_hook.py`

| Line | Code | Class |
|---|---|---|
| 13 | docstring: `\`component_damage\` is cleared` | DEF |
| 153 | docstring: `Mirror legacy \`component_damage\` ...` | DEF |
| 155 | `instance.component_damage = {}` | WRITE (reset) |
| 159 | `# without recomputing max_hp here — callers of component_damage` | DEF (doc) |
| 161 | `if cs.component_id not in instance.component_damage:` | READ |
| 162 | `instance.component_damage[cs.component_id] = int(cs.current_hp)` | WRITE |

### `game/strategy/data/ship_instance_serializer.py`

| Line | Code | Class |
|---|---|---|
| 34 | `'component_damage': ship.component_damage` (to_dict) | READ |
| 104 | `component_damage=data.get('component_damage', {})` (from_dict) | READ |
| 161 | `component_damage=copy.deepcopy(ship.component_damage)` (clone) | READ |

### `game/strategy/data/component_state.py`

| Line | Code | Class |
|---|---|---|
| 12 | docstring: `Coexists with the older \`ShipInstance.component_damage: ...` | DEF |
| 14 | docstring: `\`component_damage\` continues to serve` | DEF |

### `game/simulation/entities/ship_design_stats.py` — **LIVE HOT PATH**

| Line | Code | Class |
|---|---|---|
| 19 | `component_damage: Optional[Dict[str, int]] = None,` | DEF (param) |
| 31 | docstring: `component_damage: Optional dict ...` | DEF |
| 58 | `if component_damage:` | READ |
| 60 | `hp = _lookup_damage(comp.id, comp.max_hp, component_damage)` | READ |
| 103 | `def _lookup_damage(comp_id: str, max_hp: float, damage: Dict[str, int]) -> float:` | DEF |
| 105-113 | `_lookup_damage` body — `in damage`, `damage[comp_id]`, `damage.items()`, prefix-match | READ (3×) |

This is the function that actually runs in production. 4 READ
occurrences total. This is Phase 2's real work.

### `tests/fixtures/strategy_entities.py`

| Line | Code | Class |
|---|---|---|
| 314 | `component_damage={"laser_1": 5},` in fixture construction | WRITE (fixture) |

---

## Totals

- Production occurrences: **45** (13 DEF + 26 READ + 6 WRITE)
- Fixture occurrence: **1**
- Dead (strategy/ship_stats_calculator.py): **20 of 45**
- Truly live and needing migration: **25**
- Of the 25 live, **4** are the production stat-calc hot path
  (ship_design_stats.py).

Plan's "~47 production call sites" was close but the
"stat_calc 20 sites is the biggest migration" claim is wrong — those
20 sites are in dead code.
