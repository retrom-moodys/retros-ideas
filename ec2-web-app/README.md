# EC2 Web App (Contact Form)

Full-stack contact form on EC2: static frontend, Flask API, PostgreSQL on RDS, email notifications, and domain routing through Route 53.

## Locked-down AWS account (no CLI, no IAM changes)

If you **cannot** use AWS CLI, attach IAM policies, or modify roles, use this path. Everything runs with **console-only** actions plus **SSH/SCP**.

| Need | Workaround |
|------|------------|
| Secrets (RDS, SMTP) | Copy `backend/.env` to EC2 via **SCP** (not SSM) |
| Email (SES) | **SES SMTP credentials** in `.env` — admin creates once in SES console |
| EC2 bootstrap | `deploy/user-data.sh` — clones repo, **no AWS CLI** |
| IAM instance role | **Not required** for SMTP email |

### Quick start (locked-down)

1. **Ask your admin** for:
   - RDS endpoint, database name, username, password
   - SES **SMTP credentials** (SES console → SMTP settings → Create SMTP credentials)
   - Verified `MAIL_FROM` / `MAIL_TO` addresses (if SES sandbox)
   - EC2 security group with ports **22**, **80** open
   - Route 53 A record → EC2 Elastic IP (if using a custom domain)

2. **On your laptop**, create `backend/.env` from `backend/env.example` (fill in DB + SMTP values).

3. **Launch EC2** (Amazon Linux 2023) via console:
   - Paste `deploy/user-data.sh` into **User data** (edit `GIT_REPO_URL` and `DOMAIN`)
   - Leave `DB_HOST` empty in user-data — secrets go via SCP instead
   - **No IAM instance profile required**

4. **Copy secrets and finish setup**:

```powershell
scp backend/.env ec2-user@YOUR_EC2_IP:/opt/ec2-web-app/backend/.env
ssh ec2-user@YOUR_EC2_IP "/opt/ec2-web-app/deploy/install.sh"
```

5. **Apply database schema** (from a machine that can reach RDS — your laptop with VPN, or EC2):

```bash
psql -h YOUR_RDS_ENDPOINT -U webapp_user -d webapp -f backend/schema.sql
```

6. Open `http://YOUR_EC2_IP` or your domain. Form saves to RDS; email sends via SMTP.

Set `EMAIL_TRANSPORT=none` in `.env` if email is not set up yet — the form still works.

---

## Architecture

```
User → Route 53 (yourdomain.com)
         ↓
       EC2 (Nginx + Flask/Gunicorn)
         ↓                    ↓
    Static site          POST /api/submissions
    (website/)                ↓
                         RDS PostgreSQL
                              ↓
                           SES email
```

## End-to-end flow

1. User opens your domain (Route 53 A record → EC2 public IP).
2. Nginx serves `website/index.html`.
3. User submits the form (Name, Email, Message).
4. Browser sends `POST /api/submissions` to the Flask backend.
5. Backend validates input, inserts a row into RDS, and sends an admin notification via SMTP (or SES API if configured).
6. The submissions table refreshes from `GET /api/submissions`.

## Project layout

```
ec2-web-app/
├── website/index.html          # Form + submissions table
├── backend/
│   ├── app.py                  # Flask API (RDS + SES)
│   ├── schema.sql              # PostgreSQL table
│   ├── requirements.txt
│   ├── env.example
│   └── iam-policy.json         # Optional — admin-only (SES API + SSM path)
├── nginx/ec2-web-app.conf      # Reverse proxy + static files
└── deploy/
    ├── user-data.sh            # EC2 User Data — no AWS CLI / no IAM (default)
    ├── user-data-ssm.sh        # Optional — requires IAM role + SSM (admin)
    ├── install.sh              # Bootstrap — also called by user-data.sh
    ├── ssm-env.example         # Template for SSM path only
    └── ec2-web-app.service     # systemd unit for Gunicorn
```

## API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/submissions` | List all submissions (newest first) |
| POST | `/api/submissions` | Create submission `{ name, email, message }` |

## AWS setup

### 1. RDS (PostgreSQL)

1. Create an RDS PostgreSQL instance (e.g. `db.t3.micro`).
2. Note the endpoint, port, master username, and password.
3. Create a database (e.g. `webapp`) and application user.
4. Security group: allow inbound **5432** from the EC2 security group only.
5. Run the schema:

```bash
psql -h YOUR_RDS_ENDPOINT -U webapp_user -d webapp -f backend/schema.sql
```

### 2. Email (SES SMTP — no IAM on EC2)

**Locked-down path (recommended):** use SES **SMTP**, not the SES API. Your admin creates SMTP credentials once in the SES console; you paste them into `backend/.env`. No IAM role on EC2, no boto3.

