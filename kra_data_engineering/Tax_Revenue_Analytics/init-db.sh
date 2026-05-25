#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    SELECT 'CREATE DATABASE kra_warehouse'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'kra_warehouse')\gexec
    
    DO \$$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'kra_admin') THEN
            CREATE ROLE kra_admin WITH LOGIN PASSWORD 'kra_password';
        END IF;
    END
    \$$;
    
    GRANT ALL PRIVILEGES ON DATABASE kra_warehouse TO kra_admin;
EOSQL
