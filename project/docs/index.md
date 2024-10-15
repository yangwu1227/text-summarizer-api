# Workflows

## Environment Setup

### Install PDM

The dependency manager used in this project is [pdm](https://github.com/pdm-project/pdm). To install it, run the following command:

```bash
$ curl -sSL https://pdm-project.org/install-pdm.py | python3 -
```

Or, alternatively, other [installation methods](https://pdm-project.org/en/latest/#installation) can be used.

### Install Dependencies

The dependencies are broken into groups:

* Default dependencies: required for the core functionality of the project in production.

* Development dependencies: required for development, testing, and documentation.

The specified python version in `pyproject.toml` is `>=3.11`, and so a **python 3.11** interpreter should be used. 

#### Conda

To do so with [conda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html):

```bash
$ conda search python | grep " 3\.\(10\|11\|12\)\."
$ yes | conda create --name text_summarizer_api python=3.11.9
$ conda activate text_summarizer_api
$ pdm use -f $(which python3)
$ pdm install
```

#### Vitualenv

To do so with [virtualenv](https://github.com/pypa/virtualenv), use the [pdm venv](https://pdm-project.org/en/latest/reference/cli/#venv) command:

```bash 
$ pdm venv create --name text_summarizer_api --with virtualenv 3.11.9 
# To activate the virtual environment
$ eval $(pdm venv activate text_summarizer_api) 
$ pdm install
```

---

## Docker Compose 

The development environment is set up using [Docker Compose](https://docs.docker.com/compose/). This setup defines two services: 

* **web**: sets up the application based on `dev.Dockerfile`.

* **wev-db**: sets up a PostgreSQL database based on `db.Dockerfile`, which simply [Add](https://docs.docker.com/reference/dockerfile/#add)s a `.sql` file to the container at `/docker-entrypoint-initdb.d/`. Two databases are created: `web_dev` for development and `web_test` for testing; neither is used in production.

* **web-redis**: sets up a redis server for rate limiting.

```yaml
name: 'text-summarizer-api'

services:

  web:
    build:
      context: ./project
      dockerfile: docker/dev.Dockerfile
    container_name: dev-api
    command: uvicorn app.main:app --reload --workers 1 --host 0.0.0.0 --port 8000
    volumes:
      - ./project/app:/opt/project/app
      - ./project/tests:/opt/project/tests
      - ./project/pyproject.toml:/opt/project/pyproject.toml
      - ./project/migrations:/opt/project/migrations
    ports:
      - 8004:8000
    environment:
      - ENVIRONMENT=dev
      - TESTING=0
      - DOCS_URL=/docs
      - DATABASE_URL=postgres://postgres:postgres@web-db:5432/web_dev       
      - DATABASE_TEST_URL=postgres://postgres:postgres@web-db:5432/web_test  
      - REDIS_ENDPOINT=web-redis:6379
      - REDIS_PASSWORD=redis
    depends_on:
      - web-db
      - web-redis

  web-db:
    build:
      context: ./project
      dockerfile: docker/db.Dockerfile
    container_name: db
    expose:
      - 5432
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres

  web-redis:
    image: redis:bookworm
    container_name: redis
    expose:
      - 6379
    command: ["redis-server", "--requirepass", "redis"]
```

### Build and Run the Services

**Note**: All the commands should be run from the root of the project where `compose.yml` is located. In addition, Compose V2 is used, so the `docker-compose` command is replaced with `docker compose`.

To build the images and run the containers in the background:

```bash
$ docker compose up --detach --build
```

Directories such as `app/`, `tests/`, `migrations/`, and the `pyproject.toml` file are **bind-mounted** to their respective counterparts in the `web` service container. This setup allows for automatic reloading of the application when changes are made to the code during development.

To stop the containers without removing them:

```bash
$ docker compose stop
```

To stop, remove the containers, and remove named volumes:

```bash
$ docker compose down --volumes
```

### Logs

To view the logs of the services:

```bash
$ docker compose logs <service-name>
```

### Interactive Shell

To run an interactive shell in a service:

```bash
# Or /bin/bash
$ docker compose exec <service-name> /bin/sh
```

---

## Database Migrations

The database migrations are managed using [aerich](https://github.com/tortoise/aerich), which is a tool specifically designed for [Tortoise-ORM](https://github.com/tortoise/tortoise-orm).

### First Time Setup

#### Configuration

To set up the initial config file and generate the root migrate location:

```bash
$ docker compose exec <service-name> aerich init -t app.db.TORTOISE_ORM
```

The `-t` flag specifies the module path to the Tortoise-ORM settings inside the `app.db` module. This will add a `tool.aerich` section to the `pyproject.toml` file.

#### Initialize Database

To initialize the database:

```bash
$ docker compose exec <service-name> aerich init-db
```

This will create the tables in the database based on the models defined in `app/models/` along with the first migration file in the `migrations/` directory.

### Migration Workflow

From this point on, since the local `migrations/` directory is synced with the `migrations/` directory on the container (for both `prod` & `dev`), each time a change is made to the model, the following steps should be taken:

1. In development mode, update the model in `app/models/` and run the following command to generate a new migration:

```bash
$ docker compose exec <service-name> aerich migrate --name <migration-name>
```

2. Apply the migration in development mode:

```bash
$ docker compose exec <service-name> aerich upgrade
```

3. Run tests and any other necessary checks.

4. Merge the changes to the `main` branch, which will trigger a deployment to the production environment. 

5. Once the changes are deployed, apply the migration in production via the [heroku](https://devcenter.heroku.com/articles/heroku-cli-commands#heroku-run) CLI:

```bash
$ heroku run aerich upgrade --app <app-name>
```

See the aerich's [usage](https://github.com/tortoise/aerich?tab=readme-ov-file#usage) documentation for more commands and details.

---

## PSQL

The PostgreSQL database within the docker container can be accessed using [psql](https://www.postgresql.org/docs/current/app-psql.html), a terminal-based front-end to PostgreSQL.

```bash
$ docker compose exec -it <service-name> psql -U <username>
```

### Connect 

To connect to a specific PostgreSQL database within the server:

```bash
$ \c <database-name>
```

### List Tables

To list the tables in the connected database:

```bash
$ \dt
```

### Quit

To quit the `psql` shell:

```bash
$ \q
```

## Rate Limiting with Redis

Rate limiting is implemented using [fastapi-limiter](https://github.com/long2ice/fastapi-limiter), which requires [Redis](https://github.com/redis/redis-py) to store the rate limiting data. Redis runs locally via Docker Compose in development and testing environments, while in production, [Redis Cloud](https://redis.io/enterprise/) is used.

### Local Redis Setup

The Redis service is defined in `compose.yml`:

```yaml
services:
  web-redis:
    image: redis:bookworm
    container_name: redis
    expose:
      - 6379
    command: ["redis-server", "--requirepass", "redis"]
```

Redis is exposed internally for communication between services. The application connects to Redis through the `REDIS_ENDPOINT` and `REDIS_PASSWORD` environment variables.

### CI Redis Setup

In the CI environment, a Redis service is set up in an independent container:

* Create a network that the Redis service and the application service can connect to:

```yaml
- name: Create Docker network
  id: create-docker-network
  run: docker network create test-network
```

* Start the Redis service (pulling the [image](https://hub.docker.com/_/redis) from Docker Hub):

```yaml
- name: Start redis container
  id: start-redis-container
  run: |
    docker run \
      --name web-redis \
      --network test-network \
      --detach \
      --expose 6379 \
      redis:bookworm \ 
      redis-server --requirepass redis
```

* When running the development container, connect to the same network:

```yaml
- name: Run docker container
  id: run-docker-container
  run: |
    docker run \
      --name test-container \
      --network test-network \
      --detach \
      -e PORT=8765 \
      -e ENVIRONMENT=dev \
      -e DATABASE_URL="${DB_URL}" \
      -e DATABASE_TEST_URL="${DB_URL}" \
      -e REDIS_ENDPOINT=web-redis:6379 \
      -e REDIS_PASSWORD=redis \
      -p 5003:8765 \
      ${{ env.IMAGE }}:latest
```

### Production Redis Setup

In production, a free Redis Cloud database is utilized. To set up a Redis Cloud account, refer to [this guide](https://redis.io/docs/latest/operate/rc/rc-quickstart/). After creating the account, follow the instructions in [this guide](https://redis.io/learn/create/heroku/portal) to link it to Heroku.

The following information from the Redis Cloud console is required:

* **Public endpoint**
* **Password**

It is important to keep this information secure, as it will be necessary for the application to connect to the Redis database.

### Application Redis Initialization

Redis is initialized in the application using a lifespan context manager in `app/db.py`:

```python
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    redis_endpoint = os.getenv("REDIS_ENDPOINT")
    redis_encoded_password = quote(os.getenv("REDIS_PASSWORD"), safe="")
    redis_url = f"redis://:{redis_encoded_password}@{redis_endpoint}"
    redis_connection = redis.from_url(redis_url, encoding="utf8")
    await FastAPILimiter.init(redis_connection)

    async with RegisterTortoise(
        app=app,
        db_url=os.environ.get("DATABASE_URL"),
        modules={"models": ["app.models.tortoise_model"]},
        generate_schemas=False,
        add_exception_handlers=True,
    ):
        yield

    await FastAPILimiter.close()
```

This implementation ensures that `fastapi-limiter` effectively manages Redis-based rate limiting. The `lifespan` context manager is responsible for establishing a connection to Redis at the start of the application and closing it after the application has finished running. 

Before deploying to Heroku, ensure that the `REDIS_ENDPOINT` (public endpoint) and `REDIS_PASSWORD` (password) environment variables are set as [config vars](https://devcenter.heroku.com/articles/config-vars#managing-config-vars) in the Heroku application settings.
