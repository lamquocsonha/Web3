"""
Save AccessTrade API key to database
"""
from app import app, db, SiteSettings

API_KEY = "byMkvHrygyW5bZCaP3O2AZDv4P4DY34F"

with app.app_context():
    # Save API key
    SiteSettings.set_val('accesstrade_api_key', API_KEY, category='affiliate')

    # Save account info for reference
    from accesstrade_integration import get_accesstrade_api
    api = get_accesstrade_api(API_KEY)

    if api:
        account = api.get_account_info()
        if account:
            SiteSettings.set_val('accesstrade_account_name', account.get('name', ''), category='affiliate')
            SiteSettings.set_val('accesstrade_account_email', account.get('email', ''), category='affiliate')
            SiteSettings.set_val('accesstrade_user_id', account.get('user_id', ''), category='affiliate')

            print(f"✅ Saved AccessTrade API Key")
            print(f"📧 Account: {account.get('name')} ({account.get('email')})")
            print(f"🆔 User ID: {account.get('user_id')}")

            # Get stats
            stats = api.get_statistics_summary(days=30)
            print(f"\n📊 Stats (Last 30 days):")
            print(f"   Campaigns: {stats['campaigns_count']}")
            print(f"   Clicks: {stats['clicks']:,}")
            print(f"   Conversions: {stats['conversions']:,}")
            print(f"   Commission: {stats['commission']:,.0f} VND")
        else:
            print("⚠️  Could not fetch account info")
    else:
        print("❌ Invalid API key")
