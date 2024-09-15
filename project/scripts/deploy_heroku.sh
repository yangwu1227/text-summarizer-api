#!/bin/sh

set -e
if ! command -v heroku &> /dev/null; then
    echo "The Heroku CLI could not be found"
    exit 1
fi

# Prompt the user for the Heroku app name
read -p "Enter the name of the Heroku app: " app_name

# Check if the Heroku app exists
if ! heroku domains --app "$app_name" --json > /dev/null 2>&1; then
    # Create the Heroku app if it does not exist
    echo "App not found. Creating the Heroku app..."
    heroku create "$app_name"
else
    echo "Heroku app '$app_name' already exists. Skipping app creation."
fi

# Log in to the Heroku container registry
echo "Logging in to the Heroku container registry..."
heroku container:login
heroku stack:set container --app "$app_name"

# Provision a Heroku PostgreSQL database
addons=$(heroku addons --app "$app_name" --json)
if [ "$addons" = "[]" ]; then
    echo "Provisioning a Heroku PostgreSQL database..."
    heroku addons:create heroku-postgresql:essential-0 --app "$app_name"
else
    echo "Addons already exist, skipping the database provisioning step."
fi

# Tag the image for the Heroku container registry
image_tag=registry.heroku.com/$app_name/web

# Check if the Docker image exists
if docker images | grep -q "$image_tag"; then
    # Push the image to the Heroku container registry
    echo "Pushing the Docker image to the Heroku container registry..."
    docker push "$image_tag"
    echo "Docker image pushed to Heroku"

    # Release the image to the Heroku app
    echo "Releasing the Docker image to the Heroku app..."
    heroku container:release web --app "$app_name"
    echo "Docker image released"

    # Apply migrations to the Heroku PostgreSQL database
    echo "Applying database migrations..."
    heroku run aerich upgrade --app "$app_name"
    echo "Migrations applied to the database"
    
else
    echo "Docker image not found, skipping the push, release, and migration steps."
fi
