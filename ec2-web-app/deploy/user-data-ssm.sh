#!/bin/bash
# EC2 User Data — SSM + IAM path (requires AWS CLI on instance + instance role).
# Only use if your admin has attached iam-policy.json and created the SSM parameter.
# For locked-down accounts, use deploy/user-data.sh instead.

set -euo pipefail

LOG="/var/log/ec2-web-app-user-data.log"
MARKER="/var/lib/ec2-web-app/bootstrap-complete"
APP_ROOT="/opt/ec2-web-app"

exec > >(tee -a "$LOG") 2>&1
echo "==> EC2 user-data (SSM) started at $(date -Is)"

if [ -f "$MARKER" ]; then
  echo "==> Bootstrap already completed; skipping."
  exit 0
fi

# ── CONFIG ───────────────────────────────────────────────────────────────────
GIT_REPO_URL="https://github.com/YOUR_USER/retros-ideas.git"
GIT_BRANCH="main"
APP_SUBPATH="ec2-web-app"
SSM_ENV_PARAM="/ec2-web-app/env"
DOMAIN="yourdomain.com"
AWS_REGION="us-east-1"
# ─────────────────────────────────────────────────────────────────────────────

echo "==> Installing git and AWS CLI"
dnf install -y git awscli

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
  sed -i "s/server_name .*/server_name ${DOMAIN} www.${DOMAIN};/" \
    "$APP_ROOT/nginx/ec2-web-app.conf"
fi

chmod +x "$APP_ROOT/deploy/install.sh"
sudo -u ec2-user "$APP_ROOT/deploy/install.sh"

touch "$MARKER"
echo "==> Bootstrap complete at $(date -Is)"
