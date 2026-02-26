# One-time migration script to move existing connections.jsonl data into SQLite database
# Run once after database.py is set up, before switching honeypot.py to use the database

import json
import os
from database import initialize_db, insert_record

JSONL_FILE = "/data/connections.jsonl"

def migrate():
    if not os.path.exists(JSONL_FILE):
        print(f"No file found at {JSONL_FILE}, nothing to migrate")
        return
    
    initialize_db()
    
    migrated = 0
    failed = 0
    
    with open(JSONL_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
                
                # Handle old records missing geolocation fields
                record.setdefault('country', 'Unknown')
                record.setdefault('city', 'Unknown')
                record.setdefault('lat', 0)
                record.setdefault('lon', 0)
                record.setdefault('client_banner', None)
                record.setdefault('credentials', [])
                
                insert_record(record)
                migrated += 1
            except Exception as e:
                print(f"Failed to migrate record: {e}")
                failed += 1
    
    print(f"Migration complete: {migrated} records migrated, {failed} failed")

if __name__ == "__main__":
    migrate()