#!/bin/bash

# Description: Script to deploy a pipeline
# Usage: ./deploy.sh

# Exit on any error
set -e

# Check if prod.env file exists
if [ ! -f "prod.env" ]; then
  echo "Error: prod.env file not found."
  exit 1
fi

# Source the environment variables
source prod.env

# Ensure PIPELINE_NAME is set
if [ -z "$PIPELINE_NAME" ]; then
  echo "Error: PIPELINE_NAME must be set in prod.env."
  exit 1
fi

# Variables
GCS_BUCKET="gs://your_bucket_name/${PIPELINE_NAME}"
CURRENT_DATETIME=$(date +%Y-%m-%d-%H-%M-%S)

# Function to copy files with specific headers
copy_with_headers() {
  gsutil -h "Cache-Control:private, max-age=0, no-transform" \
    cp "$1" "$2"
}

# Upload the pipeline build YAML file to Google Cloud Storage
echo "Uploading pipeline build YAML file..."
gsutil cp "./outputs/pipeline-build-final.yaml" "${GCS_BUCKET}/${PIPELINE_NAME}-final-compiled.yaml"

# Create a symlink to the latest version of the pipeline build YAML file
echo "Creating symlink to the latest version..."
copy_with_headers "${GCS_BUCKET}/${PIPELINE_NAME}-final-compiled.yaml" "${GCS_BUCKET}/latest/${PIPELINE_NAME}-final-compiled.yaml"

# Copy the pipeline build YAML file to a versioned folder
echo "Copying to versioned folder..."
copy_with_headers "${GCS_BUCKET}/${PIPELINE_NAME}-final-compiled.yaml" "${GCS_BUCKET}/${CURRENT_DATETIME}/${PIPELINE_NAME}-final-compiled.yaml"
