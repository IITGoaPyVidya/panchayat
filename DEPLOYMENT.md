# Railway Deployment Guide

## Prerequisites
- GitHub account
- Railway account (sign up at https://railway.app)
- Push your code to GitHub

## Deployment Steps

### 1. Push Code to GitHub
```bash
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

### 2. Deploy Backend to Railway

1. Go to https://railway.app
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Click "Add variables" and set:
   ```
   JWT_SECRET=your-super-secret-jwt-key-change-this
   DATABASE_URL=postgresql://... (Railway will provide this if you add PostgreSQL)
   UPLOAD_DIR=/app/data/uploads
   PORT=8000
   ```
5. In Settings:
   - Set **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - Note the generated URL (e.g., `https://your-app.railway.app`)

### 3. Add PostgreSQL Database (Optional but Recommended)

1. In your Railway project, click "New" → "Database" → "Add PostgreSQL"
2. Railway will automatically set the `DATABASE_URL` environment variable
3. Update your backend to use PostgreSQL instead of SQLite

### 4. Deploy Frontend to Railway

1. In the same Railway project, click "New" → "GitHub Repo"
2. Select the same repository
3. Click "Add variables" and set:
   ```
   API_BASE_URL=https://your-backend.railway.app
   PORT=8501
   ```
4. In Settings:
   - Set **Start Command**: `streamlit run frontend/app.py --server.port $PORT --server.address 0.0.0.0 --server.enableCORS=false --server.enableXsrfProtection=false`

### 5. Update CORS in Backend

Your backend should allow the frontend URL. Edit `backend/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Alternative: Single Service Deployment

If you want to deploy as a single service, create a startup script:

**start.sh**:
```bash
#!/bin/bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0
```

Then set Start Command to: `bash start.sh`

## Environment Variables Summary

**Backend Service:**
- `JWT_SECRET` - Your secret key for JWT tokens
- `DATABASE_URL` - Database connection string
- `UPLOAD_DIR` - Directory for uploaded files
- `PORT` - Port number (Railway sets this automatically)

**Frontend Service:**
- `API_BASE_URL` - Backend URL (e.g., https://your-backend.railway.app)
- `PORT` - Port number (Railway sets this automatically)

## Post-Deployment

1. Visit your frontend URL
2. Create an admin account
3. Test all features
4. Monitor logs in Railway dashboard

## Troubleshooting

- **502 Bad Gateway**: Check if the PORT variable is correctly used
- **CORS errors**: Update CORS settings in backend
- **Module not found**: Ensure requirements.txt is complete
- **Database errors**: Verify DATABASE_URL is set correctly

## Useful Commands

View logs:
```bash
railway logs
```

Connect to database:
```bash
railway connect
```
