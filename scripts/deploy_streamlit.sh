#!/bin/bash
# 🚀 Streamlit Cloud Deployment Helper
# Note: Streamlit Cloud doesn't have official CLI/API, but this script helps prepare

set -e

echo "🍹 Streamlit Cloud Deployment Helper"
echo "===================================="
echo ""

# Check if git repo exists
if [ ! -d .git ]; then
    echo "⚠️  No git repository found. Initializing..."
    git init
    git add .
    git commit -m "Add Streamlit dashboard for Cocktailverse"
    echo "✅ Git initialized"
    echo ""
    echo "📝 Next steps:"
    echo "1. Create GitHub repo: https://github.com/new"
    echo "2. Run: git remote add origin https://github.com/YOUR_USERNAME/cocktailverse.git"
    echo "3. Run: git push -u origin main"
    exit 0
fi

# Check if remote exists
if ! git remote | grep -q origin; then
    echo "⚠️  No GitHub remote found."
    echo ""
    echo "📝 To add remote:"
    echo "   git remote add origin https://github.com/YOUR_USERNAME/cocktailverse.git"
    echo "   git push -u origin main"
    exit 0
fi

# Check if pushed
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse @{u} 2>/dev/null || echo "")

if [ -z "$REMOTE" ] || [ "$LOCAL" != "$REMOTE" ]; then
    echo "📤 Pushing to GitHub..."
    git push origin main || git push origin master
    echo "✅ Pushed to GitHub"
else
    echo "✅ Code already pushed to GitHub"
fi

echo ""
echo "🎯 Streamlit Cloud Deployment Steps:"
echo "===================================="
echo ""
echo "1. Go to: https://share.streamlit.io"
echo "2. Click 'New app'"
echo "3. Connect your GitHub repo"
echo "4. Settings:"
echo "   - Branch: main"
echo "   - Main file: dashboard/app.py"
echo "5. Environment Variables:"
echo "   PROJECT_ID=maps-platform-20251011-140544"
echo "   DATASET_ID=cocktailverse"
echo "   TABLE_ID=cocktails"
echo "6. Secrets (GCP credentials):"
echo "   Add service account JSON to Streamlit Cloud → Settings → Secrets"
echo "7. Click 'Deploy'"
echo ""
echo "📚 Full guide: streamlit_deploy.md"

