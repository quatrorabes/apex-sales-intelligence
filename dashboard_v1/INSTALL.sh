#!/bin/bash

echo "🚀 APEX DASHBOARD V1 - INSTALLATION SCRIPT"
echo "=========================================="
echo ""

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm not found. Please install Node.js first."
    exit 1
fi

echo "📦 Installing dependencies..."
npm install

echo ""
echo "✅ Installation complete!"
echo ""
echo "🎯 Next steps:"
echo "   1. Copy .env.example to .env and configure your API URL"
echo "   2. Run 'npm run dev' to start the development server"
echo "   3. Open http://localhost:3000 in your browser"
echo ""
echo "📚 Available commands:"
echo "   npm run dev     - Start development server"
echo "   npm run build   - Build for production"
echo "   npm run preview - Preview production build"
echo ""
