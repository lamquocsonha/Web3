"""
Database migration script - Add missing columns and tables
Run this once to update your database schema
"""
from app import app, db

def migrate():
    with app.app_context():
        print("🔍 Checking database schema...")

        # Add seo_content column to zone table (if not exists)
        try:
            db.session.execute(db.text("SELECT seo_content FROM zone LIMIT 1"))
            print("✅ zone.seo_content column exists")
        except:
            db.session.rollback()
            print("📝 Adding seo_content column to zone table...")
            db.session.execute(db.text("""
                ALTER TABLE zone ADD COLUMN seo_content TEXT DEFAULT ''
            """))
            db.session.commit()
            print("✅ zone.seo_content column added")

        # Create banner table (if not exists)
        try:
            db.session.execute(db.text("SELECT id FROM banner LIMIT 1"))
            print("✅ banner table exists")
        except:
            db.session.rollback()
            print("📝 Creating banner table...")
            db.session.execute(db.text("""
                CREATE TABLE IF NOT EXISTS banner (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(200) NOT NULL,
                    placement VARCHAR(50) DEFAULT 'sidebar',
                    vertical_slug VARCHAR(50) DEFAULT '',
                    image_url VARCHAR(500) DEFAULT '',
                    link_url VARCHAR(500) DEFAULT '',
                    html_code TEXT DEFAULT '',
                    position INTEGER DEFAULT 1,
                    is_active BOOLEAN DEFAULT 1,
                    impressions INTEGER DEFAULT 0,
                    clicks INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            db.session.commit()
            print("✅ banner table created")

        # Add template column to vertical table (if not exists)
        try:
            db.session.execute(db.text("SELECT template FROM vertical LIMIT 1"))
            print("✅ vertical.template column exists")
        except:
            db.session.rollback()
            print("📝 Adding template column to vertical table...")
            db.session.execute(db.text("""
                ALTER TABLE vertical ADD COLUMN template VARCHAR(20) DEFAULT 'general'
            """))
            db.session.commit()
            print("✅ vertical.template column added")

        # Add style column to vertical table (if not exists)
        try:
            db.session.execute(db.text("SELECT style FROM vertical LIMIT 1"))
            print("✅ vertical.style column exists")
        except:
            db.session.rollback()
            print("📝 Adding style column to vertical table...")
            db.session.execute(db.text("""
                ALTER TABLE vertical ADD COLUMN style VARCHAR(20) DEFAULT 'classic'
            """))
            db.session.commit()
            print("✅ vertical.style column added")

        # Set defaults for template/style on existing verticals
        try:
            from models import Vertical
            template_mapping = {
                'car': 'general',
                'pet': 'general',
                'bike': 'general',
                'travel': 'travel',
            }
            style_mapping = {
                'car': 'car',
                'pet': 'pet',
                'bike': 'bike',
                'travel': 'travel',
            }
            verticals = Vertical.query.all()
            changed = False
            for v in verticals:
                if not v.template or v.template == 'general':
                    new_tmpl = template_mapping.get(v.slug, 'general')
                    if v.template != new_tmpl:
                        v.template = new_tmpl
                        changed = True
                if not v.style or v.style == 'classic':
                    new_style = style_mapping.get(v.slug, 'classic')
                    if v.style != new_style:
                        v.style = new_style
                        changed = True
            if changed:
                db.session.commit()
                print("✅ Set template/style for existing verticals")
        except:
            db.session.rollback()

        # Add deeplink_template column to affiliate_network table (if not exists)
        try:
            db.session.execute(db.text("SELECT deeplink_template FROM affiliate_network LIMIT 1"))
            print("✅ affiliate_network.deeplink_template column exists")
        except:
            db.session.rollback()
            print("📝 Adding deeplink_template column to affiliate_network table...")
            db.session.execute(db.text("""
                ALTER TABLE affiliate_network ADD COLUMN deeplink_template VARCHAR(1000) DEFAULT ''
            """))
            db.session.commit()
            print("✅ affiliate_network.deeplink_template column added")

        # Add embed_code column to voucher table (if not exists)
        try:
            db.session.execute(db.text("SELECT embed_code FROM voucher LIMIT 1"))
            print("✅ voucher.embed_code column exists")
        except:
            db.session.rollback()
            print("📝 Adding embed_code column to voucher table...")
            db.session.execute(db.text("""
                ALTER TABLE voucher ADD COLUMN embed_code TEXT DEFAULT ''
            """))
            db.session.commit()
            print("✅ voucher.embed_code column added")

        # Add sync_mode column to voucher table (if not exists)
        try:
            db.session.execute(db.text("SELECT sync_mode FROM voucher LIMIT 1"))
            print("✅ voucher.sync_mode column exists")
        except:
            db.session.rollback()
            print("📝 Adding sync_mode column to voucher table...")
            db.session.execute(db.text("""
                ALTER TABLE voucher ADD COLUMN sync_mode VARCHAR(20) DEFAULT 'manual'
            """))
            db.session.commit()
            print("✅ voucher.sync_mode column added")

        # Create scheduled_csv_import table (if not exists)
        try:
            db.session.execute(db.text("SELECT id FROM scheduled_csv_import LIMIT 1"))
            print("✅ scheduled_csv_import table exists")
        except:
            db.session.rollback()
            print("📝 Creating scheduled_csv_import table...")
            db.session.execute(db.text("""
                CREATE TABLE IF NOT EXISTS scheduled_csv_import (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(200) NOT NULL,
                    csv_url VARCHAR(1000) NOT NULL,
                    part_id INTEGER NOT NULL,
                    network VARCHAR(50) DEFAULT 'shopee',
                    apply_deeplink BOOLEAN DEFAULT 0,
                    update_interval_days INTEGER DEFAULT 7,
                    is_active BOOLEAN DEFAULT 1,
                    last_import_at DATETIME,
                    next_import_at DATETIME,
                    last_import_count INTEGER DEFAULT 0,
                    last_import_status VARCHAR(20) DEFAULT 'pending',
                    last_error TEXT DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (part_id) REFERENCES part(id)
                )
            """))
            db.session.commit()
            print("✅ scheduled_csv_import table created")

        # Create voucher_widget table (if not exists)
        try:
            db.session.execute(db.text("SELECT id FROM voucher_widget LIMIT 1"))
            print("✅ voucher_widget table exists")
        except:
            db.session.rollback()
            print("📝 Creating voucher_widget table...")
            db.session.execute(db.text("""
                CREATE TABLE IF NOT EXISTS voucher_widget (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(200) NOT NULL,
                    network VARCHAR(50) DEFAULT 'accesstrade',
                    embed_code TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    placement VARCHAR(50) DEFAULT 'voucher_page',
                    position INTEGER DEFAULT 1,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            db.session.commit()
            print("✅ voucher_widget table created")

        # Add price_original column to hotel table (if not exists)
        try:
            db.session.execute(db.text("SELECT price_original FROM hotel LIMIT 1"))
            print("✅ hotel.price_original column exists")
        except:
            db.session.rollback()
            print("📝 Adding price_original column to hotel table...")
            db.session.execute(db.text("""
                ALTER TABLE hotel ADD COLUMN price_original FLOAT DEFAULT 0
            """))
            db.session.commit()
            print("✅ hotel.price_original column added")

        # Add price_original column to attraction table (if not exists)
        try:
            db.session.execute(db.text("SELECT price_original FROM attraction LIMIT 1"))
            print("✅ attraction.price_original column exists")
        except:
            db.session.rollback()
            print("📝 Adding price_original column to attraction table...")
            db.session.execute(db.text("""
                ALTER TABLE attraction ADD COLUMN price_original FLOAT DEFAULT 0
            """))
            db.session.commit()
            print("✅ attraction.price_original column added")

        print("\n🎉 Database migration complete!")

if __name__ == '__main__':
    migrate()
