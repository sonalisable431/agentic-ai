// Auto-generated validation core library

        export type JsonSchema = {
          type?: string;
          properties?: Record<string, JsonSchema>;
        };

        export const inputSchema: JsonSchema = {
  "type": "object",
  "properties": {
    "eventId": {
      "type": "string"
    },
    "customer": {
      "type": "object",
      "properties": {
        "id": {
          "type": "string"
        },
        "fullName": {
          "type": "string"
        },
        "email": {
          "type": "string"
        }
      }
    },
    "transaction": {
      "type": "object",
      "properties": {
        "amount": {
          "type": "number"
        },
        "currency": {
          "type": "string"
        },
        "timestamp": {
          "type": "string"
        }
      }
    },
    "meta": {
      "type": "object",
      "properties": {
        "source": {
          "type": "string"
        }
      }
    }
  }
};

        export const requiredFields: string[] = [
  "eventId",
  "customer.id",
  "transaction.amount",
  "transaction.currency"
];

        export interface ValidationResult {
          valid: boolean;
          errors?: string[];
        }

        export function getValueByPath(obj: any, path: string): any {
          return path.split(".").reduce((acc, key) => (acc == null ? undefined : acc[key]), obj);
        }

        export function validateInput(payload: any): ValidationResult {
          const errors: string[] = [];

          if (inputSchema.type === "object") {
            if (typeof payload !== "object" || payload === null || Array.isArray(payload)) {
              errors.push("Root must be an object");
            }
          }

          for (const field of requiredFields) {
            if (getValueByPath(payload, field) === undefined) {
              errors.push(`Missing required field: ${field}`);
            }
          }

          return {
            valid: errors.length === 0,
            errors: errors.length ? errors : undefined,
          };
        }
