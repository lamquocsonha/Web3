"""
Test AccessTrade API and fetch available data
API Documentation: https://developers.accesstrade.vn/
"""
import requests
import json
import os

API_KEY = os.environ.get("ACCESSTRADE_API_KEY", "")
BASE_URL = "https://api.accesstrade.vn/v1"

headers = {
    "Authorization": f"Token {API_KEY}",
    "Content-Type": "application/json"
}

def test_api_connection():
    """Test basic API connection"""
    print("=" * 60)
    print("TESTING ACCESSTRADE API CONNECTION")
    print("=" * 60)

    endpoints = [
        ("Campaigns", "/campaigns"),
        ("Offers", "/offers_informations"),
        ("Transactions", "/transactions"),
        ("Conversions", "/conversions_data"),
        ("Account Info", "/me"),
    ]

    results = {}

    for name, endpoint in endpoints:
        print(f"\n📡 Testing: {name}")
        print(f"   Endpoint: {endpoint}")

        try:
            response = requests.get(
                f"{BASE_URL}{endpoint}",
                headers=headers,
                timeout=10
            )

            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                results[name] = data

                # Show summary
                if isinstance(data, dict):
                    if 'data' in data:
                        print(f"   ✅ Found {len(data.get('data', []))} items")
                        if data.get('data'):
                            print(f"   Sample: {list(data['data'][0].keys())[:5]}")
                    else:
                        print(f"   ✅ Keys: {list(data.keys())[:5]}")
                elif isinstance(data, list):
                    print(f"   ✅ Found {len(data)} items")

            elif response.status_code == 401:
                print(f"   ❌ Unauthorized - API key may be invalid")
            elif response.status_code == 404:
                print(f"   ⚠️  Endpoint not found")
            else:
                print(f"   ⚠️  Error: {response.text[:100]}")

        except requests.exceptions.Timeout:
            print(f"   ⏱️  Timeout")
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:100]}")

    return results

def show_campaign_details(campaigns):
    """Display campaign information"""
    if not campaigns or 'data' not in campaigns:
        print("\n⚠️  No campaign data available")
        return

    print("\n" + "=" * 60)
    print("AVAILABLE CAMPAIGNS")
    print("=" * 60)

    for i, campaign in enumerate(campaigns['data'][:10], 1):
        print(f"\n{i}. {campaign.get('name', 'N/A')}")
        print(f"   ID: {campaign.get('id', 'N/A')}")
        print(f"   Commission: {campaign.get('commission_rate', 'N/A')}")
        print(f"   Status: {campaign.get('status', 'N/A')}")
        print(f"   Category: {campaign.get('category', 'N/A')}")

def show_transaction_summary(transactions):
    """Display transaction statistics"""
    if not transactions or 'data' not in transactions:
        print("\n⚠️  No transaction data available")
        return

    print("\n" + "=" * 60)
    print("TRANSACTION SUMMARY")
    print("=" * 60)

    data = transactions['data']

    total_clicks = sum(t.get('click', 0) for t in data)
    total_conversions = sum(t.get('conversion', 0) for t in data)
    total_commission = sum(float(t.get('commission', 0)) for t in data)

    print(f"\n📊 Total Clicks: {total_clicks:,}")
    print(f"💰 Total Conversions: {total_conversions:,}")
    print(f"💵 Total Commission: {total_commission:,.0f} VND")

    if data:
        print(f"\n📅 Recent Transactions (last 5):")
        for t in data[:5]:
            print(f"   • {t.get('date', 'N/A')} - Clicks: {t.get('click', 0)}, Conv: {t.get('conversion', 0)}, Commission: {t.get('commission', 0)}")

if __name__ == '__main__':
    print("\n🔑 API Key:", API_KEY[:20] + "..." + API_KEY[-10:])
    print(f"🌐 Base URL: {BASE_URL}\n")

    # Test all endpoints
    results = test_api_connection()

    # Show detailed information
    if 'Campaigns' in results:
        show_campaign_details(results['Campaigns'])

    if 'Transactions' in results:
        show_transaction_summary(results['Transactions'])

    # Save full results to JSON for inspection
    with open('/tmp/accesstrade_api_test.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 60)
    print(f"📁 Full results saved to: /tmp/accesstrade_api_test.json")
    print("=" * 60)
