import os
from datetime import datetime, timezone
from urllib.parse import unquote_plus

import boto3
from botocore.exceptions import ClientError

s3_client = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")


def get_table_name():
    table_name = os.environ.get("TABLE_NAME")
    if not table_name:
        raise RuntimeError("Missing Lambda environment variable: TABLE_NAME")
    return table_name


def lambda_handler(event, _context):
    table = dynamodb.Table(get_table_name())

    for record in event.get("Records", []):
        bucket = record["s3"]["bucket"]["name"]
        key = unquote_plus(record["s3"]["object"]["key"])

        if key.endswith("/"):
            continue

        try:
            head = s3_client.head_object(Bucket=bucket, Key=key)
        except ClientError as exc:
            print(f"head_object failed for s3://{bucket}/{key}: {exc}")
            continue

        metadata = head.get("Metadata", {})
        filename = metadata.get("original-filename") or key.split("/")[-1]
        uploaded_at = head.get("LastModified")
        if uploaded_at:
            uploaded_at = uploaded_at.astimezone(timezone.utc).isoformat()
        else:
            uploaded_at = datetime.now(timezone.utc).isoformat()

        item = {
            "imageID": key,
            "bucket": bucket,
            "filename": filename,
            "contentType": head.get("ContentType", "application/octet-stream"),
            "size": int(head.get("ContentLength", 0)),
            "uploadedAt": uploaded_at,
        }

        try:
            table.put_item(Item=item)
        except ClientError as exc:
            print(f"DynamoDB put_item failed for {key}: {exc}")
            raise

    return {"statusCode": 200, "body": "Processing complete"}
