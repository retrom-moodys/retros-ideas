#!/bin/bash
# EC2 User Data — paste into "Advanced details → User data" at launch (Amazon Linux 2023).
# Runs as root on first boot. Re-runs are skipped after bootstrap completes.
#
# Before launch:
#   1. Edit the CONFIG section below (repo URL, domain, SSM parameter name).
#   2. Store backend/.env contents in SSM as a SecureString (see deploy/ssm-env.example).
#   3. Attach iam-policy.json to the instance role (SES + SSM read).

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

# ── CONFIG (edit before launch) ──────────────────────────────────────────────
GIT_REPO_URL="https://github.com/YOUR_USER/retros-ideas.git"
GIT_BRANCH="main"
APP_SUBPATH="ec2-web-app"
SSM_ENV_PARAM="/ec2-web-app/env"
DOMAIN="yourdomain.com"
AWS_REGION="us-east-1"
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

echo "==> Loading backend/.env from SSM ($SSM_ENV_PARAM)"
aws ssm get-parameter \
  --name "$SSM_ENV_PARAM" \
  --with-decryption \
  --region "$AWS_REGION" \
  --query "Parameter.Value" \
  --output text > "$APP_ROOT/backend/.env"
chmod 600 "$APP_ROOT/backend/.env"
chown ec2-user:ec2-user "$APP_ROOT/backend/.env"

if [ -n "$DOMAIN" ] && [ "$DOMAIN" != "yourdomain.com" ]; then
  echo "==> Setting Nginx server_name to $DOMAIN"
  sed -i "s/server_name .*/server_name ${DOMAIN} www.${DOMAIN};/" \
    "$APP_ROOT/nginx/ec2-web-app.conf"
fi

echo "==> Running install.sh as ec2-user"
chmod +x "$APP_ROOT/deploy/install.sh"
sudo -u ec2-user "$APP_ROOT/deploy/install.sh"

touch "$MARKER"
echo "==> Bootstrap complete at $(date -Is)"
echo "    Log: $LOG"
echo "    Verify: curl http://127.0.0.1/api/health"
