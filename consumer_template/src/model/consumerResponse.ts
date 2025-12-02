export class ConsumerResponse {

  static getResponse(statusCode: number, body: any) {
    return {
      statusCode: statusCode,
      body: body,
      headers: { "content-type": "application/json" }
    }
  }
}
