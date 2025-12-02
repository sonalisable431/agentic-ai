import json
import shutil
from pathlib import Path
from textwrap import dedent
from typing import Dict, Any, List, Optional

from .utils import _write_file, _ts_type_from_json_schema_type, _generate_interface_from_schema


def convert_property(prop_schema: Dict[str, Any], prop_name: str, required_fields: set) -> str:
    """Convert a property schema to Zod string, handling types and optionality."""
    t = prop_schema.get("type")
    if t == "string":
        zod_base = "z.string()"
    elif t == "number":
        zod_base = "z.number()"
    elif t == "integer":
        zod_base = "z.number().int()"
    elif t == "boolean":
        zod_base = "z.boolean()"
    elif t == "object":
        if "properties" in prop_schema:
            nested_lines = []
            nested_required = set(prop_schema.get("required", []))
            for nested_prop, nested_prop_schema in prop_schema["properties"].items():
                nested_zod = convert_property(nested_prop_schema, nested_prop, nested_required) if isinstance(nested_prop_schema, dict) else "z.any()"
                nested_lines.append(f"    {nested_prop}: {nested_zod},")
            zod_base = f"z.object({{\n" + "\n".join(nested_lines) + "\n  }})"
        else:
            zod_base = "z.record(z.any())"
    elif t == "array":
        items = prop_schema.get("items", {})
        if isinstance(items, dict):
            item_zod = convert_property(items, "item", set())
            zod_base = f"z.array({item_zod})"
        else:
            zod_base = "z.array(z.any())"
    else:
        zod_base = "z.any()"
    if prop_name and prop_name not in required_fields:
        zod_base += ".optional()"
    return zod_base


def json_schema_to_zod(schema: Dict[str, Any], name: str = "Schema") -> str:
    """Convert a JSON schema to Zod schema string, handling nested structures and required fields."""
    required_fields = set(schema.get("required", []))

    if schema.get("type") != "object" or "properties" not in schema:
        return f"export const {name} = z.any();"

    lines = [f"export const {name} = z.object({{"]
    for prop, prop_schema in schema["properties"].items():
        zod_type = convert_property(prop_schema, prop, required_fields) if isinstance(prop_schema, dict) else "z.any()"
        lines.append(f"  {prop}: {zod_type},")
    lines.append("});")
    return "\n".join(lines)


def generate_lambda_project(
    lambda_name: str,
    input_schema: Dict[str, Any],
    output_schema: Dict[str, Any],
    required_fields: List[str],
    field_mapping: Optional[Dict[str, str]] = None,
    base_dir: str = ".",
    api_url: Optional[str] = None,
) -> None:
    """
    Generate a CDK-based TypeScript AWS Lambda project using consumer_template as base.
    Includes Zod schemas for input and output validation.
    """

    project_dir = Path(base_dir) / lambda_name
    template_dir = Path(__file__).parent.parent / "consumer_template"

    if not template_dir.exists():
        raise FileNotFoundError(f"Template directory not found: {template_dir}")

    # Copy the entire template
    shutil.copytree(template_dir, project_dir, dirs_exist_ok=True)

    # Customize package.json
    package_json_path = project_dir / "package.json"
    if package_json_path.exists():
        with open(package_json_path, 'r') as f:
            package_json = json.load(f)
        package_json["name"] = lambda_name
        # Add Zod dependency
        if "dependencies" not in package_json:
            package_json["dependencies"] = {}
        package_json["dependencies"]["zod"] = "^3.22.4"
        with open(package_json_path, 'w') as f:
            json.dump(package_json, f, indent=2)

    # Generate custom mapping if provided
    if field_mapping:
        mapping_ts_path = project_dir / "src" / "mapping.ts"
        if mapping_ts_path.exists():
            existing_content = mapping_ts_path.read_text()
            # Add custom mapping function
            custom_mapping = dedent(f"""
            // Auto-generated custom mapping from Data Mapping Rules
            export const customFieldMapping: Record<string, string> = {json.dumps(field_mapping)};

            /**
             * Retrieves a value from an object using a dot-separated path.
             * @param obj The object to traverse.
             * @param path The dot-separated path to the value.
             * @returns The value at the path, or undefined if not found.
             */
            export function getValueByPath(obj: any, path: string): any {{
              return path.split(".").reduce((acc, key) => (acc == null ? undefined : acc[key]), obj);
            }}

            /**
             * Maps input data to output data using custom field mappings.
             * @param input The input object to map from.
             * @returns The mapped output object.
             */
            export function mapInputToOutputCustom(input: any): any {{
              const output: any = {{}};
              for (const [outKey, inPath] of Object.entries(customFieldMapping)) {{
                output[outKey] = getValueByPath(input, inPath);
              }}
              return output;
            }}
            """)
            # Append to existing mapping.ts
            with open(mapping_ts_path, 'a') as f:
                f.write("\n\n" + custom_mapping)
        else:
            # Create new mapping.ts if not exists
            custom_mapping = dedent(f"""
            // Auto-generated mapping from Data Mapping Rules
            export const customFieldMapping: Record<string, string> = {json.dumps(field_mapping)};

            export function getValueByPath(obj: any, path: string): any {{
              return path.split(".").reduce((acc, key) => (acc == null ? undefined : acc[key]), obj);
            }}

            export function mapInputToOutputCustom(input: any): any {{
              const output: any = {{}};
              for (const [outKey, inPath] of Object.entries(customFieldMapping)) {{
                output[outKey] = getValueByPath(input, inPath);
              }}
              return output;
            }}
            """)
            mapping_ts_path.write_text(custom_mapping)

    # Generate Zod schemas
    schemas_ts = dedent("""
        import { z } from "zod";

        // Auto-generated Zod schemas from JSON schemas
        // These schemas provide runtime validation for input and output data
        """).strip()

    schemas_ts += "\n\n" + json_schema_to_zod(input_schema, "InputSchema")
    schemas_ts += "\n\n" + json_schema_to_zod(output_schema, "OutputSchema")

    # Write schemas.ts in src
    schemas_path = project_dir / "src" / "schemas.ts"
    schemas_path.write_text(schemas_ts)
    cdk_init_path = project_dir / "cdk" / "compData_product_consumer" / "compData_product_consumer.py"
    if cdk_init_path.exists():
        content = cdk_init_path.read_text()
        # Replace any hardcoded names if necessary
        content = content.replace("compData_product_consumer", lambda_name)
        cdk_init_path.write_text(content)

    # Update README or other files if needed
    readme_path = project_dir / "README.md"
    if readme_path.exists():
        content = readme_path.read_text()
        content = content.replace("consumer_template", lambda_name)
        readme_path.write_text(content)

    print(f"CDK Lambda project with Zod schemas generated at: {project_dir.resolve()}")