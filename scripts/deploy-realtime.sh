#!/bin/bash
set -e

export PIPELINE_NAME=$(cat PIPELINE_NAME)
echo "${PIPELINE_NAME}">configurations.env
python restructure-main.py
echo "pipeline name is ${PIPELINE_NAME}"
echo "The following packages will be installed by default"
echo "$(cat requirements.txt)"
echo "deploying a cloud function called ${PIPELINE_NAME}"
gcloud functions deploy ${PIPELINE_NAME} --gen2 --source=../${PIPELINE_NAME} --region=us-east1 --runtime=python310 --trigger-http --memory=1Gi --quiet