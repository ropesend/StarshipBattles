"""Cross-layer infrastructure services (PROJ-296).

The `game.services` package hosts cross-cutting infrastructure used by
multiple game layers (UI, AI, Strategy, etc.) without owning any
domain logic. Services depend only on `game.core` and may be imported
by any other layer.

See `docs/01_ARCHITECTURE.md` for the layer rule and acceptance
criteria for what belongs here.

Current services:
- `game.services.llm` — LLM provider abstraction (PROJ-296)
"""
