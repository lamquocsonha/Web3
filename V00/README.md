# 🏢 Unilab - Multi-Vertical Affiliate Platform

Hệ thống quản lý đa ngành dọc (vertical) với affiliate marketing tích hợp.

## 📁 Project Structure

```
V00/
├── 📄 app.py                          # Main Flask application
├── 📄 models.py                       # Database models (SQLAlchemy)
├── 📄 seed_data.py                    # Database seeding
├── 📄 migrate_db.py                   # Auto-migration script
├── 📄 accesstrade_integration.py      # AccessTrade API integration
├── 📄 requirements.txt                # Python dependencies
├──
├── 🚀 run.bat                         # Main startup script (Windows)
├── 🚀 install.bat                     # Setup & install dependencies
├──
├── 📂 templates/                      # Jinja2 templates
│   ├── admin/                         # Admin panel templates
│   └── shared/                        # Public site templates
├──
├── 📂 static/                         # Static assets
│   └── css/                           # CSS files (general, travel, blog, finance templates)
├──
├── 📂 scripts/                        # Utility scripts & migrations
│   ├── auto_generate_content.py
│   ├── generate_lorem_articles.py
│   ├── test_accesstrade_api.py
│   └── ...
├──
├── 📂 docs/                           # Documentation
│   └── uni-flow.html                  # System flow documentation
├──
├── 📂 venv/                           # Python virtual environment
└── 📄 .gitignore                      # Git ignore rules
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
install.bat
```

### 2. Run Application
```bash
run.bat
```

### 3. Access
- 🌐 Admin: http://localhost:7000/admin
- 🚗 UniCar: http://localhost:7000/car
- 🐕 Pet: http://localhost:7000/pet
- 🚴 Bike: http://localhost:7000/bike
- ✈️ Travel: http://localhost:7000/travel

## 🎨 Features

### ✨ Multi-Vertical System
- 4 template presets: **General**, **Travel**, **Blog**, **Finance**
- Easy vertical creation with auto-styling
- Shared components across verticals

### 🔗 Affiliate Integration
- **AccessTrade API** integration
- Campaign management
- Real-time statistics tracking
- Coupon & offer management

### 📝 Content Management
- Auto-generate lorem ipsum articles
- SEO content for product categories
- Article sidebar with featured/related content
- Banner ad management

### 🗄️ Database
- SQLite (auto-created on first run)
- Auto-migration on startup
- Seed data included

## 📦 Dependencies

- Flask 3.1.0
- Flask-SQLAlchemy 3.1.1
- Requests 2.31.0

## 🛠️ Development

### Database Migrations
Auto-migrations run on app startup. Manual migration:
```bash
python migrate_db.py
```

### Generate Content
```bash
python scripts/auto_generate_content.py
```

### Test AccessTrade API
```bash
python scripts/test_accesstrade_api.py
```

## 📚 Documentation

See `docs/uni-flow.html` for detailed system flow and architecture.

---

**Developed with Claude Code** 🤖
