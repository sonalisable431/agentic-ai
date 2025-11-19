import { validateInput } from "../src/core/validation";

describe("validateInput", () => {
  it("returns valid for correct payload", () => {
    const payload: any = {
      eventId: "EVT1",
      customer: { id: "C1" },
      transaction: { amount: 100, currency: "USD" }
    };
    const result = validateInput(payload);
    expect(result.valid).toBe(true);
    expect(result.errors).toBeUndefined();
  });

  it("fails when required field is missing", () => {
    const payload: any = {};
    const result = validateInput(payload);
    expect(result.valid).toBe(false);
    expect(result.errors).toBeDefined();
  });
});
