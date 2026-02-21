#!/bin/bash
# ══════════════════════════════════════════════════
# UniLab — Deploy alongside TripZone on CentOS 7
# Server: Vultr (CentOS 7, Nginx already running)
# ══════════════════════════════════════════════════
# Usage: sudo bash deploy.sh
#
# TripZone: already running on port 80/443
# UniLab:   Gunicorn on 127.0.0.1:8000 → Nginx reverse proxy
# ══════════════════════════════════════════════════

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

APP_NAME="unilab"
APP_DIR="/var/www/unilab"
VENV_DIR="$APP_DIR/venv"
GUNICORN_PORT=8000

echo ""
echo -e "${CYAN}══════════════════════════════════════════${NC}"
echo -e "${CYAN}  UniLab — Deploy on CentOS 7 (Vultr)${NC}"
echo -e "${CYAN}  Alongside existing TripZone${NC}"
echo -e "${CYAN}══════════════════════════════════════════${NC}"
echo ""

# ── Check root ──
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Chạy bằng root: sudo bash deploy.sh${NC}"
    exit 1
fi

# ── Step 1: Install Python 3.8+ (CentOS 7 ships Python 3.6) ──
echo -e "${GREEN}[1/7] Kiểm tra Python...${NC}"
if command -v python3.8 &>/dev/null; then
    PYTHON=python3.8
elif command -v python3.9 &>/dev/null; then
    PYTHON=python3.9
elif command -v python3.11 &>/dev/null; then
    PYTHON=python3.11
elif command -v python3 &>/dev/null; then
    PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    MAJOR=$(echo $PY_VER | cut -d. -f1)
    MINOR=$(echo $PY_VER | cut -d. -f2)
    if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 8 ]; then
        PYTHON=python3
    else
        echo -e "${YELLOW}Python $PY_VER quá cũ (cần >= 3.8). Cài Python 3.11...${NC}"
        yum install -y centos-release-scl 2>/dev/null || true
        yum install -y rh-python311 2>/dev/null || {
            # Fallback: install from IUS or compile
            yum install -y epel-release
            yum install -y python3 python3-pip python3-devel
        }
        if command -v python3.11 &>/dev/null; then
            PYTHON=python3.11
        else
            PYTHON=python3
        fi
    fi
else
    echo -e "${YELLOW}Chưa có Python3. Đang cài...${NC}"
    yum install -y epel-release
    yum install -y python3 python3-pip python3-devel
    PYTHON=python3
fi
echo -e "  Dùng: $($PYTHON --version)"

# ── Step 2: Copy project files ──
echo -e "${GREEN}[2/7] Chuẩn bị thư mục ứng dụng...${NC}"
mkdir -p $APP_DIR

# Check if files already exist
if [ ! -f "$APP_DIR/app.py" ]; then
    echo -e "${YELLOW}  Chưa có source code tại $APP_DIR${NC}"
    echo -e "  Hãy copy project vào trước khi chạy script:"
    echo -e "  ${CYAN}scp -r V00/* root@<server-ip>:$APP_DIR/${NC}"
    echo ""
    read -p "Đã copy xong? (y/n): " COPIED
    if [ "$COPIED" != "y" ]; then
        echo "Thoát. Copy source code rồi chạy lại."
        exit 1
    fi
fi

# ── Step 3: Virtual environment + dependencies ──
echo -e "${GREEN}[3/7] Tạo virtual environment & cài dependencies...${NC}"
cd $APP_DIR
$PYTHON -m venv venv 2>/dev/null || {
    echo -e "${YELLOW}  Cài venv module...${NC}"
    yum install -y python3-virtualenv 2>/dev/null || pip3 install virtualenv
    $PYTHON -m venv venv
}
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
echo -e "  OK — $(pip show flask | grep Version)"

# ── Step 4: Init database ──
echo -e "${GREEN}[4/7] Khởi tạo database...${NC}"
mkdir -p instance
$PYTHON -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('  Database ready: instance/unilab.db')
"

# ── Step 5: Systemd service ──
echo -e "${GREEN}[5/7] Tạo systemd service...${NC}"
cat > /etc/systemd/system/$APP_NAME.service <<EOF
[Unit]
Description=UniLab Flask App (Gunicorn)
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=$APP_DIR
Environment="PATH=$VENV_DIR/bin"
ExecStart=$VENV_DIR/bin/gunicorn --workers 2 --threads 2 --bind 127.0.0.1:$GUNICORN_PORT --timeout 120 app:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable $APP_NAME
echo -e "  Service: $APP_NAME.service"

# ── Step 6: Nginx vhost ──
echo -e "${GREEN}[6/7] Cấu hình Nginx...${NC}"
echo ""
echo -e "${YELLOW}Nhập domain cho UniLab (VD: unilab.vn):${NC}"
read -p "> " DOMAIN

if [ -z "$DOMAIN" ]; then
    echo -e "${YELLOW}  Bỏ qua Nginx config. Truy cập trực tiếp: http://<ip>:$GUNICORN_PORT${NC}"
else
    # CentOS 7 uses /etc/nginx/conf.d/ (not sites-available)
    NGINX_CONF="/etc/nginx/conf.d/$APP_NAME.conf"
    cat > $NGINX_CONF <<NGINX
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    # Static files — served by Nginx
    location /static {
        alias $APP_DIR/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /robots.txt {
        alias $APP_DIR/static/robots.txt;
    }

    # App — reverse proxy to Gunicorn
    location / {
        proxy_pass http://127.0.0.1:$GUNICORN_PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 120s;
    }

    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options SAMEORIGIN;
    add_header X-XSS-Protection "1; mode=block";
}
NGINX

    nginx -t && systemctl reload nginx
    echo -e "  Nginx config: $NGINX_CONF"

    # SSL
    echo ""
    echo -e "${YELLOW}Cài SSL (Let's Encrypt)? (y/n)${NC}"
    read -p "> " SETUP_SSL
    if [ "$SETUP_SSL" = "y" ]; then
        yum install -y epel-release 2>/dev/null || true
        yum install -y certbot python2-certbot-nginx 2>/dev/null || \
            yum install -y certbot python3-certbot-nginx 2>/dev/null || {
                pip install certbot certbot-nginx
            }
        certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN || {
            echo -e "${YELLOW}  Certbot tự động thất bại. Chạy thủ công:${NC}"
            echo -e "  certbot --nginx -d $DOMAIN"
        }
    fi
fi

# ── Step 7: Start ──
echo -e "${GREEN}[7/7] Khởi động UniLab...${NC}"
systemctl restart $APP_NAME
sleep 2
systemctl status $APP_NAME --no-pager -l

echo ""
echo -e "${CYAN}══════════════════════════════════════════${NC}"
echo -e "${GREEN}  Deploy thành công!${NC}"
echo -e "${CYAN}══════════════════════════════════════════${NC}"
echo ""
echo -e "  UniLab:    http://127.0.0.1:$GUNICORN_PORT"
if [ ! -z "$DOMAIN" ]; then
echo -e "  Website:   http://$DOMAIN"
fi
echo ""
echo -e "  ${CYAN}Quản lý:${NC}"
echo -e "  systemctl status $APP_NAME     # Xem trạng thái"
echo -e "  systemctl restart $APP_NAME    # Khởi động lại"
echo -e "  journalctl -u $APP_NAME -f     # Xem log"
echo ""
echo -e "  ${CYAN}TripZone vẫn chạy bình thường — không bị ảnh hưởng${NC}"
echo ""
