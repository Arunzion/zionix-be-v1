#!/bin/bash

# Deployment script for Zionix Backend Services
# This script handles deployment to different environments
# Optimized for large-scale microservices architecture

set -e

# Default to dev environment if not specified
ENV=${1:-dev}
valid_envs=("dev" "staging" "prod")
PARALLEL_JOBS=${2:-5}  # Number of parallel deployments

# Validate environment
if [[ ! " ${valid_envs[*]} " =~ " ${ENV} " ]]; then
    echo "Error: Invalid environment '${ENV}'. Must be one of: ${valid_envs[*]}"
    exit 1
fi

echo "Deploying Zionix Backend to ${ENV} environment with parallelism: ${PARALLEL_JOBS}..."

# Create namespace if it doesn't exist
kubectl get namespace zionix-${ENV} 2>/dev/null || kubectl create namespace zionix-${ENV}

# Apply infrastructure components first
echo "Deploying infrastructure components..."
kubectl apply -k ../k8s/overlays/${ENV}/infrastructure

# Wait for infrastructure to be ready
echo "Waiting for infrastructure components to be ready..."
kubectl -n zionix-${ENV} wait --for=condition=available --timeout=300s deployment -l tier=infrastructure

# Apply Kubernetes configurations for all microservices
echo "Applying microservices configurations..."
kubectl apply -k ../k8s/overlays/${ENV}/microservices

# Get all deployments and wait for them in parallel
echo "Waiting for deployments to be ready..."
DEPLOYMENTS=$(kubectl -n zionix-${ENV} get deployments -l tier=microservice -o name)

# Use xargs to wait for deployments in parallel
echo "$DEPLOYMENTS" | xargs -P $PARALLEL_JOBS -I {} kubectl -n zionix-${ENV} wait --for=condition=available --timeout=300s {}

# Apply Service Mesh and API Gateway configurations
echo "Configuring Service Mesh and API Gateway..."
kubectl apply -f ../k8s/base/service-mesh.yaml

# Dynamically apply all gateway configurations
echo "Applying API Gateway routes for all microservices..."
find ../gateway/kong -name "*.yaml" -type f | xargs -P $PARALLEL_JOBS -I {} kubectl apply -f {}

# Setup monitoring and observability
echo "Setting up monitoring and observability..."
kubectl apply -k ../observability

# Register services with service mesh
echo "Registering services with service mesh..."
kubectl -n zionix-${ENV} label namespace zionix-${ENV} istio-injection=enabled --overwrite

# Verify deployment health
echo "Verifying deployment health..."
kubectl -n zionix-${ENV} get pods
kubectl -n zionix-${ENV} get services

# Run post-deployment tests
echo "Running post-deployment tests..."
for service in $(kubectl -n zionix-${ENV} get deployments -l tier=microservice -o jsonpath='{.items[*].metadata.name}'); do
  echo "Testing $service health endpoint..."
  kubectl -n zionix-${ENV} exec deploy/$service -- curl -s http://localhost:8000/health || echo "Health check failed for $service"
done

echo "Deployment to ${ENV} completed successfully!"
echo "Access the API Gateway at: $(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.status.loadBalancer.ingress[0].ip}')"
echo "Access Grafana at: $(kubectl -n monitoring get service grafana -o jsonpath='{.status.loadBalancer.ingress[0].ip}'):3000"