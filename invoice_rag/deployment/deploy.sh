#!/bin/bash
# Quick deployment script for Railway.app
# Run this from the deployment/ folder

echo "🚂 Railway.app Deployment Script"
echo "=================================="
echo ""

# Move to project root
cd ..

# Check if git repo
if [ ! -d .git ]; then
    echo "❌ Not a git repository. Initializing..."
    git init
    git branch -M main
fi

# Check if files exist (relative to project root)
echo "✅ Checking deployment files..."
files=("deployment/railway.json" "deployment/Procfile" "deployment/runtime.txt" "requirements.txt" "deployment/.railwayignore")
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file - MISSING!"
    fi
done

echo ""
echo "📝 Deployment Checklist:"
echo "  [ ] All required files present"
echo "  [ ] .env file NOT committed (check .gitignore)"
echo "  [ ] Code tested locally"
echo "  [ ] Database path is 'database/invoices.db'"
echo ""

# Stage files
echo "📦 Staging files for commit..."
git add .

echo ""
echo "💡 Next Steps:"
echo "  1. Copy Railway config files to project root:"
echo "     cp deployment/railway.json deployment/Procfile deployment/runtime.txt deployment/.railwayignore ."
echo ""
echo "  2. Commit your changes:"
echo "     git commit -m 'feat: add Railway deployment configuration'"
echo ""
echo "  3. Push to GitHub:"
echo "     git push origin main"
echo ""
echo "  4. Go to https://railway.app"
echo "  5. Click 'New Project' → 'Deploy from GitHub'"
echo "  6. Select your repository"
echo "  7. Add environment variables (see deployment/.env.railway)"
echo "  8. Add volume for database: /app/database"
echo ""
echo "📖 Full guide: deployment/RAILWAY_DEPLOYMENT.md"
