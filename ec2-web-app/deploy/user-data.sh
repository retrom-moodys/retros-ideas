#!/bin/bash
# EC2 User Data — NO AWS CLI, NO SSM, NO IAM role required.
# Paste into Launch instance → Advanced details → User data (Amazon Linux 2023).
#
# Secrets workflow (pick one):
#   A) Leave DB_HOST empty → clone + install only → copy .env via SCP after launch (recommended)
#   B) Fill in CONFIG below → .env written at boot (visible in EC2 console user-data)

set -euo pipefail

LOG="/var/log/ec2-web-app-user-data.log"
MARKER="/var/lib/ec2-web-app/bootstrap-complete"
APP_ROOT="/opt/ec2-web-app"

exec > >(tee -a "$LOG") 2>&1
echo "==> EC2 user-data started at $(date -Is)"

if [ -f "$MARKER" ]; then
  echo "==> Bootstrap already completed; skipping."
  exit 0
fi

# ── CONFIG ───────────────────────────────────────────────────────────────────
GIT_REPO_URL="https://github.com/YOUR_USER/retros-ideas.git"
GIT_BRANCH="main"
APP_SUBPATH="ec2-web-app"
DOMAIN="yourdomain.com"

# Leave DB_HOST empty to copy backend/.env via SCP after launch (recommended).
DB_HOST=""
DB_PORT="5432"
DB_NAME="webapp"
DB_USER="webapp_user"
DB_PASSWORD=""
EMAIL_TRANSPORT="smtp"
SMTP_HOST="email-smtp.us-east-1.amazonaws.com"
SMTP_PORT="587"
SMTP_USER=""
SMTP_PASSWORD=""
MAIL_FROM=""
MAIL_TO=""
# ─────────────────────────────────────────────────────────────────────────────

echo "==> Installing git"
dnf install -y git

echo "==> Preparing app directory"
mkdir -p "$APP_ROOT"
chown ec2-user:ec2-user "$APP_ROOT"

echo "==> Cloning application from $GIT_REPO_URL"
TMP_DIR="$(mktemp -d)"
git clone --depth 1 --branch "$GIT_BRANCH" "$GIT_REPO_URL" "$TMP_DIR/repo"
cp -r "$TMP_DIR/repo/$APP_SUBPATH/." "$APP_ROOT/"
chown -R ec2-user:ec2-user "$APP_ROOT"
rm -rf "$TMP_DIR"

if [ ! -f "$APP_ROOT/backend/app.py" ]; then
  echo "ERROR: clone succeeded but $APP_ROOT/backend/app.py is missing."
  echo "Check GIT_REPO_URL, GIT_BRANCH, and APP_SUBPATH."
  exit 1
fi

if [ -n "$DB_HOST" ] && [ -n "$DB_PASSWORD" ]; then
  echo "==> Writing backend/.env from user-data CONFIG"
  cat > "$APP_ROOT/backend/.env" <<EOF
DB_HOST=${DB_HOST}
DB_PORT=${DB_PORT}
DB_NAME=${DB_NAME}
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}
EMAIL_TRANSPORT=${EMAIL_TRANSPORT}
SMTP_HOST=${SMTP_HOST}
SMTP_PORT=${SMTP_PORT}
SMTP_USE_TLS=true
SMTP_USER=${SMTP_USER}
SMTP_PASSWORD=${SMTP_PASSWORD}
MAIL_FROM=${MAIL_FROM}
MAIL_TO=${MAIL_TO}
CORS_ORIGINS=
EOF
  chmod 600 "$APP_ROOT/backend/.env"
  chown ec2-user:ec2-user "$APP_ROOT/backend/.env"
else
  echo "==> Skipping .env creation (copy via SCP after launch — see README)"
fi

if [ -n "$DOMAIN" ] && [ "$DOMAIN" != "yourdomain.com" ]; then
  echo "==> Setting Nginx server_name to $DOMAIN"
  sed -i "s/server_name .*/server_name ${DOMAIN} www.${DOMAIN};/" \
    "$APP_ROOT/nginx/ec2-web-app.conf"
fi

echo "==> Running install.sh as ec2-user"
chmod +x "$APP_ROOT/deploy/install.sh"
if sudo -u ec2-user "$APP_ROOT/deploy/install.sh"; then
  touch "$MARKER"
  echo "==> Bootstrap complete at $(date -Is)"
else
  echo "==> install.sh failed — check $LOG"
  echo "    If .env is missing, copy it and re-run: /opt/ec2-web-app/deploy/install.sh"
  exit 1
fi

echo "    Log: $LOG"
echo "    Verify: curl http://127.0.0.1/api/health"
