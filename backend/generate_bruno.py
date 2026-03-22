#!/usr/bin/env python3
"""Generate the Bruno API collection from the FastAPI app.

Run from the project root:
    python generate_bruno.py

The script reads app.routes for display names and app.openapi() for
request-body schemas, then writes one .bru file per endpoint under bruno/.
Existing bruno.json and environments/ are left untouched.
"""

import json
import re
import sys
from pathlib import Path

# Make project-root imports work when run directly
sys.path.insert(0, str(Path(__file__).parent))

from fastapi.routing import APIRoute  # noqa: E402
from main import app  # noqa: E402

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

BRUNO_DIR = Path(__file__).parent / "bruno"

# ---------------------------------------------------------------------------
# Heuristic example values keyed by field-name substring (checked in order)
# ---------------------------------------------------------------------------

_FIELD_HINTS: list[tuple[str, object]] = [
    # More-specific patterns first
    ("service_enable",  True),
    ("IPAddress",       "192.168.1.100"),
    ("MACAddress",      "AA:BB:CC:DD:EE:FF"),
    ("macaddress",      "AA:BB:CC:DD:EE:FF"),
    ("URL",             "http://192.168.1.1/backup.cfg"),
    ("sourceInterface", "data"),
    ("Interface",       "data"),
    ("interface",       "data"),
    ("sourcePrefix",    "0.0.0.0/0"),
    ("Prefix",          "0.0.0.0/0"),
    ("protocol",        "TCP"),
    ("Protocol",        "TCP"),
    ("origin",          "webui"),
    ("Port",            8080),
    ("port",            8080),
    ("Timeout",         30),
    ("timeout",         3600),
    ("LeaseTime",       86400),
    ("leasetime",       86400),
    ("Address",         "192.168.1.1"),
    ("Netmask",         "255.255.255.0"),
    ("hostname",        "myhome.example.org"),
    ("Username",        "admin"),
    ("username",        "admin"),
    ("Password",        "admin"),
    ("password",        "admin"),
    ("reason",          "User request"),
    ("description",     "My rule"),
    ("level",           "Medium"),
    ("WanMode",         "ADSL"),
    ("action",          "DROP"),
    ("chain",           "INPUT"),
    ("fileName",        "backup.cfg"),
    ("clientPIN",       "12345670"),
    ("DeviceName",      "AA:BB:CC:DD:EE:FF"),
    ("input",           "yes"),
    ("event",           "start"),
    ("service",         "dyndns"),
    # Generic path-param names
    ("mac",             "AA:BB:CC:DD:EE:FF"),
    ("key",             "AA:BB:CC:DD:EE:FF"),
    ("id",              "rule_001"),
    ("name",            "my-name"),
    ("flag",            ""),
]


def _example_value(field_name: str, schema: dict) -> object:
    for hint, val in _FIELD_HINTS:
        if hint in field_name:
            return val
    # Fall back on JSON-schema type
    t = schema.get("type")
    if "anyOf" in schema:
        for s in schema["anyOf"]:
            if s.get("type") != "null":
                t = s.get("type")
                break
    if t == "boolean":
        return schema.get("default", True)
    if t == "integer":
        return schema.get("default", 0)
    if t == "array":
        return []
    return schema.get("default", "")


# ---------------------------------------------------------------------------
# Schema helpers
# ---------------------------------------------------------------------------

def _resolve(schema: dict, schemas: dict) -> dict:
    """Follow $ref and merge allOf."""
    if "$ref" in schema:
        name = schema["$ref"].split("/")[-1]
        return _resolve(schemas.get(name, {}), schemas)
    if "allOf" in schema:
        merged: dict = {}
        for sub in schema["allOf"]:
            resolved = _resolve(sub, schemas)
            merged.update(resolved.get("properties", {}))
        return {"properties": merged}
    return schema


def _body_example(body_schema: dict, schemas: dict) -> dict | None:
    resolved = _resolve(body_schema, schemas)
    props = resolved.get("properties")
    if not props:
        return None
    return {k: _example_value(k, v) for k, v in props.items()}


# ---------------------------------------------------------------------------
# Naming helpers
# ---------------------------------------------------------------------------

def _func_to_display(func_name: str) -> str:
    return func_name.replace("_", " ").title()


