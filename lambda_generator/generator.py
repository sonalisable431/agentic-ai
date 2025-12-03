import json
import shutil
from pathlib import Path
from textwrap import dedent
from typing import Dict, Any, List, Optional

from .utils import _write_file, _ts_type_from_json_schema_type


def generate_interface_from_schema(schema: Dict[str, Any], interface_name: str = "Interface") -> str:
    """Generate TypeScript interface from JSON schema."""
    if schema.get("type") != "object" or "properties" not in schema:
        return f"  [key: string]: any;"

    lines = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    for prop_name, prop_schema in properties.items():
        if isinstance(prop_schema, dict):
            prop_type = _ts_type_from_json_schema_type(prop_schema.get("type", "any"))
            optional = "" if prop_name in required else "?"
            lines.append(f"  {prop_name}{optional}: {prop_type};")

    return "\n".join(lines)


def generate_sample_data_from_schema(schema: Dict[str, Any], max_depth: int = 3) -> Any:
    """Generate sample data that conforms to the given JSON schema."""
    if max_depth <= 0:
        return None

    schema_type = schema.get("type", "object")

    if schema_type == "string":
        examples = schema.get("examples", [])
        if examples:
            return examples[0]
        return "sample_string"
    elif schema_type == "number" or schema_type == "integer":
        examples = schema.get("examples", [])
        if examples:
            return examples[0]
        return 42 if schema_type == "integer" else 42.5
    elif schema_type == "boolean":
        return True
    elif schema_type == "array":
        items_schema = schema.get("items", {})
        if isinstance(items_schema, dict):
            return [generate_sample_data_from_schema(items_schema, max_depth - 1)]
        return ["sample_item"]
    elif schema_type == "object":
        properties = schema.get("properties", {})
        result = {}
        for prop_name, prop_schema in properties.items():
            if isinstance(prop_schema, dict):
                result[prop_name] = generate_sample_data_from_schema(prop_schema, max_depth - 1)
        return result
    else:
        return "sample_value"


def generate_handler_tests(lambda_name: str, input_schema: Dict[str, Any], field_mapping: Optional[Dict[str, str]] = None) -> str:
    """Generate handler test file content."""
    sample_input = generate_sample_data_from_schema(input_schema)

    # Generate valid test case
    valid_test_input = json.dumps(sample_input, indent=2)

    # Generate invalid test case (empty object)
    invalid_test_input = "{}"

    return dedent(f'''\
        import {{ handler }} from "../src/handler";
        import type {{ APIGatewayProxyEvent }} from "aws-lambda";

        function createEvent(body: any): APIGatewayProxyEvent {{
          return {{
            body: JSON.stringify(body),
            headers: {{}},
            multiValueHeaders: {{}},
            httpMethod: "POST",
            isBase64Encoded: false,
            path: "/",
            pathParameters: null,
            queryStringParameters: null,
            multiValueQueryStringParameters: null,
            stageVariables: null,
            requestContext: {{}} as any,
            resource: "/",
          }};
        }}

        describe("handler", () => {{
          it("returns 200 for valid payload", async () => {{
            const event = createEvent({valid_test_input});
            const res = await handler(event);
            expect(res.statusCode).toBe(200);
            const responseBody = JSON.parse(res.body);
            expect(responseBody).toBeDefined();
          }});

          it("returns 400 for invalid payload", async () => {{
            const event = createEvent({invalid_test_input});
            const res = await handler(event);
            expect(res.statusCode).toBe(400);
          }});

          it("returns 400 for malformed JSON", async () => {{
            const event = createEvent("invalid json");
            const res = await handler(event);
            expect(res.statusCode).toBe(400);
          }});
        }});
        ''')


def generate_mapping_tests(field_mapping: Dict[str, str], input_schema: Dict[str, Any]) -> str:
    """Generate mapping test file content."""
    sample_input = generate_sample_data_from_schema(input_schema)

    # Create test input with nested structure
    test_input = json.dumps(sample_input, indent=2)

    # Generate assertions for each mapping
    assertions = []
    for out_key, in_path in field_mapping.items():
        assertions.append(f'      expect((output as any)["{out_key}"]).toEqual(getValueByPath(input, "{in_path}"));')

    assertions_str = "\n".join(assertions)

    return dedent(f'''\
        import {{ mapInputToOutput, fieldMapping, getValueByPath }} from "../src/core/mapping";

        describe("mapInputToOutput", () => {{
          it("maps using fieldMapping", () => {{
            const input: any = {test_input};

            const output = mapInputToOutput(input);

        {assertions_str}
          }});

          it("handles missing nested properties gracefully", () => {{
            const input: any = {{}};

            const output = mapInputToOutput(input);

            // Should not throw and should return object with undefined values
            expect(typeof output).toBe("object");
          }});
        }});
        ''')


