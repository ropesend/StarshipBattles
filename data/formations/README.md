# Formation Schema Documentation

## Overview
Formation files define ship positions in fleet formations. Each file is a JSON document containing position data for ships arranged in a specific pattern.

## File Format

```json
{
    "arrows": [
        [x1, y1],    // Position of first ship
        [x2, y2],    // Position of second ship
        ...
    ]
}
```

## Schema

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `arrows` | array | Array of [x, y] coordinate pairs defining ship positions |

### Coordinate System

- **Origin**: (0, 0) is typically the formation leader's position
- **X-axis**: Positive X is to the right
- **Y-axis**: Positive Y is downward (screen coordinates)
- **Units**: Game world units (approximately 1 unit = 1 pixel at default zoom)

### Position Array

Each element in the `arrows` array is a 2-element array:
- `[0]`: X coordinate (float)
- `[1]`: Y coordinate (float)

Example:
```json
{
    "arrows": [
        [0, 0],           // Leader position (center)
        [100, 50],        // Ship 2: 100 units right, 50 units down
        [-100, 50],       // Ship 3: 100 units left, 50 units down
        [50, -100]        // Ship 4: 50 units right, 100 units up
    ]
}
```

## Formation Types

### Arrow Formation
Ships arranged in a V or arrow shape, typically with the leader at the front.

### Circle Formation
Ships arranged in a circular pattern around a center point.

### Line Formation
Ships arranged in a horizontal or vertical line.

### Custom Formations
Any arrangement of positions that suits gameplay needs.

## Validation Rules

1. The `arrows` array must exist and contain at least one position
2. Each position must be an array of exactly 2 numeric values
3. Coordinates can be positive, negative, or zero
4. Decimal values are supported for precise positioning

## Usage

Formations are loaded by the game's formation system and applied to fleets during battle setup. The first position in the array is typically assigned to the formation leader, with subsequent positions assigned to other ships in order.

## Examples

See existing formation files in this directory:
- `initial formation.json` - Basic starting formation
- `fixed arrow.json` - Fixed arrow pattern
- `relative arrow.json` - Relative positioning arrow
- `X Formation.json` - X-shaped arrangement
