
import { SamsDocumentInfo } from "../common/samsDocumentInfo";
import { ConsumerEventParser } from "./consumerEventParser";
import { ConsumerProcessor } from '../common/consumerProcessor';

export abstract class ConsumerProcessorBuilderBase {

    public interfaceKey: string;
    public docEvent: SamsDocumentInfo;
    public pfxKey: string;
    public logLevel: string;
    public consumerProcessor: ConsumerProcessor;

    constructor(event: any, config: any) {

        // Extract useful info out of event object
        this.docEvent = new ConsumerEventParser().parse(event);
        this.interfaceKey = this.docEvent.consumerKey;
        this.logLevel = config.logLevel;
        this.consumerProcessor = new ConsumerProcessor();
    }

    abstract build(): Promise<any>;
}
