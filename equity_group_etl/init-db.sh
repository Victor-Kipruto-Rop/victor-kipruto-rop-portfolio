#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE equitel_analytics;
    CREATE DATABASE pan_africa_platform;
    GRANT ALL PRIVILEGES ON DATABASE equitel_analytics TO $POSTGRES_USER;
    GRANT ALL PRIVILEGES ON DATABASE pan_africa_platform TO $POSTGRES_USER;
EOSQL
