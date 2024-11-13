import os
import boto3
from botocore.exceptions import ClientError

# Set dummy AWS credentials
os.environ["AWS_ACCESS_KEY_ID"] = "dummy"
os.environ["AWS_SECRET_ACCESS_KEY"] = "dummy"
os.environ["AWS_SESSION_TOKEN"] = "dummy"

dynamodb = boto3.resource(
    "dynamodb", region_name="ap-south-1", endpoint_url="http://localhost:4566"
)

table_schemas = {
    "users": {
        "KeySchema": [{"AttributeName": "user_id", "KeyType": "HASH"}],
        "AttributeDefinitions": [
            {"AttributeName": "user_id", "AttributeType": "S"}
        ],
        "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5}
    },
    "emails": {
        "KeySchema": [{"AttributeName": "message_id", "KeyType": "HASH"}],
        "AttributeDefinitions": [
            {"AttributeName": "message_id", "AttributeType": "S"}
        ],
        "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5}
    },
    "tracking": {
        "KeySchema": [{"AttributeName": "tracking_id", "KeyType": "HASH"}],
        "AttributeDefinitions": [
            {"AttributeName": "tracking_id", "AttributeType": "S"}
        ],
        "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5}
    }
}

for table_name, schema in table_schemas.items():
    try:
        table = dynamodb.Table(table_name)
        table.load()
        print(f"Table {table_name} already exists.")
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            # Table does not exist, create it
            table = dynamodb.create_table(
                TableName=table_name,
                KeySchema=schema["KeySchema"],
                AttributeDefinitions=schema["AttributeDefinitions"],
                ProvisionedThroughput=schema["ProvisionedThroughput"]
            )
            table.meta.client.get_waiter("table_exists").wait(TableName=table_name)
            print(f"Table {table_name} created successfully.")
        else:
            # Handle other potential exceptions
            print(f"Unexpected error: {e}")