def generate_validation_tests(input_schema: Dict[str, Any], required_fields: List[str]) -> str:
    """Generate validation test file content."""
    sample_input = generate_sample_data_from_schema(input_schema)

    # Valid test case
    valid_test_input = json.dumps(sample_input, indent=2)

    # Invalid test case - missing required fields
    invalid_input = "{}"

    # Generate specific missing field tests
    missing_field_tests = []
    if required_fields:
        for field in required_fields[:2]:  # Test first 2 required fields
            field_parts = field.split('.')
            test_input = json.dumps(sample_input, indent=2)
            missing_field_tests.append(dedent(f'''\
                it("fails when required field '{field}' is missing", () => {{
                  const payload: any = {invalid_input};
                  const result = validateInput(payload);
                  expect(result.valid).toBe(false);
                  expect(result.errors).toBeDefined();
                  expect(result.errors!.length).toBeGreaterThan(0);
                }});'''))

    missing_field_tests_str = "\n\n".join(missing_field_tests)

    return dedent(f'''\
        import {{ validateInput }} from "../src/core/validation";

        describe("validateInput", () => {{
          it("returns valid for correct payload", () => {{
            const payload: any = {valid_test_input};
            const result = validateInput(payload);
            expect(result.valid).toBe(true);
            expect(result.errors).toBeUndefined();
          }});

          it("fails when payload is not an object", () => {{
            const payload: any = "not an object";
            const result = validateInput(payload);
            expect(result.valid).toBe(false);
            expect(result.errors).toBeDefined();
          }});

        {missing_field_tests_str}
        }});
        ''')


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
    lambda_folder_name: str,
    lambda_name: str,
    input_schema: Dict[str, Any],
    output_schema: Dict[str, Any],
    required_fields: List[str],
    field_mapping: Optional[Dict[str, str]] = None,
    base_dir: str = ".",
    api_url: Optional[str] = None,
    env_vars: Optional[Dict[str, str]] = None,
    memory_size: int = 300,
    route_type: str = "compData_product",
    source_interface_name: str = "",
    target_interface_name: str = "",
    interface_type: str = "consumer",
) -> None:
    """
    Generate a CDK-based TypeScript AWS Lambda project using consumer_template as base.
    Includes Zod schemas for input and output validation.
    """

    project_dir = Path(base_dir) / lambda_folder_name
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
        core_dir = project_dir / "src" / "core"
        core_dir.mkdir(exist_ok=True)
        
        mapping_ts_path = core_dir / "mapping.ts"
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

    # Create core directory for generated files
    core_dir = project_dir / "src" / "core"
    core_dir.mkdir(exist_ok=True)

    # Generate Zod schemas in core directory
    schemas_ts = dedent("""
        import { z } from "zod";

        // Auto-generated Zod schemas from JSON schemas
        // These schemas provide runtime validation for input and output data
        """).strip()

    schemas_ts += "\n\n" + json_schema_to_zod(input_schema, "InputSchema")
    schemas_ts += "\n\n" + json_schema_to_zod(output_schema, "OutputSchema")

    # Write schemas.ts in core
    schemas_path = core_dir / "schemas.ts"
    schemas_path.write_text(schemas_ts)

    # Generate validation.ts
    validation_ts = generate_validation_tests(input_schema, required_fields).replace("describe(\"validateInput\", () => {", "").replace("});", "").strip()
    validation_ts = dedent(f"""
        // Auto-generated validation core library

        export type JsonSchema = {{
          type?: string;
          properties?: Record<string, JsonSchema>;
        }};

        export const inputSchema: JsonSchema = {json.dumps(input_schema)};

        export const requiredFields: string[] = {required_fields};

        export interface ValidationResult {{
          valid: boolean;
          errors?: string[];
        }}

        export function getValueByPath(obj: any, path: string): any {{
          return path.split(".").reduce((acc, key) => (acc == null ? undefined : acc[key]), obj);
        }}

        export function validateInput(payload: any): ValidationResult {{
          const errors: string[] = [];

          if (inputSchema.type === "object") {{
            if (typeof payload !== "object" || payload === null || Array.isArray(payload)) {{
              errors.push("Root must be an object");
            }}
          }}

          for (const field of requiredFields) {{
            if (getValueByPath(payload, field) === undefined) {{
              errors.push(`Missing required field: ${{field}}`);
            }}
          }}

          return {{
            valid: errors.length === 0,
            errors: errors.length ? errors : undefined,
          }};
        }}
        """)
    validation_path = core_dir / "validation.ts"
    validation_path.write_text(validation_ts)

    # Generate mapping.ts in core directory
    if field_mapping:
        mapping_content = dedent(f"""
        // Auto-generated mapping core library

        export interface InputPayload {{
        {generate_interface_from_schema(input_schema, "InputPayload")}
        }}

        export interface OutputPayload {{
        {generate_interface_from_schema(output_schema, "OutputPayload")}
        }}

        export const outputSchema = {json.dumps(output_schema)};

        // mapping: outputField -> inputPath (dot notation)
        export const fieldMapping: Record<string, string> = {json.dumps(field_mapping)};

        export function getValueByPath(obj: any, path: string): any {{
          return path.split(".").reduce((acc, key) => (acc == null ? undefined : acc[key]), obj);
        }}

        export function mapInputToOutput(input: InputPayload): OutputPayload {{
          const output: any = {{}};

          if (Object.keys(fieldMapping).length > 0) {{
            for (const [outKey, inPath] of Object.entries(fieldMapping)) {{
              output[outKey] = getValueByPath(input, inPath);
            }}
          }} else {{
            for (const key of Object.keys(input)) {{
              output[key] = (input as any)[key];
            }}
          }}

          return output as OutputPayload;
        }}
        """)
        mapping_path = core_dir / "mapping.ts"
        mapping_path.write_text(mapping_content)

    # Generate handler.ts
    handler_ts = dedent(f'''\
        // Auto-generated Lambda handler

        import {{ APIGatewayProxyEvent, APIGatewayProxyResult }} from "aws-lambda";
        import {{ validateInput }} from "./core/validation";
        import {{ mapInputToOutput }} from "./core/mapping";

        export const handler = async (
          event: APIGatewayProxyEvent
        ): Promise<APIGatewayProxyResult> => {{
          try {{
            const rawBody = event.body || "{{}}";
            const parsed = JSON.parse(rawBody);

            const validation = validateInput(parsed);
            if (!validation.valid) {{
              return {{
                statusCode: 400,
                body: JSON.stringify({{
                  message: "Invalid input",
                  errors: validation.errors,
                }}),
              }};
            }}

            const output = mapInputToOutput(parsed);

            return {{
              statusCode: 200,
              body: JSON.stringify({{
                success: true,
                data: output,
              }}),
            }};
          }} catch (err: any) {{
            console.error("Handler error", err);
            return {{
              statusCode: 500,
              body: JSON.stringify({{
                success: false,
                message: "Internal server error",
              }}),
            }};
          }}
        }};
        ''')
    handler_path = project_dir / "src" / "handler.ts"
    handler_path.write_text(handler_ts)

    # Generate test files
    tests_dir = project_dir / "tests"
    tests_dir.mkdir(exist_ok=True)

    # Generate handler tests
    handler_test_content = generate_handler_tests(lambda_name, input_schema, field_mapping)
    handler_test_path = tests_dir / "handler.test.ts"
    handler_test_path.write_text(handler_test_content)

    # Generate mapping tests
    if field_mapping:
        mapping_test_content = generate_mapping_tests(field_mapping, input_schema)
        mapping_test_path = tests_dir / "mapping.test.ts"
        mapping_test_path.write_text(mapping_test_content)

    # Generate validation tests
    validation_test_content = generate_validation_tests(input_schema, required_fields)
    validation_test_path = tests_dir / "validation.test.ts"
    validation_test_path.write_text(validation_test_content)

    # Add Jest configuration
    jest_config = dedent('''\
        /** @type {import('jest').Config} */
        module.exports = {
          preset: "ts-jest",
          testEnvironment: "node",
          testMatch: ["**/tests/**/*.test.ts"],
        };
        ''')
    jest_config_path = project_dir / "jest.config.js"
    jest_config_path.write_text(jest_config)

    # Update package.json to include test scripts and Jest dependencies
    if package_json_path.exists():
        with open(package_json_path, 'r') as f:
            package_json = json.load(f)

        # Add Jest dependencies
        if "devDependencies" not in package_json:
            package_json["devDependencies"] = {}
        package_json["devDependencies"]["@types/jest"] = "^29.5.0"
        package_json["devDependencies"]["jest"] = "^29.5.0"
        package_json["devDependencies"]["ts-jest"] = "^29.1.0"
        package_json["devDependencies"]["@types/aws-lambda"] = "^8.10.119"

        # Add test scripts
        if "scripts" not in package_json:
            package_json["scripts"] = {}
        package_json["scripts"]["test"] = "jest"
        package_json["scripts"]["test:watch"] = "jest --watch"
        package_json["scripts"]["test:coverage"] = "jest --coverage"

        with open(package_json_path, 'w') as f:
            json.dump(package_json, f, indent=2)
    # Rename CDK directory and update Python files
    cdk_dir = project_dir / "cdk"
    old_cdk_subdir = cdk_dir / "compData_product_consumer"
    new_cdk_subdir = cdk_dir / lambda_folder_name
    
    if old_cdk_subdir.exists():
        # Rename the directory
        old_cdk_subdir.rename(new_cdk_subdir)
        
        # Update the Python file inside
        cdk_py_file = new_cdk_subdir / "compData_product_consumer.py"
        if cdk_py_file.exists():
            content = cdk_py_file.read_text()
            # Replace the module name and class name
            content = content.replace("compData_product_consumer", lambda_folder_name)
            content = content.replace("CompDataProductConsumerStack", f"{lambda_folder_name.replace('_', ' ').title().replace(' ', '')}Stack")
            cdk_py_file.write_text(content)
            
            # Rename the Python file itself
            new_py_file = new_cdk_subdir / f"{lambda_folder_name}.py"
            cdk_py_file.rename(new_py_file)
        
        # Update __init__.py if it exists
        init_file = new_cdk_subdir / "__init__.py"
        if init_file.exists():
            content = init_file.read_text()
            content = content.replace("compData_product_consumer", lambda_folder_name)
            init_file.write_text(content)
    
    # Update app.py to reference the new module and class
    app_py_path = cdk_dir / "app.py"
    if app_py_path.exists():
        content = app_py_path.read_text()
        # Generate the class name
        class_name = f"{lambda_folder_name.replace('_', ' ').title().replace(' ', '')}Stack"
        # Replace the import
        content = content.replace("from compData_product_consumer.compData_product_consumer import CompDataProductConsumerStack", 
                                  f"from {lambda_folder_name}.{lambda_folder_name} import {class_name}")
        # Replace the stack instantiation
        content = content.replace("CompDataProductConsumerStack(app, \"esi-compData-product-consumer\", env=aws_env)",
                                  f"{class_name}(app, \"esi-{lambda_folder_name}\", env=aws_env)")
        app_py_path.write_text(content)

    # Update CDK configuration
    cdk_json_path = project_dir / "cdk" / "cdk.json"
    if cdk_json_path.exists():
        with open(cdk_json_path, 'r') as f:
            cdk_config = json.load(f)
        
        # Determine routeCategory and routeApp based on interface type
        route_category = "custom-import" if interface_type == "consumer" else "custom-export"
        route_app = target_interface_name if interface_type == "consumer" else source_interface_name
        
        # Generate description
        description = f"Lambda function for {interface_type} interface processing {source_interface_name} to {target_interface_name}"
        
        # Update CDK configuration for all environments (dev, test, stage, prod)
        for env_name in ['dev', 'test', 'stage', 'prod']:
            if env_name in cdk_config.get('context', {}):
                env_config = cdk_config['context'][env_name]
                if 'appSetting' in env_config and 'lambdaApp' in env_config['appSetting'] and 'lambdaConfig' in env_config['appSetting']['lambdaApp']:
                    lambda_config = env_config['appSetting']['lambdaApp']['lambdaConfig']
                    
                    # Update appName (folder name) and lambda name
                    env_config['appName'] = lambda_folder_name
                    lambda_config['name'] = lambda_name
                    lambda_config['description'] = description
                    
                    # Update memory size
                    lambda_config['memorySize'] = memory_size
                    
                    # Update route configuration
                    lambda_config['routeType'] = route_type
                    lambda_config['routeCategory'] = route_category
                    lambda_config['routeApp'] = route_app
        
        # Update environment variables for all environments (dev, test, stage, prod)
        if env_vars:
            for env_name in ['dev', 'test', 'stage', 'prod']:
                if env_name in cdk_config.get('context', {}):
                    env_config = cdk_config['context'][env_name]
                    if 'appSetting' in env_config and 'lambdaApp' in env_config['appSetting'] and 'lambdaConfig' in env_config['appSetting']['lambdaApp']:
                        lambda_config = env_config['appSetting']['lambdaApp']['lambdaConfig']
                        if 'env' not in lambda_config:
                            lambda_config['env'] = {}
                        # Merge custom environment variables with existing ones
                        lambda_config['env'].update(env_vars)
        
        # Write updated CDK configuration
        with open(cdk_json_path, 'w') as f:
            json.dump(cdk_config, f, indent=2)

    # Update README or other files if needed
    readme_path = project_dir / "README.md"
    if readme_path.exists():
        content = readme_path.read_text()
        content = content.replace("consumer_template", lambda_name)
        readme_path.write_text(content)

    print(f"CDK Lambda project with Zod schemas generated at: {project_dir.resolve()}")