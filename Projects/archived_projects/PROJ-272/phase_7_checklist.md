# Phase 7: Remove vestigial strategy-compiler kwargs (MEDIUM — Code M4)

**Status:** Complete
**Risk:** LOW (signature cleanup; kwargs already no-ops after PROJ-271 Phase 9)
**Depends On:** None
**Objective:** `build_strategy_battle_spec` still accepts `sector`, `system`, `empires` kwargs that are silently discarded after PROJ-271 Phase 9 deleted `_entries_from_modifier_source`. Remove them to prevent contributor confusion.

## Tasks

### Task 7.1: Grep callers [Simple]
- [ ] Grep `build_strategy_battle_spec(` across the codebase; enumerate callers passing `sector`, `system`, `empires`.
- [ ] For each: determine whether they pass the kwarg for documentation/parity reasons or because it's meaningful.
- [ ] Document findings.

### Task 7.2: Remove kwargs + migrate callers [Medium]
**File:** `game/strategy/combat/spec_compiler.py` + all callers

- [ ] Remove `sector`, `system`, `empires` from `build_strategy_battle_spec` signature.
- [ ] Remove from `_build_modifier_stack` signature.
- [ ] Update all callers to drop the kwargs (silently-discarded today, so removing them is a pure cleanup).
- [ ] Tests in `tests/unit/strategy/combat/test_spec_compiler.py` that pass these kwargs — update.

### Task 7.3: Verify tests + regression [Simple]
- [ ] All strategy compiler tests green.
- [ ] Integration tests green.

## Phase Completion Checklist
- [ ] All tasks checked
- [ ] Signature cleanup landed
- [ ] Update plan.md
