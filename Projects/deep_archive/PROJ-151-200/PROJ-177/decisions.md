# PROJ-177: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-24 | Project initialized | Starting point for Exception Handling Cleanup |
| 2026-02-24 | Audit count corrected: 29 tuple catches (not 24), 12 docstrings (not 6) | Independent agent swarm found additional blocks in galaxy.py, battle_state.py, ship.py, ship_factory.py |
| 2026-02-24 | Conservative removal: only 9 of 29 tuple catches cleaned | Only remove where try block provably has no stdlib/JSON/dict-access calls |
| 2026-02-24 | Keep generics in 20 deserialization/JSON/dict blocks | These guard against legitimate stdlib exceptions the domain doesn't control |
| 2026-02-24 | Scope out "why" comments suggestion | Low-ROI cosmetic; ErrorCode enum values are self-documenting |
| 2026-02-24 | Migrate 4 builtin raises; exclude 3 legitimate patterns | NotImplementedError (ABCs) and TypeError (__init_subclass__) are standard Python |
| 2026-02-24 | Battle_service.py:91 cleaned to (ValidationException, StateException) | BattleEngine constructor only raises domain exceptions; generics unreachable |
