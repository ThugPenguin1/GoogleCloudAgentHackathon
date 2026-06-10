#!/bin/bash
# Deploy to Google Cloud Run

echo "Starting deployment for STEM Omni-Tutor..."

# Ensure we are logged in and sets the project
gcloud config set project project-9992272a-2b12-4f3d-95f

# Enable necessary APIs
gcloud services enable run.googleapis.com
gcloud services enable build.googleapis.com

# Deploy to Cloud Run using the local Dockerfile
# We inject the MONGODB_URI directly so the server can connect
gcloud run deploy stem-tutor-mcp \
    --source . \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars="MONGODB_URI=mongodb+srv://ThugPenguin1:Hunni246886425@googlecloudrapidagentha.ffu84im.mongodb.net/StemTutorDB?appName=GoogleCloudRapidAgentHackathon"

echo "Deployment complete! Your Agent Builder can now connect to the provided URL."
