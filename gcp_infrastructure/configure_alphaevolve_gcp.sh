#!/usr/bin/env bash
set -e

echo "=== CONFIGURING GCP FOR ALPHAEVOLVE (WP S2-G) ==="

export PROJECT_ID=$(gcloud config get-value project)
export REGION="us-central1"
export SERVICE_ACCOUNT="alphaevolve-runner-sa@${PROJECT_ID}.iam.gserviceaccount.com"
export REPO_NAME="stream2-alphaevolve"
export GCS_BUCKET="gs://socrateai-datalake-${PROJECT_ID}"

echo "Project ID: $PROJECT_ID"
echo "Region:     $REGION"
echo "SA Email:   $SERVICE_ACCOUNT"
echo "GCS Bucket: $GCS_BUCKET"

# 1. Enable Required GCP APIs
echo "Enabling Vertex AI, Compute Engine, GCS, and Artifact Registry APIs..."
gcloud services enable \
    aiplatform.googleapis.com \
    compute.googleapis.com \
    storage.googleapis.com \
    artifactregistry.googleapis.com \
    --project="$PROJECT_ID"

# 2. Create Artifact Registry Docker Repository
echo "Creating Artifact Registry repository: $REPO_NAME..."
gcloud artifacts repositories create "$REPO_NAME" \
    --repository-format=docker \
    --location="$REGION" \
    --description="AlphaEvolve CY4 Metric Search Docker Container Repository" \
    --project="$PROJECT_ID" || echo "Repository $REPO_NAME already exists."

# 3. Create Service Account for AlphaEvolve
echo "Creating Service Account: alphaevolve-runner-sa..."
gcloud iam service-accounts create alphaevolve-runner-sa \
    --display-name="AlphaEvolve Vertex AI Runner Service Account" \
    --project="$PROJECT_ID" || echo "Service account already exists."

# 4. Grant IAM Policy Bindings
echo "Assigning IAM roles to AlphaEvolve Service Account..."
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/aiplatform.user" --quiet

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/storage.objectAdmin" --quiet

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/artifactregistry.reader" --quiet

echo "=== GCP CONFIGURATION FOR ALPHAEVOLVE COMPLETED SUCCESSFULLY ==="
