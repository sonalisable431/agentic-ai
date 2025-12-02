import { ESILogger, ESITrackingServiceDocument } from 'esi-common-layer';
import { AppConfig } from './config';
import { ConsumerProcessorBuilder } from './consumerProcessorBuilder';
import { performHealthCheck } from "./healthCheck";
import { getProductMapping } from "./mapping";
import { SamsDocumentInfo } from './common/samsDocumentInfo';
import { ConsumerProcessor } from './common/consumerProcessor';
import { HealthCheckMaster } from './common/healthCheckMaster';
import { ConsumerResponse } from './model/consumerResponse';
import { formatedErrorMsg } from './common/util';
import { formatError } from './errors/formatError';

export const handler = async (event: any, context: any) => {
    let logger: any;
    let esiTrackingService: ESITrackingServiceDocument.DocumentService;
    let docEvent: SamsDocumentInfo;
    let consumerProcessor: ConsumerProcessor;
    let interfaceKey: string;
    let docKey: string;

    try {

        const config: AppConfig = await AppConfig.load();
        logger = ESILogger.getLogger('index', config.logLevel);

        ({
            esiTrackingService,
            docEvent,
            consumerProcessor,
            interfaceKey
        } = await new ConsumerProcessorBuilder(event, config).build());

        docKey = docEvent.docKey;

        logger.info(`Received data from producer for document ${docKey} -> ${docEvent.samsDocument?.replace(/\n/g, "")} `);

        // Healthcheck.
        if (HealthCheckMaster.isHealthCheck(event)) {
            const healthCheckSummary = await performHealthCheck(context, config);
            const statusCode = healthCheckSummary.status == "ok" ? 200 : 500;
            return ConsumerResponse.getResponse(statusCode, healthCheckSummary);
        }

        await esiTrackingService.createStep({
            process: "Received competitive product data",
            started_time: new Date(),
            status: ESITrackingServiceDocument.StepStatus.COMPLETED,
        }, docKey);

        const response = await consumerProcessor.process(getProductMapping(docEvent.samsDocument));

        await esiTrackingService.createStep({
            process: "Consumer workflow completed",
            started_time: new Date(),
            status: ESITrackingServiceDocument.StepStatus.COMPLETED,
            error_message: JSON.stringify(response)
        }, docKey);

        const productEndpointResponse = ConsumerResponse.getResponse(200, response);
        logger.info("Consumer workflow completed successfully :" + JSON.stringify(productEndpointResponse));

        // Update the Document status
        await esiTrackingService.update({
            key: docKey,
            interface_key: interfaceKey,
            status: ESITrackingServiceDocument.DocumentStatus.COMPLETED,
            completed_time: new Date()
        });

        return productEndpointResponse;

    } catch (error) {
        console.log("Error in comp product consumer lambda " + formatedErrorMsg(error));

        if (esiTrackingService) {

            await esiTrackingService.update({
                key: docKey,
                interface_key: interfaceKey,
                status: ESITrackingServiceDocument.DocumentStatus.FAILED,
                completed_time: new Date(),
                error_message: JSON.stringify(error, Object.getOwnPropertyNames(error)),
            });
        }

        const errorMessage = `${error?.message}`;
        return formatError(errorMessage);
    }
}
