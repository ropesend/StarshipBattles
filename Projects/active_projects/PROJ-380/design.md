# PROJ-380: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Audit
- **Audit directory:** `Reviews/results/2026-05-07_220215_audit_shrink/`
- **Audit date:** 2026-05-07 22:02 UTC
- **Audit-flagged verified-safe candidates:** 13 (1 dead import + 12 CRITICAL/MAJOR duplications)
- **Independently verified:** 11 (1 dead import, 1 dead-function block scope-reduced, 9 duplications — 2 with reduced scope)
- **Rejected:** 1 (DUP-X-04 — hit-effect rendering uses specialized variations, not parameterizable)
- **Uncertain:** 1 (DUP-X-03 — ability `__init__` boilerplate; only 2 of 5 abilities are true twins)
- **Audit-claimed reclaimable LOC for the verified-only set:** ≈ 310 LOC
  (DCV-01: 1 + DUP-X-05: ≈ 89 + DUP-X-01: 60 + DUP-X-02: 25 + DUP-X-06: 18 + DUP-X-07: 24 + DUP-X-08: 15 + DUP-X-09: 12 + DUP-X-10: 8 + DUP-X-11: 40 + DUP-X-12: 25)

See [findings/verification_report.md](findings/verification_report.md) for the full per-item breakdown and [findings/source_audit.md](findings/source_audit.md) for the link to the originating audit-shrink review.

## Initial Analysis
The audit-shrink skill performs a coverage-rotated deep review (Shard 02 this run) plus deterministic vulture/radon/clone-detector passes. Its own internal verifier already filters obvious false positives. This project takes only the items that survived an additional skeptical re-verification with fresh evidence.

## Swarm Findings Summary
Verification was split across three parallel `Explore` agents:
- **Batch 1 — Dead code (DCV-01, DUP-X-05).** Confirmed both items dead with respect to external callers; flagged DUP-X-05's internal helper `remove_modifier_inplace` as a still-used dependency that must be preserved during deletion (or removed only after confirming no surviving callers).
- **Batch 2 — CRITICAL + first half of MAJOR duplications (DUP-X-01, 02, 03, 04, 06, 07).** Verified DUP-X-01, 02, 06; verified DUP-X-07 with an EDIT_MOVE divergence noted; rejected DUP-X-04 (specialized rendering, not parameterizable); flagged DUP-X-03 as UNCERTAIN (only 2 of 5 ability classes are true twins).
- **Batch 3 — Second half of MAJOR duplications (DUP-X-08, 09, 10, 11, 12).** All five verified; DUP-X-10's scope reduced to fleet_ops sites only (claimed cross-file sites in click_dispatcher / superweapons not confirmed).

### Architecture
- The repo has a documented Factory pattern (#15), CommandHandlerRegistry pattern (#7), Universal Ability Source pattern (#29), and Serializable Protocol pattern (#17). Several of the consolidations in this project are restoring conformance to those existing patterns rather than inventing new abstractions.
- `_handle_superweapon_click` (in `strategy_click_dispatcher.py`) is already a precedent for the kind of consolidation Task 3.7 will apply to the remaining click handlers.

### Key Patterns to Reuse
- **CommandHandlerRegistry (#7)**: Reused for the `MissionCommandHandler` template in Task 3.6.
- **Factory pattern (#15)**: Restored for `ProviderFactory` in Task 3.1.
- **Universal Ability Source (#29)**: Restored for `_iter_ability_sources` in Task 3.8.
- **Serializable Protocol (#17)**: Applied via base `_serialize_fields` for `BattleEndCondition` in Task 3.9.

### Dependencies & Risks
1. **`_handle_edit_move_click` divergence (DUP-X-07).** Mitigation: the `on_cancel` callback parameter on `_handle_input_mode_click` lets EDIT_MOVE perform its three extra state resets without forking the base.
2. **`remove_modifier_inplace` cross-method dependency (DUP-X-05).** Mitigation: re-grep before deleting; preserve the helper if any non-deprecated path still calls it.
3. **Save-file format risk (DUP-X-11).** Mitigation: round-trip test every `BattleEndCondition` subclass before/after; document any wire-format change explicitly.
4. **11 `pixel_to_hex` sites in 5 files (DUP-X-08).** Mitigation: do the camera-method addition as one commit, then refactor sites in a follow-up commit so the diff is auditable.

### Opportunities Discovered
- The audit's MINOR duplications (DUP-X-13 through DUP-X-22) and the UNCERTAIN DUP-X-03 are deliberately out of scope here, but several (race randomizer pick, tkinter dialog wrappers, selection prompt windows) are cheap wins that could be picked up in a follow-up project if the user wants.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
