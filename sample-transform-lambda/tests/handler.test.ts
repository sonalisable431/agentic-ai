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