def _safe_filename(name: str) -> str:
    return re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", name).strip()


# ---------------------------------------------------------------------------
# .bru renderer
# ---------------------------------------------------------------------------

def _render_bru(
    method: str,
    path: str,
    display_name: str,
    seq: int,
    operation: dict,
    schemas: dict,
) -> str:
    url = re.sub(r"\{(\w+)\}", r":\1", path)

    # Detect body
    req_body = operation.get("requestBody")
    body_type = "none"
    example: dict | None = None
    if req_body:
        json_schema = (
            req_body.get("content", {})
            .get("application/json", {})
            .get("schema", {})
        )
        if json_schema:
            body_type = "json"
            example = _body_example(json_schema, schemas)

    lines: list[str] = [
        "meta {",
        f"  name: {display_name}",
        "  type: http",
        f"  seq: {seq}",
        "}",
        "",
        f"{method} {{",
        f"  url: {{{{baseUrl}}}}{url}",
        f"  body: {body_type}",
        "  auth: none",
        "}",
        "",
    ]

    # Path params
    path_params = [p for p in operation.get("parameters", []) if p.get("in") == "path"]
    if path_params:
        lines.append("params:path {")
        for p in path_params:
            val = _example_value(p["name"], p.get("schema", {}))
            lines.append(f"  {p['name']}: {val}")
        lines += ["}", ""]

    # Query params
    query_params = [p for p in operation.get("parameters", []) if p.get("in") == "query"]
    if query_params:
        lines.append("params:query {")
        for p in query_params:
            default = p.get("schema", {}).get("default", "")
            if default is None:
                default = ""
            lines.append(f"  {p['name']}: {default}")
        lines += ["}", ""]

    # JSON body
    if body_type == "json" and example is not None:
        lines.append("body:json {")
        for line in json.dumps(example, indent=2).splitlines():
            lines.append(f"  {line}")
        lines += ["}", ""]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# bootstrap files (only written if absent)
# ---------------------------------------------------------------------------

def _bootstrap() -> None:
    BRUNO_DIR.mkdir(exist_ok=True)

    bruno_json = BRUNO_DIR / "bruno.json"
    if not bruno_json.exists():
        bruno_json.write_text(
            json.dumps(
                {"version": "1", "name": "Livebox API", "type": "collection", "ignore": []},
                indent=2,
            )
            + "\n"
        )

    env_dir = BRUNO_DIR / "environments"
    env_dir.mkdir(exist_ok=True)
    local_env = env_dir / "Local.bru"
    if not local_env.exists():
        local_env.write_text("vars {\n  baseUrl: http://localhost:8000\n}\nvars:secret {\n}\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    _bootstrap()

    openapi = app.openapi()
    schemas = openapi.get("components", {}).get("schemas", {})
    paths_spec = openapi.get("paths", {})

    # Map (method, path) → display name using actual function names
    name_map: dict[tuple[str, str], str] = {}
    for route in app.routes:
        if isinstance(route, APIRoute):
            for m in route.methods:
                name_map[(m.lower(), route.path)] = _func_to_display(
                    route.endpoint.__name__
                )

    # Group by first tag, preserving declaration order
    tag_ops: dict[str, list[tuple[str, str, str, dict]]] = {}
    for path, path_item in paths_spec.items():
        for method, operation in path_item.items():
            if method not in ("get", "post", "put", "patch", "delete"):
                continue
            tag = (operation.get("tags") or ["Untagged"])[0]
            display = name_map.get((method, path), _func_to_display(operation.get("operationId", "unknown")))
            tag_ops.setdefault(tag, []).append((method, path, display, operation))

    # Write files
    total = 0
    for tag, operations in tag_ops.items():
        folder = BRUNO_DIR / tag
        folder.mkdir(exist_ok=True)

        # Remove stale .bru files from previous runs
        for f in folder.glob("*.bru"):
            f.unlink()

        for seq, (method, path, display, operation) in enumerate(operations, 1):
            content = _render_bru(method, path, display, seq, operation, schemas)
            filename = _safe_filename(display) + ".bru"
            (folder / filename).write_text(content)
            total += 1

        print(f"  {tag:<12} {len(operations)} requests")

    print(f"\n✓  {total} requests written to {BRUNO_DIR}/")


if __name__ == "__main__":
    main()
