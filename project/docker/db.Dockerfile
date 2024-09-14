FROM postgres:16

# Run create.sql on init
ADD db/create.sql /docker-entrypoint-initdb.d
