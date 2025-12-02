import { HealthCheckResource, SummaryResource } from "../model/healthCheckResource";

export class HealthCheckMaster {

    resources: HealthCheckResource[] = [];

    AddResource(resource: HealthCheckResource) {
        this.resources.push(resource);
    }

    getHealthStatus(): boolean {
        let result = this.resources.every(key => key.isOk === true);
        return result;
    }

    cleanUpResourceResponse() {
        this.resources.forEach(function (item: any) {
            item['status'] = item.isOk ? 'ok' : 'error';
            delete item.isOk;
            if (item.error == null)
                delete item.error;
        });
    }

    // generic code for all lambdas
    getSummary(): SummaryResource {
        let isHealthy = this.getHealthStatus();
        this.cleanUpResourceResponse();
        const summaryObject: SummaryResource = {
            status: isHealthy ? "ok" : "error",
            checkTime: new Date(),
            resources: this.resources
        };
        return summaryObject;
    };

    static isHealthCheck(event: any): boolean {
        return event.path ? event.path.endsWith("/healthcheck") : false;
    };
}