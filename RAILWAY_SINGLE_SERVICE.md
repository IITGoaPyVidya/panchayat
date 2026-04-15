# Railway Single-Service Deployment Guide

## Simplified Deployment - Backend + Frontend in One Service

This configuration runs both backend (FastAPI) and frontend (Streamlit) in a single Railway service.

### Architecture
- **Backend**: Runs on port 8000 (internal)
- **Frontend**: Runs on Railway's PORT (public-facing)
- **Communication**: Frontend connects to backend via localhost:8000

### Deployment Steps

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Add Railway single-service deployment"
   git push origin main
   ```

2. **Deploy on Railway**
   - Go to [railway.app](https://railway.app)
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your `panchayat` repository
   - Railway will automatically detect the configuration

3. **Set Environment Variables**
   
   In Railway dashboard, add these variables:
   ```
   JWT_SECRET=your-super-secret-jwt-key-change-this-now
   DATABASE_URL=sqlite:///./data/society.db
   UPLOAD_DIR=./data/uploads
   API_BASE_URL=http://localhost:8000
   ```

4. **Deploy**
   - Railway will build and deploy automatically
   - The public URL will point to the Streamlit frontend
   - Backend runs internally on the same host

### Optional: Add PostgreSQL

For production, use PostgreSQL instead of SQLite:

1. Click "New" → "Database" → "Add PostgreSQL"
2. Railway automatically sets `DATABASE_URL`
3. Your app will use PostgreSQL automatically

### Environment Variables Explained

- `JWT_SECRET`: Secret key for JWT authentication (CHANGE THIS!)
- `DATABASE_URL`: Database connection (SQLite by default, or PostgreSQL)
- `UPLOAD_DIR`: Where to store uploaded files
- `API_BASE_URL`: Set to `http://localhost:8000` for single-service deployment

### Accessing Your App

Once deployed:
- Visit the Railway-provided URL
- Sign up as admin
- Start using your Society Management System!

### Monitoring

- View logs in Railway dashboard
- Check "Deployments" for build status
- Use "Metrics" to monitor resource usage

### Troubleshooting

**App won't start:**
- Check logs in Railway dashboard
- Verify all environment variables are set
- Ensure `start.sh` has execute permissions

**502 Bad Gateway:**
- Wait 30-60 seconds for services to fully start
- Backend needs to start before frontend

**Database errors:**
- SQLite works but PostgreSQL is recommended
- Check DATABASE_URL format

### Cost Optimization

Railway offers:
- $5/month hobby plan with $5 free credits
- Free trial for testing
- Single service = lower cost than separate services

### Updating Your App

```bash
git add .
git commit -m "Update app"
git push origin main
```

Railway auto-deploys on push to main branch.
