#!/bin/bash
# UniLab Deployment Script for Vultr/VPS
# Run: bash deploy.sh

set -e  # Exit on error

echo "=========================================="
echo "  UniLab Deployment Script"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Variables
APP_DIR="/var/www/unilab/V00"
VENV_DIR="$APP_DIR/venv"
SERVICE_NAME="unilab"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run as root: sudo bash deploy.sh${NC}"
    exit 1
fi

# Step 1: Update system
echo -e "${GREEN}[1/8] Updating system...${NC}"
apt update && apt upgrade -y

# Step 2: Install dependencies
echo -e "${GREEN}[2/8] Installing dependencies...${NC}"
apt install -y python3 python3-pip python3-venv nginx git

# Step 3: Create app directory
echo -e "${GREEN}[3/8] Setting up application directory...${NC}"
mkdir -p /var/www/unilab
cd /var/www/unilab

# If this is a fresh install, you need to copy files here
# Or clone from git repository

# Step 4: Setup virtual environment
echo -e "${GREEN}[4/8] Creating virtual environment...${NC}"
cd $APP_DIR
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Step 5: Run migrations and seed data
echo -e "${GREEN}[5/8] Running migrations and seeding data...${NC}"
python scripts/seed_sidebar_data.py

# Step 6: Setup Gunicorn service
echo -e "${GREEN}[6/8] Configuring Gunicorn service...${NC}"
cat > /etc/systemd/system/$SERVICE_NAME.service <<EOF
[Unit]
Description=UniLab Flask Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=$APP_DIR
Environment="PATH=$VENV_DIR/bin"
ExecStart=$VENV_DIR/bin/gunicorn --workers 4 --bind 127.0.0.1:8000 app:app

[Install]
WantedBy=multi-user.target
EOF

# Step 7: Setup Nginx (if domain provided)
echo -e "${GREEN}[7/8] Configuring Nginx...${NC}"
read -p "Enter your domain (or press Enter to skip): " DOMAIN

if [ ! -z "$DOMAIN" ]; then
    cat > /etc/nginx/sites-available/unilab <<EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static {
        alias $APP_DIR/static;
        expires 30d;
    }

    location /robots.txt {
        alias $APP_DIR/static/robots.txt;
    }

    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
}
EOF

    ln -sf /etc/nginx/sites-available/unilab /etc/nginx/sites-enabled/
    nginx -t && systemctl reload nginx

    echo -e "${YELLOW}Setup SSL? (y/n)${NC}"
    read -p "> " SETUP_SSL
    if [ "$SETUP_SSL" = "y" ]; then
        apt install -y certbot python3-certbot-nginx
        certbot --nginx -d $DOMAIN -d www.$DOMAIN
    fi
fi

# Step 8: Set permissions and start services
echo -e "${GREEN}[8/8] Starting services...${NC}"
chown -R www-data:www-data /var/www/unilab
systemctl daemon-reload
systemctl enable $SERVICE_NAME
systemctl restart $SERVICE_NAME
systemctl restart nginx

# Check status
echo ""
echo "=========================================="
echo -e "${GREEN}Deployment Complete!${NC}"
echo "=========================================="
echo ""
systemctl status $SERVICE_NAME --no-pager
echo ""
echo "App logs: journalctl -u $SERVICE_NAME -f"
echo "Nginx logs: tail -f /var/log/nginx/error.log"
echo ""
if [ ! -z "$DOMAIN" ]; then
    echo -e "Site: ${GREEN}https://$DOMAIN${NC}"
    echo -e "Robots: ${GREEN}https://$DOMAIN/robots.txt${NC}"
fi
echo ""
