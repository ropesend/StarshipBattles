# PROJ-179: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-24 | Exclude audit finding #5 (chain-of-responsibility) | Independent verification confirmed code DOES check return values at lines 124-131 in `_handle_keydown_mapped`. Audit was incorrect. |
| 2026-02-24 | Downgrade finding #1 from "critical bug" to "misleading docstring" | `get_system_of_object` is only called with Fleet objects (2 call sites verified). Planet would return None, not false-match. Fix is docstring + type hint only. |
| 2026-02-24 | Add `restore_planet()` method, not a flag on `register_planet()` | Clean API: `register_planet()` for new planets (assigns ID), `restore_planet()` for deserialization (preserves ID). Boolean flags are an anti-pattern. |
| 2026-02-24 | Add `_zone_to_system` dict for O(1) zone→system reverse lookup | Same pattern as `_planet_to_system`. Required to eliminate O(N) iteration in `get_system_at_location()`. |
| 2026-02-24 | Add `_global_hex_warp_points` for O(1) warp point spatial lookup | Warp points are the only system entity without a global hex index. Required for fully O(1) `get_system_at_location()`. |
| 2026-02-24 | Keep `from_dict()` in Galaxy facade (per PROJ-173 Decision #11) | Deserialization orchestrates rebuilding 5+ dicts in correct order. Keeping in facade is correct. What changes: it calls `restore_planet()` instead of manual index rebuilding. |
