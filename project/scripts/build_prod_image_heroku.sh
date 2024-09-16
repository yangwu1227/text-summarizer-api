#!/bin/sh

source "$(dirname "$0")/platform_selection.sh"

# Exit immediately if any command fails
set -e

# Prompt the user for the location of the production Dockerfile and build context
read -p "Enter the relative or absolute path to the production Dockerfile: " dockerfile_path
read -p "Enter the relative or absolute path to the production build context: " build_context_path
# Prompt the user for the target platform
select_target_platform
# Heroku app name
read -p "Enter the name of the Heroku app: " app_name

# Check if the Dockerfile and build context exist
if [ -f "$dockerfile_path" ] && [ -d "$build_context_path" ]; then

    # Build the production image
    image_tag="registry.heroku.com/$app_name/web"
    echo "Building the production image..."
    DOCKER_BUILDKIT=1 docker buildx build --platform "$target_platforms" -f "$dockerfile_path" -t "$image_tag" "$build_context_path"
    echo "Docker image built successfully!"
else
    echo "The specified Dockerfile or build context does not exist"
    exit 1
fi

echo "The production image tag is: $image_tag:latest"
