import { handler } from "./handler";

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

const main = async () => {
  const result = await handler(
    createEvent({
      eventId: "evt_123456789",
      customer: {
        id: "cus_98765",
        fullName: "John Doe",
        email: "john.doe@example.com",
      },
      transaction: {
        amount: 1499.5,
        currency: "USD",
        timestamp: "2025-01-15T10:45:00Z",
      },
      meta: {
        source: "webhook",
      },
    })
  );

  console.log(result);
};

(async () => {
  await main();
})();