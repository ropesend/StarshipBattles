"""Legacy code audit — Phase 1 deterministic scanner.

Scans every .py file under game/ for residue of old systems:

  1. Module aliases (top-level ``OldName = NewName``)
  2. ``__init__.py`` star-imports / aliasing imports (suspect re-export shims)
  3. Deprecation markers (regex over comments / decorators / warnings)
  4. Wrapper delegates (single-statement ``return other(...)`` functions)
  5. Name-pair drift (``LegacyX``/``OldX``/``XV1``/``XV2``/``_X`` next to ``X``;
     ``XManager``+``XService`` pairs sharing methods)
  6. Save-migration code (``migrate_*``, ``convert_legacy_*``, ``from_vN_to_vM``,
     ``*_migration.py``, ``*_compat.py``, ``data/saves/vN`` references)
  7. Superseded pattern uses (``superseded_by`` patterns from
     ``patterns_toc.json`` or parsed from ``docs/02_PATTERNS.md``)
  8. ``TYPE_CHECKING``-only re-exports (imported under ``if TYPE_CHECKING:`` AND
     re-exported via ``__all__`` or top-level alias)
  9. Optional Protocol methods (classes partially implementing a Protocol —
     legacy implementations missing newer methods)

Outputs structured JSON to REVIEW_DIR/raw/ plus a 4-shard manifest with
per-shard filtered copies of every detector output.

Usage::

    python Tools/legacy_audit/legacy_audit.py
"""

from __future__ import annotations

import ast
import json
import os
import random
import re
import sys
from datetime import datetime
from pathlib import Path


# ---------------------------------------------------------------------------
# Project root + paths
# ---------------------------------------------------------------------------


def _find_project_root() -> str:
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / "game").is_dir() and (current / "data").is_dir():
            return str(current)
        current = current.parent
    raise RuntimeError("Could not find project root")


PROJECT_ROOT = _find_project_root()
GAME_DIR = os.path.join(PROJECT_ROOT, "game")
DOCS_DIR = os.path.join(PROJECT_ROOT, "docs")
REVIEWS_DIR = os.path.join(PROJECT_ROOT, "Reviews", "results")

sys.path.insert(0, PROJECT_ROOT)

from Tools._audit_common import run_tracker  # noqa: E402


# ---------------------------------------------------------------------------
# IO helpers
# ---------------------------------------------------------------------------


def _rel(path: str) -> str:
    return os.path.relpath(path, PROJECT_ROOT).replace("\\", "/")


def _read_file(path: str) -> str | None:
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return None


def _discover_py_files(root: str) -> list[str]:
    results: list[str] = []
    for dirpath, _, filenames in os.walk(root):
        if "__pycache__" in dirpath:
            continue
        for fname in filenames:
            if fname.endswith(".py"):
                results.append(os.path.join(dirpath, fname))
    return results


def _line_at(lines: list[str], lineno: int) -> str:
    if 1 <= lineno <= len(lines):
        return lines[lineno - 1].rstrip()
    return ""


