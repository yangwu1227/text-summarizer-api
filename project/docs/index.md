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

### Build and Run the Services

**Note**: All the commands should be run from the root of the project where `docker-compose.yml` is located. In addition, Compose V2 is used, so the `docker-compose` command is replaced with `docker compose`.

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
$ docker exec <service-name> aerich init -t app.db.TORTOISE_ORM
```

The `-t` flag specifies the module path to the Tortoise-ORM settings inside the `app.db` module. This will add a `tool.aerich` section to the `pyproject.toml` file.

#### Initialize Database

To initialize the database:

```bash
$ docker exec <service-name> aerich init-db
```

This will create the tables in the database based on the models defined in `app/models/` along with the first migration file in the `migrations/` directory.

### Migration Workflow

From this point on, since the local `migrations/` directory is synced with the `migrations/` directory on the container (for both `prod` & `dev`), each time a change is made to the model, the following steps should be taken:

1. In development mode, update the model in `app/models/` and run the following command to generate a new migration:

```bash
$ docker exec <service-name> aerich migrate --name <migration-name>
```

2. Apply the migration in development mode:

```bash
$ docker exec <service-name> aerich upgrade
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

The PostgreSQL database can be accessed using [psql](https://www.postgresql.org/docs/current/app-psql.html), a terminal-based front-end to PostgreSQL.

```bash
$ docker exec -it <service-name> psql -U postgres
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
