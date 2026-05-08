# Research System Compact Reference

> **Last verified:** 2026-05-08 - Checked `docs/systems/research_system.md`, the compact ALT source, current `game/research/`, `game/ui/research/`, `data/techtree.json`, and research tests.

The research system is a stochastic tech-tree sandbox. Gameplay state lives in `game/research/`; visualization lives in `game/ui/research/` because UI may import Research, but Research must not import Pygame or UI code.

## Files

| Area | Files | Responsibility |
|---|---|---|
| Data | `data/techtree.json` | Tech definitions under top-level `"tech_tree"`. Currently 143 loadable nodes using all six price curves. |
| Node model | `game/research/data/tech_node.py` | `TechRequirement`, `TechNode`, fuzzy requirements, status checks, price curves. |
| Tree | `game/research/data/tech_tree.py` | `TechTree` loading, requirement resolution, validation, cycle detection, layout depth. |
| Session state | `game/research/data/research_tracker.py` | `NodeState`, `ResearchTracker`, RP budget/allocation, serialization. |
| Turn logic | `game/research/systems/research_service.py` | Stateless leaky-bucket processing and estimation helpers. |
| UI | `game/ui/research/research_scene.py`, `research_controls.py`, `research_renderer.py` | Pannable tech-tree scene, sidebar controls, node/edge drawing. |
| Tests | `tests/unit/research/`, `tests/integration/research_workflow/`, `tests/integration/save_load/test_roundtrip_research.py` | Unit, workflow, UI, and persistence coverage. |

Layer contract:

- `game/research/` may depend on Core and Services only. Keep UI, pygame, and renderer code under `game/ui/research/`.
- `game.research` has no stable package-level public API exports; import concrete classes from their data/system modules.
- `TechTree.load_from_json(file_path=None)` resolves the default as `os.path.join(Paths.DATA_DIR, "techtree.json")`.
- Do not recreate the old `game/research/ui/` path. It was moved to `game/ui/research/` to remove a layer violation.

## Tech Tree

`TechTree.nodes` maps node id to `TechNode`. Loading is tolerant: missing files load an empty tree via `load_json(..., default={"tech_tree": []})`; entries without `id` or `name` are skipped.

`TechNode` fields:

| Field | Default | Contract |
|---|---|---|
| `id` | required | Unique tech id, usually compact uppercase ids in shipped data. |
| `name` | required | Display name. |
| `max_levels` | `1` | Level cap; `current_level >= max_levels` means completed. |
| `requirements` | `[]` | OR-groups of AND-conditions. Empty means root/available. |
| `base_decay` | `0.005` | Chance lost per processed turn. |
| `volatility` | `0.1` | Coefficient for logarithmic RP-to-chance conversion. |
| `price` | `1.0` | Base RP multiplier. |
| `price_curve` | `flat` | `flat`, `linear`, `quadratic`, `exponential`, `logarithmic`, `sqrt`; unknown falls back to `price`. |
| `comment` | `None` | Optional section/comment metadata on real nodes. |

Requirement shape:

```json
"requirements": [
  [
    { "node_id": "TS1", "level_range": [1, 3] }
  ],
  [
    { "node_id": "ALT1", "level_range": [2, 2], "negate": true }
  ]
]
```

- Outer list is OR: any group can unlock the node.
- Inner list is AND: every requirement in that group must pass.
- `TechRequirement(node_id, level_range, resolved_level=None, negate=False)` uses `resolved_level` after `TechTree.resolve_all_requirements(seed)`.
- Normal requirements pass when prereq level is `>= resolved_level`; negated requirements pass when prereq level is below it.
- Missing prereq levels are treated as `0`.
- Negated references are still validated, but negated edges are intentionally ignored by cycle detection.

Warnings:

- Use `level_range`; the loader does not read a legacy `level` key and defaults missing ranges to `(1, 1)`.
- Comment-only entries are skipped only when they have `comment` and no `id`. A node with both `comment` and `id` is loaded and preserves `comment`.
- `TechTree.validate()` returns error strings; it does not raise. Callers decide whether to block or log.

