#!/bin/bash

set -e

# Set your AWS profile, region, and target EKS cluster
AWS_PROFILE="<YOUR_AWS_PROFILE>"
AWS_REGION="<YOUR_AWS_REGION>"
CLUSTER_NAME="<YOUR_EKS_CLUSTER_NAME>"

# Set the Kubeflow version
KUBEFLOW_VERSION="<KUBEFLOW_VERSION>"

# Update kubeconfig to use the target EKS cluster
aws eks update-kubeconfig --region "$AWS_REGION" --name "$CLUSTER_NAME" --profile "$AWS_PROFILE"

# Install and configure the AWS ALB Ingress Controller
kubectl apply -k "github.com/aws/eks-charts/stable/aws-load-balancer-controller//crds?ref=master"
helm repo add eks https://aws.github.io/eks-charts
helm upgrade -i aws-load-balancer-controller eks/aws-load-balancer-controller \
  --set clusterName="$CLUSTER_NAME" \
  --set serviceAccount.create=false \
  --set serviceAccount.name=aws-load-balancer-controller \
  --set region="$AWS_REGION" \
  --set vpcId="<YOUR_AWS_VPC_ID>" \
  -n kube-system \
  --create-namespace

# Clone the Kubeflow manifests repository with the specified version
git clone --depth 1 -b "${KUBEFLOW_VERSION}" https://github.com/kubeflow/manifests.git

# Create the k8-manifests directory if it doesn't exist
mkdir -p k8-manifests

# Copy the manifests to the k8-manifests directory
cp -R manifests/distributions/stacks/aws/kustomize/cluster k8-manifests/

# Remove the cloned Git repository
rm -rf manifests

# Change to the k8-manifests/cluster directory
cd k8-manifests/cluster

# Deploy Kubeflow components to the EKS cluster
kubectl apply -k .

# Wait for all resources to be ready
kubectl wait --for=condition=Ready --timeout=600s --all pods -n kubeflow

echo "Kubeflow deployment on AWS EKS completed."
