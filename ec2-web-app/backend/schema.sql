-- Reference schema for the local SQLite database.
-- The app creates this automatically on startup; you do not need to run this manually.

CREATE TABLE IF NOT EXISTS submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    message TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_submissions_created_at ON submissions (created_at DESC);

-- Database file (default): /opt/ec2-web-app/data/submissions.db
