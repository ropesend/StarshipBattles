# Research System Architecture

> **Last verified:** 2026-03-14

This document describes the stochastic tech tree research system.

---

## Overview

The research system uses a **probabilistic "leaky bucket"** model rather than deterministic progress bars. Players allocate Research Points (RP) across tech nodes; each turn, invested RP increases a breakthrough probability, natural decay drains it, and a random roll determines if the tech levels up.

```
game/research/
  __init__.py
  data/
    tech_node.py              # TechNode and TechRequirement dataclasses
    tech_tree.py              # TechTree - loads/validates from JSON
    research_tracker.py       # ResearchTracker - per-session state
  systems/
    research_service.py       # ResearchService - leaky bucket turn processing
```

Data file: `data/techtree.json`

---

## TechTree

`TechTree` is a container of `TechNode` objects loaded from `data/techtree.json`.

### TechNode

Each node represents a technology with multiple levels:

| Field | Type | Description |
|-------|------|-------------|
| `id` | str | Unique identifier (e.g., `"TS1"`) |
| `name` | str | Display name (e.g., `"Astrophysics"`) |
| `max_levels` | int | Maximum achievable level |
| `requirements` | `List[List[TechRequirement]]` | OR-groups of AND-conditions |
| `base_decay` | float | Chance decay per turn (default 0.005) |
| `volatility` | float | RP-to-chance conversion coefficient (default 0.1) |
| `price` | float | Base RP cost multiplier (default 1.0) |
| `price_curve` | str | How price scales: `flat`, `linear`, `quadratic`, `exponential`, `logarithmic`, `sqrt` |

### Requirements (Fuzzy)

Requirements use OR-groups of AND-conditions:
- **Outer list:** Any ONE group being satisfied unlocks the tech.
- **Inner list:** ALL conditions in a group must be met.

Each `TechRequirement` has:
- `node_id` -- prerequisite tech ID
- `level_range` -- `[min, max]` tuple for fuzzy resolution
- `negate` -- if True, requires the prerequisite to be BELOW the resolved level (mutual exclusion)

At session start, `resolve_all_requirements(seed)` locks each fuzzy range to a fixed integer using a seeded RNG, ensuring deterministic but varied prerequisites per playthrough.

### Node Status

`get_status(current_level, tech_levels)` returns:
- `'completed'` -- at max level
- `'available'` -- unlocked, can research
- `'locked'` -- requirements not met

### Price Curves

`get_effective_price(level)` scales the RP cost multiplier by target level:

| Curve | L1 | L2 | L5 | Formula |
|-------|-----|-----|-----|---------|
| `flat` | 1.0x | 1.0x | 1.0x | `price` |
| `linear` | 1.5x | 2.0x | 3.5x | `price * (1 + 0.5 * level)` |
| `quadratic` | 1.2x | 1.8x | 6.0x | `price * (1 + 0.2 * level^2)` |
| `exponential` | 1.5x | 2.25x | 7.6x | `price * 1.5^level` |
| `logarithmic` | 1.7x | 2.1x | 2.8x | `price * (1 + ln(1 + level))` |
| `sqrt` | 2.0x | 2.4x | 3.2x | `price * (1 + sqrt(level))` |

### Validation

`TechTree.validate()` checks for:
- Missing requirement references (node_id not in tree)
- Circular dependencies (DFS cycle detection, skipping negated edges)

### Depth Calculation

`calculate_depth(node_id)` computes layout depth (0 = root) for left-to-right visualization. Cached after first computation.

---

## ResearchTracker

Per-session state manager. Tracks:

- `node_states: Dict[str, NodeState]` -- per-node level, chance, and RP allocation
- `session_seed` -- seed for fuzzy requirement resolution
- `rp_budget` -- total RP available per turn (50-500, default 200)
- `turn_number` -- current turn counter
- `auto_spread_enabled: bool = False` -- when True, automatically spreads RP evenly each turn; persisted in `to_dict()`/`from_dict()`
- `turn_log` -- events from the most recent turn

### NodeState

```python
@dataclass
class NodeState:
    current_level: int = 0
    current_chance: float = 0.0   # Breakthrough probability (0.0 - 0.95)
    rp_allocation: int = 0        # RP allocated per turn (persists across turns)
```

### RP Allocation

- `set_allocation(node_id, rp)` -- clamps to `[0, remaining_budget]`, returns False if clamped
- `clear_allocation(node_id)` / `clear_all_allocations()`
- `spread_rp_evenly(tech_tree)` -- distributes budget equally across all available nodes
- `get_remaining_rp()` -- budget minus total allocated

### Serialization

`to_dict()` / `from_dict()` for save/load support.

---

## Leaky Bucket Algorithm

Implemented in `ResearchService.process_turn()`. For each available node with RP allocation:

### Per-Turn Steps

```
1. DECAY:       current_chance -= base_decay        (clamp at 0.0)
2. INVESTMENT:  added_chance = volatility * ln(1 + effective_rp)
                where effective_rp = rp_allocation / effective_price(target_level)
3. ACCUMULATE:  current_chance += added_chance       (cap at 95%)
4. ROLL:        if random(0.0, 1.0) < current_chance -> BREAKTHROUGH
5. RESET:       on breakthrough, current_chance = 0.0, level += 1
```

### Key Properties

- **Decay creates urgency:** Without investment, accumulated chance drains away.
- **Logarithmic returns:** Doubling RP does not double chance gain (diminishing returns via `ln(1 + rp)`).
- **Price scaling:** Higher levels cost more effective RP based on the node's `price_curve`.
- **95% cap:** Breakthrough is never guaranteed in a single turn.
- **Reset on success:** After leveling up, chance resets to zero -- must rebuild for next level.

### Locked Nodes

Locked nodes still receive decay (chance drains) but cannot receive investment or roll for breakthrough.

### Events

`process_turn()` returns a list of event dicts:
- `'breakthrough'` -- node leveled up (includes roll, chance, RP details)
- `'progress'` -- chance accumulated but no breakthrough
- `'decay'` -- chance decayed (no investment)

### Estimation

`estimate_turns_to_breakthrough(volatility, base_decay, rp)` gives a rough estimate: `0.50 / (added_chance - base_decay)`. Returns infinity if net gain is non-positive.

---

## Data Format

`data/techtree.json`:

```json
{
    "tech_tree": [
        {
            "comment": "--- SECTION HEADER ---",
            "id": "TS1",
            "name": "Astrophysics",
            "max_levels": 8,
            "requirements": [],
            "base_decay": 0.0043,
            "volatility": 0.071,
            "price": 1.42,
            "price_curve": "sqrt"
        },
        {
            "id": "AS33",
            "name": "Stellar Harnessing",
            "max_levels": 6,
            "requirements": [
                [
                    { "node_id": "TS1", "level_range": [1, 3] }
                ]
            ],
            "base_decay": 0.0043,
            "volatility": 0.084,
            "price": 1.37,
            "price_curve": "sqrt"
        }
    ]
}
```

Entries with `comment` but no `id` are section headers and are skipped during loading.

---

## Key Files

| Component | File |
|-----------|------|
| TechNode / TechRequirement | `game/research/data/tech_node.py` |
| TechTree | `game/research/data/tech_tree.py` |
| ResearchTracker / NodeState | `game/research/data/research_tracker.py` |
| ResearchService | `game/research/systems/research_service.py` |
| Tech tree data | `data/techtree.json` |
