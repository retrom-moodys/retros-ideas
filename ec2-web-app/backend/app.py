"""Contact form API: store submissions in RDS and notify via SES."""

import os
import re
from datetime import datetime, timezone

import boto3
import psycopg2
from flask import Flask, jsonify, request
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def get_db_config():
    return {
        "host": os.environ["DB_HOST"],
        "port": int(os.environ.get("DB_PORT", "5432")),
        "dbname": os.environ["DB_NAME"],
        "user": os.environ["DB_USER"],
        "password": os.environ["DB_PASSWORD"],
    }


def get_db_connection():
    return psycopg2.connect(**get_db_config(), cursor_factory=RealDictCursor)


def cors_origins():
    raw = os.environ.get("CORS_ORIGINS", "").strip()
    if not raw:
        return []
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


def apply_cors(response):
    origins = cors_origins()
    origin = request.headers.get("Origin")
    if origin and (not origins or origin in origins):
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Vary"] = "Origin"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


@app.after_request
def after_request(response):
    return apply_cors(response)


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/api/submissions", methods=["OPTIONS"])
def submissions_options():
    return ("", 204)


@app.route("/api/submissions", methods=["GET"])
def list_submissions():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, name, email, message, created_at
                    FROM submissions
                    ORDER BY created_at DESC
                    """
                )
                rows = cur.fetchall()
    except psycopg2.Error as exc:
        app.logger.exception("Failed to list submissions")
        return jsonify({"error": "Database error", "detail": str(exc)}), 500

    submissions = []
    for row in rows:
        created_at = row["created_at"]
        if isinstance(created_at, datetime):
            created_at = created_at.astimezone(timezone.utc).isoformat()
        submissions.append(
            {
                "id": row["id"],
                "name": row["name"],
                "email": row["email"],
                "message": row["message"],
                "created_at": created_at,
            }
        )

    return jsonify({"submissions": submissions})


@app.route("/api/submissions", methods=["POST"])
def create_submission():
    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "").strip()
    email = (payload.get("email") or "").strip()
    message = (payload.get("message") or "").strip()

    errors = {}
    if not name:
        errors["name"] = "Name is required."
    if not email:
        errors["email"] = "Email is required."
    elif not EMAIL_PATTERN.match(email):
        errors["email"] = "Enter a valid email address."
    if not message:
        errors["message"] = "Message is required."

    if errors:
        return jsonify({"error": "Validation failed", "fields": errors}), 400

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO submissions (name, email, message)
                    VALUES (%s, %s, %s)
                    RETURNING id, name, email, message, created_at
                    """,
                    (name, email, message),
                )
                row = cur.fetchone()
            conn.commit()
    except psycopg2.Error as exc:
        app.logger.exception("Failed to create submission")
        return jsonify({"error": "Database error", "detail": str(exc)}), 500

    try:
        send_notification_email(name, email, message, row["id"])
    except Exception:
        app.logger.exception("SES notification failed for submission %s", row["id"])

    created_at = row["created_at"]
    if isinstance(created_at, datetime):
        created_at = created_at.astimezone(timezone.utc).isoformat()

    return (
        jsonify(
            {
                "submission": {
                    "id": row["id"],
                    "name": row["name"],
                    "email": row["email"],
                    "message": row["message"],
                    "created_at": created_at,
                }
            }
        ),
        201,
    )


def send_notification_email(name, email, message, submission_id):
    from_email = os.environ["SES_FROM_EMAIL"]
    to_email = os.environ["SES_TO_EMAIL"]
    region = os.environ.get("AWS_REGION", "us-east-1")

    subject = f"New contact form submission #{submission_id}"
    body_text = (
        f"A new message was submitted via the contact form.\n\n"
        f"Submission ID: {submission_id}\n"
        f"Name: {name}\n"
        f"Email: {email}\n\n"
        f"Message:\n{message}\n"
    )
    body_html = f"""
    <html>
      <body>
        <h2>New contact form submission</h2>
        <p><strong>Submission ID:</strong> {submission_id}</p>
        <p><strong>Name:</strong> {name}</p>
        <p><strong>Email:</strong> {email}</p>
        <p><strong>Message:</strong></p>
        <p>{message.replace(chr(10), "<br>")}</p>
      </body>
    </html>
    """

    ses = boto3.client("ses", region_name=region)
    ses.send_email(
        Source=from_email,
        Destination={"ToAddresses": [to_email]},
        Message={
            "Subject": {"Data": subject, "Charset": "UTF-8"},
            "Body": {
                "Text": {"Data": body_text, "Charset": "UTF-8"},
                "Html": {"Data": body_html, "Charset": "UTF-8"},
            },
        },
        ReplyToAddresses=[email],
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
