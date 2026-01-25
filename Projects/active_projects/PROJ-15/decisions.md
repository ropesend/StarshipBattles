# PROJ-15: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-25 | Project initialized | Starting point for Legacy Cleanup Phase 2 - Remove Shims and Aliases |
| 2026-01-25 | Keep `ship.to_hit_profile` property declaration, only remove sync line | Investigation confirmed `to_hit_profile` is a legacy alias for `total_defense_score`. Combat system (collision.py) uses canonical name. Only `stats_layout.json` references the alias for UI display. |
| 2026-01-25 | Rename test files from "builder" to "workshop" | User explicitly requested test file renaming as part of this cleanup phase. |
| 2026-01-25 | Remove TurnEngine wrappers and update test callers | User chose to update tests to call production_engine/movement_engine directly rather than keeping deprecated wrappers with warnings. |
| 2026-01-25 | Replace `load_combat_strategies()` with direct StrategyManager calls | Function is deprecated - uses `StrategyManager.instance().load_data()` internally. Callers should use this directly. |
| 2026-01-25 | Order phases by risk (lowest first) | Pure alias files and singleton patterns are safest. BuilderSceneGUI wrapper is most complex - saved for Phase 5. |
| 2026-01-25 | Merge test directories rather than simple rename | `tests/unit/workshop/` already exists with 3 files. Need to merge `tests/unit/builder/` contents, handle naming conflicts. |

---

## Key Findings from Code Review

### to_hit_profile Investigation
- `ship.py:130` declares `self.to_hit_profile: float = 1.0` as "Defensive Multiplier"
- `ship_stats.py:390` syncs: `ship.to_hit_profile = ship.total_defense_score`
- `collision.py:112-113` uses `total_defense_score` for combat (NOT `to_hit_profile`)
- `stats_layout.json:276` uses `to_hit_profile` for UI display only
- **Conclusion:** Safe to remove alias assignment, update JSON config to use `total_defense_score`

### BuilderSceneGUI Complexity
- Not a simple alias - full delegation wrapper class (165 lines)
- Handles backward compat for test mocking patterns (`__new__`, `__getattr__`, `__setattr__`)
- Production usage only in `app.py` - straightforward to update
- Test files use various patterns - need careful migration

### TurnEngine Wrappers
- 4 deprecated methods delegate to production_engine/movement_engine
- `_execute_move_step()` emits DeprecationWarning
- Others kept for "backward compatibility" but only tests use them
- Safe to remove if tests updated to use real engines

### Singleton Pattern Standardization
- Standard pattern is `ClassName.instance()` classmethod
- 3 classes have legacy `get_instance = instance` alias
- Total 5 production calls and 9 test calls to update

---

## Questions Resolved During Planning

1. **Q:** Is `to_hit_profile` critical game mechanics?
   **A:** No - it's a legacy alias. Combat uses `total_defense_score`. Safe to remove.

2. **Q:** Should test files be renamed?
   **A:** Yes - user explicitly requested renaming from "builder" to "workshop".

3. **Q:** Remove TurnEngine wrappers or keep with warnings?
   **A:** Remove them completely, update tests to use real engines.

4. **Q:** How to handle existing `tests/unit/workshop/` directory?
   **A:** Merge contents from `tests/unit/builder/`, handle naming conflicts.
