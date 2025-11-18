#!/bin/bash

# Trading Platform Deploy Script
echo "🚀 Trading Platform Deployment"
echo "================================"

# Check if running from project root
if [ ! -f "app.py" ]; then
    echo "❌ Error: Run this script from project root (trading-platform/)"
    exit 1
fi

# Create uploads directory if not exists
if [ ! -d "uploads" ]; then
    echo "📁 Creating uploads directory..."
    mkdir -p uploads
    echo "✅ Created uploads/"
fi

# Check for sample CSV
if [ ! -f "uploads/VN30F1M__31_10_25_14_45_00__Python_format.csv" ]; then
    echo "⚠️  Warning: Sample CSV not found in uploads/"
    echo "   Please copy your CSV files to uploads/"
fi

# Install dependencies
echo ""
echo "📦 Checking dependencies..."
pip list | grep -q flask
if [ $? -ne 0 ]; then
    echo "Installing Flask..."
    pip install flask flask-cors --break-system-packages
fi

# Display structure
echo ""
echo "📂 Project Structure:"
echo "   $(pwd)/"
echo "   ├── app.py"
echo "   ├── templates/"
echo "   ├── static/"
echo "   └── uploads/        ← CSV files here"
echo "       └── *.csv"

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎯 Next steps:"
echo "   1. Copy CSV files to: $(pwd)/uploads/"
echo "   2. Run: python app.py"
echo "   3. Open: http://localhost:5000"
echo ""
echo "📖 Read UPLOAD_GUIDE.md for more details"

