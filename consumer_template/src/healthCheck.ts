import { ESIAuthTokenProvider, ESILogger } from 'esi-common-layer';
import { HealthCheckMaster } from './common/healthCheckMaster';
import { HealthCheckResource } from './model/healthCheckResource';

interface ItokenCheck {
    isOk: boolean, error: any
}

export async function performHealthCheck(
    context: any,
    config: any
): Promise<any> {

    const healthCheck: HealthCheckMaster = new HealthCheckMaster();
    // Web API Resource
    const logger = ESILogger.getLogger("healthCheck", config.logLevel);

    // Lambda Resource
    healthCheck.AddResource(CheckLambda(context));

    // config Resource
    healthCheck.AddResource(await CheckConfig(config));

    //OAuth Check
    healthCheck.AddResource(await CheckEsiToken(config));

    const healthCheckSummary = healthCheck.getSummary();

    // Rather than have logging at every step along the way, just log the summary
    logger.info(`Health check: ${JSON.stringify(healthCheckSummary)}`);

    return healthCheckSummary;
}

function CheckLambda(context: any): HealthCheckResource {
    return {
        name: context.functionName,
        type: "lambda",
        isOk: true,
        error: null,
        details: {
            memoryLimitInMB: JSON.parse(context.memoryLimitInMB),
            logGroupName: context.logGroupName,
        },
    };
}

async function CheckConfig(config: any): Promise<HealthCheckResource> {
    return {
        name: "target system configuration",
        type: "config",
        isOk: true,
        error: null,
        details: {
            processName: config.processName,
            region: config.region,
            logLevel: config.logLevel,
            productUrl: config.productUrl
        },
    };
}

async function CheckEsiToken(config: any): Promise<HealthCheckResource> {

    let response: ItokenCheck = { isOk: true, error: null };

    try {
        let webApiToken = await ESIAuthTokenProvider.getToken(config.esiOAuthParametersSecretName);
        if (webApiToken == null) {
            throw new Error("Web API token is null");
        }
    } catch (error) {
        response.error = JSON.stringify(error, Object.getOwnPropertyNames(error));
        response.isOk = false;
    }

    return {
        name: "ESI OAuth token",
        type: "web-api",
        isOk: response.isOk,
        error: response.error,
        details: { oauthSecretName: config.esiOAuthParametersSecretName }
    }
}