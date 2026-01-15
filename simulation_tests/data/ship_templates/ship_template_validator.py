"""
Ship Template Validator

Validates that test ship files follow the template patterns and have
consistent structure. This is a documentation/validation tool, not a
generator.

Usage:
    python ship_template_validator.py

This will:
1. Load all ship files from simulation_tests/data/ships/
2. Check that they follow template patterns
3. Report any inconsistencies or missing fields
4. Verify metadata version fields exist (from Phase 2)
"""

import json
from pathlib import Path
from typing import Dict, List, Any


class ShipTemplateValidator:
    """Validates test ship files against template patterns."""

    def __init__(self, ships_dir: Path):
        """
        Initialize validator.

        Args:
            ships_dir: Path to ships directory
        """
        self.ships_dir = ships_dir
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_all_ships(self) -> Dict[str, Any]:
        """
        Validate all ship files in the ships directory.

        Returns:
            Dict with validation results
        """
        ship_files = list(self.ships_dir.glob("*.json"))
        results = {
            'total_files': len(ship_files),
            'valid_files': 0,
            'errors': [],
            'warnings': []
        }

        for ship_file in ship_files:
            file_errors = self.validate_ship_file(ship_file)
            if not file_errors:
                results['valid_files'] += 1
            else:
                results['errors'].extend(file_errors)

        results['warnings'] = self.warnings
        return results

    def validate_ship_file(self, ship_file: Path) -> List[str]:
        """
        Validate a single ship file.

        Args:
            ship_file: Path to ship JSON file

        Returns:
            List of error messages (empty if valid)
        """
        errors = []

        try:
            with open(ship_file, 'r') as f:
                data = json.load(f)

            # Check metadata version fields (from Phase 2)
            if '_metadata' not in data:
                errors.append(f"{ship_file.name}: Missing _metadata field")
            else:
                metadata = data['_metadata']
                required_metadata = ['_schema_version', '_data_version', '_last_modified']
                for field in required_metadata:
                    if field not in metadata:
                        errors.append(f"{ship_file.name}: Missing metadata.{field}")

            # Check required ship fields
            required_fields = [
                'name', 'color', 'team_id', 'ship_class', 'theme_id',
                'ai_strategy', 'layers', 'expected_stats', 'resources'
            ]
            for field in required_fields:
                if field not in data:
                    errors.append(f"{ship_file.name}: Missing field '{field}'")

            # Check expected_stats structure
            if 'expected_stats' in data:
                required_stats = [
                    'max_hp', 'max_fuel', 'max_energy', 'max_ammo',
                    'max_speed', 'acceleration_rate', 'turn_speed',
                    'total_thrust', 'mass', 'armor_hp_pool'
                ]
                for stat in required_stats:
                    if stat not in data['expected_stats']:
                        errors.append(f"{ship_file.name}: Missing expected_stats.{stat}")

            # Check resources structure
            if 'resources' in data:
                required_resources = ['fuel', 'energy', 'ammo']
                for resource in required_resources:
                    if resource not in data['resources']:
                        errors.append(f"{ship_file.name}: Missing resources.{resource}")

            # Check layers structure
            if 'layers' in data:
                if 'CORE' not in data['layers']:
                    errors.append(f"{ship_file.name}: Missing layers.CORE")
                if 'ARMOR' not in data['layers']:
                    self.warnings.append(f"{ship_file.name}: Missing layers.ARMOR (optional)")

        except json.JSONDecodeError as e:
            errors.append(f"{ship_file.name}: Invalid JSON - {e}")
        except Exception as e:
            errors.append(f"{ship_file.name}: Validation error - {e}")

        return errors

    def print_report(self, results: Dict[str, Any]):
        """
        Print validation report.

        Args:
            results: Validation results from validate_all_ships()
        """
        print("\n" + "=" * 70)
        print("SHIP TEMPLATE VALIDATION REPORT")
        print("=" * 70)
        print(f"\nTotal Files: {results['total_files']}")
        print(f"Valid Files: {results['valid_files']}")
        print(f"Files with Errors: {len(results['errors'])}")
        print(f"Warnings: {len(results['warnings'])}")

        if results['errors']:
            print("\n" + "-" * 70)
            print("ERRORS:")
            print("-" * 70)
            for error in results['errors']:
                print(f"  ❌ {error}")

        if results['warnings']:
            print("\n" + "-" * 70)
            print("WARNINGS:")
            print("-" * 70)
            for warning in results['warnings']:
                print(f"  ⚠️  {warning}")

        if results['valid_files'] == results['total_files'] and not results['errors']:
            print("\n✅ All ship files are valid!")
        else:
            print("\n⚠️  Some ship files have issues. Please review errors above.")

        print("=" * 70 + "\n")


def main():
    """Main entry point."""
    # Find ships directory
    script_dir = Path(__file__).parent
    ships_dir = script_dir.parent / 'ships'

    if not ships_dir.exists():
        print(f"❌ Ships directory not found: {ships_dir}")
        return 1

    # Run validation
    validator = ShipTemplateValidator(ships_dir)
    results = validator.validate_all_ships()
    validator.print_report(results)

    # Return exit code
    return 0 if results['valid_files'] == results['total_files'] else 1


if __name__ == '__main__':
    exit(main())