Status and query API:

- `TechNode.get_status(current_level, tech_levels)` returns `completed`, `available`, or `locked`.
- `TechTree.validate_requirements()` checks missing references.
- `TechTree.detect_cycles()` DFS-checks positive dependency cycles.
- `TechTree.validate()` combines missing-reference and cycle errors.
- `calculate_depth()`, `get_nodes_at_depth()`, and `get_max_depth()` support left-to-right visualization and cache depths.
- `get_node()` returns `TechNode | None`; `get_all_node_ids()` returns current keys.

Price curves for target level `L`:

| Curve | Formula |
|---|---|
| `flat` | `price` |
| `linear` | `price * (1 + 0.5 * L)` |
| `quadratic` | `price * (1 + 0.2 * L * L)` |
| `exponential` | `price * (1.5 ** L)` |
| `logarithmic` | `price * (1 + ln(1 + L))` |
| `sqrt` | `price * (1 + sqrt(L))` |

## Tracker

`ResearchTracker(session_seed=None)` owns all session state. If no seed is passed, it generates one with `random.randint(0, 2**31 - 1)`.

`NodeState` serializes exactly:

```python
current_level: int = 0
current_chance: float = 0.0
rp_allocation: int = 0
```

Budget constants:

| Constant | Value |
|---|---|
| `MIN_RP_BUDGET` | `50` |
| `MAX_RP_BUDGET` | `500` |
| `DEFAULT_RP_BUDGET` | `200` |

Tracker API:

- `get_state(node_id)` creates missing `NodeState` entries.
- `get_all_tech_levels()`, `get_total_allocated()`, `get_remaining_rp()`, `get_nodes_with_allocation()` expose derived state.
- `set_allocation(node_id, rp)` clamps negative or over-budget values, logs a warning when clamped, still applies the clamped value, and returns `False` if clamped.
- `set_rp_budget(budget)` clamps to `[50, 500]`; if total allocation exceeds the new budget, allocations scale down proportionally and the last node receives the rounding remainder.
- `spread_rp_evenly(tech_tree, tech_levels=None)` clears current allocations, finds nodes with status `available`, divides budget evenly, and gives remainder RP to the first nodes.
- `increment_turn()`, `set_turn_log(events)`, `clear_allocation()`, `clear_all_allocations()`, and `reset()` are direct state operations.

Serialization:

- `to_dict()` stores `session_seed`, `rp_budget`, `turn_number`, `auto_spread_enabled`, and `node_states`.
- `from_dict()` defaults missing values; no migration logic is provided or desired.
- `turn_log` is runtime UI state and is not serialized.
- `reset()` clears node states, turn number, and turn log, but keeps seed, budget, and `auto_spread_enabled`. The UI Reset button instead creates a new tracker, producing a new seed and default auto-spread state.

## Leaky Bucket

`ResearchService.process_turn(tech_tree, tracker, tech_levels=None)` increments the turn, processes nodes in tree insertion order, writes `tracker.turn_log`, and returns event dicts. It is stateless; all persistent state stays in `ResearchTracker`.

Processing rules:

1. Build tech levels from the tracker, or copy the supplied `tech_levels` dict so caller input is not mutated.
2. Skip completed nodes.
3. Locked nodes can only decay accumulated chance.
4. Available nodes decay first: `current_chance = max(0, current_chance - base_decay)`.
5. If `rp_allocation <= 0`, emit `decay` only when chance changed.
6. Compute `target_level = current_level + 1`.
7. Compute `effective_price = node.get_effective_price(target_level)`.
8. Compute `effective_rp = rp_allocation / effective_price`.
9. Compute `added_chance = volatility * ln(1 + effective_rp)`.
10. Accumulate with cap: `current_chance = min(ResearchService.MAX_CHANCE, current_chance + added_chance)`, where `MAX_CHANCE = 0.95`.
11. Roll with a fresh non-deterministic `random.Random().random()`.
12. If `roll < current_chance`, emit `breakthrough`, increment level, reset chance to `0.0`, and update same-turn tech levels for downstream nodes; otherwise emit `progress`.

