export class HealthCheckResource {
   name: string;
   type: string;
   isOk: boolean;
   error: string = null;
   details?: any;
}

export interface SummaryResource {
   status: string,
   checkTime: Date;
   resources: any;
}