def _attr_chain(node: ast.expr) -> str | None:
    """Return dotted name for ``ast.Name`` or ``ast.Attribute`` chains, else None."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parts: list[str] = [node.attr]
        current = node.value
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
            parts.reverse()
            return ".".join(parts)
    return None


# ---------------------------------------------------------------------------
# Detector 1: module aliases
# ---------------------------------------------------------------------------


def detect_module_aliases(tree: ast.AST, source_lines: list[str], rel_path: str) -> list[dict]:
    out: list[dict] = []
    for node in tree.body if isinstance(tree, ast.Module) else []:
        if not isinstance(node, ast.Assign):
            continue
        if len(node.targets) != 1:
            continue
        target = node.targets[0]
        target_name = _attr_chain(target)
        value_name = _attr_chain(node.value)
        if target_name is None or value_name is None:
            continue
        # Both sides are pure name/attribute references and they aren't equal.
        if target_name == value_name:
            continue
        # Skip ALL-CAPS constants (those are config, not legacy aliases).
        last_target = target_name.split(".")[-1]
        if last_target.isupper():
            continue
        out.append({
            "file": rel_path,
            "line": node.lineno,
            "alias": target_name,
            "target": value_name,
            "context": _line_at(source_lines, node.lineno),
        })
    return out


# ---------------------------------------------------------------------------
# Detector 2: __init__ re-exports
# ---------------------------------------------------------------------------


def detect_init_reexports(tree: ast.AST, source_lines: list[str], rel_path: str) -> list[dict]:
    if not rel_path.endswith("/__init__.py"):
        return []
    out: list[dict] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                if alias.name == "*":
                    out.append({
                        "file": rel_path,
                        "line": node.lineno,
                        "kind": "star_import",
                        "module": module,
                        "context": _line_at(source_lines, node.lineno),
                    })
                elif alias.asname and alias.asname != alias.name:
                    out.append({
                        "file": rel_path,
                        "line": node.lineno,
                        "kind": "as_alias",
                        "module": module,
                        "imported": alias.name,
                        "as": alias.asname,
                        "context": _line_at(source_lines, node.lineno),
                    })
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.asname and alias.asname != alias.name:
                    out.append({
                        "file": rel_path,
                        "line": node.lineno,
                        "kind": "as_alias",
                        "module": alias.name,
                        "imported": alias.name,
                        "as": alias.asname,
                        "context": _line_at(source_lines, node.lineno),
                    })
    return out


# ---------------------------------------------------------------------------
# Detector 3: deprecation markers (regex)
# ---------------------------------------------------------------------------


_DEPRECATION_PATTERNS = [
    re.compile(r"#\s*DEPRECATED\b", re.IGNORECASE),
    re.compile(r"#\s*LEGACY\b", re.IGNORECASE),
    re.compile(r"#\s*TODO:?\s*remove\b", re.IGNORECASE),
    re.compile(r"#\s*kept for (?:backward |back-)?compat", re.IGNORECASE),
    re.compile(r"#\s*old\b", re.IGNORECASE),
    re.compile(r"@deprecated\b"),
    re.compile(r"\bDeprecationWarning\s*\("),
    re.compile(r"warnings\.warn\([^)]*DeprecationWarning"),
]


def detect_deprecation_markers(source: str, rel_path: str) -> list[dict]:
    out: list[dict] = []
    for lineno, line in enumerate(source.splitlines(), start=1):
        for pat in _DEPRECATION_PATTERNS:
            m = pat.search(line)
            if m:
                out.append({
                    "file": rel_path,
                    "line": lineno,
                    "marker": m.group(0),
                    "context": line.rstrip(),
                })
                break  # one marker per line
    return out


# ---------------------------------------------------------------------------
# Detector 4: wrapper delegates
# ---------------------------------------------------------------------------


def _args_pass_through(func_node: ast.FunctionDef | ast.AsyncFunctionDef, call_node: ast.Call) -> bool:
    """True if call args mirror the function's parameters identically (in order)."""
    pos_params = [a.arg for a in func_node.args.args]
    if func_node.args.vararg:
        pos_params.append("*" + func_node.args.vararg.arg)
    kw_params = [a.arg for a in func_node.args.kwonlyargs]
    if func_node.args.kwarg:
        kw_params.append("**" + func_node.args.kwarg.arg)

    # Positional args
    call_pos: list[str] = []
    for a in call_node.args:
        if isinstance(a, ast.Name):
            call_pos.append(a.arg if hasattr(a, "arg") else a.id)
        elif isinstance(a, ast.Starred) and isinstance(a.value, ast.Name):
            call_pos.append("*" + a.value.id)
        else:
            return False

    if call_pos != pos_params:
        return False

    # Keyword args
    call_kw: list[str] = []
    for k in call_node.keywords:
        if k.arg is None:  # **kwargs
            if isinstance(k.value, ast.Name):
                call_kw.append("**" + k.value.id)
            else:
                return False
        else:
            if isinstance(k.value, ast.Name) and k.value.id == k.arg:
                call_kw.append(k.arg)
            else:
                return False

    return call_kw == kw_params


# Names that strongly suggest the wrapper is a legacy alias rather than a
# legitimate facade method. We require at least one of these signals before
# reporting, because plain one-line delegates are the dominant pattern for
# facades, accessors, and routed lookups (e.g. App.active_scene -> _route_get).
_LEGACY_NAME_PREFIXES = ("legacy_", "old_", "_legacy_", "_old_", "deprecated_", "compat_")
_LEGACY_NAME_SUFFIXES = ("_legacy", "_old", "_v1", "_v2", "_compat", "_deprecated")


