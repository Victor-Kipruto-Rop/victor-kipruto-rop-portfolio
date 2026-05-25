Setup instructions

1. Copy .env.sample to .env and update MPESA_DATABASE_URL to point to your PostGIS instance.
2. Install Python dependencies: pip install -r requirements.txt
3. Start PostGIS (docker compose up -d postgis) or point to existing DB.
4. Place CBK CSV/XLSX files in data/cbk or PDFs in data/cbk_pdfs and run:
   - python ingestion/pdf_extractor.py
   - python ingestion/cbk_loader.py
5. Run dbt models and/or Airflow DAGs as needed.
