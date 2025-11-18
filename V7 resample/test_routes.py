#!/usr/bin/env python3
"""Test Flask routes to verify they work correctly"""

from app import app
import sys

def test_routes():
    """Test all main routes"""
    with app.test_client() as client:
        routes_to_test = [
            ('/', 'Redirect to manual-trading'),
            ('/manual-trading', 'Manual Trading'),
            ('/bot-trading', 'Bot Trading'),
            ('/strategy', 'Strategy Builder'),
            ('/backtest', 'Backtest'),
            ('/optimize', 'Optimize'),
        ]

        print("Testing Flask Routes:")
        print("=" * 60)

        all_passed = True

        for route, expected_content in routes_to_test:
            try:
                response = client.get(route, follow_redirects=True)

                # Check status code
                if response.status_code != 200:
                    print(f"❌ {route:20s} → Status {response.status_code}")
                    all_passed = False
                    continue

                # Check content
                html = response.data.decode('utf-8')

                # For redirect route
                if route == '/':
                    if 'Manual Trading' in html:
                        print(f"✅ {route:20s} → Redirects to Manual Trading")
                    else:
                        print(f"❌ {route:20s} → Unexpected redirect")
                        all_passed = False
                else:
                    if expected_content in html:
                        print(f"✅ {route:20s} → {expected_content}")
                    else:
                        print(f"❌ {route:20s} → Missing '{expected_content}'")
                        print(f"   First 200 chars: {html[:200]}")
                        all_passed = False

            except Exception as e:
                print(f"❌ {route:20s} → Error: {e}")
                all_passed = False

        print("=" * 60)
        if all_passed:
            print("✅ All routes working correctly!")
            return 0
        else:
            print("❌ Some routes failed!")
            return 1

if __name__ == '__main__':
    sys.exit(test_routes())