def _looks_like_legacy_wrapper_name(name: str) -> bool:
    lower = name.lower()
    if lower.startswith(_LEGACY_NAME_PREFIXES):
        return True
    if lower.endswith(_LEGACY_NAME_SUFFIXES):
        return True
    return False


def detect_wrapper_delegates(tree: ast.AST, source_lines: list[str], rel_path: str) -> list[dict]:
    """Detect single-line wrapper functions that delegate to another callable.

    Plain one-line delegates are extremely common in this codebase as the
    facade / accessor / routed-lookup pattern (App.active_scene ->
    self._route_get(...) etc.) and they are NOT legacy. To keep the signal
    high we require ONE of the following:

      - The wrapper name contains a legacy/old/compat/deprecated marker.
      - The wrapper passes its args straight through AND the delegate target
        is on a different module/object (cross-module shim) rather than a
        ``self.`` attribute (in-class facade pattern).
    """
    out: list[dict] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        body = node.body
        # Skip docstring-only first stmt
        if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
            body = body[1:]
        if len(body) != 1:
            continue
        ret = body[0]
        if not isinstance(ret, ast.Return):
            continue
        if not isinstance(ret.value, ast.Call):
            continue
        call = ret.value
        callable_name = _attr_chain(call.func)
        if callable_name is None:
            continue
        # Skip self-call (recursion) and trivial property accesses
        if callable_name == node.name:
            continue
        is_self_delegate = callable_name.startswith("self.")
        pass_through = _args_pass_through(node, call)
        legacy_named = _looks_like_legacy_wrapper_name(node.name)
        # Filter: in-class facades (self.X) without a legacy-name marker are
        # the dominant non-legacy pattern; skip them. A cross-module wrapper
        # that simply forwards args is the canonical shim shape we want.
        if not legacy_named and (is_self_delegate or not pass_through):
            continue
        out.append({
            "file": rel_path,
            "line": node.lineno,
            "function": node.name,
            "delegates_to": callable_name,
            "args_pass_through": pass_through,
            "legacy_named": legacy_named,
            "context": _line_at(source_lines, node.lineno),
        })
    return out


# ---------------------------------------------------------------------------
# Detector 5: name-pair drift (collected globally, computed at the end)
# ---------------------------------------------------------------------------


_LEGACY_PREFIXES = ("Legacy", "Old")
_LEGACY_SUFFIXES = ("V1", "V2", "Old", "Legacy")


def collect_top_level_names(
    tree: ast.AST, rel_path: str
) -> tuple[dict[str, dict], dict[str, set[str]]]:
    """Return (name_to_loc, classname_to_methods) for top-level classes/functions."""
    name_to_loc: dict[str, dict] = {}
    classname_to_methods: dict[str, set[str]] = {}
    if not isinstance(tree, ast.Module):
        return name_to_loc, classname_to_methods
    for node in tree.body:
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            name_to_loc[node.name] = {"file": rel_path, "line": node.lineno}
            if isinstance(node, ast.ClassDef):
                methods: set[str] = set()
                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        methods.add(child.name)
                classname_to_methods[node.name] = methods
    return name_to_loc, classname_to_methods


def compute_name_pair_drift(
    all_names: dict[str, dict],
    classnames_methods: dict[str, set[str]],
) -> list[dict]:
    out: list[dict] = []
    for name, loc in all_names.items():
        # Underscore-prefixed counterpart of an unprefixed public name
        if name.startswith("_") and not name.startswith("__"):
            base = name.lstrip("_")
            if base and base in all_names and base != name:
                out.append({
                    "kind": "underscore_pair",
                    "legacy_name": name,
                    "current_name": base,
                    "legacy": loc,
                    "current": all_names[base],
                })
            continue
        # Legacy/Old prefix
        for prefix in _LEGACY_PREFIXES:
            if name.startswith(prefix):
                base = name[len(prefix):]
                if base and base in all_names:
                    out.append({
                        "kind": f"prefix_{prefix.lower()}",
                        "legacy_name": name,
                        "current_name": base,
                        "legacy": loc,
                        "current": all_names[base],
                    })
                    break
        # V1 / V2 / Old / Legacy suffix
        for suffix in _LEGACY_SUFFIXES:
            if name.endswith(suffix) and name != suffix:
                base = name[: -len(suffix)]
                if base and base in all_names:
                    out.append({
                        "kind": f"suffix_{suffix.lower()}",
                        "legacy_name": name,
                        "current_name": base,
                        "legacy": loc,
                        "current": all_names[base],
                    })
                    break

    # XManager + XService overlap
    for name, methods in classnames_methods.items():
        if not name.endswith("Manager"):
            continue
        base = name[: -len("Manager")]
        service = base + "Service"
        if service in classnames_methods:
            shared = methods & classnames_methods[service]
            if shared:
                out.append({
                    "kind": "manager_service_overlap",
                    "manager_name": name,
                    "service_name": service,
                    "shared_methods": sorted(shared),
                    "manager": all_names.get(name, {}),
                    "service": all_names.get(service, {}),
                })
    return out


