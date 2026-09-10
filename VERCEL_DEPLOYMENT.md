# 🚀 VARUNA — Vercel Deployment Guide

This repository is pre-configured and 100% ready for deployment on [Vercel](https://vercel.com).

---

## 🏗️ Architecture Overview

| Component | Recommended Hosting | Why |
|---|---|---|
| **Frontend (React + Vite + Tailwind)** | **Vercel** | Lightning-fast Edge CDN, automatic HTTPS, SPA rewrites, zero cold starts. |
| **Backend (FastAPI + 11 AI Agents + ML)** | **Render / Railway / Fly.io / VPS** | Heavy scientific & ML packages (`xgboost`, `scikit-learn`, `netcdf4`, `copernicusmarine`) and long agent reasoning cycles (10-30s) require a persistent container environment beyond serverless timeout/size limits. |

---

## ⚡ Option 1: Deploying to Vercel via GitHub (Recommended)

### Step 1: Import Project to Vercel
1. Go to [vercel.com](https://vercel.com) and log in.
2. Click **"Add New..."** → **"Project"**.
3. Select your GitHub repository: `https://github.com/Karanpatil1201/SIH2026`.

### Step 2: Configure Project Settings in Vercel
Vercel will detect Vite automatically. Configure:
- **Framework Preset:** `Vite`
- **Root Directory:** Click **Edit** and choose `frontend` (OR leave as `./` — root `vercel.json` will automatically build `frontend`).
- **Build Command:** `npm run build`
- **Output Directory:** `dist`

### Step 3: Set Environment Variables
Under **Environment Variables** in the Vercel project settings, add:

| Variable Name | Value | Description |
|---|---|---|
| `VITE_API_URL` | `https://your-backend-service.onrender.com/api` | The live URL of your deployed FastAPI backend service. |

> 💡 *Note: If you leave `VITE_API_URL` blank or set to `/api`, Vercel will route API calls through the rewrite rule defined in `vercel.json`.*

### Step 4: Click Deploy!
Vercel will build and deploy your application in under 30 seconds with a global `https://*.vercel.app` domain.

---

## ⚙️ Configuration Files Included in This Repo

### 1. `frontend/vercel.json`
Ensures all deep links (e.g. `/admin`, `/charts`, `/chat`) route to `index.html` without 404 errors:
```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

### 2. Root `vercel.json`
Allows zero-configuration monorepo deployment if you import the repository root directly into Vercel:
```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "buildCommand": "cd frontend && npm install && npm run build",
  "outputDirectory": "frontend/dist",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

---

## 🐳 Backend Deployment (To Connect with Vercel Frontend)

Deploy your FastAPI backend to **Render.com** (Free/Starter tier):
1. Create a **New Web Service** on Render connected to `https://github.com/Karanpatil1201/SIH2026`.
2. Configure:
   - **Root Directory:** `backend`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Add backend environment variables:
   - `GEMINI_API_KEY`: Your Google Gemini API key
   - `DATABASE_URL`: Your Supabase PostgreSQL URL
   - `SECRET_KEY`: A secure random string for JWT auth
4. Once deployed, copy your Render URL (e.g. `https://varuna-backend.onrender.com`) and paste it as `VITE_API_URL` in your Vercel project settings!
