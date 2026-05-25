import json
import os
from kafka import KafkaConsumer
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

# Database setup
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5439')
DB_NAME = os.getenv('DB_NAME', 'mpesa_warehouse')
DB_USER = os.getenv('DB_USER', 'mpesa_admin')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'mpesa_password')

engine = create_engine(f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')

def create_table():
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS raw_transactions (
                transaction_id UUID PRIMARY KEY,
                sender_id VARCHAR(50),
                receiver_id VARCHAR(50),
                amount NUMERIC(15, 2),
                transaction_type VARCHAR(50),
                county VARCHAR(50),
                timestamp TIMESTAMP,
                is_fraud INTEGER,
                ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))

def run_consumer():
    print("🚀 Initializing M-Pesa Kafka Consumer...")
    create_table()
    
    consumer = KafkaConsumer(
        'mpesa_transactions',
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='mpesa_ingestion_group',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    
    print("📡 Waiting for transactions...")
    for message in consumer:
        tx = message.value
        try:
            with engine.begin() as conn:
                conn.execute(text("""
                    INSERT INTO raw_transactions (transaction_id, sender_id, receiver_id, amount, transaction_type, county, timestamp, is_fraud)
                    VALUES (:transaction_id, :sender_id, :receiver_id, :amount, :transaction_type, :county, :timestamp, :is_fraud)
                """), tx)
            print(f"Ingested: {tx['transaction_id']}")
        except Exception as e:
            print(f"Error ingesting transaction: {e}")

if __name__ == "__main__":
    run_consumer()
