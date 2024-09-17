# Text Summarizer API

This project creates an asynchronous RESTful API built with Python, FastAPI, and Docker. It allows users to create, retrieve, update, and delete text summaries. The app integrates with a PostgreSQL database and is containerized for both local development and deployment.

**Credit**: This project is based on [TestDriven.io's FastAPI TDD project](https://github.com/testdrivenio/fastapi-tdd-docker).

[**Project Workflow Documentation**](https://yangwu1227.github.io/text-summarizer-api/)

## Architecture & Tech Stack

- **Docker**: Containerized application for local development and deployment.
- **FastAPI**: Provides asynchronous API endpoints.
- **PostgreSQL**: Used as the database for storing summaries.
- **Tortoise ORM & Aerich**: ORM for database models, and Aerich for handling migrations.
- **GitHub Actions CI**: Automated testing, Docker builds, and pushing images to GitHub Packages.
- **Heroku Deployment**: FastAPI app and PostgreSQL running in Docker containers.

## Project Structure

```bash
├── compose.yml                    # Docker Compose configuration for local development
└── project
    ├── app/                       # FastAPI app, Routes, Tortoise-ORM & Pydantic models
    ├── docker/                    # Dockerfiles and ignore files for prod and dev environments
    ├── migrations/                # Database migration files
    ├── scripts/                   # Shell scripts for building and deploying
    └── tests/                     # Unit and integration tests
```

## API Endpoints

- **Create a summary:** `POST /summaries/`

    ```bash
    curl -X POST "https://text-summarizer-d918be4fb9c8.herokuapp.com/summaries/" \
    -H "Content-Type: application/json" \
    -d '{"url": "https://realpython.com/pointers-in-python/"}'
    ```

    The payload also supports two additional optional parameters:
    - `summarization_method`: Specifies the summarization algorithm. Supported values are `lsa`, `lex_rank`, `text_rank`, and `edmundson`. If not provided, the default is `lsa`.
    - `sentence_count`: Specifies the number of sentences in the generated summary, with a range of 5 to 30. If not provided, the default is 10.

    Example request with all parameters:

    ```bash
    curl -X POST "https://text-summarizer-d918be4fb9c8.herokuapp.com/summaries/" \
    -H "Content-Type: application/json" \
    -d '{"url": "https://realpython.com/pointers-in-python/", "summarization_method": "lex_rank", "sentence_count": 15}'
    ```

    For more information on the supported summarization algorithms, see the [sumy documentation](https://github.com/miso-belica/sumy/blob/main/docs/summarizators.md).

- **Get a summary:** `GET /summaries/{id}/`

  ```bash
  # Format the response using jq
  curl "https://text-summarizer-d918be4fb9c8.herokuapp.com/summaries/{id}/" | jq
  ```

- **Get all summaries:** `GET /summaries/`

  ```bash
  # Format the response using jq
  curl "https://text-summarizer-d918be4fb9c8.herokuapp.com/summaries/" | jq
  ```

- **Update a summary:** `PUT /summaries/{id}/`

  ```bash
  curl -X PUT "https://text-summarizer-d918be4fb9c8.herokuapp.com/summaries/{id}/" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://realpython.com/pointers-in-python/", "update_summary": "Updated summary text"}'
  ```

- **Delete a summary:** `DELETE /summaries/{id}/`

  ```bash
  curl -X DELETE "https://text-summarizer-d918be4fb9c8.herokuapp.com/summaries/{id}/" 
  ```

## Testing the API

Test the API via the [Swagger UI](https://text-summarizer-d918be4fb9c8.herokuapp.com/docs), which provides a user-friendly interface for interacting with the API endpoints.

## Deployment

The application is deployed on Heroku using Docker. The `scripts/` directory contains shell scripts for automating the deployment process:

1. `build_and_push_image_github.sh`: Builds a Docker image using a specified Dockerfile and build context, then pushes it to GitHub Packages. It prompts for GitHub credentials and a target platform (amd64, arm64, or both). The image is tagged and pushed to the GitHub container registry (`ghcr.io`).

2. `build_prod_image_heroku.sh`: Builds a production Docker image for a Heroku app using a specified Dockerfile and build context. It also allows platform selection and tags the image for Heroku's container registry.

3. `deploy_heroku.sh`: Automates deployment to Heroku. Logs into the Heroku container registry, provisions a PostgreSQL database if needed, pushes the Docker image, releases it, and applies database migrations using [Aerich](https://github.com/tortoise/aerich). This is only used for the very first deployment, as subsequent deployments are automated via the CI-CD pipeline.

4. `entrypoint.sh`: Waits for PostgreSQL to be ready before starting the FastAPI application. Used in the development container to ensure the app connects to the database only after it is fully initialized.

5. `platform_selection.sh`: Prompts the user to select a target platform for Docker image builds: `amd64`, `arm64`, or both. Sourced by other build scripts to standardize platform selection.

6. `release.sh`: Releases the Docker image to Heroku by updating the app's formation via the Heroku API. Fetches the image ID and automates deployment. Used in CI pipelines for automated releases.
