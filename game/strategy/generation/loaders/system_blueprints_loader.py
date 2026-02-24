"""
System blueprints loader for star system generation.

Loads and validates system blueprints from JSON configuration.
"""
import json
import random
from pathlib import Path
from typing import Dict, Any, Optional

from game.core.json_utils import load_json_required
from game.core.exceptions import ValidationException
from game.core.error_codes import ErrorCode


class SystemBlueprintsLoader:
    """
    Loader for system_blueprints.json.

    System blueprints define templates for generating star systems with
    specific characteristics (star count, planet count, mass distributions).
    """

    DEFAULT_PATH = Path("data/system_blueprints.json")

    def __init__(self, file_path: Optional[Path] = None):
        """
        Initialize loader with optional custom path.

        Args:
            file_path: Optional path to blueprints JSON. Uses default if None.
        """
        self.file_path = file_path or self.DEFAULT_PATH

    def load(self) -> Dict[str, Any]:
        """
        Load and validate blueprints from JSON file.

        Returns:
            Dict containing 'blueprints' key with all defined blueprints.

        Raises:
            FileNotFoundError: If file doesn't exist.
            json.JSONDecodeError: If file isn't valid JSON.
            ValidationException: If schema validation fails.
        """
        data = load_json_required(str(self.file_path))
        self._validate_schema(data)
        return data

    def get_blueprint(self, name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get a specific blueprint by name.

        Args:
            name: Blueprint name (e.g., 'solar_like', 'binary_no_planets').
            data: Loaded blueprints data from load().

        Returns:
            Blueprint configuration dict.

        Raises:
            KeyError: If blueprint name not found.
        """
        blueprints = data.get("blueprints", {})
        if name not in blueprints:
            raise KeyError(f"Unknown blueprint: {name}. Available: {list(blueprints.keys())}")
        return blueprints[name]

    def select_random_blueprint(self, data: Dict[str, Any], rng: Optional[random.Random] = None) -> str:
        """
        Select a random blueprint using weighted selection.

        Args:
            data: Loaded blueprints data from load().
            rng: Optional random.Random instance for deterministic selection.

        Returns:
            Name of selected blueprint.
        """
        if rng is None:
            rng = random.Random()

        blueprints = data.get("blueprints", {})

        # Build weighted list
        names = []
        weights = []
        for name, bp in blueprints.items():
            weight = bp.get("weight", 1.0)
            if weight > 0:
                names.append(name)
                weights.append(weight)

        if not names:
            raise ValidationException(
                "No blueprints with positive weight found",
                code=ErrorCode.VALIDATION_FAILED.value,
                context={"reason": "no_positive_weights"}
            )

        # Weighted random selection
        total = sum(weights)
        r = rng.random() * total
        cumulative = 0
        for name, weight in zip(names, weights):
            cumulative += weight
            if r <= cumulative:
                return name

        return names[-1]  # Fallback to last

    def _validate_schema(self, data: Dict[str, Any]) -> None:
        """
        Validate blueprints schema.

        Args:
            data: Loaded JSON data.

        Raises:
            ValidationException: If schema is invalid.
        """
        if not isinstance(data, dict):
            raise ValidationException(
                "Blueprints data must be a dict",
                code=ErrorCode.SCHEMA_VALIDATION_ERROR.value,
                context={"expected_type": "dict", "actual_type": type(data).__name__}
            )

        if "blueprints" not in data:
            raise ValidationException(
                "Missing 'blueprints' key",
                code=ErrorCode.SCHEMA_VALIDATION_ERROR.value,
                context={"missing_key": "blueprints"}
            )

        blueprints = data["blueprints"]
        if not isinstance(blueprints, dict):
            raise ValidationException(
                "'blueprints' must be a dict",
                code=ErrorCode.SCHEMA_VALIDATION_ERROR.value,
                context={"key": "blueprints", "expected_type": "dict"}
            )

        for name, bp in blueprints.items():
            self._validate_blueprint(name, bp)

    def _validate_blueprint(self, name: str, bp: Dict[str, Any]) -> None:
        """
        Validate a single blueprint.

        Args:
            name: Blueprint name (for error messages).
            bp: Blueprint configuration.

        Raises:
            ValidationException: If blueprint is invalid.
        """
        # Required fields
        if "star_count" not in bp:
            raise ValidationException(
                f"Blueprint '{name}' missing required field",
                code=ErrorCode.SCHEMA_VALIDATION_ERROR.value,
                context={"blueprint": name, "missing_field": "star_count"}
            )
        if "planet_count" not in bp:
            raise ValidationException(
                f"Blueprint '{name}' missing required field",
                code=ErrorCode.SCHEMA_VALIDATION_ERROR.value,
                context={"blueprint": name, "missing_field": "planet_count"}
            )
        if "weight" not in bp:
            raise ValidationException(
                f"Blueprint '{name}' missing required field",
                code=ErrorCode.SCHEMA_VALIDATION_ERROR.value,
                context={"blueprint": name, "missing_field": "weight"}
            )

        # Validate star_count
        star_count = bp["star_count"]
        if isinstance(star_count, int):
            if not 1 <= star_count <= 4:
                raise ValidationException(
                    f"Blueprint '{name}' star_count must be 1-4",
                    code=ErrorCode.OUT_OF_RANGE.value,
                    context={"blueprint": name, "field": "star_count", "value": star_count, "valid_range": "1-4"}
                )
        elif isinstance(star_count, dict):
            if "min" in star_count:
                if not (1 <= star_count["min"] <= star_count.get("max", 4) <= 4):
                    raise ValidationException(
                        f"Blueprint '{name}' star_count range invalid",
                        code=ErrorCode.OUT_OF_RANGE.value,
                        context={"blueprint": name, "field": "star_count", "min": star_count.get("min"), "max": star_count.get("max")}
                    )
            elif "distribution" not in star_count:
                raise ValidationException(
                    f"Blueprint '{name}' star_count missing min or distribution",
                    code=ErrorCode.SCHEMA_VALIDATION_ERROR.value,
                    context={"blueprint": name, "field": "star_count", "reason": "missing_min_or_distribution"}
                )
        else:
            raise ValidationException(
                f"Blueprint '{name}' star_count must be int or dict",
                code=ErrorCode.SCHEMA_VALIDATION_ERROR.value,
                context={"blueprint": name, "field": "star_count", "expected_type": "int or dict", "actual_type": type(star_count).__name__}
            )

        # Validate planet_count
        planet_count = bp["planet_count"]
        if not isinstance(planet_count, dict):
            raise ValidationException(
                f"Blueprint '{name}' planet_count must be dict with min/max",
                code=ErrorCode.SCHEMA_VALIDATION_ERROR.value,
                context={"blueprint": name, "field": "planet_count", "expected_type": "dict"}
            )
        if "min" not in planet_count or "max" not in planet_count:
            raise ValidationException(
                f"Blueprint '{name}' planet_count missing min or max",
                code=ErrorCode.SCHEMA_VALIDATION_ERROR.value,
                context={"blueprint": name, "field": "planet_count", "reason": "missing_min_or_max"}
            )
        if planet_count["min"] < 0 or planet_count["max"] < planet_count["min"]:
            raise ValidationException(
                f"Blueprint '{name}' planet_count range invalid",
                code=ErrorCode.OUT_OF_RANGE.value,
                context={"blueprint": name, "field": "planet_count", "min": planet_count["min"], "max": planet_count["max"]}
            )

        # Validate weight
        if bp["weight"] <= 0:
            raise ValidationException(
                f"Blueprint '{name}' weight must be positive",
                code=ErrorCode.OUT_OF_RANGE.value,
                context={"blueprint": name, "field": "weight", "value": bp["weight"], "constraint": "must be positive"}
            )
