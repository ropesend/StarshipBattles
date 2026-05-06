"""AST walker that detects illegal writes to a target attribute set.

PROJ-370: shared helper used by ``test_mutator_boundary_ast_guard.py`` (the
parameterized boundary guard) and ``test_mutator_boundary_ast_guard_self_test.py``
(the synthetic-fixture sanity test for the walker itself).

Detected patterns (per attribute in ``target_attrs``):

1. Bare ``Store``:        ``obj.attr = X``
2. ``AugStore``:          ``obj.attr += X``
3. Subscript-assign:      ``obj.attr[k] = X``
4. Mutating method call:  ``obj.attr.append/.pop/.remove/.extend/.clear/.insert(...)``

The walker is attribute-name-based — it surfaces every write to any matching
attribute regardless of what ``obj`` is. The parameterized AST-guard test
applies a path-allowlist to filter writes by file location; this is the
intentional layering so the walker stays simple and fast.

This module name starts with an underscore so pytest does not auto-discover it
as a test module.
"""
from __future__ import annotations

import ast
from dataclasses import dataclass
from typing import Iterable


__all__ = ["AttributeWriteHit", "find_attribute_writes", "MUTATING_METHODS"]


MUTATING_METHODS: frozenset[str] = frozenset(
    {"append", "pop", "remove", "extend", "clear", "insert"}
)


@dataclass(frozen=True)
class AttributeWriteHit:
    """One detected write to a target attribute."""

    line: int
    col: int
    attr: str
    pattern: str  # one of: "store", "aug-store", "subscript-assign", "method"
    method: str | None  # populated only for the "method" pattern
    filename: str

    def __str__(self) -> str:
        loc = f"{self.filename}:{self.line}:{self.col}"
        if self.pattern == "method":
            return f"{loc}  obj.{self.attr}.{self.method}(...)"
        if self.pattern == "subscript-assign":
            return f"{loc}  obj.{self.attr}[k] = ..."
        if self.pattern == "aug-store":
            return f"{loc}  obj.{self.attr} += ..."
        return f"{loc}  obj.{self.attr} = ..."


def find_attribute_writes(
    source: str,
    target_attrs: Iterable[str],
    *,
    filename: str = "<unknown>",
) -> list[AttributeWriteHit]:
    """Return every write to any attribute in ``target_attrs``.

    Returns an empty list if ``target_attrs`` is empty (callers in Phase 1
    use empty sets to keep the test green-but-wired).

    Caller is responsible for filtering by path-allowlist.
    """
    target_set = frozenset(target_attrs)
    if not target_set:
        return []

    try:
        tree = ast.parse(source, filename=filename)
    except SyntaxError:
        # If a file under game/ has a syntax error, that's not this guard's
        # problem — let the rest of the test suite catch it.
        return []

    visitor = _Visitor(target_set, filename)
    visitor.visit(tree)
    return visitor.hits


class _Visitor(ast.NodeVisitor):
    def __init__(self, target_attrs: frozenset[str], filename: str) -> None:
        self.target_attrs = target_attrs
        self.filename = filename
        self.hits: list[AttributeWriteHit] = []

    # --- Pattern 1: bare Store; Pattern 3: subscript-assign ---
    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            self._check_assign_target(target, line=node.lineno, col=node.col_offset)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if node.value is not None:
            self._check_assign_target(
                node.target, line=node.lineno, col=node.col_offset
            )
        self.generic_visit(node)

    def _check_assign_target(self, target: ast.AST, *, line: int, col: int) -> None:
        # Pattern 1: obj.attr = X
        if isinstance(target, ast.Attribute):
            if target.attr in self.target_attrs:
                self.hits.append(
                    AttributeWriteHit(
                        line=line,
                        col=col,
                        attr=target.attr,
                        pattern="store",
                        method=None,
                        filename=self.filename,
                    )
                )
            return
        # Pattern 3: obj.attr[k] = X
        if isinstance(target, ast.Subscript):
            value = target.value
            if isinstance(value, ast.Attribute) and value.attr in self.target_attrs:
                self.hits.append(
                    AttributeWriteHit(
                        line=line,
                        col=col,
                        attr=value.attr,
                        pattern="subscript-assign",
                        method=None,
                        filename=self.filename,
                    )
                )
            return
        # Tuple / list unpack: recurse into elements.
        if isinstance(target, (ast.Tuple, ast.List)):
            for elt in target.elts:
                self._check_assign_target(elt, line=line, col=col)

    # --- Pattern 2: AugStore (e.g., obj.attr += X) ---
    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        target = node.target
        if isinstance(target, ast.Attribute) and target.attr in self.target_attrs:
            self.hits.append(
                AttributeWriteHit(
                    line=node.lineno,
                    col=node.col_offset,
                    attr=target.attr,
                    pattern="aug-store",
                    method=None,
                    filename=self.filename,
                )
            )
        elif isinstance(target, ast.Subscript):
            value = target.value
            if isinstance(value, ast.Attribute) and value.attr in self.target_attrs:
                self.hits.append(
                    AttributeWriteHit(
                        line=node.lineno,
                        col=node.col_offset,
                        attr=value.attr,
                        pattern="aug-store",
                        method=None,
                        filename=self.filename,
                    )
                )
        self.generic_visit(node)

    # --- Pattern 4: obj.attr.METHOD(...) where METHOD is mutating ---
    def visit_Call(self, node: ast.Call) -> None:
        func = node.func
        if isinstance(func, ast.Attribute) and func.attr in MUTATING_METHODS:
            inner = func.value
            if (
                isinstance(inner, ast.Attribute)
                and inner.attr in self.target_attrs
            ):
                self.hits.append(
                    AttributeWriteHit(
                        line=node.lineno,
                        col=node.col_offset,
                        attr=inner.attr,
                        pattern="method",
                        method=func.attr,
                        filename=self.filename,
                    )
                )
        self.generic_visit(node)
