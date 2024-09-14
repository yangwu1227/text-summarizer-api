FROM python:3.11.10-slim-bookworm AS python-base

# Prevents Python from creating pyc files
ENV PYTHONDONTWRITEBYTECODE=1 \
    # Ensure python I/O is unbuffered so that log messages are flushed to the stream
    PYTHONUNBUFFERED=1 \
    # Working directory inside the container
    PROJECT_ROOT_PATH=/opt/project \
    # PDM version
    PDM_VERSION=2.18.2 \
    # Disable pdm update check
    PDM_CHECK_UPDATE=0

# Create an unprivileged user and group to run the application
RUN addgroup --system api && adduser --system --ingroup api api-user

FROM python-base AS build-stage

# Install pdm 
WORKDIR $PROJECT_ROOT_PATH
# Copy project toml and lock files onto the container
COPY pyproject.toml pdm.lock ./
# 1. --G test: install packages in the test group in addition to the default production dependencies
# 2. --no-editable: all packages to be installed in non-editable mode
# 3. --check: validate whether the lock is up to date
RUN pip install pdm==$PDM_VERSION && pdm install --check --no-editable -G test

FROM python-base AS production

RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-traditional \
    gcc \
    postgresql \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Retrieve packages from build stage
COPY --from=build-stage $PROJECT_ROOT_PATH $PROJECT_ROOT_PATH
ENV PATH=${PROJECT_ROOT_PATH}/.venv/bin:$PATH
WORKDIR $PROJECT_ROOT_PATH
# Copy source code from local project root onto the container
COPY app ./app
COPY tests ./tests
COPY entrypoint.sh ./
RUN chmod +x entrypoint.sh

USER api-user
ENTRYPOINT ["./entrypoint.sh"]