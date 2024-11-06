#!/bin/sh
set -e

echo "Executing entrypoint..."

# Ensure the database file exists for SQLite
if [ "$DATABASE_TYPE" = "sqlite" ]; then
    if [ ! -f "$DATABASE_PATH" ]; then
        echo "Creating database at $DATABASE_PATH..."
        touch $DATABASE_PATH
    fi
fi

exec "$@"