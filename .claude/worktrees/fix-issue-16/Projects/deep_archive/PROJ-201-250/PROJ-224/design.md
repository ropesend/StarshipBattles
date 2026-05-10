# PROJ-224 Design: Core Utilities & Shared Helpers

## Architecture Decisions

### _has_attrs Consolidation
- Keep the canonical definition in `game/core/protocols.py`
- Export it (add to `__all__` if needed, or keep as module-level function)
- Other protocol modules import from core
- Note: It's a private function (`_has_attrs`) but used across modules — consider making it public (`has_attrs`)

### display_name() Location
- Add to `game/core/` — either a new `text_utils.py` or existing `json_utils.py`
- Simple implementation: `raw.replace('_', ' ').title()`

### BattleConfig Rename Strategy
- `game/core/config.py::BattleConfig` → `CombatConstants` (or `BattleTuning`)
- Broad impact: grep for all imports and usages before renaming
- Approach: find-and-replace across entire codebase in one commit

### hex_from_dict_safe() Design
```python
def hex_from_dict_safe(data: dict, key: str = 'location', default: Optional[HexCoord] = None) -> Optional[HexCoord]:
    """Deserialize a HexCoord from a dict, returning default on failure."""
    try:
        raw = data.get(key)
        if raw is None:
            return default
        return HexCoord.from_dict(raw)
    except (KeyError, TypeError, ValueError):
        return default
```
