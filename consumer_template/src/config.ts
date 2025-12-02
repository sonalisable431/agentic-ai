
import { ESIEnvironments, ESILogger, ESIParameterStoreService } from "esi-common-layer";

/**
 * Represents a configuration class for loading environment variables and parameter store values.
 */
export class AppConfig {

    public logLevel: ESILogger.LogLevels;
    public esiEnvironment: ESIEnvironments;
    public esiOAuthParametersSecretName: string;
    private targetSystemUrl: string;
    private region: string;

    /**
     * Loads the configuration object with environment and parameter store values.
     * @returns The configuration object.
     */
    static async load() {

        const appConfig = new AppConfig();
        appConfig.logLevel = process.env.LOG_LEVEL as ESILogger.LogLevels || ESILogger.LogLevels.INFO;
        appConfig.esiEnvironment = process.env.ESI_ENVIRONMENT as ESIEnvironments || ESIEnvironments.DEV;
        appConfig.region = "us-east-2"//process.env.AWS_REGION;

        appConfig.esiOAuthParametersSecretName = 'esi/interface/edl/oauth';

        const parameterStore = new ESIParameterStoreService(appConfig.region, appConfig.logLevel);

        appConfig.targetSystemUrl = '/esi/interface/edl/compData_product/url';
        appConfig.targetSystemUrl = await parameterStore.getValue(appConfig.targetSystemUrl);
        appConfig.validate();
        return appConfig;
    }

    private validate() {

        if (!this.targetSystemUrl) {
            throw new Error(`Missing value of target system URL in parameter store, key: ${this.targetSystemUrl} `);
        }
    }

}