#!/bin/bash

echo "🚀 Apex Dashboard Deployment Script"
echo "===================================="

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
  echo "❌ Error: package.json not found. Run from dashboard_v1 directory."
  exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Build production bundle
echo "🔨 Building production bundle..."
npm run build

# Check if dist/ was created
if [ ! -d "dist" ]; then
  echo "❌ Error: Build failed - dist/ directory not created"
  exit 1
fi

echo "✅ Build complete!"
echo ""
echo "📊 Build Statistics:"
du -sh dist/
echo ""

# Prompt for deployment
read -p "Deploy to Railway? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  echo "🚂 Deploying to Railway..."
  railway up
  echo "✅ Deployment complete!"
else
  echo "⏸️  Deployment skipped. Run 'railway up' manually to deploy."
fi
