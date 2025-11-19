from lambda_agent import generate_lambda_project

if __name__ == "__main__":
    lambda_name = "sample-transform-lambda"

    input_schema = {
        "type": "object",
        "properties": {
            "eventId": {"type": "string"},
            "customer": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "fullName": {"type": "string"},
                    "email": {"type": "string"},
                },
            },
            "transaction": {
                "type": "object",
                "properties": {
                    "amount": {"type": "number"},
                    "currency": {"type": "string"},
                    "timestamp": {"type": "string"},
                },
            },
            "meta": {
                "type": "object",
                "properties": {
                    "source": {"type": "string"},
                },
            },
        },
    }

    output_schema = {
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "userId": {"type": "string"},
            "name": {"type": "string"},
            "emailAddress": {"type": "string"},
            "amountPaid": {"type": "number"},
            "ccy": {"type": "string"},
            "paymentTime": {"type": "string"},
            "processedBy": {"type": "string"},
        },
    }

    required_fields = [
        "eventId",
        "customer.id",
        "transaction.amount",
        "transaction.currency",
    ]

    field_mapping = {
        "id": "eventId",
        "userId": "customer.id",
        "name": "customer.fullName",
        "emailAddress": "customer.email",
        "amountPaid": "transaction.amount",
        "ccy": "transaction.currency",
        "paymentTime": "transaction.timestamp",
        "processedBy": "meta.source",
    }

    generate_lambda_project(
        lambda_name=lambda_name,
        input_schema=input_schema,
        output_schema=output_schema,
        required_fields=required_fields,
        field_mapping=field_mapping,
        base_dir=".",
    )
