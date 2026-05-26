# Component Transparency QA Viewer

Browser tool for reviewing staged component images after black-background removal.

## Workflow

1. Generate staged assets:

```bash
python Tools/process_components/process_components.py
```

This writes cleaned masters and size variants to:

```text
assets/images/components/_processed_preview
```

For the stronger v2 GrabCut processor, run:

```bash
python Tools/process_components/process_components.py --method grabcut
```

That writes to:

```text
assets/images/components/_processed_preview_v2
```

For the conservative v3 hybrid processor, which writes only 1024 masters until
review is complete, run:

```bash
python Tools/process_components/process_components.py --method hybrid
```

That writes to:

```text
assets/images/components/_processed_preview_v3
```

2. Start the viewer:

```bash
python Tools/component_transparency_viewer/server.py
```

Open:

```text
http://127.0.0.1:8011
```

To review a specific staged folder:

```powershell
$env:COMPONENT_TRANSPARENCY_STAGING = "C:\Developer\StarshipBattles\assets\Images\Components\_processed_preview_v3"
python Tools/component_transparency_viewer/server.py
```

3. Review each image on checkerboard, black, and white backgrounds.

Statuses are saved into:

```text
assets/images/components/_processed_preview/review_manifest.json
```

Use `Recreate` for images that should be regenerated with an image model. The viewer can export those to:

```text
assets/images/components/_processed_preview/recreate_queue.json
```

4. After QA, promote staged assets into the live component folders:

```bash
python Tools/process_components/process_components.py --promote --backup
```

The backup option copies the current live component folders to:

```text
assets/images/components/_backup_before_transparency
```
