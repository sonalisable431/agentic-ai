import { ResponseSummary } from "./model/ResponseSummary";
import { WebApiResponse } from "./model/webApiResponse";


export async function processResponse(endpointResponse: any): Promise<any> {

    const data: any = endpointResponse.data;
    const reqStatusCode: any = endpointResponse?.statusCode ?? endpointResponse?.status;

    if (data?.importTime) {
        data.importTime = new Date(parseInt(data.importTime));
    }

    const response: ResponseSummary = {
        httpResponseCode: reqStatusCode,
        data
    };

    const isEndpointCallSuccessful = new WebApiResponse(reqStatusCode, data).wasSuccessful;
    if (!isEndpointCallSuccessful) {
        throw new Error(`Failure returned from target system: ${JSON.stringify(data)}`);
    }

    return response;
}
