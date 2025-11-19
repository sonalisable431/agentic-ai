import json
from pathlib import Path
from textwrap import dedent
from typing import Dict, Any, List, Optional


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


def generate_lambda_project(
    lambda_name: str,
    input_schema: Dict[str, Any],
    output_schema: Dict[str, Any],
    required_fields: List[str],
    field_mapping: Optional[Dict[str, str]] = None,
    base_dir: str = ".",
) -> None:
    """
    Generate a TypeScript AWS Lambda project with:
      - validation core library
      - mapping core library
      - axios-based HTTP client
      - Jest unit tests
    """

    project_dir = Path(base_dir) / lambda_name
    src_dir = project_dir / "src"
    core_dir = src_dir / "core"
    tests_dir = project_dir / "tests"

    # package.json
    package_json = {
        "name": lambda_name,
        "version": "1.0.0",
        "main": "dist/handler.js",
        "scripts": {
            "build": "tsc",
            "test": "jest --coverage",
            "start": "ts-node src/handler.ts",
        },
        "dependencies": {
            "axios": "^1.7.2",
        },
        "devDependencies": {
            "@types/aws-lambda": "^8.10.138",
            "@types/jest": "^29.5.12",
            "@types/node": "^22.9.1",
            "jest": "^29.7.0",
            "ts-jest": "^29.2.5",
            "ts-node": "^10.9.2",
            "typescript": "^5.6.3",
        },
    }
    _write_file(project_dir / "package.json", json.dumps(package_json, indent=2))

    # tsconfig.json
    tsconfig = {
        "compilerOptions": {
            "target": "ES2020",
            "module": "commonjs",
            "moduleResolution": "node",
            "outDir": "dist",
            "rootDir": "src",
            "strict": True,
            "esModuleInterop": True,
            "resolveJsonModule": True,
            "types": ["node", "jest"],
        },
        "include": ["src/**/*.ts", "tests/**/*.ts"],
    }
    _write_file(project_dir / "tsconfig.json", json.dumps(tsconfig, indent=2))

    # jest.config.cjs
    jest_config = dedent(
        """
        /** @type {import('jest').Config} */
        module.exports = {
          preset: "ts-jest",
          testEnvironment: "node",
          testMatch: ["**/tests/**/*.test.ts"],
        };
        """
    ).lstrip()
    _write_file(project_dir / "jest.config.cjs", jest_config)

    # -------- core/validation.ts --------
    input_schema_ts = json.dumps(input_schema, indent=2)
    required_fields_ts = json.dumps(required_fields, indent=2)

    validation_ts = dedent(
        f"""
        // Auto-generated validation core library

        export type JsonSchema = {{
          type?: string;
          properties?: Record<string, JsonSchema>;
        }};

        export const inputSchema: JsonSchema = {input_schema_ts};

        export const requiredFields: string[] = {required_fields_ts};

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
        """
    ).lstrip()
    _write_file(core_dir / "validation.ts", validation_ts)

    # -------- core/mapping.ts --------
    output_schema_ts = json.dumps(output_schema, indent=2)
    field_mapping_ts = json.dumps(field_mapping or {}, indent=2)

    input_interface = _generate_interface_from_schema("InputPayload", input_schema)
    output_interface = _generate_interface_from_schema("OutputPayload", output_schema)

    mapping_ts = dedent(
        f"""
        // Auto-generated mapping core library

        {input_interface}

        {output_interface}

        export const outputSchema = {output_schema_ts};

        // mapping: outputField -> inputPath (dot notation)
        export const fieldMapping: Record<string, string> = {field_mapping_ts};

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
        """
    ).lstrip()
    _write_file(core_dir / "mapping.ts", mapping_ts)

    # -------- core/httpClient.ts --------
    http_client_ts = dedent(
        """
        // Auto-generated HTTP client using axios

        import axios, { AxiosRequestConfig } from "axios";

        export async function getJson<T = any>(url: string, config: AxiosRequestConfig = {}): Promise<T> {
          const response = await axios.get<T>(url, config);
          return response.data;
        }

        export async function postJson<T = any>(
          url: string,
          body: any,
          config: AxiosRequestConfig = {}
        ): Promise<T> {
          const response = await axios.post<T>(url, body, {
            headers: { "Content-Type": "application/json", ...(config.headers || {}) },
            ...config,
          });
          return response.data;
        }
        """
    ).lstrip()
    _write_file(core_dir / "httpClient.ts", http_client_ts)

    # -------- handler.ts --------
    handler_ts = dedent(
        """
        // Auto-generated Lambda handler

        import { APIGatewayProxyEvent, APIGatewayProxyResult } from "aws-lambda";
        import { validateInput } from "./core/validation";
        import { mapInputToOutput } from "./core/mapping";

        export const handler = async (
          event: APIGatewayProxyEvent
        ): Promise<APIGatewayProxyResult> => {
          try {
            const rawBody = event.body || "{}";
            const parsed = JSON.parse(rawBody);

            const validation = validateInput(parsed);
            if (!validation.valid) {
              return {
                statusCode: 400,
                body: JSON.stringify({
                  message: "Invalid input",
                  errors: validation.errors,
                }),
              };
            }

            const output = mapInputToOutput(parsed);

            return {
              statusCode: 200,
              body: JSON.stringify({
                success: true,
                data: output,
              }),
            };
          } catch (err: any) {
            console.error("Handler error", err);
            return {
              statusCode: 500,
              body: JSON.stringify({
                success: false,
                message: "Internal server error",
              }),
            };
          }
        };
        """
    ).lstrip()
    _write_file(src_dir / "handler.ts", handler_ts)

    # -------- tests/validation.test.ts --------
    first_required = required_fields[0] if required_fields else "eventId"

    validation_test_ts = dedent(
        f"""
        import {{ validateInput }} from "../src/core/validation";

        describe("validateInput", () => {{
          it("returns valid for correct payload", () => {{
            const payload: any = {{
              eventId: "EVT1",
              customer: {{ id: "C1" }},
              transaction: {{ amount: 100, currency: "USD" }}
            }};
            const result = validateInput(payload);
            expect(result.valid).toBe(true);
            expect(result.errors).toBeUndefined();
          }});

          it("fails when required field is missing", () => {{
            const payload: any = {{}};
            const result = validateInput(payload);
            expect(result.valid).toBe(false);
            expect(result.errors).toBeDefined();
          }});
        }});
        """
    ).lstrip()
    _write_file(tests_dir / "validation.test.ts", validation_test_ts)

    # -------- tests/mapping.test.ts --------
    mapping_test_ts = dedent(
        """
        import { mapInputToOutput, fieldMapping } from "../src/core/mapping";

        describe("mapInputToOutput", () => {
          it("maps using fieldMapping", () => {
            const input: any = {
              eventId: "EVT1",
              customer: { id: "C1", fullName: "John Doe", email: "john@example.com" },
              transaction: { amount: 100, currency: "USD", timestamp: "2025-01-01T00:00:00Z" },
              meta: { source: "mobile-app" },
            };

            const output = mapInputToOutput(input);

            for (const [outKey, inPath] of Object.entries(fieldMapping)) {
              const value = inPath.split(".").reduce((acc: any, key: string) => acc?.[key], input);
              expect((output as any)[outKey]).toEqual(value);
            }
          });
        });
        """
    ).lstrip()
    _write_file(tests_dir / "mapping.test.ts", mapping_test_ts)

    # -------- tests/httpClient.test.ts --------
    http_client_test_ts = dedent(
        """
        import axios from "axios";
        import { getJson, postJson } from "../src/core/httpClient";

        jest.mock("axios");
        const mockedAxios = axios as jest.Mocked<typeof axios>;

        describe("httpClient", () => {
          it("getJson calls axios.get and returns data", async () => {
            mockedAxios.get.mockResolvedValueOnce({ data: { ok: true } } as any);
            const result = await getJson("https://example.com");
            expect(mockedAxios.get).toHaveBeenCalled();
            expect(result).toEqual({ ok: true });
          });

          it("postJson calls axios.post and returns data", async () => {
            mockedAxios.post.mockResolvedValueOnce({ data: { created: true } } as any);
            const result = await postJson("https://example.com", { a: 1 });
            expect(mockedAxios.post).toHaveBeenCalled();
            expect(result).toEqual({ created: true });
          });
        });
        """
    ).lstrip()
    _write_file(tests_dir / "httpClient.test.ts", http_client_test_ts)

    # -------- tests/handler.test.ts --------
    handler_test_ts = dedent(
        """
        import { handler } from "../src/handler";
        import type { APIGatewayProxyEvent } from "aws-lambda";

        function createEvent(body: any): APIGatewayProxyEvent {
          return {
            body: JSON.stringify(body),
            headers: {},
            multiValueHeaders: {},
            httpMethod: "POST",
            isBase64Encoded: false,
            path: "/",
            pathParameters: null,
            queryStringParameters: null,
            multiValueQueryStringParameters: null,
            stageVariables: null,
            requestContext: {} as any,
            resource: "/",
          };
        }

        describe("handler", () => {
          it("returns 200 for valid payload", async () => {
            const event = createEvent({
              eventId: "EVT1",
              customer: { id: "C1" },
              transaction: { amount: 100, currency: "USD" },
            });
            const res = await handler(event);
            expect(res.statusCode).toBe(200);
          });

          it("returns 400 for invalid payload", async () => {
            const event = createEvent({});
            const res = await handler(event);
            expect(res.statusCode).toBe(400);
          });
        });
        """
    ).lstrip()
    _write_file(tests_dir / "handler.test.ts", handler_test_ts)

    print(f"Lambda project generated at: {project_dir.resolve()}")