1. Admin verifies **From** and **To** addresses in SES (required in sandbox).
2. Admin opens SES → **SMTP settings** → **Create SMTP credentials**.
3. Put credentials in `.env`:

| Variable | Example |
|----------|---------|
| `EMAIL_TRANSPORT` | `smtp` |
| `SMTP_HOST` | `email-smtp.us-east-1.amazonaws.com` |
| `SMTP_USER` | (from SES SMTP credentials) |
| `SMTP_PASSWORD` | (from SES SMTP credentials) |
| `MAIL_FROM` | `notifications@yourdomain.com` |
| `MAIL_TO` | `admin@yourdomain.com` |

**Optional — SES API via boto3:** set `EMAIL_TRANSPORT=ses`, install `requirements-ses-api.txt`, and ask admin to attach `iam-policy.json` to the EC2 role. Most locked-down accounts should use SMTP instead.

### 3. EC2

#### Option A — User Data (no AWS CLI)

Use `deploy/user-data.sh` — clones the repo and runs `install.sh`. **No AWS CLI, SSM, or IAM role.**

1. Edit **CONFIG** in `deploy/user-data.sh` (`GIT_REPO_URL`, `DOMAIN`).
2. Leave `DB_HOST` empty; copy `.env` via SCP after launch (see locked-down quick start above).
3. Launch Amazon Linux 2023 with **User data** = contents of `user-data.sh`.
4. After boot:

```bash
sudo tail -f /var/log/ec2-web-app-user-data.log
```

#### Option B — User Data + SSM (admin only)

Use `deploy/user-data-ssm.sh` only if an admin created the SSM parameter and attached `iam-policy.json`.

#### Option C — Manual SSH install

1. Launch Amazon Linux 2023 (t3.micro or similar).
2. Security group inbound rules:
   - **80** from `0.0.0.0/0` (HTTP)
   - **443** from `0.0.0.0/0` (HTTPS, optional but recommended)
   - **22** from your IP (SSH)
3. Copy this project folder to `/opt/ec2-web-app` (no IAM profile needed):

```bash
sudo mkdir -p /opt/ec2-web-app
sudo chown ec2-user:ec2-user /opt/ec2-web-app
git clone YOUR_REPO_URL /tmp/retros-ideas
cp -r /tmp/retros-ideas/ec2-web-app/* /opt/ec2-web-app/
# or from your machine: scp -r ec2-web-app ec2-user@EC2_IP:/tmp/ && ssh ec2-user@EC2_IP 'cp -r /tmp/ec2-web-app/* /opt/ec2-web-app/'
```

5. Configure backend env:

```bash
cp /opt/ec2-web-app/backend/env.example /opt/ec2-web-app/backend/.env
nano /opt/ec2-web-app/backend/.env
```

6. Update `nginx/ec2-web-app.conf` with your domain, then run:

```bash
chmod +x /opt/ec2-web-app/deploy/install.sh
/opt/ec2-web-app/deploy/install.sh
```

7. Verify on the instance:

```bash
curl http://127.0.0.1/api/health
curl http://127.0.0.1/api/submissions
```

### 4. Route 53 (domain)

1. Register or transfer a domain in Route 53 (or use an existing hosted zone).
2. Create an **A record**:
   - Name: `yourdomain.com` (and optionally `www`)
   - Value: EC2 **Elastic IP** (recommended so the IP survives restarts)
3. Update `server_name` in `nginx/ec2-web-app.conf` to match your domain.
4. Reload Nginx: `sudo systemctl reload nginx`.

Optional: add HTTPS with [Let's Encrypt](https://certbot.eff.org/) (`certbot --nginx`).

## Local development

Run PostgreSQL locally (or point at RDS), then:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy env.example .env
# edit .env with DB + SES values
python app.py
```

Serve the frontend separately (e.g. VS Code Live Server) and set `API_BASE_URL` in `website/index.html` to `http://127.0.0.1:8000`, or proxy through Nginx locally.

## Troubleshooting

| Symptom | Check |
|---------|--------|
| 502 on `/api/*` | `sudo systemctl status ec2-web-app` and `/opt/ec2-web-app/backend/.env` |
| Database connection error | RDS security group, credentials, and that `schema.sql` was applied |
| Email not sent | SMTP credentials, SES sandbox, verified addresses, `EMAIL_TRANSPORT` |
| Domain not resolving | Route 53 A record, Elastic IP association, Nginx `server_name` |
| User data failed | `sudo cat /var/log/ec2-web-app-user-data.log`, git clone URL, then SCP `.env` |

View backend logs:

```bash
sudo journalctl -u ec2-web-app -f
```
