# PROJ-354A: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-04 | Project initialized | Phase A of replay verification — capture-side fidelity. Implements C1–C3 of consensus plan r003 from Claude+Codex inter-agent discussion. |
| 2026-05-04 | Use `ComponentStatus.name` not `.value` for serialization | Codex correction (r002). The enum uses `auto()`, so numeric values are not a stable contract across Python versions. String names are stable and semantically meaningful. |
| 2026-05-04 | Do NOT add a synthesized `DESTROYED` status | Codex correction (r002). The enum has no `DESTROYED` member; destroyed condition is represented by `current_hp == 0` and `is_active == False`. The existing 6 enum values (`ACTIVE`/`DAMAGED`/`NO_CREW`/`NO_POWER`/`NO_FUEL`/`NO_AMMO`) are sufficient. |
| 2026-05-04 | Bump `REPLAY_SCHEMA_VERSION` to `"2.0.0"` (no migration) | Per CLAUDE.md Rule 3: no save/replay compat shims. `ReplayResolver` already handles `version_drift` gracefully. Pre-release moddable game; old replays are disposable. |
| 2026-05-04 | Phase A independent of sink wiring | Capture-side fields land regardless. They're not exercisable end-to-end in production until the sink wiring lands (PROJ-354B prerequisite), but they don't break anything. PROJ-354A can be implemented and merged immediately after user approval. |
| 2026-05-04 | Use `hasattr(status_obj, "name")` defensive check in extractor | Protects against the `Component` having `status=None` or some non-enum value due to a mod or unanticipated path. Falls back to `str(status)` so the extractor never crashes a battle end. |
| 2026-05-04 | DO NOT modify persistent `ComponentState` (`game/core/component_state.py`) | The persistent strategy-side type already has `max_hp`. Adding `status` to it is a separate, larger concern (save format migration). Out of scope. |
| 2026-05-04 | DO NOT modify post-battle bridge (`post_battle_hook.py`) | The bridge reads named fields off `ComponentStateSpec`; new fields are ignored gracefully. Phase 2 Task 2.3 verifies. PROJ-354B may revisit if the bridge needs to use the new fields. |
| 2026-05-04 | Test defaults for new fields: `max_hp=100.0`, `status="ACTIVE"` | For tests that don't care about the new fields, use uniform defaults so test diffs stay readable. Tests that DO care (damage tests, status-distinction tests) use scenario-specific values. |

## Audit Remediation (OpenCode review 2026-05-05)

The `2026-05-05_055833_code_proj-354a-review-replay-component-end-state-fideli`
review surfaced 0 CRIT and 3 MAJ findings. All three share a single root
cause; they are remediated together below. MIN/INFO findings are recorded
but not actioned.

| Finding | Verdict | Rationale |
|---------|---------|-----------|
| MAJ-001 — Post-battle hook ignores outcome `max_hp` and `status` | FIX (max_hp) / DEFER (status) | The bridge now reads `cs.max_hp` from `ShipOutcome.components` and writes it onto the persistent strategy-side `ComponentState`, with a fallback to the pre-battle snapshot when the outcome reports `0.0` (defensive). `status` is intentionally not propagated — `ComponentState` is a damage-only DTO with no status field, and adding one is a save-format migration that the original PROJ-354A scope explicitly excluded. The engine reconciles `ComponentStatus` from HP/active state on the next battle's first tick, and replay-side fidelity is preserved in `ReplayRecord.outcome.data` regardless. |
| MAJ-002 — Stale comment "ComponentStateSpec doesn't carry max_hp today" | FIX | Comment rewritten to document the new authoritative-from-outcome behavior, the zero-fallback rule, and the deliberate `status` drop. |
| MAJ-003 — `cs.max_hp` ignored at `_apply_survivor_outcome` line 157 | FIX | Same root cause as MAJ-001. Resolved by the same edit. |
| MIN-001 — `status="ACTIVE"` default in spec_compiler is low-fidelity | NO-OP | Review acknowledges this is correctness-preserving; engine reconciles on first tick. Out of scope for the audit pass. |
| MIN-003 — `battle_runner.py` exceeds 500 LOC ceiling | NO-OP | Pre-existing, advisory; tracked for a future cleanup pass. |
| NIT-001/002/003, MIN-002 | INFO only | Verified-positive / verified-negative findings; no action. |

**Tests added:**
- `test_apply_survivor_outcome_uses_outcome_max_hp_over_pre_battle` — proves the bridge prefers `cs.max_hp` from the outcome when it differs from the pre-battle snapshot (modifier-shaped cap scenario).
- `test_apply_survivor_outcome_falls_back_to_prior_max_hp_when_outcome_zero` — proves the defensive zero-fallback path keeps the persistent `ComponentState.max_hp` non-zero when an outcome carries `max_hp=0.0`.

**No conflict with PROJ-354B**: the verifier (`game/simulation/replay/replay_verifier.py`, commit 9dabe9042) compares `record.outcome.data` to `battle_outcome_to_dict(replayed_outcome)`. Both sides flow through the same `_extract_component_states` extractor and the same `battle_outcome_to_dict` serializer; the strategy-side `ShipInstance` is not part of the comparison. The bridge fix changes only what survives onto `ShipInstance` after a battle — replay verification is untouched.
