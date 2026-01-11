import csv
import json
import random
import time
import argparse
import os
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()

SERVICES = ['payment-service', 'inventory-service', 'user-service', 'auth-service', 'notification-service']
LEVELS = ['INFO', 'WARNING', 'ERROR', 'DEBUG']
ACTIONS = ['login', 'logout', 'view_product', 'add_to_cart', 'checkout', 'payment_processed', 'payment_failed']

def generate_ecommerce_log():
    timestamp = datetime.now() - timedelta(minutes=random.randint(0, 10000))
    level = random.choices(LEVELS, weights=[50, 20, 10, 20])[0]
    service = random.choice(SERVICES)
    action = random.choice(ACTIONS)
    user_id = fake.uuid4()
    
    message = f"User {user_id} performed {action}"
    if level == 'ERROR':
        message += f" - Failed due to {fake.sentence()}"
        
    return {
        "timestamp": timestamp.isoformat(),
        "level": level,
        "service": service,
        "user_id": user_id,
        "action": action,
        "message": message,
        "ip_address": fake.ipv4(),
        "response_time_ms": random.randint(10, 500)
    }

def save_csv(logs, filename):
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=logs[0].keys())
        writer.writeheader()
        writer.writerows(logs)
    print(f"Generated {len(logs)} logs to {filename}")

def save_json(logs, filename):
    with open(filename, 'w') as f:
        json.dump(logs, f, indent=2)
    print(f"Generated {len(logs)} logs to {filename}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate test logs')
    parser.add_argument('--count', type=int, default=100, help='Number of logs to generate')
    parser.add_argument('--format', choices=['csv', 'json', 'both'], default='both', help='Output format')
    parser.add_argument('--scenario', default='ecommerce', help='Scenario (ignored for now)')
    
    args = parser.parse_args()
    
    logs = [generate_ecommerce_log() for _ in range(args.count)]
    
    os.makedirs('data/test', exist_ok=True)
    
    if args.format in ['csv', 'both']:
        save_csv(logs, f"data/test/ecommerce_logs_{int(time.time())}.csv")
        
    if args.format in ['json', 'both']:
        save_json(logs, f"data/test/ecommerce_logs_{int(time.time())}.json")
