# Absa Open Banking API Data Product

## Architecture
The pipeline integrates with the Absa Developer Sandbox to ingest transactional data. 

### Data Flow
1. **Extraction**: `scheduled_sync.py` pulls daily transaction logs.
2. **Scoring**: `credit_scorer.py` evaluates cash-flow health.
3. **Storage**: Raw data lands in PostgreSQL `absa_open_banking`.
4. **Transformation**: dbt models create analytical marts for customer activity.
5. **Consumption**: FastAPI endpoints expose scoring and categorization to downstream apps.

## Credit Scoring Engine
The scoring model (0-1000) weights the following:
- **Stability (30%)**: Volatility of monthly inflows.
- **Surplus (30%)**: Monthly savings rate.
- **Liquidity (20%)**: Transaction velocity.
- **Risk (20%)**: Identification of debt-related keywords.
