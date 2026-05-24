import pandas as pd
import os

def create_mpesa_snapshots(project_root="MPESA_Safaricom(pipeline)"):
    # Snapshots are generated from the existing generated data/logic
    # since these projects are highly simulation-based for the portfolio
    
    # 1. Fraud Detection Data
    fraud_data = pd.read_csv(f"{project_root}/Fraud_Anomaly_Detection/data/mpesa_fraud_training.csv")
    fraud_snap_dir = f"{project_root}/Fraud_Anomaly_Detection/dashboards/snapshots"
    os.makedirs(fraud_snap_dir, exist_ok=True)
    fraud_data.to_csv(f"{fraud_snap_dir}/mpesa_fraud_training.csv", index=False)
    print(f"Snapshot created: {fraud_snap_dir}/mpesa_fraud_training.csv")
    
    # 2. Agent Network Data
    agent_data = pd.read_csv(f"{project_root}/Agent_Network_Analytics/data/agent_network_performance.csv")
    agent_snap_dir = f"{project_root}/Agent_Network_Analytics/dashboards/snapshots"
    os.makedirs(agent_snap_dir, exist_ok=True)
    agent_data.to_csv(f"{agent_snap_dir}/agent_network_performance.csv", index=False)
    print(f"Snapshot created: {agent_snap_dir}/agent_network_performance.csv")
    
    # 3. Real-Time Streaming (Mocked for Snapshot)
    # We create a static version of the 'live' stream
    streaming_data = []
    for i in range(50):
        streaming_data.append({
            "txn_id": f"MP_{2000+i}",
            "timestamp": pd.Timestamp.now() - pd.Timedelta(minutes=i*2),
            "amount": 1000 * (i % 7 + 1),
            "status": "Success",
            "type": "C2B"
        })
    df_stream = pd.DataFrame(streaming_data)
    stream_snap_dir = f"{project_root}/Real_Time_Transaction_Streaming/dashboards/snapshots"
    os.makedirs(stream_snap_dir, exist_ok=True)
    df_stream.to_csv(f"{stream_snap_dir}/raw_mpesa_streaming.csv", index=False)
    print(f"Snapshot created: {stream_snap_dir}/raw_mpesa_streaming.csv")

if __name__ == "__main__":
    create_mpesa_snapshots()
