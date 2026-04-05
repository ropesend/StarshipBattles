# Standardize star measurement to radius

## Description
Transition star size definitions and UI reporting from "diameter" to "radius" (where radius is the center hex plus outer rings) to resolve ongoing confusion over star map footprints. Stars with a specified "hex diameter" are currently incorrectly rendered using that value as their radius, making them significantly larger than intended (e.g., a 3-diameter star renders as 5 hexes in diameter).

## Screenshots
- [![Screenshot](./assets/bug_capture_144142.png)](./assets/bug_capture_144142.png) - *Shows a star that is supposed to be 3 hexes in diameter but occupies a larger area.*
- [![Screenshot](./assets/bug_capture_144159.png)](./assets/bug_capture_144159.png) - *Details of the oversized star for reference.*
- [![Screenshot](./assets/bug_capture_145050.png)](./assets/bug_capture_145050.png) - *Shows an example of a star that occupies the center plus an outer ring, illustrating a 2-radius footprint.*
- [![Screenshot](./assets/bug_capture_145101.png)](./assets/bug_capture_145101.png) - *Shows the UI reporting the same star as having a 2-diameter value instead of radius.*
