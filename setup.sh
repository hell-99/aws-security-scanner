#!/bin/bash

echo "╔═══════════════════════════════════════════════════════╗"
echo "║                                                       ║"
echo "║     AWS Security Scanner - Setup Script              ║"
echo "║                                                       ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""

# Check Python version
echo "🔍 Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python 3 found"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed successfully"
echo ""

# Make scanner executable
chmod +x scanner.py

# Run a test scan
echo "🧪 Running test scan with mock data..."
python3 scanner.py --mock --output json --report-file test-report

if [ $? -ne 0 ]; then
    echo "❌ Test scan failed"
    exit 1
fi

echo "✅ Test scan completed successfully"
echo ""

# Check if report was generated
if [ -f "test-report.json" ]; then
    echo "✅ Test report generated: test-report.json"
    rm test-report.json
else
    echo "⚠️  Warning: Test report not found"
fi

echo ""
echo "╔═══════════════════════════════════════════════════════╗"
echo "║                                                       ║"
echo "║            🎉 Setup Complete! 🎉                      ║"
echo "║                                                       ║"
echo "║  Run: python3 scanner.py --mock                       ║"
echo "║  Or:  python3 scanner.py --help                       ║"
echo "║                                                       ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""