# ---------------------------------------------------------------------------
# Detector 6: save migration code
# ---------------------------------------------------------------------------


_MIGRATE_FN_RE = re.compile(
    r"^\s*(?:async\s+)?def\s+("
    r"migrate_\w+|_migrate_\w+|convert_legacy_\w+|upgrade_save_\w+|"
    r"from_v\d+_to_v\d+|_v\d+_compat"
    r")\s*\("
)
_SAVE_VERSION_RE = re.compile(r"data/saves/v\d+")


def detect_save_migration_code(source: str, rel_path: str) -> list[dict]:
    out: list[dict] = []
    fname = os.path.basename(rel_path)
    if fname.endswith("_migration.py") or fname.endswith("_compat.py"):
        out.append({
            "file": rel_path,
            "line": 1,
            "kind": "filename_pattern",
            "context": fname,
        })
    for lineno, line in enumerate(source.splitlines(), start=1):
        m = _MIGRATE_FN_RE.match(line)
        if m:
            out.append({
                "file": rel_path,
                "line": lineno,
                "kind": "function_name",
                "function": m.group(1),
                "context": line.rstrip(),
            })
        m2 = _SAVE_VERSION_RE.search(line)
        if m2:
            out.append({
                "file": rel_path,
                "line": lineno,
                "kind": "save_version_path",
                "match": m2.group(0),
                "context": line.rstrip(),
            })
    return out


# ---------------------------------------------------------------------------
# Detector 7: superseded pattern uses
# ---------------------------------------------------------------------------


def _latest_pattern_toc() -> Path | None:
    candidates = sorted(Path(REVIEWS_DIR).glob("*_pattern-audit/raw/patterns_toc.json"))
    if not candidates:
        return None
    return candidates[-1]


def _parse_patterns_md_for_superseded() -> list[dict]:
    """Fallback: parse docs/02_PATTERNS.md for ``superseded by #N`` markers."""
    md_path = os.path.join(DOCS_DIR, "02_PATTERNS.md")
    src = _read_file(md_path)
    if src is None:
        return []
    out: list[dict] = []
    # Headings look like:  "## 30. Registrar Close-Callback"
    heading_re = re.compile(r"^##\s+(\d+)\.\s+(.+?)\s*$")
    superseded_re = re.compile(r"superseded\s+by\s+(?:pattern\s+)?#?(\d+)", re.IGNORECASE)
    current: dict | None = None
    for line in src.splitlines():
        h = heading_re.match(line)
        if h:
            current = {"number": int(h.group(1)), "name": h.group(2).strip(), "superseded_by": None}
            out.append(current)
            continue
        if current is None:
            continue
        s = superseded_re.search(line)
        if s and current["superseded_by"] is None:
            current["superseded_by"] = int(s.group(1))
    return [p for p in out if p.get("superseded_by") is not None]


