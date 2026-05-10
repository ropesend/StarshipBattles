from __future__ import annotations

import argparse
import importlib.util
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


OUTPUT_DIR = Path("output") / "profiles" / "scalene"
DEFAULT_PROFILE_ONLY = "game,combat_lab"


@dataclass(frozen=True)
class ProfileCommand:
    exec_args: list[str]
    display_args: list[str]
    outfile: Path


def _find_project_root() -> Path:
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / "game").is_dir() and (current / "data").is_dir():
            return current
        current = current.parent
    raise RuntimeError("Could not find project root")


def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%dT%H%M%S")


def _normalize_remainder(values: list[str]) -> list[str]:
    if values and values[0] == "--":
        return values[1:]
    return values


def _display_command(args: list[str]) -> str:
    display = ["python" if index == 0 else value for index, value in enumerate(args)]
    return " ".join(display)


def _base_scalene_args(args: argparse.Namespace, scenario: str) -> tuple[list[str], Path]:
    output_dir = Path(args.output_dir)
    stamp = args.timestamp or _timestamp()
    outfile = output_dir / f"{stamp}-{scenario}-{args.mode}.json"

    scalene_args = ["-m", "scalene", "run"]
    if args.mode == "cpu":
        scalene_args.append("--cpu-only")
    if args.reduced_profile:
        scalene_args.append("--reduced-profile")
    scalene_args.extend(["-o", outfile.as_posix()])
    if args.profile_only:
        scalene_args.extend(["--profile-only", args.profile_only])
    return scalene_args, outfile


def _build_pytest_command(args: argparse.Namespace) -> ProfileCommand:
    scalene_args, outfile = _base_scalene_args(args, "pytest")
    target_args = ["-m", "pytest", args.pytest_target]
    if args.pytest_filter:
        target_args.extend(["-k", args.pytest_filter])
    target_args.extend(_normalize_remainder(args.pytest_args))
    if not args.allow_xdist and not _has_explicit_xdist(target_args):
        target_args.extend(["-n", "0"])
    exec_args = [sys.executable, *scalene_args, *target_args]
    return ProfileCommand(exec_args=exec_args, display_args=["python", *scalene_args, *target_args], outfile=outfile)


def _build_app_command(args: argparse.Namespace) -> ProfileCommand:
    scalene_args, outfile = _base_scalene_args(args, "app")
    app_args = [args.entrypoint, *_normalize_remainder(args.app_args)]
    exec_args = [sys.executable, *scalene_args, *app_args]
    return ProfileCommand(exec_args=exec_args, display_args=["python", *scalene_args, *app_args], outfile=outfile)


def _build_combat_lab_command(args: argparse.Namespace) -> ProfileCommand:
    scalene_args, outfile = _base_scalene_args(args, "combat-lab")
    target_args = ["-m", "combat_lab.run_tests", *_normalize_remainder(args.combat_lab_args)]
    exec_args = [sys.executable, *scalene_args, *target_args]
    return ProfileCommand(exec_args=exec_args, display_args=["python", *scalene_args, *target_args], outfile=outfile)


def _add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--mode",
        choices=("cpu", "full"),
        default="cpu",
        help="cpu uses Scalene --cpu-only; full records CPU plus memory/copy data.",
    )
    parser.add_argument(
        "--output-dir",
        default=OUTPUT_DIR.as_posix(),
        help="Directory for Scalene JSON profiles.",
    )
    parser.add_argument(
        "--profile-only",
        default=DEFAULT_PROFILE_ONLY,
        help="Comma-separated filename fragments Scalene should include.",
    )
    parser.add_argument(
        "--timestamp",
        help="Override timestamp for repeatable output names, e.g. 20260428T000000.",
    )
    parser.add_argument(
        "--no-reduced-profile",
        action="store_false",
        dest="reduced_profile",
        help="Show all profiled lines instead of Scalene's reduced hotspot view.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the Scalene command without executing it.",
    )
    parser.set_defaults(reduced_profile=True)


def _has_explicit_xdist(args: list[str]) -> bool:
    return "-n" in args or any(value.startswith("--numprocesses") for value in args)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run repeatable Scalene profiling passes for Starship Battles.",
    )
    subparsers = parser.add_subparsers(dest="scenario", required=True)

    pytest_parser = subparsers.add_parser("pytest", help="Profile a pytest target.")
    _add_common_args(pytest_parser)
    pytest_parser.add_argument("--pytest-target", default="tests/performance")
    pytest_parser.add_argument("--pytest-filter", help="Optional pytest -k expression.")
    pytest_parser.add_argument(
        "--allow-xdist",
        action="store_true",
        help="Do not add '-n 0'. Default disables xdist for cleaner Scalene profiles.",
    )
    pytest_parser.add_argument("pytest_args", nargs=argparse.REMAINDER)

    app_parser = subparsers.add_parser("app", help="Profile the game launcher.")
    _add_common_args(app_parser)
    app_parser.add_argument("--entrypoint", default="launcher.py")
    app_parser.add_argument("app_args", nargs=argparse.REMAINDER)

    combat_parser = subparsers.add_parser("combat-lab", help="Profile Combat Lab tests.")
    _add_common_args(combat_parser)
    combat_parser.add_argument("combat_lab_args", nargs=argparse.REMAINDER)
    return parser


def build_command(args: argparse.Namespace) -> ProfileCommand:
    if args.scenario == "pytest":
        return _build_pytest_command(args)
    if args.scenario == "app":
        return _build_app_command(args)
    if args.scenario == "combat-lab":
        return _build_combat_lab_command(args)
    raise ValueError(f"Unsupported scenario: {args.scenario}")


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    project_root = _find_project_root()
    command = build_command(args)

    print(_display_command(command.display_args))
    print(f"Profile output: {command.outfile.as_posix()}")
    if args.dry_run:
        return 0

    if importlib.util.find_spec("scalene") is None:
        print(
            "Scalene is not installed. Run: pip install -r requirements-dev.txt",
            file=sys.stderr,
        )
        return 2

    (project_root / command.outfile).parent.mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(command.exec_args, cwd=project_root, check=False)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
