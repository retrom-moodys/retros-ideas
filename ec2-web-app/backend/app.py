"""Contact form API: store submissions in local SQLite and notify via email."""

import os
import re
import smtplib
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from flask import Flask, jsonify, request

app = Flask(__name__)

EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
DEFAULT_DB_PATH = "/opt/ec2-web-app/data/submissions.db"
SCHEMA_VERSION = 1


def get_db_path():
    if path := os.environ.get("DB_PATH", "").strip():
        return path
    if os.name == "nt":
        return str(Path(__file__).resolve().parent / "data" / "submissions.db")
    return DEFAULT_DB_PATH


def init_db(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )
    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_submissions_created_at
        ON submissions (created_at DESC)
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_meta (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        INSERT OR IGNORE INTO schema_meta (key, value)
        VALUES ('version', ?)
        """,
        (str(SCHEMA_VERSION),),
    )


@contextmanager
def get_db_connection():
    db_path = Path(get_db_path())
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        init_db(conn)
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


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


def mail_from_address():
    return os.environ.get("MAIL_FROM") or os.environ.get("SES_FROM_EMAIL", "")


def mail_to_address():
    return os.environ.get("MAIL_TO") or os.environ.get("SES_TO_EMAIL", "")


def email_transport():
    return os.environ.get("EMAIL_TRANSPORT", "none").strip().lower()


def email_is_configured():
    transport = email_transport()
    if transport in ("", "none", "off", "disabled"):
        return False
    if transport == "smtp":
        has_named = all(
            os.environ.get(key)
            for key in ("SMTP_HOST", "SMTP_USER", "SMTP_PASSWORD", "MAIL_FROM", "MAIL_TO")
        )
        has_legacy = all(
            os.environ.get(key)
            for key in ("SMTP_HOST", "SMTP_USER", "SMTP_PASSWORD", "SES_FROM_EMAIL", "SES_TO_EMAIL")
        )
        return has_named or has_legacy
    if transport == "ses":
        return all(os.environ.get(key) for key in ("SES_FROM_EMAIL", "SES_TO_EMAIL"))
    return False


def format_created_at(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat()
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return parsed.astimezone(timezone.utc).isoformat()
    except ValueError:
        return str(value)


def row_to_submission(row):
    return {
        "id": row["id"],
        "name": row["name"],
        "email": row["email"],
        "message": row["message"],
        "created_at": format_created_at(row["created_at"]),
    }


def build_email_content(name, email, message, submission_id):
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
    return subject, body_text, body_html


@app.after_request
def after_request(response):
    return apply_cors(response)


@app.route("/api/health", methods=["GET"])
def health():
    try:
        with get_db_connection() as conn:
            conn.execute("SELECT 1")
        db_status = "ok"
    except sqlite3.Error:
        app.logger.exception("Database health check failed")
        db_status = "error"

    return jsonify(
        {
            "status": "ok" if db_status == "ok" else "degraded",
            "database": db_status,
            "db_path": get_db_path(),
            "email_configured": email_is_configured(),
        }
    )


@app.route("/api/submissions", methods=["OPTIONS"])
def submissions_options():
    return ("", 204)


@app.route("/api/submissions", methods=["GET"])
def list_submissions():
    try:
        with get_db_connection() as conn:
            rows = conn.execute(
                """
                SELECT id, name, email, message, created_at
                FROM submissions
                ORDER BY created_at DESC
                """
            ).fetchall()
    except sqlite3.Error as exc:
        app.logger.exception("Failed to list submissions")
        return jsonify({"error": "Database error", "detail": str(exc)}), 500

    return jsonify({"submissions": [row_to_submission(row) for row in rows]})


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
            cursor = conn.execute(
                """
                INSERT INTO submissions (name, email, message)
                VALUES (?, ?, ?)
                """,
                (name, email, message),
            )
            row = conn.execute(
                """
                SELECT id, name, email, message, created_at
                FROM submissions
                WHERE id = ?
                """,
                (cursor.lastrowid,),
            ).fetchone()
    except sqlite3.Error as exc:
        app.logger.exception("Failed to create submission")
        return jsonify({"error": "Database error", "detail": str(exc)}), 500

    if email_is_configured():
        try:
            send_notification_email(name, email, message, row["id"])
        except Exception:
            app.logger.exception(
                "Email notification failed for submission %s", row["id"]
            )

    return jsonify({"submission": row_to_submission(row)}), 201


def send_notification_email(name, email, message, submission_id):
    transport = email_transport()
    subject, body_text, body_html = build_email_content(
        name, email, message, submission_id
    )

    if transport == "smtp":
        send_via_smtp(subject, body_text, body_html, email)
        return

    if transport == "ses":
        send_via_ses_api(subject, body_text, body_html, email)
        return

    app.logger.info("EMAIL_TRANSPORT=%s; skipping notification", transport)


def send_via_smtp(subject, body_text, body_html, reply_to):
    from_email = mail_from_address()
    to_email = mail_to_address()
    host = os.environ["SMTP_HOST"]
    port = int(os.environ.get("SMTP_PORT", "587"))
    username = os.environ["SMTP_USER"]
    password = os.environ["SMTP_PASSWORD"]
    use_tls = os.environ.get("SMTP_USE_TLS", "true").lower() in ("1", "true", "yes")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Reply-To"] = reply_to
    msg.attach(MIMEText(body_text, "plain", "utf-8"))
    msg.attach(MIMEText(body_html, "html", "utf-8"))

    with smtplib.SMTP(host, port, timeout=30) as client:
        if use_tls:
            client.starttls()
        client.login(username, password)
        client.sendmail(from_email, [to_email], msg.as_string())


def send_via_ses_api(subject, body_text, body_html, reply_to):
    import boto3

    from_email = mail_from_address()
    to_email = mail_to_address()
    region = os.environ.get("AWS_REGION", "us-east-1")

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
        ReplyToAddresses=[reply_to],
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
