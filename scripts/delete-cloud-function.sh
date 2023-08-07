#!/bin/bash

# Description: Script to delete a specific cloud function
# Usage: ./delete-cloud-function.sh

# Check if PIPELINE_NAME file exists
if [ ! -f "PIPELINE_NAME" ]; then
  echo "Error: PIPELINE_NAME file not found."
  exit 1
fi

# Retrieve the pipeline name
pipeline_name=$(cat PIPELINE_NAME)

# Delete the cloud function
echo "Deleting cloud function named ${pipeline_name}"
gcloud functions delete ${pipeline_name} --region=us-east1 --gen2 --quiet
