# Deployment Guide

## Google Cloud Run Deployment

### Step 1: Prerequisites

Install Google Cloud SDK:
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init
gcloud auth login
```

### Step 2: Configure Google Cloud Project

```bash
# Set your project ID
export PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### Step 3: Create Artifact Registry

```bash
gcloud artifacts repositories create ag2-repo \
  --repository-format=docker \
  --location=us-central1 \
  --description="AG2 Backend Docker Repository"
```

### Step 4: Create Service Account for GitHub Actions

```bash
# Create service account
gcloud iam service-accounts create github-actions \
  --display-name="GitHub Actions Service Account"

# Grant permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

# Create and download key
gcloud iam service-accounts keys create key.json \
  --iam-account=github-actions@$PROJECT_ID.iam.gserviceaccount.com
```

### Step 5: Configure GitHub Secrets

Add these secrets to your GitHub repository (Settings → Secrets and variables → Actions):

1. **GCP_PROJECT_ID**: Your Google Cloud project ID
2. **GCP_SA_KEY**: Contents of the `key.json` file (entire JSON)
3. **GEMINI_API_KEY**: Your Google Gemini API key
4. **DEEPSEEK_API_KEY**: Your DeepSeek API key (optional)

### Step 6: Manual Deployment (Alternative to GitHub Actions)

```bash
# Authenticate Docker with Artifact Registry
gcloud auth configure-docker us-central1-docker.pkg.dev

# Build the Docker image
docker build -t us-central1-docker.pkg.dev/$PROJECT_ID/ag2-repo/ag2-backend:latest .

# Push to Artifact Registry
docker push us-central1-docker.pkg.dev/$PROJECT_ID/ag2-repo/ag2-backend:latest

# Deploy to Cloud Run
gcloud run deploy ag2-backend \
  --image=us-central1-docker.pkg.dev/$PROJECT_ID/ag2-repo/ag2-backend:latest \
  --platform=managed \
  --region=us-central1 \
  --allow-unauthenticated \
  --set-env-vars="GEMINI_API_KEY=$GEMINI_API_KEY,DEEPSEEK_API_KEY=$DEEPSEEK_API_KEY,FRONTEND_URL=https://ag2-predictive-state-editor.vercel.app,ENVIRONMENT=production" \
  --memory=2Gi \
  --cpu=2 \
  --timeout=300 \
  --concurrency=80 \
  --min-instances=0 \
  --max-instances=10
```

### Step 7: Get Service URL

```bash
gcloud run services describe ag2-backend \
  --region=us-central1 \
  --format='value(status.url)'
```

### Step 8: Test Deployment

```bash
# Get the service URL
export SERVICE_URL=$(gcloud run services describe ag2-backend --region=us-central1 --format='value(status.url)')

# Test health endpoint
curl $SERVICE_URL/health

# Test capabilities
curl $SERVICE_URL/api/capabilities
```

## Vercel Frontend Configuration

After deploying the backend, update your Vercel frontend with the backend URL:

1. Go to your Vercel project settings
2. Add environment variable:
   - **Name**: `NEXT_PUBLIC_COPILOTKIT_API_URL`
   - **Value**: `https://your-backend-url.run.app/api/copilotkit`
3. Redeploy the frontend

## Monitoring and Logs

View logs in Google Cloud Console:
```bash
gcloud run services logs read ag2-backend \
  --region=us-central1 \
  --limit=50
```

Or stream logs in real-time:
```bash
gcloud run services logs tail ag2-backend \
  --region=us-central1
```

## Troubleshooting

### Issue: Deployment fails with authentication error
**Solution**: Ensure the service account has the correct permissions and the key.json is valid.

### Issue: Health check fails
**Solution**: Check environment variables are set correctly, especially API keys.

### Issue: CORS errors
**Solution**: Verify `FRONTEND_URL` environment variable matches your frontend domain exactly.

### Issue: Container fails to start
**Solution**: Check Cloud Run logs for errors. Ensure all dependencies are installed in Dockerfile.

## Security Best Practices

1. **Never commit API keys or secrets** - Always use environment variables
2. **Rotate service account keys** regularly
3. **Use secret manager** for production environments
4. **Enable Cloud Armor** for DDoS protection
5. **Set up Cloud Monitoring** alerts for errors and high latency
6. **Implement rate limiting** in production

## Cost Optimization

- Set `--min-instances=0` to scale to zero when not in use
- Adjust `--memory` and `--cpu` based on actual usage
- Set appropriate `--timeout` values
- Monitor usage in Google Cloud Console

## Rollback

To rollback to a previous version:
```bash
# List revisions
gcloud run revisions list --service=ag2-backend --region=us-central1

# Rollback to specific revision
gcloud run services update-traffic ag2-backend \
  --region=us-central1 \
  --to-revisions=REVISION_NAME=100
```
