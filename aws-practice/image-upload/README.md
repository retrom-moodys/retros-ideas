# Image Upload (AWS)

Static website uploads images through API Gateway. Lambda stores files in S3, a second Lambda writes metadata to DynamoDB, and the gallery lists images with presigned URLs.

## Architecture

```
Browser (S3 website)
  → API Gateway
  → upload_api Lambda (POST /upload, GET /images)
  → S3 image bucket
  → metadata_processor Lambda (S3 event)
  → DynamoDB ImageMetadata
```

## Project layout

```
image-upload/
├── website/index.html          # Static gallery UI
└── lambda/
    ├── upload_api/
    │   ├── upload_api.py       # Upload + list API
    │   ├── iam-policy.json
    │   ├── env.example
    │   └── package.ps1         # Builds upload_api.zip
    └── metadata_processor/
        ├── metadata_processor.py
        ├── iam-policy.json
        ├── env.example
        └── package.ps1         # Builds metadata_processor.zip
```

## DynamoDB table

- Table name: `ImageMetadata`
- Partition key: `imageID` (String) — case-sensitive

## Lambda environment variables

**upload_api**

| Variable | Example |
|----------|---------|
| `UPLOAD_BUCKET` | `image-storage-932930471443-us-east-1-an` |
| `TABLE_NAME` | `ImageMetadata` |
| `URL_EXPIRES` | `3600` |

**metadata_processor**

| Variable | Example |
|----------|---------|
| `TABLE_NAME` | `ImageMetadata` |

## Deploy Lambdas

From each lambda folder:

```powershell
.\package.ps1
```

Upload the generated `.zip` to the matching Lambda function. Handlers:

- `upload_api.lambda_handler`
- `metadata_processor.lambda_handler`

Attach the inline IAM policies in each folder’s `iam-policy.json`.

## S3 trigger

On the **image storage** bucket, add an event notification:

- Event: object create
- Prefix: `uploads/`
- Destination: metadata_processor Lambda

## Website

Host `website/index.html` on an S3 static website bucket. Set the API Gateway invoke URL in `index.html` (`API_BASE_URL` constant).
