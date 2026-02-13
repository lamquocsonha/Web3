# Scripts & Utilities

This folder contains utility scripts, migrations, and tools for development.

## 📝 Content Generation

- **auto_generate_content.py** - Auto-generates lorem ipsum content for articles and SEO content for zones (called by app.py on startup)
- **generate_lorem_articles.py** - Functions to generate lorem ipsum articles with proper structure
- **generate_zone_seo.py** - Functions to generate SEO content for product category pages

## 🗄️ Database Migrations

- **add_banner_table.py** - Creates banner table in database (legacy - now in migrate_db.py)
- **migrate_add_template.py** - Adds template column to vertical table (legacy - now in migrate_db.py)

## 🔗 AccessTrade Integration

- **save_accesstrade_key.py** - Saves AccessTrade API key to database
- **test_accesstrade_api.py** - Tests AccessTrade API endpoints and displays available data

## 🎨 Samples & Examples

- **sample_article_bike_groupset.py** - Example of creating a detailed article with proper structure

## 🚀 Alternative Runners

- **run.py** - Cross-platform Python runner (alternative to run.bat/start.sh)
- **start.bat** - Simple Windows batch starter (alternative to run.bat)
- **start.sh** - Linux/Mac shell starter

## 🛠️ Utilities

- **clearcache.bat** - Clears Python cache files
- **migrate.bat** - Runs database migrations manually
- **seed.bat** - Seeds database with sample data

---

**Note:** Most of these scripts are for development/setup only. The main app runs automatically without needing these scripts.
