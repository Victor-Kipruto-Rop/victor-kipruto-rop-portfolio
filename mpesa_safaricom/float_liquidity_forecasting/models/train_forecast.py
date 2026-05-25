import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
import os
from datetime import timedelta

def train_demand_forecast():
    print("🚀 Training Float Demand Forecaster...")
    
    if not os.path.exists('data/historical_float.csv'):
        print("Error: Historical data missing.")
        return
        
    df = pd.read_csv('data/historical_float.csv')
    df['date'] = pd.to_datetime(df['date'])
    
    # Feature Engineering
    df['lag_1'] = df['float_demand_kes'].shift(1)
    df['lag_7'] = df['float_demand_kes'].shift(7)
    df['rolling_7d'] = df['float_demand_kes'].rolling(window=7).mean()
    
    df = df.dropna()
    
    # Simple model features
    X = df[['lag_1', 'lag_7', 'rolling_7d']]
    y = df['float_demand_kes']
    
    model = Ridge()
    model.fit(X, y)
    
    # Generate 30-day forecast
    last_date = df['date'].max()
    forecast_dates = [last_date + timedelta(days=i) for i in range(1, 31)]
    
    # Simplified recursive forecast simulation
    preds = []
    curr_data = X.iloc[-1].values.reshape(1, -1)
    for _ in range(30):
        p = model.predict(curr_data)[0]
        preds.append(p)
        # Update features for next step (simplified)
        curr_data = np.array([[p, curr_data[0][0], np.mean([p, curr_data[0][0]])]])
        
    forecast_df = pd.DataFrame({
        'date': forecast_dates,
        'forecasted_demand_kes': preds
    })
    
    forecast_df.to_csv('data/demand_forecast.csv', index=False)
    print("✅ 30-day forecast generated.")

if __name__ == "__main__":
    train_demand_forecast()
