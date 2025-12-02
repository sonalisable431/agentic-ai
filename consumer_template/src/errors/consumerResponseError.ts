export class ConsumerResponseError extends Error {
  public body: any = {};
  public message: string;
  public status: 500;
  public constructor(message: string, esiResponse: any) {
    super(message);
    this.message = message;
    this.body = esiResponse;
  }
}
