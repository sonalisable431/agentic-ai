import { ConsumerResponseError } from "./consumerResponseError";

export function formatError(error: any) {
  const errorResponse = { statusCode: 500, body: error, headers: { "content-type": "application/json" } };
  if (error.status) {
    errorResponse.statusCode = error.status;
  }
  if (error instanceof ConsumerResponseError) {
    errorResponse.body = error.body;
  } else {
    errorResponse.body = "Failure while executing lambda " + JSON.stringify(error, Object.getOwnPropertyNames(error));
  }
  return errorResponse;
}