def detect_superseded_pattern_uses() -> dict:
    toc_path = _latest_pattern_toc()
    if toc_path is None:
        catalog = _parse_patterns_md_for_superseded()
        return {
            "detector": "superseded_pattern_uses",
            "source": "docs/02_PATTERNS.md",
            "patterns_toc_available": False,
            "note": "patterns_toc.json not available; usage scan skipped",
            "superseded_patterns": catalog,
            "findings": [],
            "total_findings": 0,
        }
    try:
        with toc_path.open("r", encoding="utf-8") as f:
            toc = json.load(f)
    except (OSError, json.JSONDecodeError):
        return {
            "detector": "superseded_pattern_uses",
            "source": str(toc_path),
            "patterns_toc_available": False,
            "note": "patterns_toc.json unreadable; usage scan skipped",
            "superseded_patterns": [],
            "findings": [],
            "total_findings": 0,
        }
    superseded = [p for p in toc.get("patterns", []) if p.get("superseded_by")]
    # Best-effort: we don't have machine-named entry points per pattern in the
    # TOC. Record the catalog so reviewers can grep manually; usage scan is
    # left to phase-2 LLM agents who can read the pattern text.
    return {
        "detector": "superseded_pattern_uses",
        "source": str(toc_path).replace("\\", "/"),
        "patterns_toc_available": True,
        "note": (
            "patterns_toc.json catalog read; per-pattern usage scan requires "
            "named entry points — left to Phase 2 LLM review"
        ),
        "superseded_patterns": superseded,
        "findings": [],
        "total_findings": 0,
    }


# ---------------------------------------------------------------------------
# Detector 8: TYPE_CHECKING-only re-exports
# ---------------------------------------------------------------------------


def _names_in_type_checking_block(tree: ast.AST) -> set[str]:
    """Return set of imported names that appear ONLY under ``if TYPE_CHECKING:``."""
    tc_names: set[str] = set()
    runtime_names: set[str] = set()

    def _collect_from_imports(n: ast.AST, into: set[str]) -> None:
        for sub in ast.walk(n):
            if isinstance(sub, ast.ImportFrom):
                for alias in sub.names:
                    into.add(alias.asname or alias.name)
            elif isinstance(sub, ast.Import):
                for alias in sub.names:
                    name = alias.asname or alias.name.split(".")[0]
                    into.add(name)

    if isinstance(tree, ast.Module):
        for node in tree.body:
            if isinstance(node, ast.If):
                test = node.test
                is_tc = (
                    (isinstance(test, ast.Name) and test.id == "TYPE_CHECKING")
                    or (isinstance(test, ast.Attribute) and test.attr == "TYPE_CHECKING")
                )
                if is_tc:
                    for child in node.body:
                        _collect_from_imports(child, tc_names)
                    continue
            _collect_from_imports(node, runtime_names)
    return tc_names - runtime_names


def _module_all_set(tree: ast.AST) -> set[str]:
    """Return the contents of ``__all__`` if statically definable, else empty."""
    out: set[str] = set()
    if not isinstance(tree, ast.Module):
        return out
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "__all__":
                    if isinstance(node.value, (ast.List, ast.Tuple)):
                        for elt in node.value.elts:
                            if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                out.add(elt.value)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == "__all__":
            if isinstance(node.value, (ast.List, ast.Tuple)):
                for elt in node.value.elts:
                    if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                        out.add(elt.value)
    return out


def _module_top_level_aliases(tree: ast.AST) -> set[str]:
    """Names assigned at top level via plain ``X = Y`` (excluding constants)."""
    out: set[str] = set()
    if not isinstance(tree, ast.Module):
        return out
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and not t.id.isupper():
                    out.add(t.id)
    return out


def detect_type_checking_reexports(tree: ast.AST, source_lines: list[str], rel_path: str) -> list[dict]:
    tc_only = _names_in_type_checking_block(tree)
    if not tc_only:
        return []
    all_set = _module_all_set(tree)
    top_aliases = _module_top_level_aliases(tree)
    out: list[dict] = []
    for name in sorted(tc_only):
        reexported_via: list[str] = []
        if name in all_set:
            reexported_via.append("__all__")
        if name in top_aliases:
            reexported_via.append("top_level_alias")
        if reexported_via:
            out.append({
                "file": rel_path,
                "line": 1,
                "name": name,
                "reexported_via": reexported_via,
            })
    return out


# ---------------------------------------------------------------------------
# Detector 9: optional Protocol methods (partial implementers)
# ---------------------------------------------------------------------------


def _is_protocol_base(base: ast.expr) -> bool:
    """True if a class base is ``Protocol`` or ``typing.Protocol`` (or subscripted)."""
    target = base
    if isinstance(base, ast.Subscript):
        target = base.value
    name = _attr_chain(target)
    if name is None:
        return False
    return name == "Protocol" or name.endswith(".Protocol")


