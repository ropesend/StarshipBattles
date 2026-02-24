# PROJ-164: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-23 | Project initialized | Starting point for Extract Ability._parse_primary_value() Base Class Helper |
| 2026-02-23 | Use `@staticmethod` not `@classmethod` | No cls/self needed — pure data transformation function |
| 2026-02-23 | Return `float` always, let callers cast to `int` | 3 abilities need `int()`. Simpler to have one return type and let callers handle integer conversion. |
| 2026-02-23 | Add `key` parameter with default `'value'` | All current callers use `'value'` key, but `key` parameter future-proofs for abilities using `'amount'` etc. |
| 2026-02-23 | Leave CrewRequired as-is (don't migrate) | Uses nested fallback `data.get('value', data.get('amount', 0))` — this is subclass-specific logic, not worth complicating the helper for 1 site |
| 2026-02-23 | Include `sync_data` migration | propulsion.py has 3 `sync_data` methods with a slightly longer 3-way pattern that the helper handles natively |
| 2026-02-23 | 3 phases: helper+tests → migrate → verify | Clean separation: Phase 1 is additive (no changes to existing code), Phase 2 is substitution, Phase 3 is verification |
