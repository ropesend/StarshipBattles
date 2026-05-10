# PROJ-363: Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-04 | Project initialized | Strategy Layer Tech Debt Review finding #4 (P2 — adding one command requires editing ~7 files) |
| 2026-05-04 | Renumbered from PROJ-353 to PROJ-363 | Merge-conflict collision on PROJ-351..360 |
| 2026-05-04 | Spec table at `game/strategy/engine/commands/specs.py` | Sibling of `commands.py`. Avoids circular imports because handlers don't import specs (per findings/01). |
| 2026-05-04 | Phase 1 = contract tests, written first | TDD entry — the single contract test ("every spec has handler + action-time + codec") will initially fail (since the table doesn't exist). It drives the Phase 2 implementation and pins coverage. |
| 2026-05-04 | Keep existing CommandHandlerRegistry as runtime dispatcher | Don't replace runtime; replace the *source* of registrations. Lower-risk refactor. |
| 2026-05-04 | Replace `dispatch_*_command` methods with `__getattr__` lookup | ~200 LOC → ~20 LOC. All call sites continue to work because attribute access is dynamic. Per findings/01 §6. |
| 2026-05-04 | Mission commands have `order_type=None`, `execution_model='mission'` | Mission DTOs decompose at runtime into MOVE+ACTION orders; they don't have a 1:1 OrderType mapping. |
| 2026-05-04 | BUILD has `execution_model='production'`; not on ORDER_TO_ABILITY_MAP | BUILD is processed by ProductionEngine ticking the construction queue, not by action-tick resolution. |
| 2026-05-04 | Superweapon dispatch is OUT OF SCOPE | PROJ-364 owns superweapon spec decomposition. PROJ-363 only generates the registry/category-set/action-time wiring; it does NOT replace `order_processor.py:706-725` superweapon dispatch lambdas. |
| 2026-05-04 | Do NOT add `serializer_codec` content yet | Commands aren't persisted (only Orders are). Field is reserved for future use; populated as `None` for all current specs. |
