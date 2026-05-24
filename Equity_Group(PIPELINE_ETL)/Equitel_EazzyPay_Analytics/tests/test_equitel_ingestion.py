import pytest
import pandas as pd
import os
from ingestion.generate_equitel_data import generate_equitel_data

def test_equitel_data_generation():
    test_dir = "test_ingest"
    generate_equitel_data(output_dir=test_dir)
    
    assert os.path.exists(f"{test_dir}/equitel_subscribers.csv")
    assert os.path.exists(f"{test_dir}/eazzypay_transactions.csv")
    
    df_sub = pd.read_csv(f"{test_dir}/equitel_subscribers.csv")
    assert not df_sub.empty
    assert "subscribers" in df_sub.columns
    
    # Cleanup
    import shutil
    shutil.rmtree(test_dir)
