#!/bin/bash

# Description: Script to test integration with a cloud function
# Usage: ./integration-test-cloud-function.sh <path/to/payload.json>

# Exit on any error
set -e

# Check if the payload file is provided
if [ -z "$1" ]; then
  echo "Error: Please provide the path to the payload JSON file."
  exit 1
fi

# Source environment variables
source configurations.env

# Make a POST request to the cloud function
curl -XPOST ${CLOUD_FUNCTION_URL} -H "Authorization: Bearer $(gcloud auth print-identity-token)" -H "Content-Type:application/json" -d @$1
