#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE kcb_financials;
    CREATE DATABASE kcb_mpesa;
    
    CREATE USER kcb_admin WITH PASSWORD 'kcb_password';
    GRANT ALL PRIVILEGES ON DATABASE kcb_financials TO kcb_admin;
    GRANT ALL PRIVILEGES ON DATABASE kcb_mpesa TO kcb_admin;
EOSQL
