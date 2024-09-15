#!/bin/sh

# Exit immediately if any command fails
set -e

# Prompt the user for the location of the production Dockerfile and build context
read -p "Enter the relative or absolute path to the production Dockerfile: " dockerfile_path
read -p "Enter the relative or absolute path to the production build context: " build_context_path
# Prompt the user for the target platform
read -p "Enter the target platform (e.g., linux/amd64, linux/arm64, or both): " target_platforms
# Github username, repository, and PAT
read -p "Enter a Github username: " github_username
read -p "Enter a Github repository name: " github_repo_name
read -p "Enter a Github personal access token (PAT): " github_pat
# Name of the production image
read -p "Enter the name of the production image: " image_name

# Check if the Dockerfile and build context exist
if [ -f "$dockerfile_path" ] && [ -d "$build_context_path" ]; then

    # Build the production image
    image_tag="ghcr.io/$github_username/$github_repo_name/$image_name:latest"

    # Authenticate with the Github packages with masking the PAT
    echo "Authenticating with Github packages..."
    echo "$github_pat" | docker login ghcr.io -u "$github_username" --password-stdin
    unset github_pat

    echo "Building the production image..."
    DOCKER_BUILDKIT=1 docker buildx build --platform "$target_platforms" -f "$dockerfile_path" -t "$image_tag" "$build_context_path"
    echo "Docker image built successfully!"

    echo "Pushing the production image to Github packages..."
    docker push "$image_tag"
else
    echo "The specified Dockerfile or build context does not exist"
    exit 1
fi
