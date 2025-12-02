import { ESIAuthTokenProvider, ESITrackingServiceDocument, ESIAPIHelper } from 'esi-common-layer';
import { APIRequest } from "./apiRequest";
import { ConsumerProcessorBuilderBase } from './common/consumerProcessorBuilderBase';

export class ConsumerProcessorBuilder extends ConsumerProcessorBuilderBase {

    private config: any;

    public constructor(event: any, config: any) {
        super(event, config);
        this.config = config;
    }

    public async build() {

        // Get ESI azure auth token
        const esiAuthToken = await ESIAuthTokenProvider.getToken(this.config.esiOAuthParametersSecretName);

        // Initialize BatchService
        const esiTrackingService = new ESITrackingServiceDocument.DocumentService({ env: this.config.esiEnvironment, accessToken: esiAuthToken }, this.interfaceKey);

        const webApiHelper = new ESIAPIHelper.WebApiHelper(this.config.logLevel);

        const compDataProductUrl = this.config.productUrl;
        const OAuthParametersSecretName = this.config.esiOAuthParametersSecretName;

        const apiRequest = new APIRequest(webApiHelper, compDataProductUrl, this.config.logLevel, esiTrackingService, this.docEvent.docKey, OAuthParametersSecretName);

        this.consumerProcessor.addRequest(apiRequest);

        return {
            esiTrackingService: esiTrackingService,
            docEvent: this.docEvent,
            consumerProcessor: this.consumerProcessor,
            interfaceKey: this.interfaceKey
        };
    }

}
