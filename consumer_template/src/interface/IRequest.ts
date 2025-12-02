import { ResponseSummary } from "../model/ResponseSummary";
import { SamsDocumentInfo } from "../common/samsDocumentInfo";

export interface IRequest {
    post(docEvent: SamsDocumentInfo): Promise<ResponseSummary>;
}