import { SamsDocumentInfo } from './common/samsDocumentInfo';
import { formatedErrorMsg } from './common/util';
import { IRequest } from './interface/IRequest';
import { ResponseSummary } from './model/ResponseSummary';
import { processResponse } from './processResponse';
import { ESILogger, ESITrackingServiceDocument, ESIAPIHelper, ESIAuthTokenProvider } from 'esi-common-layer';

export class APIRequest implements IRequest {

    private apiService: ESIAPIHelper.WebApiHelper;
    private url: string;
    private logger: any;
    private docKey: any;
    private esiTrackingService: ESITrackingServiceDocument.DocumentService;
    private oAuthParameterName: string;

    public constructor(
        apiService: ESIAPIHelper.WebApiHelper,
        url: string,
        logLevel: ESILogger.LogLevels,
        esiTrackingService: ESITrackingServiceDocument.DocumentService,
        docKey: string,
        oAuthParameterName: string
    ) {
        this.apiService = apiService;
        this.url = url;
        this.esiTrackingService = esiTrackingService;
        this.docKey = docKey;
        this.oAuthParameterName = oAuthParameterName;
        this.logger = ESILogger.getLogger(APIRequest.name, logLevel);
    }

    public async post(samsDocument: SamsDocumentInfo): Promise<ResponseSummary> {

        let endpointResponse: any;
        let response: any;
        const requestBody = samsDocument;
        this.logger.info(`Received request body: ${JSON.stringify(requestBody)}`);
        const postMsg = "Post request to target system";

        const startedTime = new Date();
        try {
                               
            const requestConfig: ESIAPIHelper.RequestConfig = await this.getHeaderDetails();

            this.logger.info(`Endpoint API URL: ${this.url}`);
            this.logger.info(`Request to body: ${JSON.stringify(requestBody)}`);


            // const product = { title: 'New Product', price: 29.99 };
            endpointResponse = await this.apiService.sendRequest('POST', "https://fakestoreapi.com/products", requestBody, requestConfig);
            this.logger.debug(`endpointResponse : ${JSON.stringify(endpointResponse)}`);
            response = await processResponse(endpointResponse);

            this.createDocumentStep(postMsg, ESITrackingServiceDocument.StepStatus.COMPLETED, startedTime);

        } catch (error) {
            // Upon failure track with complete status
            const errorResponse = error?.response ? error.response.data : error.message;
            this.logger.error(`Error while ${postMsg}: statusCode: ${error?.response?.status}, Error: ${errorResponse} ` + formatedErrorMsg(error));
            this.createDocumentStep(postMsg, ESITrackingServiceDocument.StepStatus.FAILED, startedTime, errorResponse);

            throw new Error(`Failure during[${postMsg}]: ${error?.message} | ${JSON.stringify(error.response.data)} `);
        }

        return response;
    }

    // ESI Tracking
    private async createDocumentStep(message: string, status: ESITrackingServiceDocument.StepStatus, startedTime: Date, errorMessage?: any) {

        await this.esiTrackingService.createStep({
            process: message,
            status: status,
            started_time: startedTime,
            error_message: errorMessage,
        }, this.docKey);
    }

    private async getHeaderDetails(): Promise<any> {

        try {
            this.logger.info(`Generating Bearer Token for ${this.oAuthParameterName}`);
             const token: string = await ESIAuthTokenProvider.getToken(this.oAuthParameterName);
            return {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`,
            };
        } catch (error) {
            const errorMessage = `Error occurred while fetching token: ${this.oAuthParameterName}`;
            this.logger.error(`${errorMessage} ${formatedErrorMsg(error)}`);
            throw new Error(`${errorMessage} ${JSON.stringify(error)}`);
        }
    }
    
}