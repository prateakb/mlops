#!/bin/bash
set -e

# Set variables
PROJECT_ID="your_project_id"
CLUSTER_NAME="your_cluster_name"
REGION="your_region"
VPC_NAME="your_vpc_name"
SUBNET_NAME="your_subnet_name"
MIN_NODES=1
MAX_NODES=5
MACHINE_TYPE="your_machine_type"

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