Event types:

- `breakthrough`: includes old/new level, max level, chance, roll, raw/effective RP, effective price, and turn.
- `progress`: includes current chance, roll, raw/effective RP, effective price, added chance, decay applied, and turn.
- `decay`: includes old/new chance and decay amount.

Helpers:

- `calculate_added_chance(volatility, rp)` returns `0.0` for `rp <= 0` and does not apply node price. Pass effective RP when price matters.
- `estimate_turns_to_breakthrough(volatility, base_decay, rp)` estimates turns to 50 percent chance and returns infinity when RP or net gain is non-positive.

Core invariants:

- Fuzzy prerequisites are deterministic per session seed; breakthrough rolls are intentionally not deterministic unless tests patch `random.Random`.
- Chance leaks before investment, caps at `0.95`, and resets on breakthrough.
- Locked nodes cannot invest or roll, but accumulated chance still decays.
- RP allocations persist until explicitly changed, cleared, scaled by budget changes, spread evenly, or reset.
- A breakthrough can unlock another node later in the same turn because the local `tech_levels` copy is updated immediately.

## UI Boundary

`ResearchTreeScene` loads `TechTree`, creates a `ResearchTracker`, resolves requirements with `tracker.session_seed`, logs up to five missing-reference errors and five cycle errors, calculates positions by depth, and uses `Camera` over the canvas area.

`ResearchControlPanel` owns the sidebar controls: RP budget, allocation slider, auto-spread toggle, selected-node details, next-turn/reset/close buttons, and a five-turn event log. The allocation slider should use the panel's `_selected_node`, not an external selected id, because selection can change during UI event routing.

`ResearchRenderer` draws dependency lines, node state colors, chance/allocation text, viewport-culls offscreen nodes, quantizes font sizes, and renders negated requirements as dashed red lines. Keep renderer/UI changes under `game/ui/research/`.

## Extension Recipes

Add or edit a tech:

1. Edit `data/techtree.json` under `"tech_tree"`.
2. Use `id`, `name`, `max_levels`, tuning fields, and `price_curve`.
3. Use `level_range: [min, max]` for requirements; use `negate: true` only for exclusions/mutual locks.
4. Run tree validation in a focused test or scene initialization path.
5. Add or update tests under `tests/unit/research/tech_tree/`, `tests/unit/research/test_tech_node.py`, or `tests/unit/research/test_tech_requirement_negation.py`.

Change tracker or persistence behavior:

1. Add the failing round-trip or allocation test first.
2. Keep `to_dict()` and `from_dict()` field names synchronized.
3. Do not add save migration shims for old research saves.
4. Cover with `tests/unit/research/test_research_tracker.py` and `tests/integration/save_load/test_roundtrip_research.py`.

Change leaky-bucket mechanics:

1. Add focused tests in `tests/unit/research/test_research_service.py` or `test_research_service_edge_cases.py`.
2. Preserve the event schema or update UI and integration tests in the same change.
3. If deterministic outcomes are needed, patch `game.research.systems.research_service.random.Random` in tests.

Change research UI:

1. Keep imports and pygame code in `game/ui/research/`.
2. Cover scene lifecycle and events under `tests/unit/research/research_scene/` and `tests/unit/research/research_controls/`.
3. Cover renderer drawing and DI under `tests/unit/research/test_research_renderer*.py` and `test_research_scene_di.py`.

## Tests And Commands

Targeted commands:

```bash
pytest tests/unit/research
pytest tests/unit/research/tech_tree
pytest tests/unit/research/research_scene tests/unit/research/research_controls
pytest tests/integration/research_workflow
pytest tests/integration/save_load/test_roundtrip_research.py
```

Useful combined research sweep:

```bash
pytest tests/unit/research tests/integration/research_workflow tests/integration/save_load/test_roundtrip_research.py
```

Full-suite command:

```bash
python Tools/test_sharded/test_sharded.py
```
