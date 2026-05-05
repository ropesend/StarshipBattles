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
