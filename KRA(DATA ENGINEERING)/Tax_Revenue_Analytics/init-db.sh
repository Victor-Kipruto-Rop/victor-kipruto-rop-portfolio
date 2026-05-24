#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE kra_warehouse;
    CREATE USER kra_admin WITH PASSWORD 'kra_password';
    GRANT ALL PRIVILEGES ON DATABASE kra_warehouse TO kra_admin;
EOSQL
