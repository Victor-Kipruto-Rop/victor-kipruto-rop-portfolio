import json
import time
import random
from kafka import KafkaProducer
from faker import Faker
from datetime import datetime

fake = Faker()

def get_transaction():
    """Generates a random M-Pesa like transaction."""
    transaction_types = ['PayBill', 'BuyGoods', 'SendMoney', 'Withdrawal', 'Airtime']
    counties = ['Nairobi', 'Mombasa', 'Kiambu', 'Nakuru', 'Uasin Gishu', 'Kisumu', 'Kajiado']
    
    return {
        'transaction_id': fake.uuid4(),
        'sender_id': fake.msisdn()[:12],
        'receiver_id': fake.msisdn()[:12],
        'amount': round(random.uniform(10, 150000), 2),
        'transaction_type': random.choice(transaction_types),
        'county': random.choice(counties),
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'is_fraud': random.choices([0, 1], weights=[0.99, 0.01])[0]
    }

def run_producer():
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda v: json.dumps(json_serial(v) if not isinstance(v, str) else v).encode('utf-8')
    )
    
    # Wait for Kafka to be ready in docker
    time.sleep(10)
    
    print("🚀 Starting M-Pesa Transaction Stream...")
    while True:
        transaction = get_transaction()
        producer.send('mpesa_transactions', transaction)
        print(f"Sent: {transaction['transaction_id']} | {transaction['amount']} KES")
        time.sleep(random.uniform(0.5, 3))

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

if __name__ == "__main__":
    run_producer()
