import pandas as pd
import numpy as np
import os
from sqlalchemy import create_engine

def clean_data(df, value_name):
    # Melt the dataframe
    id_vars = [df.columns[0]] # 'Industry'
    value_vars = df.columns[1:] # Years
    
    df_melted = pd.melt(df, id_vars=id_vars, value_vars=value_vars, var_name='year', value_name=value_name)
    df_melted = df_melted.rename(columns={df.columns[0]: 'industry'})
    
    # Clean industry strings
    df_melted['industry'] = df_melted['industry'].str.replace('\n', ' ')
    
    # Clean values
    df_melted[value_name] = df_melted[value_name].astype(str).str.replace(',', '')
    # Handle negative values that might be represented with hyphens instead of minus signs
    df_melted[value_name] = df_melted[value_name].str.replace('–', '-') 
    
    # Convert to numeric, errors='coerce' turns unparseable to NaN
    df_melted[value_name] = pd.to_numeric(df_melted[value_name], errors='coerce')
    
    return df_melted

def main():
    print("Processing Economic Survey Data...")
    
    # Paths
    gdp_current_path = "KRA(DATA ENGINEERING)/ingestion/gdp_by_industry_current_prices.csv"
    growth_rates_path = "KRA(DATA ENGINEERING)/ingestion/gdp_growth_rates.csv"
    
    if not os.path.exists(gdp_current_path) or not os.path.exists(growth_rates_path):
        print("Required CSV files not found.")
        return
        
    df_gdp = pd.read_csv(gdp_current_path)
    df_growth = pd.read_csv(growth_rates_path)
    
    # Clean and Melt
    df_gdp_clean = clean_data(df_gdp, 'gdp_current_prices_m_kes')
    df_growth_clean = clean_data(df_growth, 'growth_rate_percent')
    
    # Merge
    merged_df = pd.merge(df_gdp_clean, df_growth_clean, on=['industry', 'year'], how='outer')
    
    # Filter out empty or header rows
    merged_df = merged_df.dropna(subset=['gdp_current_prices_m_kes', 'growth_rate_percent'], how='all')
    merged_df = merged_df[merged_df['industry'].notna()]
    merged_df = merged_df[merged_df['industry'] != '']
    merged_df = merged_df[~merged_df['industry'].str.contains('Current Prices', case=False, na=False)]
    
    print("\nMerged Data (First 10 rows):")
    print(merged_df.head(10))
    
    # Connect and Ingest
    host = "postgres-kra" if os.path.exists("/.dockerenv") else "localhost"
    try:
        engine = create_engine(f'postgresql://kra_admin:kra_password@{host}:5438/kra_warehouse')
        merged_df.to_sql('raw_economic_survey_gdp', engine, if_exists='replace', index=False)
        print("\nSuccessfully ingested Economic Survey GDP data into raw_economic_survey_gdp.")
    except Exception as e:
        print(f"\nIngestion to DB failed: {e}")
        # Save output to processed file just in case
        output_dir = "KRA(DATA ENGINEERING)/Tax_Revenue_Analytics/data"
        os.makedirs(output_dir, exist_ok=True)
        merged_df.to_csv(f"{output_dir}/processed_economic_survey_gdp.csv", index=False)
        print(f"Saved processed data to {output_dir}/processed_economic_survey_gdp.csv")

if __name__ == "__main__":
    main()
