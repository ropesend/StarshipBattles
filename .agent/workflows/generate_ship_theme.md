---
description: Generate a new ShipTheme with 19 assets (11 ships, 4 fighters, 4 satellites)
---
# AI Ship Theme Asset Creation Workflow

This workflow guides you through creating a complete `ShipTheme` using AI.

## 1. Initialization
- [ ] Determine the **Theme Name** (e.g., "Obsidian", "Vanguard").
- [ ] Provide a **Seed Image** (top-down view) and **Skin Reference**.
- [ ] Create the theme directory: `assets/ShipThemes/[ThemeName]/`
- [ ] Create subdirectories: `Skins/`, `Portraits/`, `Original/`.

## 2. Generating Skins (Interactive)
For each of the 11 ship classes, 4 fighters, and 4 satellites:

### Classes:
- **Ships**: Escort, Frigate, Destroyer, Light Cruiser, Cruiser, Heavy Cruiser, Battle Cruiser, Battleship, Dreadnought, Superdreadnought, Monitor
- **Fighters**: Fighter (Small), Fighter (Medium), Fighter (Large), Fighter (Heavy)
- **Satellites**: Satellite (Small), Satellite (Medium), Satellite (Large), Satellite (Heavy)

### Prompt Strategy:
- **Reference**: Always provide the **Seed Image** path to the generation tool.
- **Constraints**: 
    - Top-down view, flat black background.
    - **NO rocket/engine plumes** (directional light rays/fire), but glowing engine ports are encouraged.
    - No text, labels, or UI elements.

### Differentiation Strategy:
| Class | Suggested Variations |
| :--- | :--- |
| **Escort/Fighter** | Sleek, narrow body, single pair of wings/fins, fewer windows. |
| **Cruiser** | Wider body, dual engine clusters, 2-3 sets of wings, visible bridge/windows. |
| **Battleship** | Massive central spine, multiple hull segments, 4+ engine pods, heavy armor plating. |
| **Dreadnought** | Extremely wide or long, extra sets of outrigger wings, maximum detail/windows. |
| **Satellite** | Circular or hexagonal symmetry, solar panels, sensor arrays, no obvious "front" cockpit. |

### Step-by-Step Generation:
1. Generate **all 11 ship classes** in a single pass (Escort through Monitor).
2. **Batch Review**:
    - The user reviews the entire fleet.
    - Specific ships are **Accepted** (moved to `Original/`) or **Re-rolled** (regenerated with tweaked prompts).
3. Once the 11 ships are finalized, proceed to Fighters and Satellites in a similar batch.

## 3. Background Removal (IOPaint)
- [ ] Run **IOPaint** on all images in `Original/`.
- [ ] Export processed images to `Skins/` as transparent PNGs.
- [ ] Run the processing script to center and frame:
```powershell
python scripts/ship_background_remover.py --input "assets/ShipThemes/[ThemeName]/Skins" --output "assets/ShipThemes/[ThemeName]/Skins" --threshold 30
```

## 4. Generating Portraits
- [ ] For each class, generate a cinematic **Portrait** (perspective view, industrial/space background).
- [ ] Save as JPGs in `Portraits/` with naming: `[Class]_Portrait.jpg`.

## 5. Finalizing Theme
- [ ] Generate `theme.json` mapping all 19 assets.
- [ ] Verify in-game in the "Select Ship Theme" gallery.
