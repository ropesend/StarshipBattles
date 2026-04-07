# Phase 4: Determinism Verification Tests

**Objective:** Add integration tests that prove battle determinism is seed-based and fully independent of process-global state.

**Key Principle:** These tests act as a regression guardrail — if anyone reintroduces global RNG usage, these tests break.

---

## Checklist

### Tests
- [ ] Write test: run same battle scenario twice with identical seed → identical damage dealt per ship, identical tick count, identical survivor list
- [ ] Write test: interleave `random.random()` calls between two sequential battles with same seed → both produce identical results (proves isolation from global RNG)
- [ ] Write test: run two battles with same seed but different global random state (seed global differently) → identical results (proves no global contamination)
- [ ] Write test: run battle, record all damage events, replay with same seed → events match exactly
- [ ] Write test: `ConflictResolutionEngine` with seeded RNG produces identical outcomes across repeated runs
- [ ] Write test: two `BattleEngine` instances running in same process with different seeds produce different results and don't interfere

### Verification
- [ ] All new tests pass
- [ ] Run full test suite — no regressions
- [ ] Tests are placed in `tests/integration/` (they exercise multiple subsystems)
