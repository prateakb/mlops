#!/bin/bash

# Set your GCP project ID and OAuth credentials
PROJECT_ID="<YOUR_PROJECT_ID>"
PROJECT_NUMBER="<YOUR_PROJECT_NUMBER>"
CLIENT_ID="<YOUR_OAUTH_CLIENT_ID>"
CLIENT_SECRET="<YOUR_OAUTH_CLIENT_SECRET>"

# Set the Kubeflow version
KUBEFLOW_VERSION="<KUBEFLOW_VERSION>"

# Clone the Kubeflow manifests repository with the specified version
git clone --depth 1 -b "${KUBEFLOW_VERSION}" https://github.com/kubeflow/manifests.git

# Create the k8-manifests directory if it doesn't exist
mkdir -p k8-manifests

# Copy the manifests to the k8-manifests directory
cp -R manifests/distributions/stacks/gcp/kustomize/cluster k8-manifests/

# Remove the cloned Git repository
rm -rf manifests

# Change to the k8-manifests/cluster directory
cd k8-manifests/cluster

# Deploy Kubeflow components to the GKE cluster
kubectl apply -k .

# Wait for all resources to be ready
kubectl wait --for=condition=Ready --timeout=600s --all pods -n kubeflow

# Retrieve the backend service ID for the envoy-ingress service
ENVOY_INGRESS_NAME=envoy-ingress
NAMESPACE=kubeflow
ENVOY_INGRESS_BACKEND_NAME=$(kubectl get svc -n "${NAMESPACE}" "${ENVOY_INGRESS_NAME}" -o jsonpath='{.metadata.annotations.ingress\.kubernetes\.io\/backends}' | jq -r 'keys[0]')
BACKEND_SERVICE_ID=$(gcloud compute backend-services list --filter="name=${ENVOY_INGRESS_BACKEND_NAME}" --format="value(id)")

# Update the istio-ingressgateway deployment with the backend service ID
kubectl patch deployment istio-ingressgateway -n kubeflow --type strategic --patch "
spec:
  template:
    spec:
      containers:
      - name: istio-proxy
        env:
        - name: GCP_IAP_AUTH_ENABLED
          value: \"true\"
        - name: GCP_IAP_PROJECT_NUMBER
          value: \"${PROJECT_NUMBER}\"
        - name: GCP_IAP_BACKEND_SERVICE_ID
          value: \"${BACKEND_SERVICE_ID}\"
"

echo "Kubeflow deployment with IAP completed."
