import pandas as pd
import numpy as np
import random
import os

def generate_agent_network_data(num_agents=1000, output_dir="MPESA_Safaricom(pipeline)/Agent_Network_Analytics/data"):
    os.makedirs(output_dir, exist_ok=True)
    
    counties = [
        "Nairobi", "Mombasa", "Kiambu", "Nakuru", "Machakos", "Kisumu", 
        "Uasin Gishu", "Kilifi", "Kajiado", "Nyeri"
    ]
    
    # Nairobi coordinates approx -1.28, 36.82
    # Mombasa coordinates approx -4.04, 39.66
    
    data = []
    for i in range(num_agents):
        agent_id = f"AG_{200000 + i}"
        county = random.choices(counties, weights=[40, 10, 8, 7, 7, 7, 6, 5, 5, 5])[0]
        
        # Simple coordinate simulation
        if county == "Nairobi":
            lat, lon = -1.28 + np.random.normal(0, 0.05), 36.82 + np.random.normal(0, 0.05)
        elif county == "Mombasa":
            lat, lon = -4.04 + np.random.normal(0, 0.03), 39.66 + np.random.normal(0, 0.03)
        else:
            lat, lon = -1.28 + np.random.uniform(-3, 3), 36.82 + np.random.uniform(-3, 3)
            
        txn_volume = np.random.exponential(100000)
        float_level = txn_volume * np.random.uniform(0.1, 0.3)
        commission = txn_volume * 0.01
        
        data.append({
            "agent_id": agent_id,
            "county": county,
            "latitude": lat,
            "longitude": lon,
            "monthly_txn_volume_kes": round(txn_volume, 2),
            "current_float_kes": round(float_level, 2),
            "monthly_commission_kes": round(commission, 2),
            "status": np.random.choice(["Active", "Inactive"], p=[0.9, 0.1]),
            "last_restock_days": np.random.randint(0, 10)
        })
        
    df = pd.DataFrame(data)
    df.to_csv(f"{output_dir}/agent_network_performance.csv", index=False)
    print(f"Generated {len(df)} agent records in {output_dir}")

if __name__ == "__main__":
    generate_agent_network_data()
