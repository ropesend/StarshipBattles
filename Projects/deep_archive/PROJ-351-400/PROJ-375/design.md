# PROJ-375: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Audit

**Audit directory:** `Reviews/results/2026-05-05_185819_audit_shrink/`

| Metric | Value |
|--------|-------|
| Audit verified-safe candidates | 11 (1 dead method + 9 CRITICAL/MAJOR duplication clusters + 1 deep-review MAJOR duplication) |
| Independently verified | 10 |
| Rejected | 0 |
| Uncertain (excluded from plan) | 1 (DUP-X-08) |
| Verified-but-excluded (low priority) | 1 (DEEP-01-004) |
| Audit-claimed total reclaimable LOC | ~460 |
| Verified-only reclaimable LOC | ~442 (Phase 1: 3, Phase 2: 289, Phase 3: 150) |

A note on the zero-rejection result: the protocol explicitly flags zero
rejections as a possible smell — past audit-shrink runs (e.g. 2026-05-02
where `_eval_least_armor_rule` was reachable via `data/targeting_policies.json`)
have produced false positives. The 2026-05-05 audit is a small one
(vulture flagged only 7 items, all already classified as false positives by
the audit's own internal verifier; only 1 dead method survived). With so few
candidates, zero rejections in re-verification is plausible rather than
suspicious. See [findings/verification_report.md](findings/verification_report.md)
for the full re-verification trail.

## Initial Analysis

The audit's main finding is that vulture detects no genuine dead code in
`game/` — strong positive signal about TDD practice and `TYPE_CHECKING`
discipline. The shrinkage opportunity is overwhelmingly **duplicate
consolidation**, not dead-code deletion.

The verified-safe items cluster around four root patterns:

1. **"Iterate facility components → extract abilities → read field"** —
   reimplemented in 9+ engines and one UI formatter (DUP-X-02 + DUP-X-06).
2. **Owner-id ownership-validation + planet resolution** — 7 hand-rolled
   copies of the same check across `planet_command_handlers.py` (DUP-X-01),
   plus 3 near-clone `SetXTargetCommandHandler`s on top of that (Cluster 5).
3. **Existing helpers that callers fail to use** — `_emit_validated_order`
   exists but the 4 superweapon handlers re-implement its body (DUP-X-07 /
   Cluster 11).
4. **Mirror-method pairs that should be field-parameterized** — bio/socio in
   the LLM controller (DUP-X-05); harvester/storage in `harvesting_engine`
   (Cluster 29+30); planet/star list windows (DUP-X-04); component-item
   variants (Cluster 6); workshop dropdown handlers (DUP-X-03).

## Swarm Findings Summary

Three parallel `Explore` subagents re-verified the audit's claims in three
batches (dead code; strategy duplications; UI duplications). Aggregated
results live in
[findings/verification_report.md](findings/verification_report.md). The agent
batch reports are in `.agent_reports/2026-05-05_audit_shrink/`.

### Architecture

- `BaseCommandHandler` (`game/strategy/engine/handlers/base.py`) is the
  intended home for handler-resolution helpers. The existing
  `_resolve_player_fleet` pattern (lines 135-156) is the template for
  Phase 2's new `_resolve_player_planet`. The existing `_emit_validated_order`
  pattern (lines 228-247, added by PROJ-319) is the helper Phase 2 Task 2.4
  retro-applies to superweapon handlers.
- `component_inspector` (`game/strategy/services/component_inspector.py`)
  already centralizes `extract_abilities_from_component`. Phase 2 Task 2.1
  extends it with `get_ability_field_from_facility` to encapsulate the rest
  of the pattern.
- `DataListWindowMixin` already mixes into both `PlanetListWindow` and
  `StarListWindow`. Phase 3 Task 3.2 should extend that mixin or add a
  sibling rather than introducing a third base class.

### Key Patterns to Reuse
- **`_resolve_player_fleet` pattern**: `game/strategy/engine/handlers/base.py:135-156` — template for `_resolve_player_planet` (Phase 2 Task 2.2).
- **`_emit_validated_order` pattern**: `game/strategy/engine/handlers/base.py:228-247` — already exists; Phase 2 Task 2.4 just routes 4 handlers through it.
- **`extract_abilities_from_component`**: `game/strategy/services/component_inspector.py` — the existing centralizer; extend rather than duplicate (Phase 2 Task 2.1).
- **`DataListWindowMixin`**: shared mixin already on both list windows; extend for the update() template (Phase 3 Task 3.2).

### Dependencies & Risks
1. **Task 2.1 (DUP-X-02 + DUP-X-06) touches 10 files** — biggest blast
   radius in the project. Mitigation: add helper + tests first, then
   migrate one file at a time, running per-file tests between migrations.
2. **Task 2.3 (Cluster 5 — merge 3 SetXTarget handlers) builds on Task
   2.2's `_resolve_player_planet`** — sequence the tasks accordingly.
3. **Task 2.5 (DUP-X-05 bio/socio unification)** changes attribute shape
   (`_bio_call`/`_socio_call` → `_fields[field_name].call`). Any external
   readers of those attributes will break — verifier did not check for
   external readers, so the implementing agent must grep before refactoring.
4. **Task 3.1 (DUP-X-03)** — the role variant uses a registry-loop resolver
   while movement/targeting use options-list. Verifier flagged this; the
   dispatch table must parameterize the resolver function, not just the
   setter name.

### Opportunities Discovered
- The protocol-style "shared helper exists but isn't used" pattern (Task 2.4)
  suggests adding a lint or AST guard that flags handlers building `Order(...)`
  + `fleet.add_order(...)` without going through `_emit_validated_order`. Out
  of scope for this project but worth a follow-up ticket.
- The "iterate components → extract abilities → read field" replication
  across 10 files (Task 2.1) suggests the canonical helper should be
  prominently documented — consider linking it from `docs/02_PATTERNS.md`
  during Task 2.1.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
