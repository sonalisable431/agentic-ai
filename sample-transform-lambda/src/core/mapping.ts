// Auto-generated mapping core library

        export interface InputPayload {
  eventId: string;
  customer: Record<string, any>;
  transaction: Record<string, any>;
  meta: Record<string, any>;
}

        export interface OutputPayload {
  id: string;
  userId: string;
  name: string;
  emailAddress: string;
  amountPaid: number;
  ccy: string;
  paymentTime: string;
  processedBy: string;
}

        export const outputSchema = {
  "type": "object",
  "properties": {
    "id": {
      "type": "string"
    },
    "userId": {
      "type": "string"
    },
    "name": {
      "type": "string"
    },
    "emailAddress": {
      "type": "string"
    },
    "amountPaid": {
      "type": "number"
    },
    "ccy": {
      "type": "string"
    },
    "paymentTime": { 
      "type": "string"
    },
    "processedBy": {
      "type": "string"
    }
  }
};

        // mapping: outputField -> inputPath (dot notation)
        export const fieldMapping: Record<string, string> = {
  "id": "eventId",
  "userId": "customer.id",
  "name": "customer.fullName",
  "emailAddress": "customer.email",
  "amountPaid": "transaction.amount",
  "ccy": "transaction.currency",
  "paymentTime": "transaction.timestamp",
  "processedBy": "meta.source"
};

        export function getValueByPath(obj: any, path: string): any {
          return path.split(".").reduce((acc, key) => (acc == null ? undefined : acc[key]), obj);
        }

        export function mapInputToOutput(input: InputPayload): OutputPayload {
          const output: any = {};

          if (Object.keys(fieldMapping).length > 0) {
            for (const [outKey, inPath] of Object.entries(fieldMapping)) {
              output[outKey] = getValueByPath(input, inPath);
            }
          } else {
            for (const key of Object.keys(input)) {
              output[key] = (input as any)[key];
            }
          }

          return output as OutputPayload;
        }
