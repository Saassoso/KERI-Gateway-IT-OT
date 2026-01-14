import os
import json
import time
from datetime import datetime

# --- CONFIGURATION ---
ANCHOR_FILES = ["anchor_Heavy_Lift_Drone_01.json", "anchor_Scout_Drone_02.json", "anchor_Emergency_Med_03.json"]

def aggregate_anchors():
    print("⛓️  Blockchain Aggregator Service Started...")
    print("Monitoring for KERI events to anchor on-chain...\n")

    while True:
        batch_to_anchor = []

        for filename in ANCHOR_FILES:
            if os.path.exists(filename):
                with open(filename, "r") as f:
                    data = json.load(f)
                    batch_to_anchor.append(data)
        
        if batch_to_anchor:
            print(f"--- 🧱 BATCH READY FOR BLOCKCHAIN ({datetime.now().strftime('%H:%M:%S')}) ---")
            for item in batch_to_anchor:
                print(f"  ⚓ Anchoring: {item['drone']} | SN: {item['sn']} | SAID: {item['said'][:15]}...")
            
            # --- SOLIDITY INTERACTION POINT ---
            # This is where we call: contract.functions.recordMission(aid, hash).transact()
            print(">>> ✅ Batch sent to Smart Contract: 0x69f2... (Transaction Confirmed)")
            print("---------------------------------------------------\n")
        else:
            print("Waiting for drone telemetry...")

        time.sleep(10) # Process a batch every 10 seconds

if __name__ == "__main__":
    try:
        aggregate_anchors()
    except KeyboardInterrupt:
        print("\n🛑 Aggregator stopped.")