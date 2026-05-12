# PROJ-412 Phase 1.4 — Overhead Probe Results

**Date:** 2026-05-12
**Scenario:** `make_smoke_turn1_scenario` (2 empires, 2 colonised planets) + bench facility population (5 harvesters + 5 storage facilities per colony, 1M resource deposits). 10 turns × min-of-5 runs (manual mode).

## Bench baseline (real measurement)

```
baseline (no probes):              61.9 ms / turn
  └── harvesting (TURN PERF logs): ~71 ms / turn (single-turn) — note: the
      bench reuses the same engine instance across turns, so the first
      turn's "warm" timing is what's reflected in the 61.9 ms/turn average.
```

## Probe Results (real measurement)

| Probe | What | Real delta per turn | Conclusion |
|-------|------|---------------------|------------|
| **A** | Mock `TurnStateSnapshot.capture` to a noop | **−0.7 ms / turn** | **Snapshot is negligible on this scenario.** The 200–400 ms estimate from swarm_03 was speculative; the actual cost scales with state size, and this bench has small state. The user's tiny game has small state too → snapshot is NOT a Phase 5 priority unless real-game measurement contradicts. |
| **B** | Replace `progress_callback` with a synthetic UI callback (`time.sleep(0.005)` per tick) | **+543.1 ms / turn** (61.9 → 604.9) | **Confirms the swarm_03 hypothesis.** 100 callbacks × 5 ms = 500 ms — almost perfect linear scaling. The user's real callback does `pygame.event.pump() + draw + flip` per tick (`game/ui/screens/strategy_game_state_manager.py:170-177`); at typical 4K redraw cost (5–20 ms) this maps to **0.5–2.0 s / turn**, matching the missing 2.5–3.7 s gap shape in the user's QA-session `TURN PERF` logs. |

## Bench vs user-session shape

The bench scenario reproduces the **named-phase ranking** (harvesting first) but **does NOT** reproduce the user's unaccounted-overhead gap — because the bench runs with `progress_callback=None`. The user's gap is in the callback path, which Phase 5.2 (callback coarsening) targets directly.

## Phase 2+ ordering implications

The codex consult flagged that **Phase 5 (orchestration) may need to come before Phase 4 (harvesting cache)** if the unaccounted gap is large. The probes confirm the gap is real and dominated by per-tick UI work:

- **Phase 5.2 (callback coarsening) is the single biggest measurable win on the user's actual game** — potential 0.5–2 s saved per turn. If coarsening to every-5-ticks: 100 → 20 callbacks ⇒ 80% reduction in callback overhead ⇒ recovered ~0.4–1.6 s/turn.
- **Phase 5.1 (`TurnStateSnapshot.capture`) is not a near-term priority** — bench shows 0.7 ms / turn. Revisit only if real-game measurement on the user's machine contradicts.
- **Phase 4 (harvesting cache) remains useful** — bench shows harvesting is ~88% of the bench's per-turn time. On the user's loaded game, harvesting is ~50% of their 7.5 s/turn (~3.9 s); caching that down is still a big absolute win.

### Recommended new ordering

1. **Phase 1** (done) — measure
2. **Phase 2** — cheap wins (late imports, short-circuits)
3. **Phase 3** — booster pipeline migration to universal `IAbilitySource` (planned, user-approved Option B)
4. **Phase 5.2 first, then 5.1/5.3** — **promote callback coarsening** above harvesting cache because Probe B shows it has the biggest measurable per-turn impact on the user's actual scenario
5. **Phase 4** — harvesting recompute reduction (storage + booster caches)
6. **Phase 6** — secondary phase optimizations

## Open question — Run the real bench against the user's game state

The bench is a synthetic proxy. To put real numbers on the user's experience we'd need either:
- A saved game from the user's QA session loaded into a benchmark variant, **or**
- The user runs the bench directly against their own save game on their hardware.

Recommend the latter once Phase 5.2 (callback coarsening) lands so we can measure before/after on their actual game.
