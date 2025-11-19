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
