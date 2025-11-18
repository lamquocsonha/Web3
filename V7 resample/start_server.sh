#!/bin/bash

echo "========================================="
echo "  Starting V7 Resample Flask Server"
echo "========================================="
echo ""
echo "📍 Server will run on: http://localhost:5000"
echo ""
echo "📝 Routes available:"
echo "   http://localhost:5000/              → Manual Trading (redirect)"
echo "   http://localhost:5000/manual-trading → Manual Trading"
echo "   http://localhost:5000/bot-trading   → Bot Trading"
echo "   http://localhost:5000/strategy      → Strategy (TEST MODE - RED PAGE)"
echo "   http://localhost:5000/backtest      → Backtest"
echo "   http://localhost:5000/optimize      → Optimize"
echo ""
echo "⚠️  IMPORTANT: /strategy currently shows TEST PAGE (red background)"
echo "    If you see red page, route is working!"
echo ""
echo "Press Ctrl+C to stop server"
echo "========================================="
echo ""

cd "$(dirname "$0")"

# Check if Flask is installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "❌ Flask not installed!"
    echo "📦 Installing Flask and dependencies..."
    pip3 install flask flask-cors
    echo ""
fi

# Run Flask app
export FLASK_APP=app.py
export FLASK_ENV=development
python3 app.py
