"""Run the game under pyinstrument and dump an HTML report on exit.

Usage:
    python Tools/profile_game/profile_game.py
    python Tools/profile_game/profile_game.py --interval 0.005
    python Tools/profile_game/profile_game.py --output my_report.html

The wrapper starts a pyinstrument sampling profiler, hands control to
``launcher.main`` (the normal game entry point), and on exit (clean shutdown
or Ctrl+C) writes:

  - an HTML report (interactive, opens in a browser)
  - a console summary of the heaviest call stacks

Reports land in ``AgentCoordination/Scratchpad/reports/profiles/`` by
default — that directory is gitignored.

Sampling profiling has very low overhead, so the game should feel close to
normal speed. Reproduce the laggy interaction during the run, then quit
the game normally to flush the report.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import os
import sys
import webbrowser
from pathlib import Path

# Make the repo root importable when invoked directly.
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from pyinstrument import Profiler  # noqa: E402


def _default_output_dir() -> Path:
    return _REPO_ROOT / "AgentCoordination" / "Scratchpad" / "reports" / "profiles"


def _timestamp() -> str:
    return _dt.datetime.now().strftime("%Y%m%dT%H%M%S")


def main() -> int:
    parser = argparse.ArgumentParser(description="Profile Starship Battles with pyinstrument.")
    parser.add_argument(
        "--interval",
        type=float,
        default=0.001,
        help="Sampling interval in seconds (default: 0.001 = 1ms).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="HTML output path (default: AgentCoordination/Scratchpad/reports/profiles/<timestamp>.html).",
    )
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="Do not auto-open the HTML report in a browser on exit.",
    )
    parser.add_argument(
        "--async-mode",
        choices=("enabled", "disabled", "strict"),
        default="enabled",
        help="pyinstrument async mode (default: enabled).",
    )
    args, passthrough = parser.parse_known_args()

    # Forward any remaining args to the game (it ignores unknown args today,
    # but this keeps the door open for future flags).
    sys.argv = [sys.argv[0], *passthrough]

    output_path: Path
    if args.output is None:
        out_dir = _default_output_dir()
        out_dir.mkdir(parents=True, exist_ok=True)
        output_path = out_dir / f"profile_{_timestamp()}.html"
    else:
        output_path = args.output
        output_path.parent.mkdir(parents=True, exist_ok=True)

    profiler = Profiler(interval=args.interval, async_mode=args.async_mode)
    profiler.start()

    exit_code = 0
    try:
        # Import directly from game.app — launcher.py only exposes main()
        # inside its `if __name__ == "__main__"` guard, so it's not importable.
        from game.app import main as game_main  # noqa: WPS433 (intentional late import)

        game_main()
    except KeyboardInterrupt:
        print("\n[profile_game] Caught Ctrl+C — finalizing report.", file=sys.stderr)
    except SystemExit as exc:
        exit_code = int(exc.code) if isinstance(exc.code, int) else 0
    except Exception:  # noqa: BLE001 — top-level wrapper, must always flush report
        import traceback

        traceback.print_exc()
        exit_code = 1
    finally:
        profiler.stop()

        # Console summary first — useful even if the HTML write fails.
        # Force ASCII + no color on Windows-default consoles to avoid cp1252 crashes.
        _can_unicode = (getattr(sys.stderr, "encoding", "") or "").lower().startswith("utf")
        print("\n" + "=" * 72, file=sys.stderr)
        print("[profile_game] pyinstrument summary", file=sys.stderr)
        print("=" * 72, file=sys.stderr)
        try:
            print(
                profiler.output_text(unicode=_can_unicode, color=_can_unicode, show_all=False),
                file=sys.stderr,
            )
        except UnicodeEncodeError:
            print(profiler.output_text(unicode=False, color=False, show_all=False), file=sys.stderr)

        try:
            html = profiler.output_html()
            output_path.write_text(html, encoding="utf-8")
            print(f"\n[profile_game] HTML report written to: {output_path}", file=sys.stderr)
            if not args.no_open:
                webbrowser.open(output_path.as_uri())
        except Exception as write_exc:  # noqa: BLE001 — best-effort report write
            print(f"[profile_game] Failed to write HTML report: {write_exc}", file=sys.stderr)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
