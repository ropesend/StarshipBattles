# Finding: Hardcoded Log File Paths

**Severity:** Minor
**Category:** Architecture
**Agent:** File I/O Operations Mapper

## Description
Log and diagnostic files are written to hardcoded locations in the project root, with no central configuration.

## Locations

### game/core/logger.py (Line 36)
```python
fh = logging.FileHandler('battle.log', mode='w')
```
**Issue:** Creates `battle.log` in current working directory.

### game/app.py (Line 747)
```python
with open('crash_log.txt', 'w') as f:
    f.write(crash_info)
```
**Issue:** Creates `crash_log.txt` in current working directory.

### game/core/profiling.py (Line 109)
```python
history_file = 'profiling_history.json'
```
**Issue:** Creates profiling data in current working directory.

### game/core/screenshot_manager.py (Line 60)
```python
SCREENSHOT_DIR = os.path.join(ROOT_DIR, "screenshots")
```
**Note:** This one correctly uses ROOT_DIR from constants.

## Impact
- Log files created in unpredictable locations if working directory changes
- Cannot redirect logs to a dedicated logs folder
- Crash logs may be lost if working directory is unexpected

## Recommendation
```python
from game.core.paths import Paths

fh = logging.FileHandler(Paths.BATTLE_LOG, mode='w')
with open(Paths.CRASH_LOG, 'w') as f:
history_file = Paths.PROFILING_HISTORY
```

Optionally, add a `LOGS_DIR` for all logs:
```python
LOGS_DIR = os.path.join(ROOT_DIR, "logs")
BATTLE_LOG = os.path.join(LOGS_DIR, "battle.log")
```

## Files Affected
- `game/core/logger.py`
- `game/app.py`
- `game/core/profiling.py`
