export class WebApiResponse {
  statusCode: number;
  body: any;
  wasSuccessful: boolean;
  constructor(statusCode: number, body: any) {
    this.statusCode = statusCode;
    this.body = body;
    this.wasSuccessful = statusCode < 207;
  }

}
