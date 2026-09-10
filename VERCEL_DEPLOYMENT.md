# 🚀 VARUNA — Vercel Deployment Guide

This repository is **100% pre-configured and ready for 1-click deployment on [Vercel](https://vercel.com)**.

---

## ⚡ 1-Click Zero-Config Deployment on Vercel

### Step 1: Import Project on Vercel
1. Go to [vercel.com](https://vercel.com) and log in.
2. Click **"Add New..."** → **"Project"**.
3. Select your GitHub repository: **`https://github.com/Karanpatil1201/SIH2026`**.

### Step 2: Deploy! (Zero Changes Needed)
- **Framework Preset**: Automatically detected
- **Root Directory**: `./` (Default — root `package.json` and `vercel.json` handle building `frontend` automatically)
- **Build Command**: `npm run build` (Default)
- **Output Directory**: `frontend/dist` (Pre-configured in `vercel.json`)

Click **"Deploy"**!  
Vercel will compile and deploy your live app in ~30 seconds with a global `https://*.vercel.app` domain.

---

## 🧠 Built-In Features on Vercel

1. **Direct In-Browser Gemini AI Engine:**
   - The AI Assistant uses Google Gemini 2.0 / 3.5 Flash directly in the browser to answer any question in **Hindi, Marathi, English, Tamil**, etc.
   - Generates custom, tailored advisories for road trips (e.g. Mumbai to Gokarna), coastal weather, fishing conditions, and specific coordinates (`16.99° N, 73.31° E`).
2. **Live Open-Meteo Ocean & Weather Ingestion:**
   - Real-time significant wave height, wind velocity, swell, and SST are fetched directly in the browser over HTTPS.
3. **Resilient Demo Authentication:**
   - Click any persona card (*Fisherman Ops*, *Shipping Captain*, *System Admin*, etc.) to enter the platform instantly.
4. **Client-Side SPA Deep Routing:**
   - All sub-pages and routes (`/`, `/admin`, `/login`, etc.) are served cleanly without 404 errors.

---

## ⚙️ Optional: Connecting a Persistent FastAPI Backend

If you also want the deep 11-agent DAG reasoning with local XGBoost ML models and Supabase PostgreSQL:

### Step 1: Deploy Backend to [Render.com](https://render.com) (Free)
1. In Render, click **New +** → **Web Service** → Connect `https://github.com/Karanpatil1201/SIH2026`.
2. Settings:
   - **Root Directory:** `backend`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Add Environment Variables:
   - `GEMINI_API_KEY`: Your Gemini API key
   - `DATABASE_URL`: Your Supabase PostgreSQL connection string
   - `SECRET_KEY`: Your JWT encryption key
4. Copy your live Render URL (e.g. `https://varuna-backend.onrender.com`).

### Step 2: Point Vercel to Your Backend
Choose either:
- **In Browser (Instant):** On your Vercel website's login screen, click **"Configure Server"** at the bottom, paste your backend URL, and click **Save & Reload**!
- **In Vercel Settings:** Add environment variable `VITE_API_URL` = `https://varuna-backend.onrender.com/api` and redeploy.
