# PROJ-420: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-13 | Project initialized | Starting point for Legacy removal — lazy-init registry cache consolidation (2026-05-13) |
| 2026-05-13 | Bundled findings from `2026-05-13_194106_legacy-audit` by removal cluster `lazy_cache_consolidation` per user direction | Bundling driven by removal cluster (one project per system being eradicated) rather than severity to maximize deletion-PR coherence; full bundling discussion in findings/bundling_decisions.md |
| 2026-05-14 | Helper location: `game/core/registry_cache.py` (not `game/ui/services/`, not inlined into `registry.py`) | Core layer is correct — no layer inversion; `registry.py` is already ~470 LOC and must stay under 500 LOC ceiling; a sibling module keeps the helper narrow and direct-imported |
| 2026-05-14 | `setup_data_io.py` migration: construct `ShipFactory(registry_provider=get_cached_registries())` inline, no separate `get_cached_ship_factory()` helper | ShipFactory.__init__ only stores the ref (no expensive work); Core cannot import UI services (layer boundary); avoids adding a UI dependency to game/core |
| 2026-05-14 | `reset_cached_registries()` is a production module function (not test-only gated); must also be called from `set_default_registry_manager()` and `clear_registry()` to avoid stale GameRegistries refs after manager replacement or registry clear | Mirrors pattern of existing `clear_registry()` as lifecycle function; conftest.py manager-swap in reset_game_state would leave stale cache without this |
| 2026-05-14 | Scope expanded: `setup_screen.py` added as Task 1.5 — its `_ship_factory` / `_get_ship_factory()` block is dead code (function defined but never called; all IO delegated to setup_data_io.py); must be deleted so the zero-hit grep verification passes | Discovered by codex consult; confirmed by grep showing no production callers of _get_ship_factory outside the two defining files |
| 2026-05-14 | No optional ApplicationContext parameter on helper; keep `get_cached_registries()` name as-is | Transitional API design pre-PROJ-258 would be premature; migration is trivial delete-and-replace when PROJ-258 lands |
