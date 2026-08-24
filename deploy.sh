#!/bin/bash
PROJECT_ID=$(gcloud config get-value project)
REGION="us-central1"
SERVICE_NAME="skillforge-autonomous"
echo "Deploying SkillForge Autonomous to Google Cloud Run in $REGION..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2
