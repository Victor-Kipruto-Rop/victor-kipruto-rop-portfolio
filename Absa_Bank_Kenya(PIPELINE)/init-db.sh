#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE absa_warehouse;
    CREATE DATABASE absa_open_banking;
    GRANT ALL PRIVILEGES ON DATABASE absa_warehouse TO $POSTGRES_USER;
    GRANT ALL PRIVILEGES ON DATABASE absa_open_banking TO $POSTGRES_USER;
EOSQL
