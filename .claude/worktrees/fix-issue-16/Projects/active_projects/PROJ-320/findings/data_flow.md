# PROJ-320 Swarm Combat Model — Data Flow Impact Analysis

## Executive Summary

The new per-fleet-per-movement-opportunity combat trigger model reduces invocations from ~100/contested-hex/turn to sum(engaged_fleet_speeds). This analysis traces state mutations through serializers, DTOs, events, and rollback snapshots. **Critical finding:** the model is entirely stateless; no new persistent Fleet fields are required.

---

## 1. Fleet State Additions

**Current serialized fields** (Fleet.to_dict, lines 461-492):
- `id`, `owner_id`, `location`, `speed`
- `display_name` (FEAT-17)
- `ships` (ShipInstance[])
- `orders`, `path` (Order[] + HexCoord[])
- `construction_queue`, `construction_queue_paused`
- `task_forces`, `fleet_policy` (optional)

**New fields needed:** NONE.

**Rationale:**
- Combat eligibility derives from: `tick % (100 / fleet.speed) == 0` plus post-movement location collision check.
- No debounce, counter, or flag needed; the tick interval itself throttles invocations deterministically.
- Per-user confirmation in PROJ-320 context: "stateless: derive from tick % interval == 0 plus post-movement location check."

**Backwards compatibility:** Existing saves load without modification.

**Severity:** LOW — no schema change.

---

## 2. DTO Impact (FleetInfo, FleetInfoExtended)

**Examined:** game/strategy/facade/dto/fleet_dto.py (lines 56-238)

**FleetInfo fields** (lines 56-103):
- Fleet identity, location, speed, composition
- Orders, path, construction, cargo resources, carried items
- NO "rounds remaining" or "combat state" fields

**Impact assessment:**
- UI consumers (EventLogWindow, StrategyScreen) display fleet snapshots post-turn, not per-tick.
- No UI element tracks "rounds remaining at current encounter" (not exposed in facades).
- Combat state remains internal to ConflictResolutionEngine; audited via COMBAT_RESOLVED events.

**Required changes:** NONE.

**Severity:** NONE.

---

## 3. COMBAT_RESOLVED Event Payload

**Current** (ConflictResolutionEngine._log_combat_result, lines 107-194):
Payload carries: participating_fleet_ids, surviving_fleet_ids, destroyed_fleet_ids, location_hex, system_name, storm_names, replay_id.

**Proposed additions:** OPTIONAL
- `triggering_fleet_id: int` — debug/audit only.
- `round_number: int` — ordinal within encounter; no consumer requests it.

**Event log consumption** (EventLogWindow, lines 63-120):
- VirtualTable renders columns: Turn, Empire, Message, Details, Replay button.
- All combat events treated identically; no round-level filtering.

**Required changes:** OPTIONAL (defer unless debug tracing needed).

**Severity:** OPTIONAL.

---

## 4. ConflictResult Shape

**Current** (ConflictResolutionEngine, lines 42-45):
```python
@dataclass
class ConflictResult:
    combats_resolved: int
    fleets_destroyed: List[int]
```

**Semantics change:**
- Old: combats_resolved = 1 per contested hex per turn.
- **New:** combats_resolved = sum(engaged_fleet_speeds) / 100 × tick_count (potentially 5–30 per encounter).

**Callers** (grep results):
- TurnEngine._time_phase() — logs execution time only; does NOT inspect result.
- Test assertions: `assert result.combats_resolved == 1` must relax to `>= 1`.
- No production code branches on combats_resolved.

**Required changes:** Update test assertions; document semantics.

**Severity:** MEDIUM (test maintenance).

---

## 5. BattleResult.replay_id Plumbing

**Current** (ConflictResolutionEngine, line 373):
```python
replay_id=getattr(result, "replay_id", None),
```

**Replay store** (game/strategy/services/replay_store.py, lines 56–86):
- ReplaySettings.max_replays_per_save default = 50.
- Ring buffer eviction: write, then delete oldest beyond cap.

