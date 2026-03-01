# PROJ-208: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Review
- **Review:** [2026-02-27_211111_general_facade-bypass-layering-violations](../../Reviews/results/2026-02-27_211111_general_facade-bypass-layering-violations/)
- **Command Gap Analysis:** [command_gap_analyst_report.md](../../Reviews/results/2026-02-27_211111_general_facade-bypass-layering-violations/findings/command_gap_analyst_report.md)
- **DTO Coverage Analysis:** [dto_coverage_analyst_report.md](../../Reviews/results/2026-02-27_211111_general_facade-bypass-layering-violations/findings/dto_coverage_analyst_report.md)

## Architecture Pattern

All UI state mutations follow the same pattern:

```
UI Action -> Construct Command -> facade.handle_command(cmd) -> Handler validates -> Handler mutates domain -> Return ValidationResult
```

### Existing Pattern to Follow
See how `IssueMoveCommand` works end-to-end:
1. `commands.py`: `@dataclass class IssueMoveCommand(Command): fleet_id: int; target_hex: HexCoord`
2. `command_handlers.py`: `MoveCommandHandler.handle()` validates and mutates
3. `strategy_session_facade.py`: `handle_command()` delegates to `GameSession`
4. UI: `facade.handle_command(IssueMoveCommand(fleet_id=..., target_hex=...))`

---

## New Command Specifications

### Phase 1: Fleet Management Commands

#### 1. SplitFleetCommand
```python
@dataclass
class SplitFleetCommand(Command):
    """Remove ships from a fleet and create a new fleet."""
    fleet_id: int
    ship_instance_ids: List[str]  # instance_id strings from ShipInfo
```
**Validation:**
- Fleet exists and belongs to current player
- All ship_instance_ids belong to the fleet
- At least one ship remains in source fleet after split
- Fleet is not currently executing orders that would be invalidated

**Handler logic:**
1. Remove ships from source fleet
2. Generate new fleet ID via empire
3. Create new Fleet at same location
4. Add ships to new fleet (triggers speed recalculation)
5. Register new fleet with empire
6. Return success with new fleet_id in result

**Replaces:** `fleet_report_window.py:235-286` (direct fleet.remove_ship, Fleet() constructor, empire.add_fleet)

#### 2. DeleteFleetOrderCommand
```python
@dataclass
class DeleteFleetOrderCommand(Command):
    """Remove a specific order from a fleet's order queue."""
    fleet_id: int
    order_index: int
```
**Validation:**
- Fleet exists
- order_index is valid (0 <= index < len(orders))

**Handler logic:**
1. Pop order at index
2. If index == 0 (active order), invalidate fleet.path
3. Return the removed order in result (for undo support)

**Replaces:** `fleet_orders_window.py:295-307` (direct fleet.orders.pop + fleet.path = [])

#### 3. ReorderFleetOrderCommand
```python
@dataclass
class ReorderFleetOrderCommand(Command):
    """Move a fleet order up or down in the queue."""
    fleet_id: int
    order_index: int
    direction: int  # -1 for up, +1 for down
```
**Validation:**
- Fleet exists
- order_index is valid
- Target index (order_index + direction) is valid

**Handler logic:**
1. Swap orders at index and index+direction
2. If either index is 0 (active order affected), invalidate fleet.path
3. Return success

**Replaces:** `fleet_orders_window.py:281-293` (direct orders swap + fleet.path = [])

### Phase 2: Build Queue Commands

#### 4. AddToConstructionQueueCommand
```python
@dataclass
class AddToConstructionQueueCommand(Command):
    """Add a design to a planet or fleet construction queue."""
    entity_id: int
    entity_type: str  # "planet" or "fleet"
    design_id: str
    category: str  # "complex", "ship", "satellite", "fighter"
    index: Optional[int] = None  # None = append, int = insert at position
    target_planet_id: Optional[int] = None  # For complexes built at fleet yards
```
**Validation:**
- Entity exists and can build this category
- Design exists in registry
- If index specified, index is valid

**Handler logic:**
1. Look up design, calculate build time/cost
2. Create queue item dict
3. Insert at index or append to queue
4. Return success

**Replaces:** `build_queue_controller.py:413-538` (direct construction_queue.insert/append)

