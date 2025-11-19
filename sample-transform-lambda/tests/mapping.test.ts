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
