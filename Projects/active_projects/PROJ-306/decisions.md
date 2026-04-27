# PROJ-306: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-26 | Project initialized | Closes PROJ-274 / PROJ-211 by eliminating the two surviving global-lookup fallbacks in the Simulation layer |
| 2026-04-26 | Both call sites in scope; `protocols.py:38` TYPE_CHECKING import is OUT OF SCOPE | The TYPE_CHECKING import is a documented unavoidable trade-off (acknowledged in the original code review). Touching it would create new problems without solving any |
| 2026-04-26 | `ApplicationContext`-based migration is preferred when caller surface is large | If many callers exist, requiring them all to pass `ship_builder`/`registry_provider` is high churn. Pulling from a context (analogous to `get_default_ship_materializer`) keeps caller surface small while still eliminating the global-lookup pattern from Simulation. Phase 1/2 surveys will inform the choice per call site |
| 2026-04-26 | Line-90 comment in `registry_loader.py` is KEPT after the fix | "Pass registry_provider explicitly (no fallback)" is the correct documentation once the fallback is actually gone. Becomes truthful, useful for future maintainers |
