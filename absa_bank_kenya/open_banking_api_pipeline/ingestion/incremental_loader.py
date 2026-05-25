import logging
import pandas as pd
from sqlalchemy import text

class IncrementalLoader:
    """
    Handles incremental loading of transaction data by tracking the last synced transaction ID or timestamp.
    """
    def __init__(self, db_engine):
        self.engine = db_engine

    def get_last_sync_timestamp(self, table_name="raw_transactions"):
        """Fetches the latest transaction date from the target table."""
        query = text(f"SELECT MAX(transaction_date) FROM {table_name}")
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query).scalar()
                return result
        except Exception as e:
            logging.warning(f"Could not fetch last sync timestamp (table might be empty): {e}")
            return None

    def load_new_data(self, df, table_name="raw_transactions"):
        """Loads data that is newer than the existing records in the database."""
        last_sync = self.get_last_sync_timestamp(table_name)
        
        if last_sync and not df.empty:
            # Ensure df transaction_date is datetime
            df['transaction_date'] = pd.to_datetime(df['transaction_date'])
            # Filter for new records only
            new_records = df[df['transaction_date'] > pd.to_datetime(last_sync)]
            
            if not new_records.empty:
                new_records.to_sql(table_name, self.engine, if_exists='append', index=False)
                logging.info(f"Incrementally loaded {len(new_records)} new records.")
                return len(new_records)
            else:
                logging.info("No new records to load.")
                return 0
        else:
            # Full load if table is empty
            df.to_sql(table_name, self.engine, if_exists='append', index=False)
            logging.info(f"Performed initial load of {len(df)} records.")
            return len(df)