#### 5. RemoveFromConstructionQueueCommand
```python
@dataclass
class RemoveFromConstructionQueueCommand(Command):
    """Remove an item from a construction queue."""
    entity_id: int
    entity_type: str  # "planet" or "fleet"
    item_index: int
```
**Validation:**
- Entity exists
- item_index is valid

**Handler logic:**
1. Pop item from queue
2. If fleet context and queue becomes empty, handle BUILD order cleanup
3. Return removed item in result

**Replaces:** `build_queue_screen.py:301-315` (direct queue.pop), `build_queue_drag_handler.py:182` (direct queue.pop during drag)

#### 6. ReorderConstructionQueueCommand
```python
@dataclass
class ReorderConstructionQueueCommand(Command):
    """Move a construction queue item to a new position."""
    entity_id: int
    entity_type: str
    from_index: int
    to_index: int
```
**Validation:**
- Entity exists
- Both indices valid

**Handler logic:**
1. Pop item from from_index
2. Insert at to_index
3. Return success

**Replaces:** `build_queue_drag_handler.py:180-198` (drag-and-drop via pop+insert)

### Phase 3: Research Commands

#### 7. SetResearchBudgetCommand
```python
@dataclass
class SetResearchBudgetCommand(Command):
    """Set the RP budget per turn for an empire."""
    empire_id: int
    budget: int
```
**Validation:** Budget within min/max bounds
**Replaces:** `research_controls.py:268-271` (direct tracker.set_rp_budget)

#### 8. SetResearchAllocationCommand
```python
@dataclass
class SetResearchAllocationCommand(Command):
    """Set RP allocation for a specific research node."""
    empire_id: int
    node_id: str
    allocation: int
```
**Validation:** Node available for research, allocation within remaining RP
**Replaces:** `research_controls.py:275-285` (direct tracker.set_allocation)

#### 9. SpreadResearchRPCommand
```python
@dataclass
class SpreadResearchRPCommand(Command):
    """Spread RP evenly across available research nodes."""
    empire_id: int
```
**Validation:** Empire has research tracker
**Replaces:** `research_controls.py:350-362` (direct tracker.spread_rp_evenly)

---

## Routing Fixes (No New Commands Needed)

### facade vs session routing
Two files route through `session.handle_command()` instead of `facade.handle_command()`:
- `strategy_build_queue_manager.py:142,146` — change to facade
- `strategy_window_manager.py:284` — change to facade

### Backward compatibility fallback
- `fleet_orders_window.py:400-404` — Remove `fleet.clear_orders()` fallback, make `_clear_orders_callback` required

---

## Phase 4: DTO Enhancements (Read Path)

### FleetInfo additions
```python
capabilities: Tuple[str, ...] = field(default_factory=tuple)  # Available ability names
```
This eliminates 6 raw Fleet accesses in `strategy_superweapons.py`.

### New facade methods
- `get_colonizable_planets(fleet_id) -> List[PlanetInfo]`
- `get_fleet_capabilities(fleet_id) -> List[str]`
- `get_scuttle_events(turn) -> List[dict]`

### isinstance replacements
- `strategy_build_queue_manager.py:48-49` — Replace `isinstance(obj, Planet)` with `is_planet(obj)` protocol check

---

## What's Working Well (No Changes Needed)
- Fleet movement/combat orders (11 commands, all properly routed)
- Superweapon operations (6 commands, all via facade)
- Transfer/cargo (1 command, properly routed)
- BUILD order lifecycle (2 commands, since PROJ-207)
- DTO infrastructure (10 frozen dataclasses, 20 facade query methods)

## Command Pipeline Coverage After PROJ-208
| Category | Before | After |
|----------|--------|-------|
| Fleet movement/combat | 11/11 | 11/11 |
| Superweapon operations | 6/6 | 6/6 |
| Transfer/cargo | 1/1 | 1/1 |
| Fleet management | 1/4 | 4/4 |
| Build queue | 2/6 | 6/6 |
| Research | 0/3 | 3/3 |
| **Total** | **21/31** | **31/31** |

## Dependencies & Risks
1. **Build queue complexity** — The BuildQueueController has complex multi-queue distribution logic. Commands may need to handle batch operations carefully.
2. **Drag-and-drop** — Two-phase (remove on drag start, insert on drop) needs careful command ordering.
3. **Fleet splitting validation** — Need to handle edge cases (last ship, fleet with orders, fleet mid-movement).
4. **Test coverage** — Each new command handler needs unit tests for both success and failure cases.
