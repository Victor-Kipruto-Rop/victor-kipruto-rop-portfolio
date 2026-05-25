#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE mpesa_warehouse;
    CREATE USER mpesa_admin WITH PASSWORD 'mpesa_password';
    GRANT ALL PRIVILEGES ON DATABASE mpesa_warehouse TO mpesa_admin;
EOSQL
