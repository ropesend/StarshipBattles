# Find Orphaned Tests

Finds test files in `tests/unit/` whose corresponding source file no longer exists.

## Purpose

When production source files are renamed, moved, or deleted, their test files can become orphaned -- they still exist but test code that no longer exists in the expected location. This tool identifies those orphaned test files so they can be updated or removed.

## Requirements

No additional dependencies beyond the base project.

## Usage

```bash
python Tools/find_orphaned_tests/find_orphaned_tests.py
```

No arguments. Scans `tests/unit/` against `game/` automatically.

## How It Works

For each `test_*.py` file found under `tests/unit/`, the tool constructs expected source file paths using naming conventions:

1. **Direct mapping**: `tests/unit/core/test_config.py` expects `game/core/config.py`
2. **Package mapping**: `tests/unit/core/test_config.py` expects `game/core/config/__init__.py`

If neither expected path exists, the test file is flagged as orphaned.

## Output

```
Scanning for orphaned tests...
Found 3 potentially orphaned tests.
Orph: C:\Dev\Starship Battles\tests\unit\core\test_old_module.py
Orph: C:\Dev\Starship Battles\tests\unit\simulation\test_removed_system.py
Orph: C:\Dev\Starship Battles\tests\unit\ui\test_legacy_screen.py
```

## Limitations

- Only checks `tests/unit/` against `game/`. Does not scan `tests/integration/` or other test directories.
- Assumes the `test_<name>.py` to `<name>.py` naming convention. Tests with non-standard names will not be matched.
- A test file may test code that was intentionally restructured (not deleted), so results should be reviewed manually.
