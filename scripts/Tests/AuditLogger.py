import json
from datetime import datetime

def log_verified_event(event_data):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = (
        f"[{timestamp}] AID: {event_data['aid'][:10]}... | "
        f"SN: {event_data['sn']} | "
        f"HASH: {event_data['event_hash'][:10]} | "
        f"STATUS: VERIFIED & ANCHORED\n"
    )
    
    with open("scada_audit_trail.txt", "a") as f:
        f.write(log_entry)
    
    print(f"Audit Log Updated: {log_entry.strip()}")

# Load your anchor file and log it
with open("blockchain_anchor.json", "r") as f:
    data = json.load(f)
    log_verified_event(data)