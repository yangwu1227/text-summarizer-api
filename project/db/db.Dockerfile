FROM postgres:16

# Run create.sql on init
ADD create.sql /docker-entrypoint-initdb.d
