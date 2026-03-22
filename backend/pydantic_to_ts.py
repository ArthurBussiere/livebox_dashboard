#!/usr/bin/env python3
"""pydantic_to_ts.py – Convert Pydantic BaseModel classes to TypeScript interfaces.

Usage:
    python pydantic_to_ts.py <model_file_or_dir> [output_file]

    If output_file is omitted, prints to stdout.
    If a directory is given, all .py files in it are processed in order.

Examples:
    python pydantic_to_ts.py models/firewall.py
    python pydantic_to_ts.py models/ ../liveboxUI/src/app/models/generated.ts
"""

import ast
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Python type  →  TypeScript type
# ---------------------------------------------------------------------------

TYPE_MAP: dict[str, str] = {
    "str": "string",
    "int": "number",
    "float": "number",
    "bool": "boolean",
    "None": "null",
    "Any": "unknown",
    "dict": "Record<string, unknown>",
    "Dict": "Record<string, unknown>",
    "list": "unknown[]",
    "List": "unknown[]",
    "bytes": "string",
    "UUID": "string",
    "datetime": "string",
    "date": "string",
    "time": "string",
}


def map_name(name: str) -> str:
    return TYPE_MAP.get(name, name)


def node_to_ts(node: ast.expr) -> tuple[str, bool]:
    """Return (ts_type_string, is_optional).

    is_optional is True when the type includes None / null.
    """
    # None literal
    if isinstance(node, ast.Constant) and node.value is None:
        return "null", True

    # Simple name: str, int, MyModel, …
    if isinstance(node, ast.Name):
        if node.id == "None":
            return "null", True
        return map_name(node.id), False

    # Dotted name (e.g. pydantic.BaseModel — rare in annotations)
    if isinstance(node, ast.Attribute):
        return node.attr, False

    # X | Y  (Python 3.10+ union syntax)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        left, left_opt = node_to_ts(node.left)
        right, right_opt = node_to_ts(node.right)
        if right == "null":
            return left, True
        if left == "null":
            return right, True
        return f"{left} | {right}", left_opt or right_opt

    # Subscript: list[X], dict[K,V], Optional[X], Union[X,Y,…], Literal[…]
    if isinstance(node, ast.Subscript):
        origin = node.value
        if not isinstance(origin, ast.Name):
            return "unknown", False
        name = origin.id

        # list / sequence
        if name in ("list", "List", "Sequence", "FrozenSet", "Set", "Tuple"):
            inner, _ = node_to_ts(node.slice)
            return f"{inner}[]", False

        # dict
        if name in ("dict", "Dict"):
            if isinstance(node.slice, ast.Tuple) and len(node.slice.elts) >= 2:
                val_ts, _ = node_to_ts(node.slice.elts[1])
            else:
                val_ts = "unknown"
            return f"Record<string, {val_ts}>", False

        # Optional[X]  →  X  (optional flag = True)
        if name == "Optional":
            inner, _ = node_to_ts(node.slice)
            return inner, True

        # Union[X, Y, None, …]
        if name == "Union":
            elts = node.slice.elts if isinstance(node.slice, ast.Tuple) else [node.slice]
            parts: list[str] = []
            optional = False
            for elt in elts:
                t, o = node_to_ts(elt)
                if t == "null":
                    optional = True
                else:
                    parts.append(t)
            # deduplicate while preserving order
            seen: dict[str, None] = {}
            for p in parts:
                seen[p] = None
            return " | ".join(seen), optional

        # Literal['a', 'b', 1]
        if name == "Literal":
            elts = node.slice.elts if isinstance(node.slice, ast.Tuple) else [node.slice]
            vals: list[str] = []
            for elt in elts:
                if isinstance(elt, ast.Constant):
                    vals.append(f"'{elt.value}'" if isinstance(elt.value, str) else str(elt.value))
            return " | ".join(vals) or "unknown", False

        # ClassVar[X] – skip (not a request/response field)
        if name == "ClassVar":
            return "__classvar__", False

    return "unknown", False


# ---------------------------------------------------------------------------
# Class conversion
# ---------------------------------------------------------------------------

_PYDANTIC_ROOTS = {"BaseModel"}


def convert_class(cls: ast.ClassDef, model_names: set[str]) -> str | None:
    """Return a TypeScript interface string, or None if not a pydantic model."""
    base_ids: list[str] = []
    for base in cls.bases:
        if isinstance(base, ast.Name):
            base_ids.append(base.id)
        elif isinstance(base, ast.Attribute):
            base_ids.append(base.attr)

    if not any(b in model_names for b in base_ids):
        return None

    ts_parents = [b for b in base_ids if b not in _PYDANTIC_ROOTS]
    extends = f" extends {', '.join(ts_parents)}" if ts_parents else ""

    fields: list[str] = []
    for item in cls.body:
        if not isinstance(item, ast.AnnAssign) or not isinstance(item.target, ast.Name):
            continue
        field_name = item.target.id
        if field_name.startswith("_"):
            continue

        ts_type, is_optional = node_to_ts(item.annotation)

        if ts_type == "__classvar__":
            continue

        # Any default value (including `= None`) makes the field optional
        if item.value is not None:
            is_optional = True

        opt = "?" if is_optional else ""
        fields.append(f"  {field_name}{opt}: {ts_type};")

    return "\n".join([f"export interface {cls.name}{extends} {{", *fields, "}"])


# ---------------------------------------------------------------------------
# File / directory processing
# ---------------------------------------------------------------------------

def collect_model_names(tree: ast.Module, seed: set[str]) -> set[str]:
    """Transitively find all class names that inherit from seed names."""
    model_names = set(seed)
    changed = True
    while changed:
        changed = False
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef) or node.name in model_names:
                continue
            base_ids = {
                b.id if isinstance(b, ast.Name) else (b.attr if isinstance(b, ast.Attribute) else "")
                for b in node.bases
            }
            if base_ids & model_names:
                model_names.add(node.name)
                changed = True
    return model_names


def convert_file(path: Path) -> str:
    source = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        return f"// SyntaxError in {path.name}: {exc}"

    model_names = collect_model_names(tree, _PYDANTIC_ROOTS)

    blocks: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            result = convert_class(node, model_names)
            if result:
                blocks.append(result)

    return "\n\n".join(blocks)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)

    input_path = Path(args[0])
    output_path = Path(args[1]) if len(args) > 1 else None

    if input_path.is_dir():
        files = sorted(f for f in input_path.glob("*.py") if f.name != "__init__.py")
    elif input_path.is_file():
        files = [input_path]
    else:
        print(f"Error: '{input_path}' not found.", file=sys.stderr)
        sys.exit(1)

    sections: list[str] = []
    for f in files:
        block = convert_file(f)
        if block.strip():
            sections.append(f"// ---- {f.stem} ----\n\n{block}")

    result = "\n\n".join(sections) + "\n"

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(result, encoding="utf-8")
        print(f"Written {len(sections)} section(s) to {output_path}")
    else:
        print(result, end="")


if __name__ == "__main__":
    main()
