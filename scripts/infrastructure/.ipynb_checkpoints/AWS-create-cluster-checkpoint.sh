#!/bin/bash
set -e

# Set variables
AWS_REGION="<YOUR_AWS_REGION>"
CLUSTER_NAME="my-eks-cluster"
VPC_ID="<YOUR_VPC_ID>"
SUBNET_IDS="<SUBNET_ID_1>,<SUBNET_ID_2>,<SUBNET_ID_3>"
MIN_NODES=1
MAX_NODES=5
INSTANCE_TYPE="t2.medium"
KEY_NAME="<YOUR_KEY_PAIR_NAME>"
ROLE_ARN="<YOUR_EKS_SERVICE_ROLE_ARN>"

# Create the EKS cluster
aws eks create-cluster \
  --region "${AWS_REGION}" \
  --name "${CLUSTER_NAME}" \
  --role-arn "${ROLE_ARN}" \
  --resources-vpc-config "subnetIds=${SUBNET_IDS}"

# Wait for the EKS cluster to be created
aws eks wait cluster-active \
  --region "${AWS_REGION}" \
  --name "${CLUSTER_NAME}"

# Configure kubectl to use the new cluster
aws eks update-kubeconfig \
  --region "${AWS_REGION}" \
  --name "${CLUSTER_NAME}"
