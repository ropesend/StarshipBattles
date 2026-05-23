# PROJ-498: Decisions Log

> **LOG ALL DECISIONS HERE**
> When the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-23 | Project initialized | Carved out of PROJ-489 audit follow-up. See `findings/source_review.md`. |
| 2026-05-23 | Sequence: PROJ-497 → PROJ-498 | Codex consult recommended the matrix test should encode the *chosen* truth, not today's accidental truth. Running PROJ-498 first would force matrix re-runs after every PROJ-497 data edit. |
| 2026-05-23 | Adopt reason-bearing allowance API (`check_allowance()`) | Codex consult agreement. Bare bool can't distinguish unknown-id from wrong-ability, which makes save-restore log warnings vague. Keep `is_modifier_allowed()` as a bool-returning convenience that delegates to `check_allowance()`. |
| 2026-05-23 | Log rejection at save-restore boundary, NOT inside `Component.add_modifier()` | Builder/regression tests intentionally reject pairs; logging there would create noise. `docs/05_ERROR_HANDLING.md:137-143,181-184` says log at handling boundary. |
| 2026-05-23 | Matrix test reads JSON at collection time, no hardcoded pairs | Future-proof against PROJ-497's data edits. Test asserts canonical intersection rule (allow_abilities/allow_types/deny_types matches component abilities/type). |
| 2026-05-23 | NO save-file migration | `CLAUDE.md`: "no save-file migrations". Old saves with now-rejected modifiers will load with those modifiers dropped + a warning logged. User can re-export from builder if they care. |
| 2026-05-23 | One parametrized matrix test, NOT per-rejected-pair snapshots | Codex consult: per-rejected-pair snapshots would be noise; snapshot comparator's "ignore extra keys" behavior makes snapshots a weak fit for negative coverage anyway. |
| 2026-05-23 | Mid-project review (Codex Q5): drop `ABILITY_DENIED` from reason enum | The live service does NOT enforce `deny_abilities` (`game/simulation/services/modifier_service.py:79-106`). Including the reason would silently expand semantics. Reason set locked to: `UNKNOWN_MODIFIER_ID`, `TYPE_NOT_ALLOWED`, `TYPE_DENIED`, `ABILITY_NOT_ALLOWED`, `ALLOWED`. See `AgentCoordination/Scratchpad/Consult/20260523T120300Z_mpr-PROJ-497-498/response.md`. |
| 2026-05-23 | Mid-project review (Codex Q2): matrix test MUST use live rule, not PROJ-497's pre-correction scan | The pre-correction scan in PROJ-497 `findings/source_review.md` applied `deny_abilities` and undercounted `hardened_mount` as 162. The live rule yields 169. PROJ-498 Phase 3 Task 3.1/3.2 already specifies "canonical intersection rule" matching live service; PROJ-497 scan has been corrected. |
| 2026-05-23 | Mid-project review (Codex Q4): manifest updated with three additional `is_modifier_allowed()` callers | `modifier_manager.py:124-128`, `component_service.py:104-109`, `modifier_logic.py:54-56` are downstream callers. Phase 1 Task 1.4 already spot-checks them, but the manifest now lists them so conflict detection works. |
| 2026-05-23 | Mid-project review (Codex Q4): Phase 1 must include bool-semantics regression guard | Added to Task 1.2 — `is_modifier_allowed()` bool return must not change. |

## Open questions

- Reason enum shape (Phase 1 design decision). **Locked** values (live-service-only): `UNKNOWN_MODIFIER_ID`, `TYPE_NOT_ALLOWED`, `TYPE_DENIED`, `ABILITY_NOT_ALLOWED`, `ALLOWED`. **Explicitly excluded:** `ABILITY_DENIED` — `deny_abilities` is not enforced by the live service (`game/simulation/services/modifier_service.py:79-106`); including the reason would imply a semantic change. Flagged by Codex mid-project review Q5.
- Whether to emit log at `ensure_mandatory_modifiers()` path too (`modifier_service.py:222-234`). Default: NO — that's the auto-application path where every allowed modifier is added; rejection there would be a service-internal contradiction worth a stronger signal than a warning. Revisit if a real case appears.
- Whether `deny_abilities` should ever be enforced. **Out of scope for PROJ-498.** That is a behavior-change project; would need its own user-decision project. Currently 8 modifier rows declare `deny_abilities` (e.g., `hardened_mount.deny_abilities=Armor`); enabling enforcement would change 7+ valid-pair counts.
