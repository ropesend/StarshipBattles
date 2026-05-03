# Review Scope: 2026-01-27_general_path-centralization

## Metadata
- **Date:** 2026-01-27
- **Type:** General Review - Path Configuration Analysis
- **Description:** Find all file path references to enable centralized configuration

## Scope Definition

### Target
- [x] Entire codebase (all Python files)
- [x] Focus areas:
  - Hardcoded file paths
  - Directory references
  - Data file loading (JSON, assets, etc.)
  - Log file locations
  - Save/load operations

### Priorities
1. Find all hardcoded paths that bypass existing constants
2. Identify path categories (data, assets, saves, logs, etc.)
3. Design centralized configuration system
4. Create migration plan with minimal code changes

### Exclusions
- Third-party code
- Generated files
- Test data files (content, not path references)

## Agent Configuration
**Agents Used:**
- File I/O Operations Mapper (Explore agent)
- Path Configuration Designer (Plan agent)

**Rationale:** Focused analysis requiring comprehensive search followed by design recommendation

### Assessment Approach
| Phase | Action | Status |
|-------|--------|--------|
| 1 | Map all file I/O operations | Complete |
| 2 | Identify hardcoded paths | Complete |
| 3 | Categorize path types | Complete |
| 4 | Design centralized system | Complete |
| 5 | Generate migration plan | Complete |

## Findings Summary

| Category | Files Affected | Key Paths |
|----------|---------------|-----------|
| Core Data | 6 | `DATA_DIR`, `COMPONENTS_FILE`, `MODIFIERS_FILE` |
| Assets | 4 | `ASSET_DIR`, `ASSET_MANIFEST_FILE`, `SHIP_THEMES_DIR` |
| User Data | 4 | `SAVES_DIR`, `RACES_DIR`, `SHIPS_DIR` |
| Config | 3 | `FORMATIONS_DIR`, `TECH_PRESETS_DIR` |
| Logs | 3 | `BATTLE_LOG`, `CRASH_LOG`, `PROFILING_HISTORY` |
| **Total** | **47+** | Files with hardcoded paths |

## User Requirements
- Single location to control all folder paths
- Moving a folder should require minimal code edits
- Prefer Python (.py) or JSON format
- Keep new file formats to minimum

## Notes
- Partial centralization already exists in `game/core/constants.py` (lines 39-53)
- Test fixtures at `tests/fixtures/paths.py` use modern pathlib pattern
- Solution should maintain backward compatibility with existing imports
