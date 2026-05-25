#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE sector_dwh;
    CREATE USER sector_admin WITH PASSWORD 'sector_password';
    GRANT ALL PRIVILEGES ON DATABASE sector_dwh TO sector_admin;
EOSQL