**Impact assessment:**
- Old model: ~100 replays/turn = 5,000/100-turn game → evicts immediately.
- **New model:** ~15–30 rounds/encounter × ~5 encounters/turn ≈ 150 replays/100 turns → well under cap.
- Ring buffer cap needs NO adjustment; it becomes far less critical.

**Required changes:** NONE (cap is safe).

**Severity:** NONE.

---

## 6. Snapshot Rollback

**Examined:** game/strategy/engine/turn_state_snapshot.py (lines 23–68)

**Fleet fields round-tripped via to_dict() / from_dict():**
All 11 serialized fields are captured and restored with graceful .get(key, default) pattern.

**If new Fleet fields added:**
- Must appear in to_dict() output.
- Must be restored in from_dict() with graceful default.
- TurnStateSnapshot.restore() deserializes via Empire.from_dict() → Fleet.from_dict(); no special handling needed.

**Example pattern** (fleet.py, line 575):
```python
fleet.construction_queue_paused = data.get('construction_queue_paused', False)
```

**Required changes:** NONE (no new fields).

**Severity:** NONE.

---

## 7. Backwards Compatibility

**Pattern example** (Fleet.from_dict, lines 532–575):
All optional fields use `.get(key, default)` for safe loading of old saves.

**If new stateless field added later:**
- `data.get('new_field', computed_default)` — compute at deserialization, not storage.

**Impact assessment:**
- No new fields needed; no compatibility burden now.
- Established .get() pattern is ready for future additions.

**Severity:** LOW (no action required now).

---

## 8. AI / Strategic Scoring Impact

**Examined:** game/ai/ (10 files), game/strategy/services/

**Findings:** ZERO references to ConflictResult, combats_resolved, or turn-level combat statistics.

**AI subsystem:**
- Reads fleet state (location, ships, orders, health) for decision-making.
- No combat audit queries.

**Strategic scoring:**
- Reads empire/fleet/planet data for cost/evaluation.
- No turn-level combat statistics.

**Impact assessment:**
- AI decision-making is UNAFFECTED by combat frequency change.
- No recalibration needed.

**Required changes:** NONE.

**Severity:** NONE.

---

## 9. Event Log Empire-ID Quirk

**Current** (ConflictResolutionEngine._log_combat_result, lines 163–169):
```python
empire_id = min(owner_ids) if owner_ids else 0
```

**Event volume verification:**

- **Old model:** 100 ticks × ~1 contested hex/turn ≈ 100 COMBAT_RESOLVED events.
- **New model:** sum(engaged_fleet_speeds) rounds per encounter × ~5 encounters/turn ≈ 15–150 events.
- **Net:** FEWER events overall per turn, as asserted.

**Event log filter (empire_id):**
- Filter logic unchanged; no swamping risk.

**Required changes:** NONE; assertion holds.

**Severity:** NONE.

---

## Summary Table

| Item | Current State | Change Required | Severity |
|------|---------------|-----------------|----------|
| Fleet fields | 11 serialized | None | NONE |
| FleetInfo/DTO | No combat state | None | NONE |
| COMBAT_RESOLVED event | 8 payload fields | Optional fields | OPTIONAL |
| ConflictResult | combats_resolved: int | Test assertions adapt | MEDIUM |
| Replay store | Cap = 50 replays | None | NONE |
| Snapshot rollback | All fields round-trip | None | NONE |
| Backwards compat | .get(key, default) | Follow pattern | LOW |
| AI / scoring | No combat audit | None | NONE |
| Event log | ~100 events/turn | ~15–150 (fewer) | NONE |

---

## Final Verdict

**New persistent state required:** **NO**

Model is stateless. Combat triggers are computed per tick; no flags or counters stored.

**Event payload schema change:** **OPTIONAL**

Current payload is sufficient. Optional debug fields could be added without breaking existing code (dict.get fallback).

---

Report generated: Data Flow Tracer (READ-ONLY mode)
Scope: game/strategy/* serialization, events, snapshots, DTOs
