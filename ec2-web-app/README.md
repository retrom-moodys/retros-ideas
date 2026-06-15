# EC2 Web App (Contact Form)

Full-stack contact form on a single EC2 instance: Nginx frontend, Flask API, **local SQLite database**, and optional SMTP email. No RDS, no IAM, no AWS CLI required.

## Locked-down AWS account

Works when you **cannot** create RDS, use AWS CLI, or modify IAM roles.

| Component | Solution |
|-----------|----------|
| Database | **SQLite file** on EC2 (`/opt/ec2-web-app/data/submissions.db`) |
| Email | **Optional** SES SMTP credentials in `.env` |
| Secrets | `.env` via user-data CONFIG or **SCP** |
| Bootstrap | `deploy/user-data.sh` — clone + install, no AWS API calls |

### Quick start

1. **Launch EC2** (Amazon Linux 2023) via console:
   - Security group: **22**, **80**
   - Paste `deploy/user-data.sh` into **User data** (edit `GIT_REPO_URL`, `DOMAIN`)
   - No IAM instance profile needed

2. **Wait for bootstrap**, then verify:

```bash
ssh ec2-user@YOUR_EC2_IP
curl http://127.0.0.1/api/health
```

3. Open `http://YOUR_EC2_IP` — submit the form. Data is stored locally on the instance.

4. **Optional — enable email** (ask admin for SES SMTP credentials):

```powershell
# Edit backend/.env locally, set EMAIL_TRANSPORT=smtp and SMTP_* values, then:
scp backend/.env ec2-user@YOUR_EC2_IP:/opt/ec2-web-app/backend/.env
ssh ec2-user@YOUR_EC2_IP "sudo systemctl restart ec2-web-app"
```

Set `EMAIL_TRANSPORT=none` to skip email entirely.

---

## Architecture

```
User → Route 53 (optional) → EC2
                              ├── Nginx (static frontend)
                              ├── Flask API (Gunicorn)
                              ├── SQLite (/opt/ec2-web-app/data/submissions.db)
                              └── SMTP email (optional)
```

## End-to-end flow

1. User opens your domain or EC2 public IP.
2. Nginx serves `website/index.html`.
3. User submits the form (Name, Email, Message).
4. Browser sends `POST /api/submissions` to the Flask backend.
5. Backend saves the row to **local SQLite** and optionally sends email via SMTP.
6. The submissions table refreshes from `GET /api/submissions`.

## Project layout

```
ec2-web-app/
├── website/index.html          # Form + submissions table
├── backend/
│   ├── app.py                  # Flask API (SQLite + optional email)
│   ├── schema.sql              # SQLite schema reference (auto-applied by app)
│   ├── requirements.txt
│   ├── env.example
│   └── iam-policy.json         # Optional — admin-only (SES API path)
├── nginx/ec2-web-app.conf      # Reverse proxy + static files
└── deploy/
    ├── user-data.sh            # EC2 User Data (default)
    ├── user-data-ssm.sh        # Optional — admin-only SSM path
    ├── install.sh              # Bootstrap script
    ├── ssm-env.example
    └── ec2-web-app.service     # systemd unit for Gunicorn
```

## API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check (includes database status) |
| GET | `/api/submissions` | List all submissions (newest first) |
| POST | `/api/submissions` | Create submission `{ name, email, message }` |

## Configuration

Copy `backend/env.example` to `backend/.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_PATH` | `/opt/ec2-web-app/data/submissions.db` | SQLite database file |
| `EMAIL_TRANSPORT` | `none` | `none`, `smtp`, or `ses` |
| `SMTP_*` | — | Required when `EMAIL_TRANSPORT=smtp` |

The database and tables are **created automatically** on first API request. No manual schema step.

### Backup

The SQLite file lives on the EC2 instance. Back it up periodically:

```bash
scp ec2-user@YOUR_EC2_IP:/opt/ec2-web-app/data/submissions.db ./submissions-backup.db
```

Or use EBS snapshots of the instance volume.

## AWS setup

### 1. EC2

#### Option A — User Data (recommended)

1. Edit **CONFIG** in `deploy/user-data.sh` (`GIT_REPO_URL`, `DOMAIN`).
2. Launch Amazon Linux 2023 with **User data** = contents of `user-data.sh`.
3. Check logs: `sudo tail -f /var/log/ec2-web-app-user-data.log`

#### Option B — Manual SSH install

```bash
sudo mkdir -p /opt/ec2-web-app
sudo chown ec2-user:ec2-user /opt/ec2-web-app
git clone YOUR_REPO_URL /tmp/retros-ideas
cp -r /tmp/retros-ideas/ec2-web-app/* /opt/ec2-web-app/
cp /opt/ec2-web-app/backend/env.example /opt/ec2-web-app/backend/.env
chmod +x /opt/ec2-web-app/deploy/install.sh
/opt/ec2-web-app/deploy/install.sh
```

### 2. Email (optional, SES SMTP)

1. Admin verifies **From** and **To** addresses in SES.
2. Admin creates **SMTP credentials** in SES console.
3. Set in `.env`:

| Variable | Example |
|----------|---------|
| `EMAIL_TRANSPORT` | `smtp` |
| `SMTP_HOST` | `email-smtp.us-east-1.amazonaws.com` |
| `SMTP_USER` | (from SES SMTP credentials) |
| `SMTP_PASSWORD` | (from SES SMTP credentials) |
| `MAIL_FROM` | `notifications@yourdomain.com` |
| `MAIL_TO` | `admin@yourdomain.com` |

Restart: `sudo systemctl restart ec2-web-app`

### 3. Route 53 (optional domain)

1. Create an **A record** pointing to the EC2 Elastic IP.
2. Update `server_name` in `nginx/ec2-web-app.conf`.
3. Reload: `sudo systemctl reload nginx`

## Local development

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy env.example .env
python app.py
```

SQLite file defaults to `backend/data/submissions.db` on Windows. Set `API_BASE_URL` in `website/index.html` to `http://127.0.0.1:8000` for local frontend testing.

## Troubleshooting

| Symptom | Check |
|---------|--------|
| 502 on `/api/*` | `sudo systemctl status ec2-web-app`, `sudo journalctl -u ec2-web-app -f` |
| Database error | `ls -la /opt/ec2-web-app/data/`, permissions (owned by `ec2-user`) |
| Email not sent | `EMAIL_TRANSPORT`, SMTP credentials, SES sandbox |
| User data failed | `sudo cat /var/log/ec2-web-app-user-data.log`, git clone URL |

View backend logs:

```bash
sudo journalctl -u ec2-web-app -f
```
