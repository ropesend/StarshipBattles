# Starship Battles Theme Notes

`ShipThemeManager` discovers themes from `assets/ShipThemes/<ThemeName>/theme.json`.

Use the legacy-compatible manifest schema:

```json
{
  "name": "<ThemeName>",
  "description": "<short art direction>",
  "images": {
    "Escort": "Skins/escort.png"
  }
}
```

Portrait loading is convention-based and separate from `theme.json`:

- `Escort` -> `Portraits/Escort_Portrait.jpg`
- `Light Cruiser` -> `Portraits/LightCruiser_Portrait.jpg`
- `Fighter (Medium)` -> `Portraits/MediumFighter_Portrait.jpg`
- `Satellite (Heavy)` -> `Portraits/HeavySatellite_Portrait.jpg`

Target dimensions:

- Skins: `2048x2048` PNG with alpha.
- Portraits: `1024x1024` JPG.

Source images from the model should be preserved under `Production/skin_sources` and `Production/portrait_sources`.
