#!/bin/bash

# Description: Script to deploy a real-time model as a cloud function
# Usage: ./deploy-realtime.sh

# Exit on any error
set -e

# Check if PIPELINE_NAME file exists
if [ ! -f "PIPELINE_NAME" ]; then
  echo "Error: PIPELINE_NAME file not found."
  exit 1
fi

# Retrieve the pipeline name
export PIPELINE_NAME=$(cat PIPELINE_NAME)
echo "${PIPELINE_NAME}">configurations.env

# Run restructuring script
echo "Restructuring the model..."
python restructure-main.py

# Print deployment information
echo "Pipeline name is ${PIPELINE_NAME}"
echo "The following packages will be installed by default:"
echo "$(cat requirements.txt)"

# Deploy the cloud function
echo "Deploying a cloud function called ${PIPELINE_NAME}"
gcloud functions deploy ${PIPELINE_NAME} --gen2 --source=../${PIPELINE_NAME} --region=us-east1 --runtime=python310 --trigger-http --memory=1Gi --quiet
