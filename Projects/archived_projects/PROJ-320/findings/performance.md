# PROJ-320 Performance Analysis Report

## Executive Summary

PROJ-320 proposes reducing contested-hex combat invocations from 100 per turn (current) to approximately sum of engaged fleet speeds (5-30 typical). This analysis quantifies performance gains.

## 1. Today's Per-Turn Combat Cost

Profile path:
- turn_engine.py:524 — loop drives 100 ticks per turn
- turn_engine.py:698 — calls resolve_all_conflicts unconditionally each tick
- conflict_resolution_engine.py:247-268 — rebuilds hex_map from scratch every invocation
- conflict_resolution_engine.py:269-374 — each hex invokes run_battle once

Hex-map cost: O(fleets) per tick. With 200 fleets: ~20,000 scan ops per turn.

Battle cost: Each run_battle (SimulationBattleResolver:186-191) compiles spec, materializes ships, runs engine, captures replay (~50ms typical). 100 battles/turn = 5s at one contested hex.

## 2. Expected Savings

Current: 100 contested detections → ≤100 battles/encounter
New: ~(sum of speeds) = 5-30 battles/encounter
- Speed 5 → tick interval 20 (fleet_speed_calculator.py:39)
- 2 fleets @ speed 5 → ~10 rounds per turn

Typical (2 hexes, 2 fleets each, speed 5):
- Today: 200 battles/turn
- New: 20 battles/turn
- Ratio: 10% (10x speedup)

## 3. Hex-map Rebuild

Current: O(fleets) per tick unavoidable.
Opportunity: Event-driven detection only on movement events (Phase 3 outcome, line 695).
Saves: 100x faster scanning if re-architected.

## 4. Per-Fleet-Tick Overhead

New model: if tick % get_tick_interval(speed) == 0 for each fleet.
Cost: ~(fleets × 100) = same as hex-map scan.
Net: Overhead is wash; wins come from fewer battles, not fewer ticks.

## 5. Battle-Runner Setup

With 10x fewer invocations:
- Fewer allocations
- Fewer AI controller instantiations
- Fewer spec compilations (~10ms each)

Estimated win: 10x fewer setups = ~500ms per turn (2 hexes).

## 6. Replay Capture (PROJ-312)

Fewer battles = fewer disk writes.
Today: 100 writes/turn per hex
New: ~10 writes/turn
Savings: ~2-3MB log reduction per turn if heavily contested.

## 7. Event-Bus Log

COMBAT_RESOLVED event fired once per battle (line 107-194).
Today: 100 events/turn
New: ~10 events/turn
Faster save/reload cycles, smaller logs.

## 8. AI Tactical Updates

Fewer combat ticks = fewer AI decision cycles per encounter.
Trade-off: Slightly less frequent reactions, but strategic layer still gets N combat decisions.
Acceptable: Yes, if encounter mechanics remain fair.

## 9. Negative Scenarios

Many low-speed hexes: 10 hexes × 2 fleets @ speed 2 = 50 battles.
Today: 1000 battles. Still 20x win.

N-team spike: 10 fleets @ 1 hex, speeds summed could hit 50+ rounds.
Mitigation: Clarify round combinator (sum vs. max vs. pairwise).

## 10. Regression Test

Recommended: YES
Scenario: 5 contested hexes, 3 empires, 100 turns
Assertions:
- Total battles ≤150 (today: 500+)
- Per-turn time ≤5s (today: 20s+)
Location: tests/performance/test_contested_hex_round_budget.py

## Summary

| Metric | Today | New | Ratio |
|--------|-------|-----|-------|
| Battle invocations (2 hexes) | 200 | 20 | 10% |
| Hex-map scans | 100 | 100 (*) | 1x |
| Per-battle setup | 50ms | 50ms | 1x |
| Total battle time | 10s | 1s | 10% |
| Replay writes | 200 | 20 | 10% |
| Event-log entries | 200+ | 20+ | 10% |
| AI cycles | ~100 | ~10 | 10% |

(*) Unless event-driven re-architecture.

## Conclusions

**Expected speedup factor for typical contested-hex scenario: ~10x**
- 2-5 hexes with 2-3 fleets each at typical speeds (5 hexes/turn)
- 10x reduction in battles + multiplicative setup savings
- Conservative; high-speed fleets see smaller rounds but fewer battles overall

**New performance regression test recommended: YES**
- Scenario: 5 contested hexes, 3 empires, 100 turns
- Assertions: ≤150 total battles, ≤5s per turn with replay
- Location: tests/performance/test_contested_hex_round_budget.py
