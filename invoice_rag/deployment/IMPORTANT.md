# ⚠️ Important Note for Railway Deployment

## Railway Configuration Files Location

Railway.app expects certain configuration files to be in the **root of your project**, not in a subfolder.

### Before Deploying to Railway:

You need to **copy** (not move) these files from `deployment/` to the project root:

```powershell
# PowerShell
cd invoice_rag
Copy-Item deployment/railway.json, deployment/Procfile, deployment/runtime.txt, deployment/.railwayignore .
```

```bash
# Bash
cd invoice_rag
cp deployment/railway.json deployment/Procfile deployment/runtime.txt deployment/.railwayignore .
```

### Why?

- Railway looks for `railway.json`, `Procfile`, and `runtime.txt` in the project root
- We keep them in `deployment/` folder for organization
- But they must be copied to root before deployment

### Files to Copy:

1. ✅ `railway.json` → Root
2. ✅ `Procfile` → Root  
3. ✅ `runtime.txt` → Root
4. ✅ `.railwayignore` → Root

### Note:

- The `deployment/` folder itself doesn't need to be deployed
- It's just for organization and documentation
- Railway will use the copies in the root directory

---

**The deployment scripts (`deploy.ps1` and `deploy.sh`) will remind you to do this!**
