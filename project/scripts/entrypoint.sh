#!/bin/sh

# Function to wait for a service to start
wait_for_service() {
  local service_name="$1"
  local service_host="$2"
  local service_port="$3"

  echo "Waiting for $service_name to start..."

  # The nc (Netcat) is utility to check network connectivity
  # The -z flag ensures nc only scan for open ports without sending data
  # If the connection fails (e.g., PostgreSQL or redis isn't up yet), the loop continues
  while ! nc -z "$service_host" "$service_port"; do
    sleep 0.1
  done

  echo "$service_name started"
}

# Wait for PostgreSQL and Redis to start
wait_for_service "PostgreSQL" "web-db" 5432
wait_for_service "Redis" "web-redis" 6379

# 'exec' replaces the current shell process with the command and arguments passed to the script, preserving all arguments as separate arguments
# For example: ./script.sh command --option value -> exec command --option value
exec "$@"
