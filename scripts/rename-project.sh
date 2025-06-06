#!/bin/bash

# Script to rename project from zcare-platform to zionix-be-v1
# This script helps with the migration process

set -e

OLD_NAME="zcare-platform"
NEW_NAME="zionix-be-v1"

echo "Starting migration from ${OLD_NAME} to ${NEW_NAME}..."

# Function to find and replace in files
find_and_replace() {
    echo "Searching for occurrences of ${OLD_NAME} in $1"
    grep -l "${OLD_NAME}" $1 | xargs -r sed -i "s/${OLD_NAME}/${NEW_NAME}/g"
}

# Update Docker Compose file
if [ -f "docker-compose.yml" ]; then
    echo "Updating docker-compose.yml..."
    sed -i "s/${OLD_NAME}/${NEW_NAME}/g" docker-compose.yml
fi

# Update Kubernetes manifests
echo "Updating Kubernetes manifests..."
find_and_replace "k8s/**/*.yaml"

# Update README and documentation
echo "Updating documentation..."
find_and_replace "*.md"
find_and_replace "**/*.md"

# Update service configurations
echo "Updating service configurations..."
find_and_replace "gateway/kong/*.yaml"

# Update CI/CD workflows
echo "Updating CI/CD workflows..."
find_and_replace ".github/workflows/*.yaml"

# Update Docker image references
echo "Updating Docker image references..."
sed -i "s/zcare\//zionix\//g" docker-compose.yml
sed -i "s/zcare\//zionix\//g" k8s/**/*.yaml

# Update namespace references
echo "Updating namespace references..."
sed -i "s/namespace: zcare/namespace: zionix/g" k8s/**/*.yaml

echo "Migration from ${OLD_NAME} to ${NEW_NAME} completed successfully!"
echo "Please review the changes and make any necessary manual adjustments."