# PROJ-311: Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-26 | Project initialized | User directive: "lets add the return types and update claude.md" |
| 2026-04-26 | Verified count: 1408 unannotated of 4930 total = 71.4% (NOT 59.5%/2145) | Independent AST audit |
| 2026-04-26 | Dunder methods exempt from denominator | PEP 484: `__init__` and other dunders typically don't need return annotations |
| 2026-04-26 | Return-types only; parameter annotations OUT OF SCOPE | Keeps this project bounded; parameter-coverage can be a follow-up |
| 2026-04-26 | Modern Python type syntax (PEP 604 unions, native generics) | Python 3.13+ baseline (PROJ-295); no reason to use `Optional`/`List`/`Dict` from typing |
| 2026-04-26 | Backfill in waves by subsystem (Core → Simulation → Strategy → AI → UI) | 1408 changes is too big for one PR; per-subsystem review is tractable |
| 2026-04-26 | Tests OUT OF SCOPE | Test annotations are encouraged but not blocking; fixtures resist simple annotation |
| 2026-04-26 | `mypy --strict` / `pyright --strict` adoption is OUT OF SCOPE | This project adds annotations; making the type-checker happy is a much larger separate effort |
| 2026-04-26 | Coverage CI gate (Phase 4) is OPTIONAL | Strict typing is great but conflates concerns; a simple coverage gate is the minimal protection |
| 2026-04-26 | Coordinate with PROJ-309 to avoid merge conflicts | PROJ-309 moves code around; per-wave check ensures we don't fight |
