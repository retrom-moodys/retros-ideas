import base64
import json
import os
import traceback
import uuid
from decimal import Decimal

import boto3
from botocore.exceptions import ClientError

s3_client = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
}


def get_config():
    missing = [name for name in ("UPLOAD_BUCKET", "TABLE_NAME") if not os.environ.get(name)]
    if missing:
        raise RuntimeError(f"Missing Lambda environment variables: {', '.join(missing)}")

    return {
        "upload_bucket": os.environ["UPLOAD_BUCKET"],
        "table_name": os.environ["TABLE_NAME"],
        "url_expires": int(os.environ.get("URL_EXPIRES", "3600")),
    }


def lambda_handler(event, _context):
    try:
        method = (
            event.get("requestContext", {}).get("http", {}).get("method")
            or event.get("httpMethod")
            or "GET"
        )
        path = event.get("rawPath") or event.get("path") or "/"
        route_key = event.get("routeKey", "")

        if method == "OPTIONS":
            return response(200, {"message": "ok"})

        if method == "POST" and matches_route(path, route_key, "/upload"):
            return handle_upload(event)

        if method == "GET" and matches_route(path, route_key, "/images"):
            return handle_list_images()

        return response(404, {"error": f"Not found: {method} {path}"})
    except Exception as exc:
        print(traceback.format_exc())
        return response(500, {"error": str(exc)})


def matches_route(path, route_key, suffix):
    return path.endswith(suffix) or route_key.endswith(suffix)


def handle_upload(event):
    config = get_config()
    body = parse_body(event)
    filename = body.get("filename")
    content_type = body.get("contentType", "application/octet-stream")
    image_data = body.get("data")

    if not filename:
        return response(400, {"error": "filename is required"})
    if not image_data:
        return response(400, {"error": "data is required (base64-encoded image bytes)"})

    try:
        image_bytes = base64.b64decode(image_data)
    except (ValueError, TypeError):
        return response(400, {"error": "data must be valid base64"})

    if not image_bytes:
        return response(400, {"error": "image data is empty"})

    key = f"uploads/{uuid.uuid4()}/{sanitize_filename(filename)}"

    try:
        s3_client.put_object(
            Bucket=config["upload_bucket"],
            Key=key,
            Body=image_bytes,
            ContentType=content_type,
            Metadata={
                "original-filename": filename,
            },
        )
    except ClientError as exc:
        return response(500, {"error": f"S3 upload failed: {exc.response['Error']['Message']}"})

    return response(
        200,
        {
            "key": key,
            "filename": filename,
            "contentType": content_type,
            "size": len(image_bytes),
            "message": "Upload complete. Metadata will be available shortly.",
        },
    )


def handle_list_images():
    config = get_config()
    table = dynamodb.Table(config["table_name"])

    try:
        items = scan_all_items(table)
    except ClientError as exc:
        return response(500, {"error": f"DynamoDB read failed: {exc.response['Error']['Message']}"})

    images = []
    for item in items:
        bucket = item.get("bucket", config["upload_bucket"])
        key = item.get("imageID") or item.get("imageId")
        if not key:
            continue

        try:
            url = s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket, "Key": key},
                ExpiresIn=config["url_expires"],
            )
        except ClientError:
            url = ""

        images.append(
            {
                "imageId": key,
                "filename": item.get("filename", key.split("/")[-1]),
                "contentType": item.get("contentType"),
                "size": item.get("size"),
                "uploadedAt": item.get("uploadedAt"),
                "url": url,
            }
        )

    images.sort(key=lambda image: image.get("uploadedAt") or "", reverse=True)
    return response(200, {"images": images})


def scan_all_items(table):
    items = []
    scan_kwargs = {}

    while True:
        result = table.scan(**scan_kwargs)
        items.extend(result.get("Items", []))

        last_key = result.get("LastEvaluatedKey")
        if not last_key:
            break
        scan_kwargs["ExclusiveStartKey"] = last_key

    return items


def parse_body(event):
    body = event.get("body")
    if not body:
        return {}

    if event.get("isBase64Encoded"):
        body = base64.b64decode(body).decode("utf-8")

    if isinstance(body, str):
        return json.loads(body)

    return body


def sanitize_filename(filename):
    safe_name = os.path.basename(filename).replace("\\", "_").replace("/", "_")
    return safe_name or "image"


def to_json_safe(value):
    if isinstance(value, Decimal):
        return int(value) if value % 1 == 0 else float(value)
    if isinstance(value, dict):
        return {key: to_json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [to_json_safe(item) for item in value]
    return value


def response(status_code, payload):
    return {
        "statusCode": status_code,
        "headers": {
            **CORS_HEADERS,
            "Content-Type": "application/json",
        },
        "body": json.dumps(to_json_safe(payload)),
    }