def collect_protocols_and_classes(
    tree: ast.AST, rel_path: str
) -> tuple[dict[str, dict], dict[str, dict]]:
    """Return (protocols, regular_classes), each keyed by class name."""
    protocols: dict[str, dict] = {}
    regular: dict[str, dict] = {}
    if not isinstance(tree, ast.Module):
        return protocols, regular
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        is_protocol = any(_is_protocol_base(b) for b in node.bases)
        bases: set[str] = set()
        for b in node.bases:
            target = b.value if isinstance(b, ast.Subscript) else b
            chain = _attr_chain(target)
            if chain is None:
                continue
            # Store both the full chain and the leaf name so a partial-impl
            # check can match either ``IFoo`` or ``module.IFoo``.
            bases.add(chain)
            bases.add(chain.split(".")[-1])
        methods: set[str] = set()
        for child in node.body:
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if child.name.startswith("__") and child.name.endswith("__"):
                    continue
                methods.add(child.name)
        info = {
            "name": node.name,
            "file": rel_path,
            "line": node.lineno,
            "methods": methods,
            "bases": bases,
        }
        if is_protocol:
            protocols[node.name] = info
        else:
            regular[node.name] = info
    return protocols, regular


def compute_optional_protocol_methods(
    protocols: dict[str, dict],
    regulars: dict[str, dict],
) -> list[dict]:
    """Compute partial Protocol implementers.

    Two filters keep this signal high:
      - Only consider classes that explicitly declare the Protocol (or any
        of its subclasses) as a base. Loose method-name overlap is too
        noisy — many unrelated classes share a name like ``is_alive`` or
        ``radius`` without intending to implement the Protocol.
      - Require ``implements_ratio >= 0.5`` so we surface real partial
        implementations, not coincidental one-method overlaps.
    """
    out: list[dict] = []
    # Map every class -> its declared bases (a flat set of Name strings).
    for pname, p in protocols.items():
        pmethods: set[str] = p["methods"]
        if not pmethods:
            continue
        partial: list[dict] = []
        for cname, c in regulars.items():
            if cname == pname:
                continue
            bases: set[str] = c.get("bases", set())
            if pname not in bases:
                # Class doesn't declare the Protocol as a base — skip.
                continue
            cmethods: set[str] = c["methods"]
            shared = cmethods & pmethods
            if not shared:
                continue
            missing = pmethods - cmethods
            ratio = len(shared) / len(pmethods)
            if ratio < 0.5:
                continue
            if shared and missing:
                partial.append({
                    "class": cname,
                    "file": c["file"],
                    "line": c["line"],
                    "implemented_methods": sorted(shared),
                    "missing_methods": sorted(missing),
                    "implements_ratio": round(ratio, 2),
                })
        if partial:
            out.append({
                "protocol": pname,
                "file": p["file"],
                "line": p["line"],
                "protocol_methods": sorted(pmethods),
                "partial_implementers": partial,
            })
    return out


# ---------------------------------------------------------------------------
# Manifest
# ---------------------------------------------------------------------------


def _simple_balance(files: list[tuple[str, int]], shard_count: int) -> list[list[tuple[str, int]]]:
    shards: list[list[tuple[str, int]]] = [[] for _ in range(shard_count)]
    totals = [0] * shard_count
    for filepath, loc in files:
        min_idx = min(range(shard_count), key=lambda i: totals[i])
        shards[min_idx].append((filepath, loc))
        totals[min_idx] += loc
    return shards


def _generate_manifest(rel_files: list[str], shard_count: int = 4) -> dict:
    seed = f"legacy-{datetime.now().strftime('%Y-%m-%d')}"
    rng = random.Random(seed)
    shuffled = list(rel_files)
    rng.shuffle(shuffled)

    loc_map: dict[str, int] = {}
    for f in shuffled:
        try:
            with open(os.path.join(PROJECT_ROOT, f), encoding="utf-8") as fp:
                loc_map[f] = sum(1 for _ in fp)
        except OSError:
            loc_map[f] = 0

    pairs = [(f, loc_map.get(f, 0)) for f in shuffled]
    shards = _simple_balance(pairs, shard_count)
    manifest: dict = {
        "audit_name": "legacy",
        "seed": seed,
        "shard_count": shard_count,
        "total_files": len(rel_files),
        "total_loc_estimate": sum(loc_map.values()),
        "shards": {},
    }
    for i, shard in enumerate(shards):
        sid = f"{i + 1:02d}"
        file_paths = sorted(p for p, _ in shard)
        manifest["shards"][sid] = {
            "label": f"Shard {sid}",
            "file_count": len(file_paths),
            "loc_estimate": sum(loc for _, loc in shard),
            "files": file_paths,
        }
    return manifest


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


