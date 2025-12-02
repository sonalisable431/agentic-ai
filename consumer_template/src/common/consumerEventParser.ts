import { SamsDocumentInfo } from "../common/samsDocumentInfo";

export class ConsumerEventParser {

  parse(event: any): SamsDocumentInfo {

    const path = event?.path;
    const docType = event?.headers?.["Content-Type"];
    const producerKey = event?.headers?.["Producer-Key"];
    const consumerKey = event?.headers?.["Consumer-Key"];
    const nativeBusinessId = event?.headers?.["Native-Business-Id"];
    const docKey = event?.headers?.["Document-Key"];
    const samsDocument = event?.body;

    const missingParams: string[] = [];

    if (!path) missingParams.push("path");

    if (!event.path.endsWith("/healthcheck")) {
      if (!docType) missingParams.push("Content-Type");
      if (!producerKey) missingParams.push("Producer-Key");
      if (!consumerKey) missingParams.push("Consumer-Key");
      if (!nativeBusinessId) missingParams.push("Native-Business-Id");
      if (!samsDocument) missingParams.push("body");
    }

    if (missingParams.length > 0) {
      const missingParamsString = missingParams.join(', ');
      throw new Error(`Missing parameters : ${missingParamsString}`);
    }

    return new SamsDocumentInfo(path, docType, producerKey, consumerKey, nativeBusinessId, docKey, samsDocument);
  }
}
