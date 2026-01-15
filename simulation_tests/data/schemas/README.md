# Combat Lab Data Schemas

JSON Schema definitions for validating Combat Lab test data files.

## Overview

These schemas validate the structure and data types of Combat Lab test data to catch errors early:

- **Required fields** - Ensures all mandatory fields are present
- **Data types** - Validates strings, numbers, arrays, objects
- **Value constraints** - Checks ranges, patterns, enums
- **Referential integrity** - Validates component references exist

## Schema Files

| Schema | Validates | Required Fields |
|--------|-----------|-----------------|
| [components.schema.json](components.schema.json) | Component definitions | id, name, type, mass, hp |
| [vehicleclasses.schema.json](vehicleclasses.schema.json) | Vehicle class definitions | name, type, max_mass, default_hull_id, layers |
| [ship.schema.json](ship.schema.json) | Ship configuration files | name, color, team_id, ship_class, layers |
| [modifiers.schema.json](modifiers.schema.json) | Stat modifier definitions | id, name, type, stat, value |

## Usage

### Automatic Validation (Pytest)

Schemas are automatically validated when running pytest:

```bash
pytest simulation_tests/
```

The `conftest.py` fixture validates all data files before tests run. If validation fails, the test session aborts with clear error messages.

### Manual Validation

Run the validator directly:

```bash
# From project root
python -m simulation_tests.data.schema_validator

# Output:
# [PASS] components.json: Valid
# [PASS] modifiers.json: Valid
# [PASS] vehicleclasses.json: Valid
# [PASS] Test_Attacker.json: Valid
# ...
# Results: 25 passed, 0 failed
```

### Programmatic Validation

Use the validation utilities in your code:

```python
from simulation_tests.data.schema_validator import validate_file, validate_test_data

# Validate single file
result = validate_file('components.json', 'components.schema.json')
if result.success:
    print(f"{result.file_path} is valid")
else:
    for error in result.errors:
        print(f"Error: {error}")

# Validate all test data
passed, failed = validate_test_data(verbose=True)
```

## Schema Details

### components.schema.json

Validates component definitions with:

- **Component ID pattern**: `^[a-zA-Z0-9_]+$`
- **Mass/HP constraints**: `>= 0`
- **Accuracy range**: `0-1` for weapons
- **Type validation**: Any string (flexible for test components)

Example component structure:
```json
{
  "id": "test_beam_weapon",
  "name": "Test Beam Weapon",
  "type": "BeamWeapon",
  "mass": 10,
  "hp": 50,
  "damage": 1,
  "accuracy": 0.8,
  "accuracy_falloff": 0.001,
  "range": 1000
}
```

### vehicleclasses.schema.json

Validates vehicle class definitions with:

- **Layer types**: CORE, ARMOR, SURFACE, EXTERNAL, WEAPONS, INNER, OUTER
- **Radius percentage**: `0-1`
- **Mass percentage**: `0-1`
- **Vehicle types**: Ship, Fighter, Station, Base, Satellite

Example vehicle class structure:
```json
{
  "name": "TestS_2L",
  "type": "Ship",
  "max_mass": 2000,
  "default_hull_id": "hull_test_s",
  "layers": [
    {
      "type": "CORE",
      "radius_pct": 0.6,
      "max_mass_pct": 1.0
    },
    {
      "type": "ARMOR",
      "radius_pct": 1.0,
      "max_mass_pct": 1.0
    }
  ]
}
```

### ship.schema.json

Validates ship configuration files with:

- **Team ID**: `>= 0` (0=neutral, 1=team1, 2=team2)
- **RGB color**: `[0-255, 0-255, 0-255]`
- **Component references**: Must have `id` field
- **Layer validation**: Matches vehicle class layer types
- **Optional fields**: expected_stats, resources, _test_notes

Example ship structure:
```json
{
  "name": "Test Attacker",
  "color": [255, 0, 0],
  "team_id": 1,
  "ship_class": "TestM_2L",
  "theme_id": "Federation",
  "ai_strategy": "test_do_nothing",
  "layers": {
    "CORE": [
      {"id": "test_bridge_basic"},
      {"id": "test_engine_std"}
    ],
    "ARMOR": [
      {"id": "test_armor_light"}
    ]
  },
  "resources": {
    "fuel": 1000.0,
    "energy": 500.0,
    "ammo": 100.0
  }
}
```

### modifiers.schema.json

Validates stat modifier definitions with:

- **Modifier types**: additive, multiplicative, override
- **Stat name**: Any string
- **Value**: Any number

Example modifier structure:
```json
{
  "id": "damage_boost_10",
  "name": "Damage Boost +10%",
  "type": "multiplicative",
  "stat": "damage",
  "value": 1.1,
  "description": "Increases damage by 10%"
}
```

## Validation Features

### Schema Validation

- **Structure checks**: Required fields, correct types
- **Range validation**: min/max constraints on numbers
- **Pattern matching**: Regex validation for IDs
- **Enum validation**: Restricted values for specific fields

### Referential Integrity

Beyond schema validation, the validator also checks:

- **Component references**: All component IDs in ship files exist in `components.json`
- **Cross-file consistency**: Ship classes reference valid vehicle classes

Example output:
```
============================================================
Component References: 22 valid, 0 invalid
============================================================
```

## Error Messages

Clear, actionable error messages pinpoint issues:

```
[FAIL] Test_Attacker.json: Invalid
  At team_id: 0 is less than the minimum of 1
```

The error shows:
- **File name**: Which file has the error
- **Path**: Exact location in the JSON structure
- **Issue**: What constraint was violated

## Maintenance

### Adding New Component Types

If you add a new component type, it will automatically work (type field accepts any string). No schema updates needed.

### Adding New Fields

To require new fields in schemas:

1. Edit the appropriate `.schema.json` file
2. Add field to `required` array
3. Add field definition to `properties` object
4. Run validator to ensure existing data still passes

### Testing Schema Changes

After modifying schemas:

```bash
# Validate all test data
python -m simulation_tests.data.schema_validator

# Run full test suite
pytest simulation_tests/
```

## Dependencies

Requires the `jsonschema` package:

```bash
pip install jsonschema
```

If `jsonschema` is not installed, validation is skipped with a warning.

## Benefits

1. **Early error detection** - Catch data errors before runtime
2. **Clear error messages** - Pinpoint exact location of issues
3. **Prevents silent failures** - Missing/wrong data is immediately visible
4. **Documentation** - Schemas serve as formal data structure documentation
5. **Confidence** - Test data is known to be structurally valid

## References

- [JSON Schema Documentation](https://json-schema.org/)
- [jsonschema Python Package](https://python-jsonschema.readthedocs.io/)
- [Combat Lab Data README](../README.md)
