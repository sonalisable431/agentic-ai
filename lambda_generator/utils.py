import json
from pathlib import Path
from typing import Dict, Any


def _write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _ts_type_from_json_schema_type(t: str) -> str:
    mapping = {
        "string": "string",
        "number": "number",
        "integer": "number",
        "boolean": "boolean",
        "object": "Record<string, any>",
        "array": "any[]",
    }
    return mapping.get(t, "any")


def _generate_interface_from_schema(name: str, schema: Dict[str, Any]) -> str:
    """
    Simple TS interface generator for top-level properties only.
    Nested objects are typed as Record<string, any>.
    """
    props = schema.get("properties") or {}
    if not isinstance(props, dict) or not props:
        return f"export interface {name} {{ [key: string]: any; }}"

    lines = [f"export interface {name} {{"]
    for field_name, field_schema in props.items():
        ts_type = "any"
        if isinstance(field_schema, dict):
            t = field_schema.get("type", "any")
            # If nested object, just make it generic object
            if t == "object":
                ts_type = "Record<string, any>"
            else:
                ts_type = _ts_type_from_json_schema_type(t)
        lines.append(f"  {field_name}: {ts_type};")
    lines.append("}")
    return "\n".join(lines)