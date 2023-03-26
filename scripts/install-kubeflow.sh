#!/bin/bash

# Set the Kubeflow version
KUBEFLOW_VERSION="<KUBEFLOW_VERSION>"

# Clone the Kubeflow manifests repository with the specified version
git clone --depth 1 -b "${KUBEFLOW_VERSION}" https://github.com/kubeflow/manifests.git

# Create the k8-manifests directory if it doesn't exist
mkdir -p kf-k8-manifests

# Copy the manifests to the k8-manifests directory
cp -R manifests/distributions/stacks/gcp/kustomize/cluster kf-k8-manifests/

# Remove the cloned Git repository
rm -rf manifests

# Change to the k8-manifests/cluster directory
cd kf-k8-manifests/cluster

# Deploy Kubeflow components to the GKE cluster
kubectl apply -k .

# Wait for all resources to be ready
kubectl wait --for=condition=Ready --timeout=600s --all pods -n kubeflow

echo "Kubeflow deployment completed."
