
export class SamsDocumentInfo {

    path: string;
    docType: string;
    producerKey: string;
    consumerKey: string;
    nativeBusinessId: string;
    samsDocument: any
    docKey: string

    constructor(path: string, docType: string, producerKey: string, consumerKey: string,
        nativeBusinessId: string, docKey: string, samsDocument: any) {

        this.path = path;
        this.docType = docType;
        this.producerKey = producerKey;
        this.consumerKey = consumerKey;
        this.nativeBusinessId = nativeBusinessId;
        this.samsDocument = samsDocument;
        this.docKey = docKey;
    }
}  