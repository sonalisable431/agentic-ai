
import { IRequest } from "../interface/IRequest";
import { IValidator } from "../interface/IValidator";
import { ResponseSummary } from "../model/ResponseSummary";

export class ConsumerProcessor {

    private requests: IRequest[] = [];

    private validationChecks: IValidator[] = [];

    public constructor(private logLevel?: string) { }

    public addRequest(request: IRequest) {
        this.requests.push(request);
    }


    public addValidationCheck(check: IValidator) {
        this.validationChecks.push(check);
    }

    private createResponse(warnings: any, errors: any, response: any) {
        const finalResponse = {
            validationWarnings: warnings,
            validationErrors: errors,
            endPointResponse: response
        };

        return finalResponse;
    }

    //=================================================================
    // Process source data and push to target system using all defined requests
    public async process(samsDocument: any): Promise<any> {

        const responses: ResponseSummary[] = [];
        const warnings: string[] = [];
        const errors: string[] = [];
        const consumerData = typeof samsDocument == "string" ? JSON.parse(samsDocument) : samsDocument;
        

        for (const check of this.validationChecks) {
            const result: boolean = await check.performCheck(consumerData, warnings, errors);
            if (!result) {
                return this.createResponse(warnings, errors, responses);
            }
        }

        for (const request of this.requests) {
            const response: ResponseSummary = await request.post(consumerData);
            responses.push(response);
        }

        return {
            targetSystemResponse: responses
        };
    }
}