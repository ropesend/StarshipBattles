"""Ship-portrait regeneration CLI (PROJ-314).

Backfills missing ship portraits via ``gpt-image-2`` through the
:class:`game.ui.services.image.ImageProvider` abstraction. Idempotent:
skips ships whose portrait already exists unless ``--force`` is set.

Pre-conditions:

* ``OPENAI_API_KEY`` set in the environment.
* The target theme.json has been migrated to the PROJ-314 schema (PROJ-314
  Phase 5).

Examples::

    # Backfill every missing portrait in Aetherwake.
    python -m Tools.regenerate_ship_portraits.cli --theme Aetherwake

    # Backfill a single ship in a single theme.
    python -m Tools.regenerate_ship_portraits.cli --theme Atlantians \\
        --ship-class "Light Cruiser"

    # Plan only — print what would be generated, do not call OpenAI.
    python -m Tools.regenerate_ship_portraits.cli --theme Aetherwake --dry-run

    # Re-generate even if the portrait already exists.
    python -m Tools.regenerate_ship_portraits.cli --theme Aetherwake --force

Cost cap: ``--cost-cap`` (default $5.00) is a hard limit on estimated
spend per run. The tool uses an estimated $0.04 per 2048×2048 image
which is OpenAI's quoted high-resolution price; adjust the constant
:data:`COST_PER_IMAGE_USD` if pricing changes.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import pathlib
import sys
import time
from dataclasses import asdict, dataclass, field
from typing import Optional

from game.core.exceptions import ImageException
from game.core.paths import Paths
from game.core.ship_classes import SHIP_CLASSES_WITH_VISUAL_THEMES
from game.ui.services.image import (
    ImageProvider,
    ImageProviderFactory,
    ImageResult,
    NullImageProvider,
)

from Tools.regenerate_ship_portraits.prompts import build_prompt

logger = logging.getLogger(__name__)

# Default per-image cost estimate ($0.04 = OpenAI's quoted price for
# 2048x2048 high-quality gpt-image-2 generations as of 2026-04. Override
# with --cost-per-image if pricing changes.).
COST_PER_IMAGE_USD: float = 0.04

LAST_RUN_PATH = (
    pathlib.Path(__file__).resolve().parent / "last_run.json"
)


@dataclass
class GenerationRequest:
    """A single planned portrait generation."""
    theme: str
    ship_class: str
    portrait_path: str
    prompt: str
    skip_reason: Optional[str] = None  # set when this entry will be skipped.


@dataclass
class GenerationResult:
    """Outcome of one generation request."""
    request: GenerationRequest
    ok: bool
    actual_size: Optional[tuple[int, int]] = None
    bytes_written: int = 0
    error: Optional[str] = None
    request_id: Optional[str] = None
    revised_prompt: Optional[str] = None
    latency_ms: float = 0.0


@dataclass
class RunManifest:
    """Manifest persisted to ``last_run.json``."""
    started_at: str
    finished_at: str
    args: dict
    results: list[dict] = field(default_factory=list)


def _load_theme_json(theme_dir: pathlib.Path) -> dict:
    """Load and return the theme.json payload."""
    json_path = theme_dir / "theme.json"
    if not json_path.exists():
        raise FileNotFoundError(f"theme.json not found in {theme_dir}")
    with json_path.open(encoding="utf-8") as fh:
        return json.load(fh)


def _list_themes() -> list[str]:
    """Return sorted list of theme names under assets/ShipThemes/."""
    root = pathlib.Path(Paths.SHIP_THEMES_DIR)
    return sorted(p.name for p in root.iterdir() if p.is_dir())


def _portrait_default_path(ship_class: str) -> str:
    """Default relative path for a generated portrait file."""
    safe = (
        ship_class.lower()
        .replace("(", "")
        .replace(")", "")
        .replace(" ", "_")
        .replace("__", "_")
    )
    return f"Portraits/{safe}.png"


def plan_generations(
    theme: str,
    ship_class_filter: Optional[str],
    *,
    force: bool,
) -> list[GenerationRequest]:
    """Build the list of GenerationRequest for a theme.

    Args:
        theme: Theme name (must be a directory under assets/ShipThemes/).
        ship_class_filter: When set, plan only this single ship class.
        force: When True, regenerate even if portrait file exists.

    Returns:
        List of GenerationRequest, with ``skip_reason`` set on entries
        that won't be regenerated.
    """
    theme_dir = pathlib.Path(Paths.SHIP_THEMES_DIR) / theme
    if not theme_dir.is_dir():
        raise FileNotFoundError(f"Theme not found: {theme_dir}")
    data = _load_theme_json(theme_dir)
    description = data.get("description", "")
    assets = data.get("assets") or {}

    classes = (
        [ship_class_filter] if ship_class_filter
        else list(SHIP_CLASSES_WITH_VISUAL_THEMES)
    )

    plans: list[GenerationRequest] = []
    for ship_class in classes:
        if ship_class not in SHIP_CLASSES_WITH_VISUAL_THEMES:
            plans.append(GenerationRequest(
                theme=theme,
                ship_class=ship_class,
                portrait_path="",
                prompt="",
                skip_reason=f"unknown ship class: {ship_class!r}",
            ))
            continue

        entry = assets.get(ship_class) if isinstance(assets, dict) else None
        portrait_rel = (entry or {}).get("portrait") if isinstance(entry, dict) else None
        if not portrait_rel:
            portrait_rel = _portrait_default_path(ship_class)

        portrait_abs = theme_dir / portrait_rel
        portrait_str = str(portrait_abs)
        if portrait_abs.exists() and not force:
            plans.append(GenerationRequest(
                theme=theme,
                ship_class=ship_class,
                portrait_path=portrait_str,
                prompt="",
                skip_reason="portrait already exists (pass --force to overwrite)",
            ))
            continue

        prompt = build_prompt(theme, description, ship_class)
        plans.append(GenerationRequest(
            theme=theme,
            ship_class=ship_class,
            portrait_path=portrait_str,
            prompt=prompt,
        ))
    return plans


def generate_one(
    provider: ImageProvider,
    request: GenerationRequest,
    *,
    model: str,
    size: str,
) -> GenerationResult:
    """Generate one portrait via the provider and write it to disk."""
    start = time.monotonic()
    try:
        result: ImageResult = provider.generate_image(
            request.prompt, size=size, model=model,
        )
    except ImageException as e:
        return GenerationResult(
            request=request,
            ok=False,
            error=f"{type(e).__name__}: {e}",
            latency_ms=(time.monotonic() - start) * 1000.0,
        )

    portrait_path = pathlib.Path(request.portrait_path)
    portrait_path.parent.mkdir(parents=True, exist_ok=True)
    portrait_path.write_bytes(result.image_bytes)

    return GenerationResult(
        request=request,
        ok=True,
        actual_size=result.size,
        bytes_written=len(result.image_bytes),
        request_id=result.request_id,
        revised_prompt=result.revised_prompt,
        latency_ms=result.latency_ms,
    )


def _format_plan(plans: list[GenerationRequest], cost_per_image: float) -> str:
    """Pretty-print the planned generations."""
    to_run = [p for p in plans if p.skip_reason is None]
    skipped = [p for p in plans if p.skip_reason is not None]
    out: list[str] = []
    out.append(f"Planned: {len(to_run)} generations  Skipped: {len(skipped)}")
    out.append(f"Estimated cost: ${len(to_run) * cost_per_image:.2f} "
               f"(@ ${cost_per_image:.2f} / image)")
    out.append("")
    for p in to_run:
        out.append(f"  + {p.theme} / {p.ship_class}  -> {p.portrait_path}")
    if skipped:
        out.append("")
        for p in skipped:
            out.append(f"  - {p.theme} / {p.ship_class}: {p.skip_reason}")
    return "\n".join(out)


def _write_last_run(manifest: RunManifest) -> None:
    """Persist the run manifest to last_run.json (gitignored)."""
    LAST_RUN_PATH.write_text(json.dumps(asdict(manifest), indent=2))


def main(argv: Optional[list[str]] = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="regenerate_ship_portraits",
        description=(
            "Backfill missing ship portraits via gpt-image-2 (PROJ-314). "
            "Requires OPENAI_API_KEY in the environment unless --dry-run."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--theme", help="Target theme name (e.g. Aetherwake).")
    parser.add_argument("--ship-class", help="Single ship class within --theme.")
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Plan only — print the request list and estimated cost; do not call OpenAI.",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Re-generate even if the portrait file already exists.",
    )
    parser.add_argument(
        "--cost-cap", type=float, default=5.00,
        help="Hard cap on estimated total cost in USD (default 5.00).",
    )
    parser.add_argument(
        "--cost-per-image", type=float, default=COST_PER_IMAGE_USD,
        help=f"Estimated cost per image in USD (default {COST_PER_IMAGE_USD}).",
    )
    parser.add_argument(
        "--model", default="gpt-image-2",
        help="Image-generation model (default gpt-image-2).",
    )
    parser.add_argument(
        "--size", default="2048x2048",
        help="Target image size (default 2048x2048).",
    )
    parser.add_argument(
        "--batch", action="store_true",
        help="Run for every theme. Requires neither --theme nor --ship-class.",
    )
    parser.add_argument(
        "--list-themes", action="store_true",
        help="List the themes discovered under assets/ShipThemes/ and exit.",
    )
    parser.add_argument(
        "--list-classes", action="store_true",
        help="List the canonical ship-class set and exit.",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Verbose logging (DEBUG level).",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    if args.list_themes:
        for name in _list_themes():
            print(name)
        return 0
    if args.list_classes:
        for cls in sorted(SHIP_CLASSES_WITH_VISUAL_THEMES):
            print(cls)
        return 0

    # Validate scope flags.
    if args.ship_class and not args.theme:
        print("--ship-class requires --theme", file=sys.stderr)
        return 2
    if args.batch and (args.theme or args.ship_class):
        print("--batch is mutually exclusive with --theme/--ship-class", file=sys.stderr)
        return 2
    if not (args.theme or args.batch):
        parser.print_help()
        return 2

    # Build target theme list.
    if args.batch:
        themes = _list_themes()
    else:
        themes = [args.theme]

    all_plans: list[GenerationRequest] = []
    for theme in themes:
        try:
            all_plans.extend(plan_generations(
                theme,
                args.ship_class if args.theme else None,
                force=args.force,
            ))
        except FileNotFoundError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 2

    print(_format_plan(all_plans, cost_per_image=args.cost_per_image))

    to_run = [p for p in all_plans if p.skip_reason is None]
    estimated_cost = len(to_run) * args.cost_per_image
    if estimated_cost > args.cost_cap:
        print(
            f"\nABORT: estimated cost ${estimated_cost:.2f} exceeds "
            f"cost cap ${args.cost_cap:.2f}. Re-run with a higher --cost-cap "
            f"or restrict scope.",
            file=sys.stderr,
        )
        return 3

    if args.dry_run:
        print("\n--dry-run set; not calling OpenAI.")
        return 0

    if not to_run:
        print("\nNothing to do.")
        return 0

    # Construct the provider (real OpenAI unless overridden).
    provider = ImageProviderFactory.create()
    if provider is None or isinstance(provider, NullImageProvider):
        print(
            "\nERROR: no real image provider available (is OPENAI_API_KEY set?). "
            "Set the env var, or use --dry-run to print the plan only.",
            file=sys.stderr,
        )
        return 4

    # Persist run manifest as we go.
    manifest = RunManifest(
        started_at=time.strftime("%Y-%m-%dT%H:%M:%S"),
        finished_at="",
        args=vars(args),
    )

    failures = 0
    for plan in to_run:
        print(f"  [generate] {plan.theme} / {plan.ship_class} ...", end=" ", flush=True)
        result = generate_one(provider, plan, model=args.model, size=args.size)
        manifest.results.append({
            "theme": plan.theme,
            "ship_class": plan.ship_class,
            "portrait_path": plan.portrait_path,
            "ok": result.ok,
            "actual_size": result.actual_size,
            "bytes_written": result.bytes_written,
            "error": result.error,
            "request_id": result.request_id,
            "revised_prompt": result.revised_prompt,
            "latency_ms": result.latency_ms,
        })
        _write_last_run(manifest)  # Save after every call so a crash mid-run preserves state.
        if result.ok:
            print(
                f"OK ({result.actual_size[0]}x{result.actual_size[1]} "
                f"-> {plan.portrait_path})"
            )
        else:
            print(f"FAIL ({result.error})")
            failures += 1

    manifest.finished_at = time.strftime("%Y-%m-%dT%H:%M:%S")
    _write_last_run(manifest)

    print(
        f"\nDone. {len(to_run) - failures}/{len(to_run)} succeeded; "
        f"manifest written to {LAST_RUN_PATH}."
    )
    print(
        "NOTE: open game and reload — portraits are cached at startup and "
        "won't appear until the game restarts."
    )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
