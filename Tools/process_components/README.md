# process_components

Component image processing pipeline. Three scripts cover the workflow from
raw component images to canonical sized + tagged sprites:

| Script | Purpose |
|---|---|
| `process_components.py` | Main pipeline. Trim, background-remove, resize, and emit per-component PNGs at the canonical sizes used by the game. |
| `recreate_ai_samples.py` | Generate AI-recreated component samples (uses an external image model) for QA against original art. |
| `run_ai_recreate_batches.py` | Batch driver around `recreate_ai_samples.py` for large component sets. |

## Usage

```powershell
python Tools/process_components/process_components.py --help
python Tools/process_components/recreate_ai_samples.py --help
python Tools/process_components/run_ai_recreate_batches.py --help
```

## Companion tools

- **[component_transparency_viewer](../component_transparency_viewer/)** — browser
  reviewer for staged outputs from `process_components.py` before they are
  promoted to the canonical asset set.
- **[component_visuals_manager](../component_visuals_manager/)** — web UI for
  managing sprite indices and tags after processing.
- **[image_comparator](../image_comparator/)** — side-by-side comparison of
  original vs AI-recreated samples produced by `recreate_ai_samples.py`.
