# PROJ-198: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-25 | Project initialized | Starting point for UI Layer Duck Typing Elimination - Strategy Screens & Services |
| 2026-02-25 | Organize phases by fix type, not by file | Front-loads easy wins; ~90 trivial deletions in Phase 1 before any structural work. Original plan organized by functional domain but that mixes trivial and complex changes together. |
| 2026-02-25 | Drop ViewModel/ISelectable/IRenderable adapter proposal | Deep analysis showed `self.scene` is always `StrategyScreen` — single concrete type. No polymorphism exists. ViewModels would be unnecessary abstraction. |
| 2026-02-25 | Keep 5 exempt categories (~10 instances) | keybindings_scene.py (module introspection), input_mapper.py (pygame constant lookup), modifier_row.py (library compat), planet_data_source.py/planet_list_filters.py (generic dotted-path column traversal). All are legitimate dynamic dispatch. |
| 2026-02-25 | Add `id: str = str(id(self))` to Ship and Projectile | Eliminates `getattr(x, 'id', id(x))` fallback in 3+ locations. Using `str(id(self))` preserves current behavior. |
| 2026-02-25 | Init `crew_onboard`/`crew_required` = 0 in Ship.__init__ | ShipStatsCalculator sets these dynamically. Initializing to 0 makes them safe to access before calc runs. |
| 2026-02-25 | Init `build_queue_screen = None` in StrategyScreen.__init__ | Single change eliminates 5+ hasattr checks across 3 files (strategy_event_router, strategy_input_handler, strategy_build_queue_manager). |
| 2026-02-25 | Replace monkey-patched UIButton attrs with dict lookups | 3 locations stamp custom attrs on pygame_gui UIButton objects (design_selector_window, build_queue_selector, fleet_orders_window). Dict lookups are cleaner and avoid modifying library objects. |
| 2026-02-25 | Fix planet_list_filters.get_owner_name to accept empires param | Galaxy has no `empires` attribute. Current `hasattr(galaxy, 'empires')` check always fails, making the entire owner name lookup dead code. Fix by passing empires from caller. |
| 2026-02-25 | Remove `_temp_system_ref` monkey-patch on Planet objects | Planet is a dataclass; stamping temp attributes on it is fragile. Replace with a `{planet_id: system_name}` lookup dict passed through parameters. |
| 2026-02-25 | Add stub `show_confirmation_dialog` and `show_ship_picker` to StrategyUI | These methods are referenced in strategy_superweapons.py but don't exist. The hasattr guards always fail, meaning superweapon confirmation dialogs never show. |
| 2026-02-25 | fleet_orders_window: filter by dict key name, not hasattr | Row dicts have known keys: idx, desc, up, down, del (UI elements) and order_ref (data). Filtering by `key != 'order_ref'` is explicit and doesn't rely on duck typing. |
| 2026-02-25 | Keep `getattr(build_context, 'name', 'unknown')` in error path (L179) | This is only used inside a ValidationException message. Defensive coding in error paths is acceptable — the error case means something is already wrong. |
