#!/bin/bash
set -e
CLUSTER_NAME="kubeflow-pipelines-dev"
REGION="us-east1"
MACHINE_TYPE="e2-standard-2" # A machine with 2 CPUs and 8GB memory.
SCOPES="cloud-platform" # This scope is needed for running some pipeline samples. Read the warning below for its security implication

gcloud container clusters create $CLUSTER_NAME \
     --region $REGION \
     --machine-type $MACHINE_TYPE \
     --scopes $SCOPES 