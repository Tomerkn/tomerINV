# Railway Deployment Guide

## Environment Variables

Set these in Railway:

```
DATABASE_URL=${{inv_db_Postgres.DATABASE_URL}}
OLLAMA_URL=http://ollama-3cac589c.railway.internal:11434
PORT=4000
```

## Files Structure

```
tomerINV/
├── app.py                    # Main Flask application
├── dbmodel.py               # Database models and operations
├── ollamamodel.py           # AI model integration
├── requirements.txt         # Python dependencies
├── Dockerfile              # Web app container
├── Dockerfile.ollama       # Ollama AI container
├── railway.json            # Web app deployment config
├── railway.ollama.json     # Ollama deployment config
├── templates/              # HTML templates
└── static/                 # CSS, JS, images
```

## Deployment Steps

### 1. Deploy PostgreSQL Database
- Create new service in Railway
- Choose PostgreSQL template
- Note the DATABASE_URL

### 2. Deploy Web Application
- Create new service from GitHub repo
- Set environment variables:
  ```
  DATABASE_URL=${{inv_db_Postgres.DATABASE_URL}}
  PORT=4000
  ```
- Railway will use `railway.json` config

### 3. Deploy Ollama AI Service
- Create new service from same GitHub repo
- Use `Dockerfile.ollama`
- Set railway.json to `railway.ollama.json`
- This will download llama3.1:8b model (4.9GB)

## Local Testing

```bash
# Set environment variables
export DATABASE_URL="your_postgresql_url"
export PORT=4000
export OLLAMA_URL="http://localhost:11434"  # Optional

# Run the application
python app.py
```

## Troubleshooting

### Health Checks
- `/ping` - Simple OK response
- `/health` - Detailed health check
- `/health-simple` - Basic health check

### Common Issues
1. **Database connection** - Check DATABASE_URL
2. **Port conflicts** - Ensure PORT=4000 everywhere
3. **Ollama connection** - Check OLLAMA_URL

### Logs
Check Railway logs for:
- Database connection errors
- Port binding issues
- Import errors
- AI service connectivity 