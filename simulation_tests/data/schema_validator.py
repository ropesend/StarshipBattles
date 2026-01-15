"""
Schema Validation Utility for Combat Lab Test Data

Validates JSON data files against JSON Schema definitions to catch:
- Missing required fields
- Invalid data types
- Out-of-range values
- Invalid references
- Malformed structures

Usage:
    from simulation_tests.data.schema_validator import validate_test_data

    # Validate all test data
    validate_test_data()

    # Validate specific file
    from simulation_tests.data.schema_validator import validate_file
    validate_file('components.json', 'components.schema.json')
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, List, Tuple

try:
    import jsonschema
    from jsonschema import validate, ValidationError, SchemaError
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False
    print("Warning: jsonschema not installed. Schema validation disabled.")
    print("Install with: pip install jsonschema")


# Paths
DATA_DIR = Path(__file__).parent
SCHEMAS_DIR = DATA_DIR / "schemas"
SHIPS_DIR = DATA_DIR / "ships"


class ValidationResult:
    """Result of schema validation."""

    def __init__(self, file_path: str, success: bool, errors: Optional[List[str]] = None):
        self.file_path = file_path
        self.success = success
        self.errors = errors or []

    def __str__(self):
        if self.success:
            return f"[PASS] {self.file_path}: Valid"
        else:
            error_str = "\n  ".join(self.errors)
            return f"[FAIL] {self.file_path}: Invalid\n  {error_str}"


def load_schema(schema_name: str) -> Optional[Dict]:
    """
    Load a JSON schema file.

    Args:
        schema_name: Schema filename (e.g., 'components.schema.json')

    Returns:
        Schema dictionary, or None if not found
    """
    schema_path = SCHEMAS_DIR / schema_name

    if not schema_path.exists():
        print(f"Warning: Schema not found: {schema_path}")
        return None

    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in schema {schema_name}: {e}")
        return None


def validate_file(
    data_file: str,
    schema_file: str,
    data_dir: Optional[Path] = None
) -> ValidationResult:
    """
    Validate a JSON data file against a schema.

    Args:
        data_file: Data filename (e.g., 'components.json')
        schema_file: Schema filename (e.g., 'components.schema.json')
        data_dir: Optional data directory (defaults to DATA_DIR)

    Returns:
        ValidationResult object
    """
    if not JSONSCHEMA_AVAILABLE:
        return ValidationResult(data_file, True, ["jsonschema not available - validation skipped"])

    # Load schema
    schema = load_schema(schema_file)
    if schema is None:
        return ValidationResult(data_file, False, [f"Schema {schema_file} not found"])

    # Load data
    data_path = (data_dir or DATA_DIR) / data_file
    if not data_path.exists():
        return ValidationResult(data_file, False, [f"Data file not found: {data_path}"])

    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return ValidationResult(data_file, False, [f"Invalid JSON: {e}"])

    # Validate
    try:
        validate(instance=data, schema=schema)
        return ValidationResult(data_file, True)
    except ValidationError as e:
        # Extract meaningful error message
        error_path = " -> ".join(str(p) for p in e.path) if e.path else "root"
        error_msg = f"At {error_path}: {e.message}"
        return ValidationResult(data_file, False, [error_msg])
    except SchemaError as e:
        return ValidationResult(data_file, False, [f"Schema error: {e.message}"])


def validate_ship_file(ship_file: str) -> ValidationResult:
    """
    Validate a ship configuration file.

    Args:
        ship_file: Ship filename (e.g., 'Test_Target_Stationary.json')

    Returns:
        ValidationResult object
    """
    return validate_file(ship_file, 'ship.schema.json', data_dir=SHIPS_DIR)


def validate_test_data(verbose: bool = True) -> Tuple[int, int]:
    """
    Validate all Combat Lab test data files.

    Args:
        verbose: If True, print validation results

    Returns:
        Tuple of (passed_count, failed_count)
    """
    if not JSONSCHEMA_AVAILABLE:
        if verbose:
            print("Warning: jsonschema not installed. Schema validation disabled.")
        return (0, 0)

    results = []

    # Validate core data files
    core_files = [
        ('components.json', 'components.schema.json'),
        ('modifiers.json', 'modifiers.schema.json'),
        ('vehicleclasses.json', 'vehicleclasses.schema.json')
    ]

    for data_file, schema_file in core_files:
        result = validate_file(data_file, schema_file)
        results.append(result)

    # Validate all ship files
    if SHIPS_DIR.exists():
        for ship_file in SHIPS_DIR.glob('*.json'):
            result = validate_ship_file(ship_file.name)
            results.append(result)

    # Count results
    passed = sum(1 for r in results if r.success)
    failed = sum(1 for r in results if not r.success)

    # Print results
    if verbose:
        print(f"\n{'='*60}")
        print("Combat Lab Test Data Validation")
        print(f"{'='*60}\n")

        for result in results:
            print(result)

        print(f"\n{'='*60}")
        print(f"Results: {passed} passed, {failed} failed")
        print(f"{'='*60}\n")

        if failed > 0:
            print("[WARNING] Some files failed validation. Please fix errors above.")
        else:
            print("[SUCCESS] All test data files are valid!")

    return (passed, failed)


def validate_component_references(verbose: bool = True) -> Tuple[int, int]:
    """
    Validate that all component references in ship files exist in components.json.

    This is a semantic validation beyond JSON Schema - ensures referential integrity.

    Args:
        verbose: If True, print validation results

    Returns:
        Tuple of (valid_ships, invalid_ships)
    """
    # Load component IDs
    components_path = DATA_DIR / 'components.json'
    if not components_path.exists():
        if verbose:
            print("Error: components.json not found")
        return (0, 0)

    try:
        with open(components_path, 'r', encoding='utf-8') as f:
            components_data = json.load(f)
        component_ids = {comp['id'] for comp in components_data.get('components', [])}
    except (json.JSONDecodeError, KeyError) as e:
        if verbose:
            print(f"Error loading components.json: {e}")
        return (0, 0)

    # Check each ship file
    valid_ships = 0
    invalid_ships = 0
    errors = []

    if not SHIPS_DIR.exists():
        if verbose:
            print("Warning: ships directory not found")
        return (0, 0)

    for ship_file in SHIPS_DIR.glob('*.json'):
        try:
            with open(ship_file, 'r', encoding='utf-8') as f:
                ship_data = json.load(f)

            # Extract all component references
            ship_errors = []
            layers = ship_data.get('layers', {})
            for layer_name, components in layers.items():
                for idx, comp_ref in enumerate(components):
                    comp_id = comp_ref.get('id')
                    if comp_id not in component_ids:
                        ship_errors.append(
                            f"  Layer {layer_name}[{idx}]: Unknown component '{comp_id}'"
                        )

            if ship_errors:
                invalid_ships += 1
                errors.append(f"[FAIL] {ship_file.name}:")
                errors.extend(ship_errors)
            else:
                valid_ships += 1
                if verbose:
                    print(f"[PASS] {ship_file.name}: All component references valid")

        except (json.JSONDecodeError, KeyError) as e:
            invalid_ships += 1
            errors.append(f"[FAIL] {ship_file.name}: Error reading file: {e}")

    # Print errors
    if verbose and errors:
        print(f"\n{'='*60}")
        print("Component Reference Validation Errors")
        print(f"{'='*60}\n")
        for error in errors:
            print(error)

    if verbose:
        print(f"\n{'='*60}")
        print(f"Component References: {valid_ships} valid, {invalid_ships} invalid")
        print(f"{'='*60}\n")

    return (valid_ships, invalid_ships)


if __name__ == "__main__":
    """Run validation when executed directly."""
    import sys

    print("Validating Combat Lab test data...\n")

    # Schema validation
    passed, failed = validate_test_data(verbose=True)

    # Referential integrity validation
    valid_refs, invalid_refs = validate_component_references(verbose=True)

    # Summary
    if failed > 0 or invalid_refs > 0:
        print("\n[FAILED] Validation completed with errors")
        sys.exit(1)
    else:
        print("\n[SUCCESS] All validation checks passed!")
        sys.exit(0)
