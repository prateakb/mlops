#!/bin/bash
set -e

# Load environment variables from prod.env
if [ -f prod.env ]; then
  export $(cat prod.env | xargs)
else
  echo "Error: prod.env file not found."
  exit 1
fi

# Check that required environment variables are set
if [ -z "${PIPELINE_NAME}" ]; then
  echo "Error: PIPELINE_NAME is not set in prod.env."
  exit 1
fi

# Set pipeline name
export PIPELINE_NAME=$(echo "${PIPELINE_NAME}" | tr " " "_")
echo "pipeline name is ${PIPELINE_NAME}"

# Build and push Docker image
echo "building docker image"
docker build . -t "gcr.io/your-project/base-image-${PIPELINE_NAME}:latest"
docker push "gcr.io/your-project/base-image-${PIPELINE_NAME}:latest"

# Compile pipeline
echo "compiling pipeline"
python make_pipeline.py --from-build
