#!/usr/bin/env bash
set -e

echo "=== DEPLOYING STREAM 5 ALPHAEVOLVE K3-T2 POC TO GCP VERTEX AI ==="

export PROJECT_ID=$(gcloud config get-value project)
export REGION="us-central1"

gcloud ai custom-jobs create \
    --project="$PROJECT_ID" \
    --region="$REGION" \
    --config=config/gcp_vertex_job_spec.json

echo "=== STREAM 5 VERTEX AI JOB SUBMITTED SUCCESSFULLY ==="
