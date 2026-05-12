# FEAT-09: Log Resource Depletion Events When Production Is Paused

## Description
When a production tick occurs and there are insufficient resources to complete building, log a structured event indicating:
- Which resource was the limiting factor
- How many of that resource were available
- How many were needed
- Which build yard(s) were unable to progress

Currently, resource shortages are handled silently in `ProductionEngine._process_queue_tick_dynamic()` (line ~279-280) — production pauses but no event is logged and the player receives no notification.

The event logging infrastructure already exists (`EventType`, `EventLog`, `log_event()`). All required data (`expenditure.cost_this_step`, `empire.resource_pool`, queue item details including planet/yard) is already available at the shortage detection point.

### Implementation Notes
- Add a new `EventType` (e.g., `RESOURCE_SHORTAGE` or `PRODUCTION_PAUSED`) in `game/strategy/events/event_types.py`
- Add `log_event()` call in `ProductionEngine._process_queue_tick_dynamic()` at the affordability check failure point
- Event details should include: limiting resource name, amount available, amount needed, build yard identifier (planet + yard type), and the queued item that was blocked

### Screenshot Reference
[![Empire Overview Treasury panel showing construction queue expenses](../../Tools/qa_observer/session_data/20260323_143412/images/bug_capture_144008.png)](../../Tools/qa_observer/session_data/20260323_143412/images/bug_capture_144008.png)

## Priority
Low

## Status
Awaiting Confirmation

## Analysis Report

### Architecture Impact
- **Layers affected:** Strategy layer only (write path) → UI layer (read path, zero changes needed)
- **No cross-layer violations** — EventType is in strategy, ProductionEngine is in strategy, log_event() is in core
- **No new dependencies introduced**
- **EventCategory:** Use existing `PRODUCTION` — no new category needed
- **Event flow:** ProductionEngine → log_event() → GameSession handler → EventLog → Facade → UI (all generic/string-based, no exhaustive matching anywhere)

### Dependency Map
**Files requiring changes (2):**
1. `game/strategy/events/event_types.py` — Add `RESOURCE_SHORTAGE` enum member
2. `game/strategy/engine/production_engine.py` — Add `log_event()` call at affordability check failure (line ~279-280)

**Files requiring test updates (1):**
3. `tests/unit/strategy/events/test_event_types.py` — Update `len(EventType)` assertion from 10 → 11

**Files needing NO changes (all generic/string-based):**
- `game/strategy/events/event_log.py` — Event dataclass accepts any details dict
- `game/strategy/engine/game_session.py` — Handler captures all kwargs generically
- `game/strategy/facade/strategy_session_facade.py` — Queries are category-based, not type-based
- `game/ui/screens/event_log_window.py` — Already displays all PRODUCTION category events
- `game/ui/screens/event_log_data_source.py` — Uses `.get()` with fallback for icons

**Blast radius:** Minimal. Event system uses string-based categories with no exhaustive pattern matching.

### Similar Patterns Found
**Existing event logging pattern in ProductionEngine (e.g., SHIP_BUILT at line ~655):**
```python
log_event(
    EventType.SHIP_BUILT,
    category=EventCategory.PRODUCTION,
    empire_id=empire.id,
    message=f"Built {design_data.get('name', design_id)} at {planet.name}",
    design_id=design_id,
    planet_id=planet.id,
    location_hex=[spawn_loc.q, spawn_loc.r],
    system_name=system_name,
    local_hex=local_hex,
)
```

**Data available at shortage detection point (`_process_queue_tick_dynamic` line ~279):**
| Data | Variable | Available? |
|------|----------|-----------|
| Limiting resource | `expenditure.cost_this_step` | Yes |
| Amount available | `empire.resource_pool` | Yes |
| Amount needed | `expenditure.remaining_cost` | Yes |
| Build location | `colony_or_fleet` (Planet or Fleet) | Yes |
| Blocked item | `item` (queue[0]) — `design_id`, `type` | Yes |
| Empire ID | `empire.id` | Yes |

**No existing "negative" events in production** — all current events are success-only (BUILT). Superweapons have destructive events but from the actor's perspective.

