#!/bin/sh

set -e

IMAGE_ID=$(docker inspect ${HEROKU_REGISTRY_IMAGE} --format={{.Id}})
PAYLOAD='{"updates": [{"type": "web", "docker_image": "'"$IMAGE_ID"'"}]}'

# See https://devcenter.heroku.com/articles/container-registry-and-runtime#api 
# And https://help.heroku.com/APMGC7PO/how-can-my-off-platform-application-use-the-heroku-api-to-obtain-my-app-s-config-vars-or-db-credentials
curl -n -X PATCH https://api.heroku.com/apps/$HEROKU_APP_NAME/formation \
  -d "${PAYLOAD}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/vnd.heroku+json; version=3.docker-releases" \
  -H "Authorization: Bearer ${HEROKU_AUTH_TOKEN}"
