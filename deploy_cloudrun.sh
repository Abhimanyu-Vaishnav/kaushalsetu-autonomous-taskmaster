#!/bin/bash
# Google Cloud Run Deployment Script for SkillForge Autonomous

PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
REGION="us-central1"
SERVICE_NAME="skillforge-autonomous"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest"

echo "=========================================================="
echo "⚡ Deploying SkillForge Autonomous to Google Cloud Run"
echo "=========================================================="
echo "Project ID: ${PROJECT_ID}"
echo "Region:     ${REGION}"
echo "Image:      ${IMAGE_NAME}"
echo "=========================================================="

# 1. Enable required GCP services
echo "1. Enabling GCP Artifact Registry & Cloud Run APIs..."
gcloud services enable containerregistry.googleapis.com run.googleapis.com

# 2. Build Container Image using Google Cloud Build
echo "2. Building container image via Cloud Build..."
gcloud builds submit --tag ${IMAGE_NAME} .

# 3. Deploy to Cloud Run
echo "3. Deploying service to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME} \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --set-env-vars GEMINI_API_KEY=${GEMINI_API_KEY} \
    --port 8501

echo "=========================================================="
echo "✅ Deployment Complete!"
echo "Service URL:"
gcloud run services describe ${SERVICE_NAME} --platform managed --region ${REGION} --format 'value(status.url)'
echo "=========================================================="
