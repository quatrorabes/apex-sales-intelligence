#!/bin/bash

echo "🔧 Standardizing API_URL across all components..."

# Use src/config.ts as the single source of truth (it already exists)
# It exports: API_BASE

# Fix ContactEnrichmentView.tsx (broken string literals)
sed -i '' "s|fetch('\${import.meta.env.VITE_API_URL || \"http://localhost:8000\"}/api|fetch(\`\${API_BASE}/api|g" src/components/ContactEnrichmentView.tsx
sed -i '' "1a\\
import { API_BASE } from '../config';
" src/components/ContactEnrichmentView.tsx
echo "✅ ContactEnrichmentView.tsx"

# Fix WhyMeTab.tsx
sed -i '' "s|fetch('\${import.meta.env.VITE_API_URL || \"http://localhost:8000\"}/api|fetch(\`\${API_BASE}/api|g" src/components/WhyMeTab.tsx
sed -i '' "1a\\
import { API_BASE } from '../config';
" src/components/WhyMeTab.tsx
echo "✅ WhyMeTab.tsx"

# Fix SignalsFeed.tsx
sed -i '' "s|fetch('\${import.meta.env.VITE_API_URL || \"http://localhost:8000\"}/api|fetch(\`\${API_BASE}/api|g" src/components/SignalsFeed.tsx
sed -i '' "s|fetch(\`\${import.meta.env.VITE_API_URL || \"http://localhost:8000\"}/api|fetch(\`\${API_BASE}/api|g" src/components/SignalsFeed.tsx
sed -i '' "1a\\
import { API_BASE } from '../config';
" src/components/SignalsFeed.tsx
echo "✅ SignalsFeed.tsx"

# Fix ApexIntelligence.tsx
sed -i '' "s|fetch('\${import.meta.env.VITE_API_URL || \"http://localhost:8000\"}/api|fetch(\`\${API_BASE}/api|g" src/components/ApexIntelligence.tsx
sed -i '' "1a\\
import { API_BASE } from '../config';
" src/components/ApexIntelligence.tsx
echo "✅ ApexIntelligence.tsx"

# Fix RawDataViewer.tsx
sed -i '' "s|const API_BASE = '\${import.meta.env.VITE_API_URL || \"http://localhost:8000\"}'|// API_BASE imported from config|g" src/components/RawDataViewer.tsx
sed -i '' "1a\\
import { API_BASE } from '../config';
" src/components/RawDataViewer.tsx
echo "✅ RawDataViewer.tsx"

# Fix why_me.tsx
sed -i '' "s|const API_BASE = '\${import.meta.env.VITE_API_URL || \"http://localhost:8000\"}'|// API_BASE imported from config|g" src/components/why_me.tsx
sed -i '' "1a\\
import { API_BASE } from '../config';
" src/components/why_me.tsx
echo "✅ why_me.tsx"

# Fix ActivityLogger.tsx
sed -i '' "s|fetch('\${import.meta.env.VITE_API_URL || \"http://localhost:8000\"}/api|fetch(\`\${API_BASE}/api|g" src/components/ActivityLogger.tsx
sed -i '' "1a\\
import { API_BASE } from '../config';
" src/components/ActivityLogger.tsx
echo "✅ ActivityLogger.tsx"

# Fix ActivityTimeline.tsx
sed -i '' "s|import.meta.env.VITE_API_URL || \"http://localhost:8000\"|API_BASE|g" src/components/ActivityTimeline.tsx
sed -i '' "1a\\
import { API_BASE } from '../config';
" src/components/ActivityTimeline.tsx
echo "✅ ActivityTimeline.tsx"

# Fix ContentGenerator.tsx
sed -i '' "s|import.meta.env.VITE_API_URL || \"http://localhost:8000\"|API_BASE|g" src/components/ContentGenerator.tsx
sed -i '' "1a\\
import { API_BASE } from '../config';
" src/components/ContentGenerator.tsx
echo "✅ ContentGenerator.tsx"

# Fix CadenceDashboard.tsx (remove local definition, use import)
sed -i '' "s|const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';|// Using API_BASE from config|g" src/components/CadenceDashboard.tsx
sed -i '' "s|API_URL|API_BASE|g" src/components/CadenceDashboard.tsx
sed -i '' "s|import.meta.env.VITE_API_URL || \"http://localhost:8000\"|API_BASE|g" src/components/CadenceDashboard.tsx
sed -i '' "1a\\
import { API_BASE } from '../config';
" src/components/CadenceDashboard.tsx
echo "✅ CadenceDashboard.tsx"

# Fix TodaysBoard.tsx
sed -i '' "s|const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';|// Using API_BASE from config|g" src/components/TodaysBoard.tsx
sed -i '' "s|API_URL|API_BASE|g" src/components/TodaysBoard.tsx
sed -i '' "1a\\
import { API_BASE } from '../config';
" src/components/TodaysBoard.tsx
echo "✅ TodaysBoard.tsx"

# Fix ContactDetailModal.tsx (has nested broken string)
sed -i '' "s|const API_URL = import.meta.env.VITE_API_URL || '\${import.meta.env.VITE_API_URL || \"http://localhost:8000\"}';|// Using API_BASE from config|g" src/components/ContactDetailModal.tsx
sed -i '' "s|API_URL|API_BASE|g" src/components/ContactDetailModal.tsx
sed -i '' "1a\\
import { API_BASE } from '../config';
" src/components/ContactDetailModal.tsx
echo "✅ ContactDetailModal.tsx"

# Fix OnboardingModal.tsx
sed -i '' "s|const API_BASE = import.meta.env.VITE_API_URL || \"http://localhost:8000\";|// Using API_BASE from config|g" src/components/OnboardingModal.tsx
sed -i '' "1a\\
import { API_BASE } from '../config';
" src/components/OnboardingModal.tsx
echo "✅ OnboardingModal.tsx"

# Fix App.tsx (uses API_URL internally)
sed -i '' "s|const API_URL = import.meta.env.VITE_API_URL || 'https://apex-intelligence-production.up.railway.app';|// Using API_BASE from config|g" src/App.tsx
sed -i '' "s|API_URL|API_BASE|g" src/App.tsx
sed -i '' "1a\\
import { API_BASE } from './config';
" src/App.tsx
echo "✅ App.tsx"

echo ""
echo "🎯 All files patched! Run: npm run dev"
