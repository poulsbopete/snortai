# Deploying SnortAI to Vercel

This guide explains how to deploy the SnortAI application to Vercel.

## Prerequisites

1. A Vercel account (sign up at https://vercel.com)
2. Vercel CLI installed: `npm i -g vercel`
3. Environment variables configured

## Setup Steps

### 1. Install Vercel CLI (if not already installed)
```bash
npm i -g vercel
```

### 2. Login to Vercel
```bash
vercel login
```

### 3. Set Environment Variables

Set the following environment variables in Vercel dashboard or via CLI:

```bash
vercel env add ELASTICSEARCH_URL
vercel env add ELASTICSEARCH_API_KEY
vercel env add OPENAI_API_KEY
vercel env add ELASTICSEARCH_INDEX
vercel env add OPENAI_MODEL
vercel env add AI_BACKEND
```

Or set them in the Vercel dashboard:
- Go to your project settings
- Navigate to "Environment Variables"
- Add each variable for Production, Preview, and Development environments

### 4. Deploy

#### First Deployment
```bash
vercel
```

#### Production Deployment
```bash
vercel --prod
```

### 5. Build Frontend (if needed)

If you need to rebuild the frontend:
```bash
cd frontend
npm install
npm run build
cd ..
```

## Project Structure for Vercel

- `api/index.py` - Vercel serverless function entry point
- `app/` - FastAPI application code
- `frontend/build/` - React frontend build output
- `vercel.json` - Vercel configuration
- `.vercelignore` - Files to exclude from deployment

## Configuration

The `vercel.json` file configures:
- Python serverless function at `/api/index.py`
- Routes API requests to the FastAPI app
- Serves static frontend files from `/frontend/build/`
- Sets function timeout to 30 seconds
- Allocates 1024MB memory

## Environment Variables

Required environment variables:
- `ELASTICSEARCH_URL` - Your Elasticsearch cluster URL
- `ELASTICSEARCH_API_KEY` - API key for Elasticsearch
- `ELASTICSEARCH_INDEX` - Index name (default: "snort-alerts")
- `OPENAI_API_KEY` - OpenAI API key (optional if using MCP server)
- `OPENAI_MODEL` - OpenAI model name (default: "gpt-4o-mini")
- `AI_BACKEND` - Backend to use: "openai" or "onechat" (default: "openai")

## API Endpoints

Once deployed, your API will be available at:
- `https://your-project.vercel.app/api/` - All API endpoints
- `https://your-project.vercel.app/` - Frontend interface

## Troubleshooting

### Function Timeout
If you experience timeouts, increase the `maxDuration` in `vercel.json` (up to 60 seconds on Pro plan).

### Memory Issues
Increase the `memory` setting in `vercel.json` if you encounter memory errors.

### Environment Variables Not Working
- Ensure variables are set for the correct environment (Production/Preview/Development)
- Redeploy after adding new environment variables
- Check variable names match exactly (case-sensitive)

### Import Errors
- Ensure `PYTHONPATH` is set correctly in `vercel.json`
- Check that all dependencies are in `requirements.txt`

## Differences from AWS Lambda

1. **Environment Variables**: Set in Vercel dashboard instead of AWS Secrets Manager
2. **Static Files**: Served directly by Vercel, not through FastAPI
3. **Function Limits**: 
   - Free: 10s timeout, 1024MB memory
   - Pro: 60s timeout, 3008MB memory
4. **Cold Starts**: Similar to Lambda, but may vary

## Continuous Deployment

Vercel automatically deploys when you push to your connected Git repository:
- `main` branch → Production
- Other branches → Preview deployments
- Pull requests → Preview deployments
