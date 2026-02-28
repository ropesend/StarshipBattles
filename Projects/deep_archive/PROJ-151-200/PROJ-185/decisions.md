# PROJ-185: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-24 | Project initialized | Post-PROJ-174 backward compatibility eradication |
| 2026-02-24 | Keep UI utils __init__.py re-exports, fix comment | Standard Python package API pattern - __init__.py defines public API, decouples callers from internal module structure. Zero maintenance cost. |
| 2026-02-24 | Keep build queue Window facade properties | Proper encapsulation (Law of Demeter). Tests should access `win.all_sources` not `win._viewmodel.all_sources`. Just fix misleading "backward compatibility" comments. |
| 2026-02-24 | Remove ViewModel single-select shim | Clean-sheet: `selected_indices` (Set[int]) is the authoritative selection state. Single-select convenience can be derived on Window facade without ViewModel maintaining duplicate fields. |
| 2026-02-24 | Remove build queue test state exposure | Tests should not depend on internal wiring (`self.columns`, `self.column_toggle_buttons`, etc. copied from sub-components). Expose through proper properties if tests need access. |
| 2026-02-24 | `turns_remaining` is NOT legacy | Field is actively consumed by 6+ UI files for display. The "legacy" comment is misleading - fix it. |
| 2026-02-24 | GameConfig race field serialization is NOT compat | Conditional inclusion of optional fields is sparse serialization, not backward compatibility. Fix misleading comment. |
| 2026-02-24 | Window convenience properties derive from selected_indices | `selected_source` and `selected_index` stay on Window but compute from `get_selected_sources()` and `selected_indices` respectively, rather than reading from ViewModel shim fields. |
