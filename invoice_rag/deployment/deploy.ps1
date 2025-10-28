# 🚂 Railway.app Quick Setup Script
# Run this from the deployment/ folder before deploying to Railway

Write-Host "🚂 Railway.app Deployment Preparation" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Move to project root
Set-Location ..

# Check if git repo
if (-not (Test-Path .git)) {
    Write-Host "❌ Not a git repository. Initializing..." -ForegroundColor Red
    git init
    git branch -M main
}

# Check required files (relative to project root)
Write-Host "✅ Checking deployment files..." -ForegroundColor Green
$files = @("deployment/railway.json", "deployment/Procfile", "deployment/runtime.txt", "deployment/.railwayignore", "requirements.txt")
foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $file - MISSING!" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "📝 Deployment Checklist:" -ForegroundColor Yellow
Write-Host "  [ ] All required files present"
Write-Host "  [ ] .env file NOT committed (check .gitignore)"
Write-Host "  [ ] Code tested locally"
Write-Host "  [ ] Database path is 'database/invoices.db'"
Write-Host ""

# Check .env is not staged
$gitStatus = git status --short .env 2>$null
if ($gitStatus) {
    Write-Host "⚠️  WARNING: .env file is staged for commit!" -ForegroundColor Red
    Write-Host "   Run: git reset .env" -ForegroundColor Yellow
    Write-Host ""
}

# Stage files
Write-Host "📦 Staging files for commit..." -ForegroundColor Cyan
git add .

Write-Host ""
Write-Host "💡 Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Copy Railway config files to project root:"
Write-Host "     Copy-Item deployment/railway.json, deployment/Procfile, deployment/runtime.txt, deployment/.railwayignore ."
Write-Host ""
Write-Host "  2. Commit your changes:"
Write-Host "     git commit -m 'feat: add Railway deployment configuration'"
Write-Host ""
Write-Host "  3. Push to GitHub:"
Write-Host "     git push origin main"
Write-Host ""
Write-Host "  4. Go to https://railway.app" -ForegroundColor Cyan
Write-Host "  5. Click 'New Project' → 'Deploy from GitHub'"
Write-Host "  6. Select your repository"
Write-Host "  7. Add environment variables (see deployment/.env.railway)"
Write-Host "  8. Add volume for database: /app/database"
Write-Host ""
Write-Host "📖 Full guide: deployment/RAILWAY_DEPLOYMENT.md" -ForegroundColor Green
