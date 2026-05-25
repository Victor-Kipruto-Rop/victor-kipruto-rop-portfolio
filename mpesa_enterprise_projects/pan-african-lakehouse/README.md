# 🏠 Pan-African Medallion Lakehouse

This project implements a high-scale data lakehouse architecture for consolidating M-Pesa enterprise data across multiple African markets.

## 🏗️ Medallion Architecture
- **Bronze Layer**: Raw data ingested directly from M-Pesa API gateways.
- **Silver Layer**: Cleaned, deduplicated, and standardized transactions with multi-currency normalization.
- **Gold Layer**: Analytical marts optimized for executive reporting and ML feature engineering.

## 🛠️ Tech Stack
- **DuckDB**: Local analytical engine for processing Parquet files.
- **dbt**: Management of the Medallion transformation layers.
- **Parquet**: Highly efficient columnar storage format.

## Data Sources
This lakehouse consolidates data from:
- `ingestion/raw_api_logs.csv`
- `ingestion/market_config.json`
- GSMA Global Mobile Money benchmarks
