# Nebula to Alpha

Converts nebula and space background images on black backgrounds into transparent PNGs using pixel intensity as alpha.

## Purpose

Many space art assets (nebulae, system backgrounds, warp point effects) are delivered as images on a solid black background. This tool converts them into transparent PNGs so they can be composited and layered in-game. It uses the maximum channel intensity of each pixel to derive an alpha value, then applies gamma correction to brighten midtones and preserve detail in darker regions.

## Requirements

- `Pillow` (PIL)
- `numpy`

## Usage

```bash
python Tools/nebula_to_alpha/nebula_to_alpha.py
```

The tool takes no command-line arguments. It processes three hardcoded asset directories automatically:

1. **Nebulae** -- `assets/Images/Stellar Objects/Nebulae/Nebulae_*.png` (outputs `*_transparent.png` alongside originals)
2. **System Backgrounds** -- `assets/Images/System Backgrounds/*.jpg` (outputs `.png` versions)
3. **Warp Points** -- `assets/Images/Stellar Objects/Warp Points/*.jpg` (outputs `.png` versions)

### Processing Parameters

All three directories use `gamma_color=0.7` and `gamma_alpha=0.5`. The core function `process_nebula()` accepts:

| Parameter     | Default | Description                                              |
|---------------|---------|----------------------------------------------------------|
| `gamma_color` | 0.8     | Gamma applied to RGB channels. Lower values brighten midtones. |
| `gamma_alpha` | 0.6     | Gamma applied to the alpha channel. Lower values make more of the image opaque. |

## Output

Transparent RGBA `.png` files saved alongside (or in place of) the originals. Files already containing `_transparent` in the name are skipped to avoid reprocessing.
