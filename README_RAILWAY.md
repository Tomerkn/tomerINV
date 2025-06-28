# Railway Deployment Guide

## Services to Deploy:

1. **PostgreSQL Database** - Data storage
2. **Web Application** - Flask portfolio management app  
3. **Ollama AI Service** - AI model with llama3.1:8b

## Deployment Steps:

### Step 1: Prepare Project
```bash
git add .
git commit -m "Ready for Railway deployment"
git push
```

### Step 2: Create Railway Project

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your project

### Step 3: Add Services

#### Service 1: PostgreSQL Database
1. Click "New Service"
2. Select "Database" → "PostgreSQL"
3. Railway will create database automatically

#### Service 2: Ollama AI
1. Click "New Service" 
2. Select "GitHub Repo"
3. Use: `ollama/ollama`
4. Set environment variable: `OLLAMA_HOST=0.0.0.0`

#### Service 3: Web Application
1. Click "New Service"
2. Select "GitHub Repo"
3. Choose your project repository

### Step 4: Configure Environment Variables

In your Web Application service, set these variables:

```
DATABASE_URL=postgresql://postgres:password@host:port/database
PORT=8080
OLLAMA_URL=http://ollama-service:11434
```

### Step 5: Deploy

1. Railway will automatically deploy all services
2. Check deployment logs for any errors
3. Your app will be available at the provided URL

## Troubleshooting:

- Check Railway deployment logs
- Verify environment variables are set correctly
- Ensure all services are running
- Test database connection
- Test Ollama AI connection

## Local Testing:

```bash
export DATABASE_URL="your_postgresql_url"
export PORT=8080
export OLLAMA_URL="http://localhost:11434"
python app.py
``` 