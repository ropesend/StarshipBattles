import ast
import json
import os
import sys
from pathlib import Path
from collections import defaultdict


def _find_project_root():
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / "game").is_dir() and (current / "data").is_dir():
            return str(current)
        current = current.parent
    raise RuntimeError("Could not find project root")


PROJECT_ROOT = _find_project_root()
sys.path.insert(0, PROJECT_ROOT)

from game.core.paths import Paths

GAME_DIR = Path(Paths.GAME_DIR)
MIN_SIMILARITY = 0.75
MIN_LINES = 5
MIN_TOKENS_FOR_FINGERPRINT = 10
MIN_MEANINGFUL_TOKENS = 8


def _node_type_fingerprint(node):
    """Walk AST node and emit a structural fingerprint of statement types."""
    tokens = []
    for child in ast.walk(node):
        if isinstance(child, ast.stmt) and not isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            tokens.append(type(child).__name__)
        elif isinstance(child, ast.expr) and isinstance(getattr(child, 'value', None), ast.Call):
            func = child.value
            if isinstance(func.func, ast.Attribute):
                tokens.append(f"CALL_ATTR_{func.func.attr}")
            elif isinstance(func.func, ast.Name):
                tokens.append(f"CALL_{func.func.id}")
        elif isinstance(child, ast.BoolOp):
            tokens.append(f"BOOL_{type(child.op).__name__}")
        elif isinstance(child, ast.Compare):
            ops = "_".join(type(o).__name__ for o in child.ops)
            tokens.append(f"CMP_{ops}")
        elif isinstance(child, ast.BinOp):
            tokens.append(f"BINOP_{type(child.op).__name__}")
    return tuple(tokens)


def _extract_functions(file_path):
    """Parse file and return list of (function_name, function_ast, start_line, end_line)."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
    except Exception:
        return []

    try:
        tree = ast.parse(source, filename=file_path)
    except SyntaxError:
        return []

    functions = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            end_line = node.end_lineno if hasattr(node, 'end_lineno') else node.lineno + len(node.body)
            functions.append((node.name, node, node.lineno, end_line))

    return functions


def _extract_body_tokens(node):
    """Extract a normalized token stream from a function body."""
    tokens = []

    class TokenCollector(ast.NodeVisitor):
        def generic_visit(self, n):
            if isinstance(n, ast.Name) and not isinstance(n.ctx, ast.Load):
                tokens.append("VAR")
            elif isinstance(n, ast.Name):
                tokens.append(n.id)
            elif isinstance(n, ast.Constant):
                tokens.append("CONST")
            elif isinstance(n, ast.Attribute):
                parts = []
                current = n
                while isinstance(current, ast.Attribute):
                    parts.append(current.attr)
                    current = current.value
                if isinstance(current, ast.Name):
                    parts.append(current.id)
                tokens.append(".".join(reversed(parts)))
            elif isinstance(n, ast.Call):
                tokens.append("CALL_START")
                super().generic_visit(n)
                tokens.append("CALL_END")
                return
            elif isinstance(n, ast.stmt):
                tokens.append(type(n).__name__)
            elif isinstance(n, ast.expr):
                pass
            super().generic_visit(n)

    TokenCollector().visit(node)
    return tuple(tokens)


def _find_clones(game_dir):
    """Find near-duplicate function bodies across all Python files."""
    all_functions = []

    for py_file in sorted(game_dir.rglob("*.py")):
        if "__pycache__" in str(py_file) or "__pycache__" in py_file.parts:
            continue
        rel_path = str(py_file.relative_to(game_dir))
        file_functions = _extract_functions(str(py_file))
        for name, node, start, end in file_functions:
            tokens = _extract_body_tokens(node)
            if len(tokens) < MIN_MEANINGFUL_TOKENS:
                continue
            fingerprint = _node_type_fingerprint(node)
            if len(fingerprint) < MIN_TOKENS_FOR_FINGERPRINT:
                continue
            all_functions.append({
                "file": rel_path,
                "name": name,
                "lines": (start, end),
                "tokens": tokens,
                "fingerprint": fingerprint,
            })

    # Group by structural fingerprint
    by_fingerprint = defaultdict(list)
    for f in all_functions:
        by_fingerprint[f["fingerprint"]].append(f)

    # Compare within fingerprint groups using token similarity
    clones = []
    for fingerprint, group in by_fingerprint.items():
        if len(group) < 2:
            continue

        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                a, b = group[i], group[j]
                effective_len = max(len(a["tokens"]), len(b["tokens"]))
                if effective_len < MIN_LINES:
                    continue

                from difflib import SequenceMatcher
                ratio = SequenceMatcher(None, a["tokens"], b["tokens"]).ratio()

                if ratio >= MIN_SIMILARITY:
                    loc = max(
                        a["lines"][1] - a["lines"][0],
                        b["lines"][1] - b["lines"][0],
                    )
                    clones.append({
                        "function_a": a["file"] + f":{a['name']}:{a['lines'][0]}",
                        "function_b": b["file"] + f":{b['name']}:{b['lines'][0]}",
                        "similarity": round(ratio, 3),
                        "estimated_loc": loc,
                    })

    # Cluster overlapping clones (same function appearing in multiple pairs)
    clusters = _cluster_clones(clones)
    return clusters


def _cluster_clones(clone_pairs):
    """Group clone pairs into connected clusters."""
    adjacency = defaultdict(set)
    all_nodes = set()

    for pair in clone_pairs:
        a, b = pair["function_a"], pair["function_b"]
        adjacency[a].add(b)
        adjacency[b].add(a)
        all_nodes.add(a)
        all_nodes.add(b)

    visited = set()
    clusters = []

    for node in all_nodes:
        if node in visited:
            continue
        component = set()
        stack = [node]
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            component.add(current)
            stack.extend(adjacency[current])

        if len(component) >= 2:
            members = []
            total_loc = 0
            max_similarity = 0
            for pair in clone_pairs:
                if pair["function_a"] in component and pair["function_b"] in component:
                    max_similarity = max(max_similarity, pair["similarity"])
                    total_loc = max(total_loc, pair["estimated_loc"])

            for func_key in sorted(component):
                parts = func_key.split(":")
                members.append({
                    "file": parts[0],
                    "function": parts[1],
                    "line": int(parts[2]),
                })

            clusters.append({
                "member_count": len(component),
                "max_similarity": max_similarity,
                "estimated_loc": total_loc,
                "members": members,
            })

    clusters.sort(key=lambda c: (-c["member_count"], -c["max_similarity"]))
    return clusters


def run(output_path=None):
    clones = _find_clones(GAME_DIR)

    result = {
        "total_clusters": len(clones),
        "total_duplicated_loc": sum(c["estimated_loc"] for c in clones),
        "clusters": clones,
    }

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        print(f"Clone detector complete: {len(clones)} clusters found, output to {output_path}")

    return result


if __name__ == "__main__":
    _, output_path = sys.argv if len(sys.argv) > 1 else (None, None)
    run(output_path)