def _wrap(detector: str, scanned_files: int, findings: list[dict]) -> dict:
    return {
        "detector": detector,
        "scanned_files": scanned_files,
        "total_findings": len(findings),
        "findings": findings,
    }


def _write_json(path: str, payload: object) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def run(force_output_dir: str | None = None) -> str:
    date_slug = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_dir = force_output_dir or os.path.join(REVIEWS_DIR, f"{date_slug}_legacy-audit")
    raw_dir = os.path.join(output_dir, "raw")
    os.makedirs(raw_dir, exist_ok=True)

    print("=== Phase 1: Legacy Code Audit ===")
    print(f"Output: {output_dir}")
    print()

    files = _discover_py_files(GAME_DIR)
    print(f"Scanning {len(files)} files...")

    module_aliases: list[dict] = []
    init_reexports: list[dict] = []
    deprecation_markers: list[dict] = []
    wrapper_delegates: list[dict] = []
    save_migration: list[dict] = []
    type_checking_reexports: list[dict] = []

    all_top_names: dict[str, dict] = {}
    all_class_methods: dict[str, set[str]] = {}
    all_protocols: dict[str, dict] = {}
    all_regular_classes: dict[str, dict] = {}

    scanned = 0
    for filepath in files:
        source = _read_file(filepath)
        if source is None:
            continue
        try:
            tree = ast.parse(source, filename=filepath)
        except SyntaxError:
            continue
        scanned += 1
        rel_path = _rel(filepath)
        source_lines = source.splitlines()

        module_aliases.extend(detect_module_aliases(tree, source_lines, rel_path))
        init_reexports.extend(detect_init_reexports(tree, source_lines, rel_path))
        deprecation_markers.extend(detect_deprecation_markers(source, rel_path))
        wrapper_delegates.extend(detect_wrapper_delegates(tree, source_lines, rel_path))
        save_migration.extend(detect_save_migration_code(source, rel_path))
        type_checking_reexports.extend(detect_type_checking_reexports(tree, source_lines, rel_path))

        names, methods = collect_top_level_names(tree, rel_path)
        # Last write wins on duplicate names across modules — name-pair drift
        # cares about co-existence, not exact provenance.
        all_top_names.update(names)
        all_class_methods.update(methods)

        protocols, regulars = collect_protocols_and_classes(tree, rel_path)
        all_protocols.update(protocols)
        all_regular_classes.update(regulars)

    name_pair_drift = compute_name_pair_drift(all_top_names, all_class_methods)
    optional_protocol_methods = compute_optional_protocol_methods(all_protocols, all_regular_classes)
    superseded = detect_superseded_pattern_uses()

    # Wrapped payloads (consistent schema)
    payloads = {
        "module_aliases": _wrap("module_aliases", scanned, module_aliases),
        "init_reexports": _wrap("init_reexports", scanned, init_reexports),
        "deprecation_markers": _wrap("deprecation_markers", scanned, deprecation_markers),
        "wrapper_delegates": _wrap("wrapper_delegates", scanned, wrapper_delegates),
        "name_pair_drift": _wrap("name_pair_drift", scanned, name_pair_drift),
        "save_migration_code": _wrap("save_migration_code", scanned, save_migration),
        "superseded_pattern_uses": superseded,
        "type_checking_only_reexports": _wrap("type_checking_only_reexports", scanned, type_checking_reexports),
        "optional_protocol_methods": _wrap("optional_protocol_methods", scanned, optional_protocol_methods),
    }

    for name, payload in payloads.items():
        _write_json(os.path.join(raw_dir, f"{name}.json"), payload)

    rel_files = [_rel(f) for f in files]
    manifest = _generate_manifest(rel_files)
    _write_json(os.path.join(raw_dir, "manifest.json"), manifest)

    # Per-shard filtered copies for every detector that has file-tagged findings.
    file_tagged = [
        "module_aliases",
        "init_reexports",
        "deprecation_markers",
        "wrapper_delegates",
        "save_migration_code",
        "type_checking_only_reexports",
    ]
    for sid, shard_info in manifest["shards"].items():
        shard_files = set(shard_info["files"])
        for name in file_tagged:
            payload = payloads[name]
            filtered = [it for it in payload["findings"] if it.get("file") in shard_files]
            _write_json(
                os.path.join(raw_dir, f"{name}_{sid}.json"),
                _wrap(payload["detector"], shard_info["file_count"], filtered),
            )
        # name_pair_drift: keep entries where either side's file is in shard
        npd_filtered = [
            it for it in payloads["name_pair_drift"]["findings"]
            if (it.get("legacy", {}).get("file") in shard_files)
            or (it.get("current", {}).get("file") in shard_files)
            or (it.get("manager", {}).get("file") in shard_files)
            or (it.get("service", {}).get("file") in shard_files)
        ]
        _write_json(
            os.path.join(raw_dir, f"name_pair_drift_{sid}.json"),
            _wrap("name_pair_drift", shard_info["file_count"], npd_filtered),
        )
        # optional_protocol_methods: keep protocols whose file OR any partial
        # implementer's file is in shard.
        opm_filtered = []
        for entry in payloads["optional_protocol_methods"]["findings"]:
            in_shard_partials = [
                pi for pi in entry["partial_implementers"]
                if pi.get("file") in shard_files
            ]
            protocol_in_shard = entry.get("file") in shard_files
            if protocol_in_shard or in_shard_partials:
                opm_filtered.append({
                    **entry,
                    "partial_implementers": in_shard_partials or entry["partial_implementers"],
                })
        _write_json(
            os.path.join(raw_dir, f"optional_protocol_methods_{sid}.json"),
            _wrap("optional_protocol_methods", shard_info["file_count"], opm_filtered),
        )
        # superseded_pattern_uses is global / catalog-only — copy verbatim.
        _write_json(os.path.join(raw_dir, f"superseded_pattern_uses_{sid}.json"), superseded)

    # Trend tracker entry
    summary = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "review_dir": _rel(output_dir),
        "findings": {
            "module_aliases": len(module_aliases),
            "init_reexports": len(init_reexports),
            "deprecation_markers": len(deprecation_markers),
            "wrapper_delegates": len(wrapper_delegates),
            "name_pair_drift": len(name_pair_drift),
            "save_migration_code": len(save_migration),
            "type_checking_only_reexports": len(type_checking_reexports),
            "optional_protocol_methods": len(optional_protocol_methods),
            "superseded_pattern_uses": superseded.get("total_findings", 0),
        },
        "by_category": {
            "module_aliases": len(module_aliases),
            "init_reexports": len(init_reexports),
            "deprecation_markers": len(deprecation_markers),
            "wrapper_delegates": len(wrapper_delegates),
            "name_pair_drift": len(name_pair_drift),
            "save_migration_code": len(save_migration),
            "type_checking_only_reexports": len(type_checking_reexports),
            "optional_protocol_methods": len(optional_protocol_methods),
        },
    }
    try:
        run_tracker.add_run(REVIEWS_DIR, "legacy", summary)
    except OSError as e:  # Intentional broad-ish catch: tracker is advisory; never fail the run.
        print(f"  (run_tracker write failed: {e})")

    print(f"  Module aliases:                 {len(module_aliases)}")
    print(f"  __init__ re-exports:            {len(init_reexports)}")
    print(f"  Deprecation markers:            {len(deprecation_markers)}")
    print(f"  Wrapper delegates:              {len(wrapper_delegates)}")
    print(f"  Name-pair drift:                {len(name_pair_drift)}")
    print(f"  Save migration code:            {len(save_migration)}")
    print(f"  TYPE_CHECKING re-exports:       {len(type_checking_reexports)}")
    print(f"  Optional Protocol methods:      {len(optional_protocol_methods)}")
    print(f"  Superseded patterns (catalog):  {len(superseded.get('superseded_patterns', []))}")
    print()
    print(f"Phase 1 complete. Raw results: {raw_dir}")
    print(f"Output directory: {output_dir}")
    return output_dir


if __name__ == "__main__":
    run()
