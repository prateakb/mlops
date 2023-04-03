#!/bin/bash
set -e
# Source the environment variables
source prod.env

# Set variables
PROJECT_ID="your_project_id"
REPO_ID="your_repo_id"
GCS_BUCKET="gs://your_bucket_name/${PIPELINE_NAME}"
CURRENT_DATETIME=$(date +%Y-%m-%d-%H-%M-%S)

# Upload the pipeline build YAML file to Google Cloud Storage
gsutil cp "./outputs/pipeline-build-final.yaml" "${GCS_BUCKET}/${PIPELINE_NAME}-final-compiled.yaml"

# Create a symlink to the latest version of the pipeline build YAML file
gsutil -h "Cache-Control:private, max-age=0, no-transform" \
    cp "${GCS_BUCKET}/${PIPELINE_NAME}-final-compiled.yaml" "${GCS_BUCKET}/latest/${PIPELINE_NAME}-final-compiled.yaml"

# Copy the pipeline build YAML file to a versioned folder
gsutil -h "Cache-Control:private, max-age=0, no-transform" \
    cp "${GCS_BUCKET}/${PIPELINE_NAME}-final-compiled.yaml" "${GCS_BUCKET}/${CURRENT_DATETIME}/${PIPELINE_NAME}-final-compiled.yaml"
