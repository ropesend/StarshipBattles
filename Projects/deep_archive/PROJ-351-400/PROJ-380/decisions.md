# PROJ-380: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-08 | Project initialized | Starting point for Audit-shrink cleanup 2026-05-07 |
| 2026-05-08 | Acted only on findings that passed independent verification of `2026-05-07_220215_audit_shrink` | Audit-shrink reports have produced false positives in past runs (e.g. `_eval_least_armor_rule` reachable via `data/targeting_policies.json`); rejected and uncertain items recorded in `findings/verification_report.md` |
| 2026-05-08 | Reclassified DCV-01 + DUP-X-05 from REJECTED → VERIFIED relative to the verifier-agent's labels | The verifier-agent's evidence supported the audit's deletion claim in both cases; the agent labeled them REJECTED based on disagreement with the audit's *framing* (DCV-01) or with the audit's deletion *scope* (DUP-X-05). The protocol's REJECTED state is reserved for "concrete evidence the item is not actually dead/duplicate"; neither agent provided that. DUP-X-05 entered the project with reduced scope (preserve `remove_modifier_inplace`). |
| 2026-05-08 | Reduced scope on DUP-X-10 to fleet_ops only | Verifier could not confirm the audit's claim of additional sites in `strategy_click_dispatcher.py:274` and `strategy_superweapons.py`. Three confirmed sites in `strategy_fleet_ops.py` remain in scope. |
| 2026-05-08 | Excluded DUP-X-04 from this project | Verification rejected the claim: the three hit-effect functions have specialized rendering (different line counts, widths, flash logic) and are not parameterizable. |
| 2026-05-08 | Parked DUP-X-03 as UNCERTAIN, out of scope for this project | Only 2 of the 5 named ability classes (`ShieldModifierAbility`, `DamageModifierAbility`) are true twins. The other three diverge in field schemas. Needs human judgement on partial-vs-full consolidation. |