### Scope Assessment
**Complexity Rating: Simple**
- 2 files modified + 1 test assertion update
- Single layer (strategy)
- Existing patterns followed exactly
- Purely additive (no changes to existing behavior)
- <50 LOC new code
- No new test infrastructure needed

**Recommendation: Implement as feature (not project)**

### Design Consideration: Event Frequency
The affordability check runs every tick (100 ticks/turn). Logging on every failed tick would generate up to 100 identical events per turn per blocked queue item. **Should log once per item per turn, not every tick.** Options:
1. Track a `_shortage_logged_this_turn` flag per queue item
2. Log only on the first tick of a turn (tick == 1)
3. Log after the 100-tick loop completes, for items that made no progress

### Documentation Discrepancies
- **Pattern #10 (Event Bus)** in `docs/02_PATTERNS.md` describes the UI-only `EventBus` in `game/ui/screens/builder/event_bus.py` — this is NOT the same as the strategy event logging system (`log_event()` in `game/core/event_logging.py`). No discrepancy, just different systems.
- No code-docs mismatches found in the production system area.

## Requirements Context

**Event type name:** `RESOURCE_SHORTAGE`
**Event frequency:** Once per item per turn (log on first tick where affordability fails, skip subsequent ticks for same item)
**Visibility:** Event log only — no additional UI notifications or popups
**Detail level:** Specific resource — identify the bottleneck resource, amount available, and amount needed
**Additive only:** No changes to existing behavior — production still pauses silently; the event is purely informational

## Complexity Assessment

| Criterion | Value |
|-----------|-------|
| **Lines of Code Affected** | ~30 new LOC (enum + log call + dedup logic + tests) |
| **Files Requiring Changes** | 2 production files + 1 test assertion |
| **New Abstractions Needed** | None |
| **Test Infrastructure** | Existing — extend production engine tests |
| **Cross-Layer Changes** | None — strategy layer only |

**Complexity Rating: Simple** (1-3 files, single layer, existing patterns, <100 LOC)

## Implementation Strategy

**Ordered file modification list:**

1. **`game/strategy/events/event_types.py`** — Add `RESOURCE_SHORTAGE = "resource_shortage"` to EventType enum
2. **`game/strategy/engine/production_engine.py`** — At the affordability check failure in `_process_queue_tick_dynamic()`:
   - Determine the limiting resource (the one with highest `needed / available` ratio from `expenditure.cost_this_step` vs `empire.resource_pool`)
   - Add dedup: use a set (e.g., `_shortage_logged`) passed into or tracked on the queue item to avoid logging the same item multiple times per turn
   - Call `log_event(EventType.RESOURCE_SHORTAGE, category=EventCategory.PRODUCTION, ...)` with details: `design_id`, `item_type`, `limiting_resource`, `available`, `needed`, `location_hex`, and build context
3. **`tests/unit/strategy/events/test_event_types.py`** — Update `len(EventType)` assertion from 10 → 11
4. **New test(s)** — Add test in production engine tests verifying:
   - Event is logged when affordability fails
   - Event contains correct limiting resource details
   - Event is logged only once per item per turn (dedup)

**Test strategy:** Write tests first (TDD), then implement.

## Work Log
- 2026-03-23: Created from QA Session 20260323_143412.
- 2026-03-23: Deep dive Phase 0-1 complete. Agent swarm explored architecture impact, dependencies, patterns, and scope. Feature is Simple complexity — 2 files + 1 test update. Key design question: event frequency (once per turn vs every tick).
- 2026-03-23: Phase 2-4 complete. User confirmed: RESOURCE_SHORTAGE name, once-per-item-per-turn frequency, event log only, specific resource details. Implementation strategy written.
- 2026-03-23: Phase 5 — TDD implementation complete. Changes:
  - `game/strategy/events/event_types.py`: Added `RESOURCE_SHORTAGE = "resource_shortage"` to EventType enum
  - `game/strategy/engine/production_engine.py`: Added `_log_resource_shortage()` helper + dedup via `_shortage_logged` flag on queue items (reset on tick 1)
  - `tests/unit/strategy/events/test_event_types.py`: Updated count assertion (10→11), added value test
  - `tests/unit/strategy/engine/test_production_refactor.py`: Added 5 tests in `TestResourceShortageEventLogging` class
  - All 913 strategy tests pass, 0 failures. No docs changes needed.
