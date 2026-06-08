# EC2 Web App (Contact Form)

Full-stack contact form on EC2: static frontend, Flask API, PostgreSQL on RDS, email notifications via SES, and domain routing through Route 53.

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
5. Backend validates input, inserts a row into RDS, and sends an admin notification via SES.
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
│   └── iam-policy.json         # EC2 instance role for SES
├── nginx/ec2-web-app.conf      # Reverse proxy + static files
└── deploy/
    ├── install.sh              # EC2 bootstrap script
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

### 2. SES (email)

1. Verify the **From** address (or domain) in SES.
2. Verify the **To** (admin) address if your account is still in the SES sandbox.
3. Request production access when ready to email unverified recipients.
4. Attach `backend/iam-policy.json` to the EC2 instance IAM role so the app can call `ses:SendEmail`.

Environment variables (see `backend/env.example`):

| Variable | Example |
|----------|---------|
| `SES_FROM_EMAIL` | `notifications@yourdomain.com` |
| `SES_TO_EMAIL` | `admin@yourdomain.com` |
| `AWS_REGION` | `us-east-1` |

### 3. EC2

1. Launch Amazon Linux 2023 (t3.micro or similar).
2. Security group inbound rules:
   - **80** from `0.0.0.0/0` (HTTP)
   - **443** from `0.0.0.0/0` (HTTPS, optional but recommended)
   - **22** from your IP (SSH)
3. Attach an IAM instance profile with SES permissions (`iam-policy.json`).
4. Copy this project folder to `/opt/ec2-web-app`:

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
| Email not sent | SES sandbox limits, verified identities, EC2 IAM role, CloudWatch/app logs |
| Domain not resolving | Route 53 A record, Elastic IP association, Nginx `server_name` |

View backend logs:

```bash
sudo journalctl -u ec2-web-app -f
```
