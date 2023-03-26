#!/bin/bash
set -e

# Set variables
PROJECT_ID="<YOUR_PROJECT_ID>"
CLUSTER_NAME="my-gke-cluster"
REGION="us-east1"
VPC_NAME="<my-vpc>"
SUBNET_NAME="<subnet-for-vpc>"
MIN_NODES=1
MAX_NODES=5
MACHINE_TYPE="n1-standard-2"

# Set the project and region
gcloud config set project "${PROJECT_ID}"
gcloud config set compute/region "${REGION}"

# Create a GKE cluster with autoscaling enabled and in the specified VPC and subnet
gcloud container clusters create "${CLUSTER_NAME}" \
  --network="${VPC_NAME}" \
  --subnetwork="${SUBNET_NAME}" \
  --machine-type="${MACHINE_TYPE}" \
  --enable-autoscaling \
  --num-nodes="${MIN_NODES}" \
  --min-nodes="${MIN_NODES}" \
  --max-nodes="${MAX_NODES}" \
  --region="${REGION}"

# Configure kubectl to use the new cluster
gcloud container clusters get-credentials "${CLUSTER_NAME}"
