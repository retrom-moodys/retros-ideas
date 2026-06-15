#!/usr/bin/env bash
set -euo pipefail

APP_ROOT="/opt/ec2-web-app"
WEB_ROOT="/var/www/ec2-web-app"

echo "==> Installing system packages"
sudo dnf update -y
sudo dnf install -y nginx python3.11 python3.11-pip postgresql15

echo "==> Creating app directories"
sudo mkdir -p "$APP_ROOT" "$WEB_ROOT"
sudo chown -R ec2-user:ec2-user "$APP_ROOT" "$WEB_ROOT"

echo "==> Copy project files into place (run from repo root on EC2)"
echo "    Expected layout:"
echo "      $APP_ROOT/backend"
echo "      $WEB_ROOT/index.html"

if [ ! -f "$APP_ROOT/backend/app.py" ]; then
  echo "ERROR: $APP_ROOT/backend/app.py not found."
  echo "Clone or copy this repo to $APP_ROOT first, then re-run."
  exit 1
fi

echo "==> Python virtual environment"
cd "$APP_ROOT/backend"
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt

ENV_READY=true
if [ ! -f "$APP_ROOT/backend/.env" ]; then
  echo "WARNING: $APP_ROOT/backend/.env missing."
  echo "Copy backend/env.example to .env, fill in RDS + SMTP, then re-run this script."
  ENV_READY=false
fi

echo "==> Deploy static site"
sudo cp -r "$APP_ROOT/website/." "$WEB_ROOT/"
sudo chown -R nginx:nginx "$WEB_ROOT"

echo "==> Configure Nginx"
sudo cp "$APP_ROOT/nginx/ec2-web-app.conf" /etc/nginx/conf.d/ec2-web-app.conf
sudo nginx -t
sudo systemctl enable nginx
sudo systemctl restart nginx

echo "==> Configure systemd service"
sudo cp "$APP_ROOT/deploy/ec2-web-app.service" /etc/systemd/system/ec2-web-app.service
sudo systemctl daemon-reload
sudo systemctl enable ec2-web-app

if [ "$ENV_READY" = false ]; then
  echo "==> Skipping backend start until .env exists"
  exit 0
fi

sudo systemctl restart ec2-web-app

echo "==> Done"
echo "==> Validating app health"
if ! curl -f http://127.0.0.1/api/health; then
  echo "ERROR: App failed health check"
  exit 1
fi
echo "  sudo systemctl status ec2-web-app nginx"
