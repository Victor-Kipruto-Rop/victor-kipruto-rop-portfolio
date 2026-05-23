# M-Pesa Float & Liquidity Forecasting Pipeline

> **Enterprise-grade time series forecasting system for M-Pesa agent float demand prediction**

## 📋 Overview

This production-ready pipeline forecasts M-Pesa float demand at agent level using advanced time-series models (Prophet + LSTM ensemble), historical transaction patterns, public holidays, salary cycles, and regional events. It provides 7-day ahead forecasts to optimize float top-up logistics and reduce stockouts/excess inventory.

### Key Features

- 🎯 **Ensemble Forecasting**: Prophet + LSTM with dynamic weight optimization
- 📊 **Advanced Features**: Salary cycles, event calendars, regional patterns
- 🔄 **MLOps Ready**: MLflow tracking, model versioning, automated retraining
- 📅 **Airflow DAGs**: Daily forecasts and monthly retraining pipelines
- 🐳 **Docker Support**: Full stack containerization (Postgres, Airflow, MLflow, Grafana)
- ✅ **Production Grade**: Comprehensive testing, logging, error handling
- 📈 **Monitoring**: Prometheus metrics, Grafana dashboards

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose (optional)
- PostgreSQL 13+ (if not using Docker)

### Installation

```bash
# Clone and setup
git clone <repo>
cd Float_Liquidity_Forecasting

# Quick setup
make setup
make install

# Or manually
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Running with Docker

```bash
# Start all services
make docker-up

# Access interfaces
# - Airflow: http://localhost:8080 (admin/admin)
# - MLflow: http://localhost:5000
# - Grafana: http://localhost:3000 (admin/admin)
# - pgAdmin: http://localhost:5050 (admin@example.com/admin)

# Run tests
make test

# Cleanup
make docker-down
```

## 📁 Project Structure

```
Float_Liquidity_Forecasting/
├── config.py                 # Configuration management
├── logger.py                 # Logging setup
├── db.py                     # Database utilities
├── requirements.txt          # Python dependencies
├── docker-compose.yml        # Full stack containerization
├── Makefile                  # Development commands
├── .env                      # Environment variables
│
├── ingestion/               # Data ingestion
│   ├── cbk_stats.py        # CBK M-Pesa statistics
│   ├── calendar_client.py   # Kenya holidays API
│   └── __init__.py
│
├── features/               # Feature engineering
│   ├── feature_engineering.py  # Time series features
│   ├── salary_cycle.py        # Salary cycle analysis
│   ├── event_calendar.py      # Event features
│   └── __init__.py
│
├── models/                # Forecasting models
│   ├── prophet_model.py   # Facebook Prophet
│   ├── lstm_model.py      # LSTM neural network
│   ├── ensemble.py        # Ensemble combination
│   ├── evaluate.py        # Evaluation metrics
│   └── __init__.py
│
├── dags/                 # Airflow DAGs
│   ├── forecast_dag.py   # Daily forecasting
│   └── retrain_dag.py    # Monthly retraining
│
├── tests/               # Test suite
│   ├── test_features.py
│   ├── test_ingestion.py
│   ├── test_models.py
│   └── __init__.py
│
├── notebooks/          # Jupyter notebooks
├── data/              # Data storage
├── outputs/           # Forecast outputs
├── models/            # Trained models
├── logs/              # Application logs
└── docs/              # Documentation
```

## 🛠️ Development

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-coverage

# Run specific test
pytest tests/test_models.py -v

# Run fast tests (exclude integration)
make test-fast
```

### Code Quality

```bash
# Format code
make format

# Run linting
make lint

# Type checking
make type-check

# All quality checks
make dev-setup
```

## 🔄 Pipelines

### Daily Forecasting DAG

Runs daily at 2 AM to generate 7-day forecasts:

```
ingest_data → engineer_features → train_models → generate_forecast → save_forecast
```

### Monthly Retraining DAG

Runs 1st of month at 3 AM to retrain models with latest data.

## 📊 Features

### Time Series Features
- Lag features (1, 7, 30 days)
- Rolling statistics (mean, std, min, max)
- Trend analysis (linear trend, differencing)
- Seasonal features (day of week, month, cyclical)

### Domain Features
- Salary cycles (25th, 28th of month)
- Public holidays
- School fee periods (May-June, Sept-Oct)
- Election periods
- Shopping seasons

## 🤖 Models

- **Prophet**: Seasonal decomposition with holiday effects
- **LSTM**: 2-layer neural network (64→32 units) with dropout
- **Ensemble**: Weighted combination (50% Prophet, 50% LSTM)

## 📚 Documentation

See documentation for:
- API details
- Data dictionary
- Model architecture
- Troubleshooting
- Performance tuning

## 🔐 Configuration

Create `.env` file with database and API credentials.

## 🧪 Testing

- Unit tests for all modules
- Integration tests for pipelines
- Coverage target: >80%

## 📞 Support

For issues or questions, contact the Data Engineering team or check the troubleshooting guide in docs/.
