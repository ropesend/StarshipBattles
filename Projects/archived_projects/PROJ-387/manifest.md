# PROJ-387 File Manifest

## Files

| File | Type | Action | Notes |
|------|------|--------|-------|
| `game/strategy/data/galaxy.py` | Production | Edit | LEG-03-022 — delete 5 forwarders at lines 97-131 |
| `game/strategy/data/movement.py` | Production | Migrate-callers | Replace forwarder reads with `GalaxyState` accessors |
| `game/strategy/services/fleet_navigation_service.py` | Production | Migrate-callers | Same |
| `game/ui/screens/strategy_render/hex_outlines.py` | Production | Migrate-callers | Same |
