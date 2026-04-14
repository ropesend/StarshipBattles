# Phase 11: UX polish (LOW — E2E M-1, M-2)

**Status:** Complete
**Risk:** LOW (UI-only)
**Depends On:** None
**Objective:** Two small UX issues surfaced by round-2 audit:
1. `BattleScreen.get_active_modifier_labels` formats multipliers as "+0.75" — looks positive/green when it's actually a 25% NERF.
2. `get_active_modifier_labels` uses `value:.2f` with no guard for non-numeric values; a future aura producing a non-numeric could crash the HUD.

## Tasks

### Task 11.1: Multiplier-aware sign format [Medium]
**File:** `game/ui/screens/battle_screen.py` `get_active_modifier_labels`

- [ ] For `_mult` stat_keys: format as `{ability}={value:.2f}x` (e.g., `"shield_capacity_mult=0.50x"`) — no + sign, clear multiplicative semantic.
- [ ] For `_add` stat_keys: format as `{ability}={value:+.2f}` (e.g., `"shield_bonus_add=+50.00"`) — +/- sign clarifies additive direction.
- [ ] Other keys: fall back to neutral `{value:.2f}`.
- [ ] Test: verify both formats render correctly.

### Task 11.2: Non-numeric guard [Simple]
**File:** `game/ui/screens/battle_screen.py` `get_active_modifier_labels`

- [ ] Wrap the format step: if `value` is not a `(int, float)`, skip the entry with a logger warning (one-per-key).
- [ ] Test: label generation with a non-numeric value (via mock) doesn't crash; warning logged.

## Phase Completion Checklist
- [ ] All tasks checked
- [ ] UX polish landed
- [ ] Update plan.md
