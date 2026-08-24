@echo off
REM Google Cloud Run Batch Deployment Script for KaushalSetu Taskmaster

set REGION=us-central1
set SERVICE_NAME=kaushalsetu-taskmaster

echo ==========================================================
echo 🌉 Deploying KaushalSetu Taskmaster to Google Cloud Run
echo ==========================================================

gcloud services enable containerregistry.googleapis.com run.googleapis.com

echo Building container image...
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/%SERVICE_NAME%:latest .

echo Deploying to Cloud Run...
gcloud run deploy %SERVICE_NAME% ^
    --image gcr.io/YOUR_PROJECT_ID/%SERVICE_NAME%:latest ^
    --platform managed ^
    --region %REGION% ^
    --allow-unauthenticated ^
    --port 8501

echo ==========================================================
echo ✅ Deployment Process Initiated
echo ==========================================================
pause
